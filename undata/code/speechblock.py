import re
from unmisc import unexception, IsNotQuiet, MarkupLinks
from voteblock import recvoterequest
from nations import FixNationName, FixSpeakerNationName


#<b>Mr. Al-Mahmoud </b>(Qatar) (<i>spoke in Arabic</i>):
respek = """(?x)<b>([^<]*?)\s*</b>   # group 1  speaker name
			(?:\s*\((?:<i>)?(?!interpretation|spoke)([^\)<]*)(?:</i>)?\))?  # group 2  nation
			(?:,\sRapporteur\sof\sthe\s(.{0,60}?\sCommittee(?:\s\([^\)]*\))?))?  # group 3  committee rapporteur
			(?:\s*(?:\(|<i>)+
				(?:spoke\sin|interpretation\sfrom)\s(\w+)    # group 4  speaker language
				(?:.{0,60}?the\sdelegation)?   # translated by [their] delegation
			(?:\)|</i>)+)?
			\s*(?:<i>)?:(?:</i>)?\s*"""
#<b>The President</b>  (<i>spoke in French</i>):
respekp1 = """(?x)<b>(The\sPresident)\s*</b>
			  (?:\s*\(([^\)<]*)\))?\s*
			  (dummy)?
			  (?:\(<i>?:spoke\sin\s(\w+)</i>\))?
			  \s*:\s*"""
respekp2 = """(?x)<b>(The\sPresident)\s*</b>
			  (dummy)?
			  (dummy)?
			  (?:\s|\(|</?i>|</?b>)+
			      (?:spoke\sin|interpretation\sfrom)\s(\w+)
			  (?:\)|</i>|</?b>)+
			  \s*(?:<[ib]>)?:(?:</[ib]>)?\s*"""
respekp3 = """(?x)<b>(The(?:\sActing)?\sPresident)\s*:\s*</b>
			  (dummy)?
			  (dummy)?
			  (dummy)?
			  """

def DetectSpeaker(ptext, lastindent, paranum):
	#print ptext, "\n\n\n"
	if re.match("<i>(?:In favour|Against|Abstaining)", ptext): # should be part of a voteblock
		print ptext
		#print tlcall[i - 1].paratext
		assert False

	mspek = re.match(respekp1, ptext)
	if not mspek:
		mspek = re.match(respekp2, ptext)
	if not mspek:
		mspek = re.match(respekp3, ptext)
	if not mspek:
		mspek = re.match(respek, ptext)
	if mspek:
		#print "&&&&& ", mspek.groups()
		assert not lastindent
		assert not re.match("<i>", ptext)
		nation = ""
		if mspek.group(2):
			nation = FixSpeakerNationName(mspek.group(2), paranum.sdate)
			if not nation:
				print ptext
				print "----unknown speakernation", mspek.group(2)
				assert False
		assert mspek.group(1)
		typ = "spoken"
		currentspeaker = (mspek.group(1), nation, mspek.group(4) or "")

		ptext = ptext[mspek.end(0):]

	# non-spoken text
	if not mspek:
		#<b>Mr. Al-Mahmoud </b>(Qatar) (<i>spoke in Arabic</i>):
		if re.match("<b>.*?</b>.*?:(?!</b>$)", ptext):
			print ptext
			raise unexception("unmatched spoken text", paranum)
		if lastindent and re.match("<i>", ptext):
			mptext = re.match("<i>(.*?)</i>\s*(?:\(resolution ([\d/]*)\))?\.?$", ptext)
			if not mptext:
				print ptext
				assert False
			ptext = re.sub("</?i>", "", ptext)
			if re.match("It was so decided\.", ptext):
				pass
			elif re.match(".*?(?:resolution|decision).*?was adopted", ptext):
				pass
			elif re.match("The meeting (?:was called to order|rose) at", ptext):
				pass
			else:
				print "unrecognized--", ptext
			typ = "italicline"
			currentspeaker = None

		elif re.match("<b>", ptext):
			if not re.match("<b>.*?</b>(\(|\)|</?i>|\s|continued)*$", ptext):
				print ptext
				assert False
			ptext = re.sub("</?b>", "", ptext)
			typ = "boldline"
			currentspeaker = None

		else:
			typ = "unknown"
			print ptext
			assert False
			currentspeaker = None

	return ptext, typ, currentspeaker


