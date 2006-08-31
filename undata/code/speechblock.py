import re
from unmisc import unexception, IsNotQuiet, MarkupLinks
from voteblock import recvoterequest
from nations import FixNationName, nonnations


#<b>Mr. Al-Mahmoud </b>(Qatar) (<i>spoke in Arabic</i>):
respek = """(?x)<b>([^<]*?)\s*</b>   # group 1  speaker name
			(?:\s*\((?:<i>)?(?!interpretation|spoke)([^\)<]*)(?:</i>)?\))?  # group 2  nation
			(?:,\s(?:Rapporteur|President|Chairman|Vice-Chairperson)\sof\sthe\s
				(.{0,130}?\s(?:Committee|Council|panel|People|Rwanda)(?:\s\([^\)]*\))?))?  # group 3 committee rapporteur
			(?:\s\(((?:Acting\s)?(?:Chairman|Rapporteur)\sof\sthe\s(?:Ad\sHoc\s|Special\s)?Committee\s.{0,140}?)\))?  # group 4 extra chairman setting
			(?:\s*(?:\(|<i>)+
				(?:spoke\sin|interpretation\sfrom)\s(\w+)    # group 5  speaker language
				(?:.{0,60}?the\sdelegation)?   # translated by [their] delegation
			(?:\)|</i>)+)?
			\s*
			(?:<i>:</i>|<b>\s*:\s*</b>|:)
			\s*"""

# use this to disentangle failures in the above regexp
#respekSS = """(?x)<b>([^<]*?)\s*</b>   # group 1  speaker name
#			(?:\s*\((?:<i>)?(?!interpretation|spoke)([^\)<]*)(?:</i>)?\))?  # group 2  nation
#			(?:,\s(?:Rapporteur|President|Chairman)\sof\sthe\s
#				(.{0,60}?\s(?:Committee|Council)(?:\s\([^\)]*\))?))?  # group 3 committee rapporteur
#			(?:\s\((Chairman\sof\sthe\sCommittee\s.{0,90}?)\))?  # group 4 extra chairman setting
#"""

#<b>The President</b>  (<i>spoke in French</i>):
respekp1 = """(?x)<b>(The\sPresident)\s*</b>
			  (?:\s*\(([^\)<]*)\))?\s*
			  (dummy)?
			  (dummy)?
			  (?:\(<i>?:spoke\sin\s(\w+)</i>\))?
			  \s*:\s*"""
respekp2 = """(?x)<b>\s*(The\sPresident)\s*</b>
			  (dummy)?
			  (dummy)?
			  (dummy)?
			  (?:\s|\(|</?i>|</?b>)+
			      (?:spoke\sin|interpretation\sfrom)\s(\w+)
			  (?:\)|</i>|</?b>)+
			  \s*(?:<[ib]>)?:\s*(?:</[ib]>)?\s*"""
respekp3 = """(?x)<b>\s*(.{0,20}?(?:President|King|Sultan|Secretary-General).{0,20}?)\s*(?:</b>\s*:|:\s*</b>)
			  (dummy)?
			  (dummy)?
			  (dummy)?
			  (dummy)?
			  """

reboldline = """(?x)<b>.*?</b>
					(
					\(|\)|
					</?i>|\s|
					continued|and|
					Rev\.|L\.|Add\.|Corr\.|
					(?:para(?:graph|\.)|sect(?:ion|\.)|[Cc]hap(?:ter|\.)|draft\sresolution)\s[A-Z0-9]|
					Parts?|
					HIV|AIDS|CRP\.|rule|
					A/|/|\d|,|;|-|I|X|[A-Z]-
					)*$"""