class SpeechBlock:
	def DetectEndSpeech(self, ptext, lastindent, sdate):
		if re.match(recvoterequest, ptext):
			return True
		if re.match("<b>.*?</b>.*?:(?!</b>$)", ptext):
			return True
		if re.match("<[ib]>.*?</[ib]>\s\(resolution [\d/]*\)\.$", ptext):
			#print "----eee-", ptext
			return True
		if re.match(".{0,40}?<i>.{0,40}?(?:resolution|decision).{0,40}?was adopted.{0,40}$", ptext):
			#print "----fff-", ptext
			return True
		if re.match(".{0,40}?was so decided.{0,40}?$", ptext):
			#print "---sss--", ptext
			return True
		return False


	def __init__(self, tlcall, i, lundocname, lsdate):
		self.tlcall = tlcall
		self.i = i
		self.sdate = lsdate
		self.undocname = lundocname
		self.pageno, self.paranum = tlcall[i].txls[0].pageno, tlcall[i].paranum
		# paranum = ( undocname, sdate, tlc.txls[0].pageno, paranumber )
		self.gid = self.paranum.MakeGid()

		tlc = self.tlcall[self.i]
		ptext, self.typ, self.speaker = DetectSpeaker(tlc.paratext, tlc.lastindent, self.paranum)
		ptext = MarkupLinks(ptext)
		self.i += 1
		if self.typ == "italicline":
			self.paragraphs = [ (None, ptext) ]
			return

		## series of boldlines
		if self.typ == "boldline":
			blinepara = tlc.lastindent and "blockquote" or "p"
			if re.match("Agenda item (\d+)", ptext):
				blinepara = "agenda"
			self.paragraphs = [ (blinepara, ptext) ]
			while self.i < len(self.tlcall):
				tlc = self.tlcall[self.i]
				mptext = re.match("<b>(.*?)</b>$", tlc.paratext)
				if not mptext:
					break
				ptext = mptext.group(1)
				ptext = MarkupLinks(ptext)
				self.paragraphs.append((tlc.lastindent and "blockquote" or "p", ptext))
				self.i += 1
			return

		# actual spoken section
		assert self.typ == "spoken"
		assert not tlc.lastindent # doesn't happen in first paragraph of speech
		self.paragraphs = [ ("p", ptext) ]
		while self.i < len(self.tlcall):
			tlc = self.tlcall[self.i]
			if self.DetectEndSpeech(tlc.paratext, tlc.lastindent, self.sdate):
				break
			ptext = MarkupLinks(tlc.paratext)
			self.paragraphs.append((tlc.lastindent and "blockquote" or "p", ptext))
			self.i += 1

	def writeblock(self, fout):
		fout.write("\n")
		fout.write('<div class="%s" id="%s">\n' % (self.typ, self.gid))
		if self.typ == "spoken":
			fout.write('<span class="speaker" name="%s" nation="%s" language="%s">\n' % self.speaker)
			fout.write('\t%s' % self.speaker[0])
			if self.speaker[1]:
				fout.write(' (%s)' % self.speaker[1])
			fout.write('\n</span>\n')

		if self.typ == "spoken":
			fout.write('<div class="spokentext">\n')
		for para in self.paragraphs:
			if not para[0]:
				fout.write('\t%s\n' % para[1])
			#elif para[0] in ["p", "blockquote"]:
			#	fout.write('\t<%s>%s</%s>\n' % (para[0], para[1], para[0]))
			else:
				fout.write('\t<div class="%s">%s</div>\n' % (para[0], para[1]))
		if self.typ == "spoken":
			fout.write('</div>\n')
		fout.write('</div>\n')