def DetectSpeaker(ptext, indents, paranum, speakerbeforetookchair):

	#print ptext, "\n\n\n"
	if re.match("<i>(?:In favour|Against|Abstaining)", ptext): # should be part of a voteblock
		print ptext
		#print tlcall[i - 1].paratext
		assert False

	indentationerror = ""
	if len(indents) == 1 and indents[0][0] == 0:
		indentationerror = "unindented-paragraph"
	if len(indents) > 2:
		indentationerror = "too many different indents"
	if len(indents) == 2 and indents[1][0] != 0:
		indentationerror = "un-left-justified paragraph"

	mspek = re.match(respekp1, ptext)
	if not mspek:
		mspek = re.match(respekp2, ptext)
	if not mspek:
		mspek = re.match(respekp3, ptext)
	if not mspek:
		mspek = re.match(respek, ptext)

	if not mspek and re.match("<[ib]>", ptext):
		speakerbeforetookchair = ""

	if mspek or speakerbeforetookchair:
		if indentationerror == "unindented-paragraph" and speakerbeforetookchair:
			indentationerror = False
		if indentationerror == "unindented-paragraph" and paranum.undocname in [ "A-55-PV.60", "A-55-PV.63", "A-55-PV.64", "A-55-PV.68", "A-55-PV.59", "A-55-PV.44", "A-55-PV.46", "A-55-PV.48", "A-55-PV.49", "A-55-PV.52", "A-55-PV.56", "A-55-PV.51" ]:
			indentationerror = False
		if indentationerror:
			print ptext
			print indents
			raise unexception(indentationerror + " of speaker-intro", paranum)

	#if not mspek:
	#	m = re.match(respekSS, ptext)
	#	print ptext
	#	print "   ___ ", m and m.group(0)
	if mspek:
		assert not indentationerror
		assert not re.match("<i>", ptext)
		nation = ""
		if mspek.group(2):
			lnation = mspek.group(2)
			if lnation in nonnations:
				nation = lnation
			else:
				nation = FixNationName(lnation, paranum.sdate)
			if not nation:
				print ptext
				print "\ncheck if misspelt or new nonnation: ", lnation
				raise unexception("unrecognized nation or nonnation", paranum)
		assert mspek.group(1)
		typ = "spoken"
		currentspeaker = (mspek.group(1), nation, mspek.group(5) or "")
		ptext = ptext[mspek.end(0):]
		if re.search("</b>", ptext):
			print ptext
			raise unexception("bold in spoken text", paranum)

	elif speakerbeforetookchair:
		assert not indentationerror
		typ = "spoken"
		currentspeaker = speakerbeforetookchair
		#print "Continuation speaker", speakerbeforetookchair

	# non-spoken text
	else:
		#<b>Mr. Al-Mahmoud </b>(Qatar) (<i>spoke in Arabic</i>):
		if re.match("<b>.*?(?:</b>.*?:|:</b>)(?!</b>$)", ptext):
			print ptext
			raise unexception("improperly detected spoken text", paranum)

		if re.match("<i>", ptext):
			mballots = re.search("Number of ballot papers", ptext)
			if mballots:
				#print "BALLOT:", ptext, "\n"
				indentationerror = False

			if indentationerror:
				print ptext
				print indents
				raise unexception(indentationerror + " of unspoken text", paranum)

			if not mballots:
				mptext = re.match("<i>(.*?)</i>\s*(?:\((?:resolutions?|decision|draft resolution) ([\d/]*\s*(?:[A-Z]{1,2}|[A-Z] (?:and|to) [A-Z])?)\))?\.?$", ptext)
				if not mptext:
					print "--%s--" % ptext
					raise unexception("improper italicline", paranum)

			ptext = re.sub("</?[ib]>", "", ptext).strip()

			# further parsing of these phrases may take place in due course
			msodecided = re.match("It was so decided(?: \(decision [\d/]*\s*(?:A|B|C|A and B)?\))?\.?$", ptext)
			mwasadopted = re.match(".*?(?:resolution|decision|agenda|amendment).*?(?:was|were) adopted", ptext)
			mcalledorder = re.match("The meeting (?:was called to order|rose|was suspended|was adjourned) at", ptext)
			mtookchair = re.match("\s*(?:In the absence of the President, )?(.*?)(?:, \(?Vice[\-\s]President\)?,)? (?:took|in) the [Cc]hair\.?$", ptext)
			mretchair = re.match("The President (?:returned to|in) the Chair.$", ptext)
			mescort = re.search("(?:was escorted|escorted the.*?) (?:(?:from|to) the (?:rostrum|podium)|(?:from|into|to its place in) the (?:General Assembly Hall|Conference Room))\.?$", ptext)
			msecball = re.search("A vote was taken by secret ballot\.(?: The meeting was suspended at|$)", ptext)
			mminsil = re.search("The members of the General Assembly observed a minute of (?:silent prayer (?:or|and) meditation|silence)\.$", ptext)
			mtellers = re.search("At the invitation of the (?:Acting )?President,.*?acted as tellers\.$", ptext)
			mmisc = re.search("The Acting President drew the following.*?from the box|sang.*?for the General Assembly", ptext)
			melected = re.search("Having obtained (?:the required (?:two-thirds )?|an absolute )majority.*?(?:(?:were|was|been) s?elected|will be included [io]n the list)", ptext)

			if not (msodecided or mwasadopted or mcalledorder or mtookchair or mretchair or mballots or mescort or msecball or mminsil or mtellers or mmisc or melected):
				print "unrecognized--%s--" % ptext
				print re.match("(?:In the absence of the President, )?(.*?)(?:, \(?Vice[\-\s]President\)?,)? (?:took|in) the Chair\.$", ptext)
				raise unexception("unrecognized italicline", paranum)

			# we can add subtypes to these italic-lines
			typ = "italicline"
			if mtookchair or mretchair:
				typ = "italicline-tookchair"
			currentspeaker = None

		elif re.match("<b>", ptext):
			if not re.match(reboldline, ptext):
				print ptext
				raise unexception("unrecognized bold completion", paranum)
			ptext = re.sub("</?b>", "", ptext)
			typ = "boldline"
			currentspeaker = None

		else:
			typ = "unknown"
			print ptext, indents
			raise unexception("possible indent failure", paranum)

	return ptext, typ, currentspeaker

def CleanupTags(ptext, typ, paranum):
	assert typ in ["italicline", "italicline-tookchair", "boldline", "spoken"]
	if typ == "boldline":
		ptext = re.sub("</?b>", "", ptext)
	if typ == "spoken":
		if re.match("<i>\(spoke in \w+(?:\)|.*?delegation\))</i>", ptext):
			pass	# could put in a type for this
		elif re.match("<i>.*?</i>[\s\.\-]?$", ptext):
			print ptext
			raise unexception("total italics in spoken text", paranum)
		elif re.search("<[^/i]+>", ptext):
			print ptext
			raise unexception("other than italics in spoken text", paranum)
	return ptext

class SpeechBlock:
	def DetectEndSpeech(self, ptext, lastindent, sdate):
		if re.match(recvoterequest, ptext):
			return True
		if re.match("<b>.*?</b>.*?:(?!</b>$)", ptext):
			return True
		if re.match("<b>\s*The(?: Acting)? President", ptext):
			return True
		if re.match("<[ib]>.*?</[ib]>\s\(resolution [\d/AB]*\)\.$", ptext):
			return True
		if re.match(".{0,40}?<i>.{0,40}?(?:resolution|decision|amendment).{0,60}?was adopted.{0,40}$", ptext):
			return True
		if re.match(".{0,40}?was so decided.{0,40}?$", ptext):
			return True
		if re.match("<i>\s*The meeting (?:was called to order|rose|was suspended|was adjourned).{0,60}?$", ptext):
			return True
		if re.match("<i>A vote was taken", ptext):
			return True
		if re.match("<i>.*?was escorted", ptext):
			return True
		if re.match("<i>.*?(?:took|returned to) the [Cc]hair", ptext):
			return True
		if re.match("<i>\s*The members of the General Assembly observed .{0,80}?$", ptext):
			return True

		# anything bold
		if re.match("<b>.*?</b>$", ptext):
			return True
		if re.match("<b>", ptext):
			return True

		if re.match("<i>\(spoke in \w+(?:\)|.*?delegation\))</i>$", ptext):
			return False

		# total italics
		if re.match("<i>.*?</i>[\s\.\-]?$", ptext):
			return True

		return False


	def __init__(self, tlcall, i, lundocname, lsdate, speakerbeforetookchair):
		self.tlcall = tlcall
		self.i = i
		self.sdate = lsdate
		self.undocname = lundocname
		self.pageno, self.paranum = tlcall[i].txls[0].pageno, tlcall[i].paranum
		# paranum = ( undocname, sdate, tlc.txls[0].pageno, paranumber )
		self.gid = self.paranum.MakeGid()

		tlc = self.tlcall[self.i]
		#print tlc.indents, tlc.paratext
		ptext, self.typ, self.speaker = DetectSpeaker(tlc.paratext, tlc.indents, self.paranum, speakerbeforetookchair)
		ptext = MarkupLinks(CleanupTags(ptext, self.typ, self.paranum))
		self.i += 1
		if self.typ in ["italicline", "italicline-tookchair"]:
			self.paragraphs = [ (None, ptext) ]
			return

		# series of boldlines
		if self.typ == "boldline":
			blinepara = tlc.lastindent and "blockquote" or "p"
			if re.match("Agenda item (\d+)", ptext):
				blinepara = "boldline-agenda"
			self.paragraphs = [ (blinepara, ptext) ]
			while self.i < len(self.tlcall):
				tlc = self.tlcall[self.i]
				if not re.match(reboldline, tlc.paratext):
					break
				ptext = MarkupLinks(CleanupTags(tlc.paratext, self.typ, self.paranum))
				self.paragraphs.append((tlc.lastindent and "boldline-indent" or "boldline-p", ptext))
				self.i += 1
			return

		# actual spoken section
		assert self.typ == "spoken"
		assert not tlc.lastindent or len(tlc.indents) == 1 # doesn't happen in first paragraph of speech
		self.paragraphs = [ ("p", ptext) ]
		while self.i < len(self.tlcall):
			tlc = self.tlcall[self.i]
			if self.DetectEndSpeech(tlc.paratext, tlc.lastindent, self.sdate):
				break
			ptext = MarkupLinks(CleanupTags(tlc.paratext, self.typ, self.paranum))
			bIndent = (len(tlc.indents) == 1) and (tlc.indents[0][0] != 0) and (tlc.indents[0][1] > 1)
			self.paragraphs.append(((bIndent and "blockquote" or "p"), ptext))
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
			fout.write('\t<div class="spokentext">\n')
		for para in self.paragraphs:
			#print para[1]
			if re.search("</?b>", para[1]):
				print self.typ, para[1]
				assert False
			if not para[0]:
				fout.write('\t%s\n' % para[1])
			else:
				fout.write('\t<div class="%s">%s</div>\n' % (para[0], para[1]))
		if self.typ == "spoken":
			fout.write('\t</div>\n')
		fout.write('</div>\n')

