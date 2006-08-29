import os
import re
from nations import FixNationName, FixSpeakerNationName, GenerateNationsVoteList
from paranum import paranum
from unexception import unexception

#	<blockquote><i>A recorded vote was taken.</i></blockquote>
#	<blockquote><i>In favour:</i> Algeria, Andorra, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bangladesh, Belarus, Belgium, Brazil, Brunei Darussalam, Bulgaria, Burkina Faso, Cameroon, Canada, Cape Verde, Chad, Chile, Colombia, Costa Rica, Côte d'Ivoire, Cuba, Cyprus, Czech Republic, Denmark, Djibouti, Dominican Republic, Ecuador, Egypt, El Salvador, Estonia, Ethiopia, Finland, France, Georgia, Germany, Ghana, Greece, Guinea, Guinea-Bissau, Guyana, Hungary, Indonesia, Iran (Islamic Republic of), Ireland, Israel, Italy, Jamaica, Japan, Kazakhstan, Kuwait, Latvia, Libyan Arab Jamahiriya, Liechtenstein, Lithuania, Luxembourg, Malaysia, Maldives, Mali, Malta, Mauritius, Mexico, Micronesia (Federated States of), Monaco, Mongolia, Morocco, Mozambique, Myanmar, Namibia, Netherlands, New Zealand, Nicaragua, Niger, Norway, Oman, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Republic of Korea, Republic of Moldova, Romania, San Marino, Saudi Arabia, Senegal, Singapore, Slovakia, Slovenia, South Africa, Spain, Sri Lanka, Sudan, Suriname, Swaziland, Sweden, Thailand, the former Yugoslav Republic of Macedonia, Togo, Tunisia, Turkey, Ukraine, United Arab Emirates, United Kingdom of Great Britain and Northern Ireland, United Republic of Tanzania, United States of America, Uruguay, Vanuatu, Venezuela, Yemen</blockquote>
#	<blockquote><i>Against:</i> Democratic People's Republic of Korea</blockquote>
#	<blockquote><i>Abstaining:</i> Bhutan, Botswana, China, India, Lao People's Democratic Republic, Pakistan, Syrian Arab Republic, Viet Nam</blockquote>

voteblocks = [ ]
undoclinks = "http://seagrass.goatchurch.org.uk/~undocs/cgi-bin/getundoc.py?doc="
recvoterequest = "A recorded vote has been requested|(?:<i>)?A recorded vote was taken|<i>In favour"

def MarkupLinks(paratext):
	stext = re.split("(A/\d+/[\w\d\.]*?\d+(?:/(?:Add|Rev)\.\d+)?|resolution \d+/\d+|</b>\s*<b>|</i>\s*<i>)(?!=\s)", paratext)
	res = [ ]
	for st in stext:
		mres = re.match("resolution (\d+/\d+)", st)
		mdoc = re.match("A/\d+/\S*", st)
		mcan = re.match("</b>\s*<b>|</i>\s*<i>", st)
		if mres:
			res.append('<a href="%sA/RES/%s">%s</a>' % (undoclinks, mres.group(1), st))
		elif mdoc:
			res.append('<a href="%s%s">%s</a>' % (undoclinks, st, st))
		elif mcan:
			res.append(' ')
		else:
			res.append(st)
	return "".join(res)


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
			assert False
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


class VoteBlock:
	# problem is overflowing paragraphs across pages, where double barrelled country names can get split
	def DetectNationList(self, ptext, fromlast):
		bforce = (not not fromlast)
		if fromlast and fromlast not in ["FIRST", "ANDLIST"]:
			print "carryingforward $%s$" % fromlast
			ptext = "%s %s" % (fromlast, ptext)
		if ptext == "None":
			return "presentcomplete", [ ], None
		ptext = re.sub("</?i>", "", ptext)
		votelist = [ c.strip()  for c in re.split("[,\.]", ptext)  if not re.match("\s*$", c) ]

		if fromlast == "ANDLIST":
			#print "vvvv", votelist
			assert votelist
			if not FixNationName(votelist[-1], self.sdate):
				mand = re.search("(.*?) and (.*)$", votelist[-1])
				if mand:
					votelist[-1] = mand.group(1)
					votelist.append(mand.group(2))

		if re.match("<i>", ptext):
			if bforce:
				print fromlast, bforce, ptext
				assert False
			return "nothingmore", -1, -1

		if votelist and not FixNationName(votelist[-1], self.sdate) and (ptext[-1] != ",") and fromlast != "ANDLIST":
			carryforward = votelist[-1]
			votelist = votelist[:-1]
		else:
			carryforward = None

		res = [ ]
		fres = [ ]
		for lnation in votelist:
			nation = FixNationName(lnation, self.sdate)
			if not nation and fromlast == "ANDLIST" and re.match("[Tt]he ", lnation):
				nation = FixNationName(lnation[4:], self.sdate)
			if nation:
				if nation != "INVALID":
					res.append(nation)
			else:
				fres.append(lnation)
		if bforce and fres:
			print "****", fres
			print "cccccc", carryforward
			assert False
		if res and not fres:
			return "present", res, carryforward
		if bforce:
			assert not fres
			return "presentblank", res, ""  # the "In favour" is followed by a new page
		#print fres
		return "nothingmore", -1, -1

	def DetectVote(self, votere):
		tlc = self.tlcall[self.i]
		votem = re.match(votere, tlc.paratext)
		if not votem:
			# missing abstain column case
			if re.match("<i>(?:The )?[Dd]raft|<b>The President|<i>Operative paragraph", tlc.paratext) \
				and re.search("Abstain", votere):
				# and self.undocname in ["A-53-PV.81", "A-55-PV.103", "A-55-PV.83", "A-55-PV.86", "A-56-PV.105", "A-56-PV.68", "A-56-PV.82", "A-56-PV.86", "A-57-PV.57", "A-57-PV.66", "A-57-PV.77", "A-58-PV.55", "A-58-PV.72"]:
				return [ ]
			if self.undocname in ["A-55-PV.44"] and re.search("Against", votere) and re.match("<i>Abstaining", tlc.paratext):
				return [ ]
			print "failed with:", votere, tlc.paratext

		#print tlc.paratext
		mess, natlist, carryforward = self.DetectNationList(tlc.paratext[votem.end(0):].strip(), "FIRST")
		assert mess != "nothingmore"
		self.i += 1

		# deal with nation names merging across pages.
		while True:
			mess, cnatlist, carryforward = self.DetectNationList(self.tlcall[self.i].paratext, carryforward)
			if mess == "nothingmore":
				#print self.tlcall[self.i].paratext
				break
			natlist.extend(cnatlist)
			self.i += 1
		return natlist

	#<blockquote indent="31"><i>Draft resolution A/53/L.52 was adopted by 149 votes</i> <i>to 1, with 7 abstentions </i>(resolution 53/37).</blockquote>

	#  and the following should affect the vote, by making it Haiti: absent/favour
	#<blockquote indent="32">[Subsequently, the delegations of Haiti and Mozambique informed the Secretariat that they had intended to vote in favour.]</blockquote>
	def DetectAdoption(self):
		adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
		madtext = re.search("(adopted|carried|retained.*?|rejected)(?:, as amended,|, as a whole,)?\s+by(?: votes)?\s+(\d+)(?:\s+votes)? to\s+(\d+|none)(?:,? with (\d+) abstentions?)?", adtext)
		if not madtext:
			madtext = re.match("(By)\s+(\d+)(?:\s+votes)? to\s+(\d+|none)(?:,? with (\d+) abstentions?)?", adtext)
		if not madtext:
			print "====", self.i, adtext
		ifavour = int(madtext.group(2))
		iagainst = (madtext.group(3) != "none" and int(madtext.group(3)) or 0)
		if madtext.group(1) == "rejected":
			i = ifavour;  ifavour = iagainst;  iagainst = i
		iabstain = (madtext.group(4) and int(madtext.group(4)) or 0)
		il = (ifavour, iagainst, iabstain)
		ivl = (len(self.vlfavour), len(self.vlagainst), len(self.vlabstain))
		if il != ivl:
			print "wrong-count", self.undocname, il, ivl
			# wrong values are found on A-57-PV.73 s(favour=154, 152)
			assert self.undocname in [ "A-56-PV.82", "A-57-PV.73" ]
		self.motiontext = MarkupLinks(adtext)
		self.i += 1

	def DetectSubsequentVoteChange(self, gnv):
		adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
		msubseq = re.match("\[Subsequently,? (.*?)\.\]", adtext)
		self.votechanges = {}
		if not msubseq:
			assert not re.search("Subsequently", adtext)
			return

		for sadtext in re.split(";\s*", msubseq.group(1)):
			if not sadtext:
				continue
			msadtext = re.match("the delegations? of (.*?) (?:informed|advised) the Secretariat that (?:it|they) had intended to (vote in favour|vote against|abstain)$", sadtext)
			if not msadtext:
				msadtext = re.match("the delegation of (.*?)(?:(?:informed|advised) the Secretariat that (?:it|they))? had (not) intended to participate$", sadtext)
			if not msadtext:
				msadtext = re.match("the delegation of (.*?) had intended to (abstain)$", sadtext)
			if not msadtext:
				print "--- ---", sadtext
				assert False

			mess, natlist, carryforward = self.DetectNationList(msadtext.group(1), "ANDLIST")
			assert natlist
			#print sadtext, msadtext.group(1)
			#print natlist, "(", msadtext.group(2)
			assert not carryforward
			for nat in natlist:
				assert nat not in self.votechanges
				if re.search("favour", msadtext.group(2)):
					vch = "favour"
				elif re.search("against", msadtext.group(2)):
					vch = "against"
				elif re.search("abstain", msadtext.group(2)):
					vch = "abstain"
				elif re.search("not", msadtext.group(2)):
					vch = "absent"
				else:
					assert False
				self.votechanges[nat] = vch

		self.votechange = adtext
		self.i += 1

		for nat in self.votechanges:
			gnv[nat] = "%s/%s" % (gnv[nat], self.votechanges[nat])


	def __init__(self, tlcall, i, lundocname, lsdate):
		self.tlcall = tlcall
		self.i = i
		self.sdate = lsdate
		self.undocname = lundocname
		
		self.pageno, self.paranum = tlcall[i].txls[0].pageno, tlcall[i].paranum

		if re.match("A recorded vote has been requested(?: for this item|\. We shall now begin the voting process|<i>\.</i>)?\.?$", tlcall[self.i].paratext):
			self.i += 1
		if re.match("(?:<i>)?\s*A recorded vote was taken\.?\s*(?:</i>)?\.?$", tlcall[self.i].paratext):
			self.i += 1
		if not (self.i != i or self.undocname == "A-55-PV.86"):
			print tlcall[self.i].paratext
			print tlcall[self.i - 1].paratext
			assert False

		self.vlfavour = self.DetectVote("<i>In(?:</i> <i>| )favour:?\s*</i>:?")
		self.vlagainst = self.DetectVote("(?:<i>)?Against:?\s*(?:</i>)?:?")
		self.vlabstain = self.DetectVote("(?:<i>)?Abstaining:?(?:</i>)?:?")
		gnv, self.vlabsent = GenerateNationsVoteList(self.vlfavour, self.vlagainst, self.vlabstain, self.sdate)
		self.votecount = "favour=%d against=%d abstain=%d absent=%d" % (len(self.vlfavour), len(self.vlagainst), len(self.vlabstain), len(self.vlabsent))
		#print "  ", self.votecount
		self.DetectAdoption()
		self.DetectSubsequentVoteChange(gnv)

		#res = [ '\t\t<div style="border:1px solid black; margin-left:2em"><b>VOTE ', votecount, "</b><br>\n", "\t\t<i>", self.motiontext, "</i>\n" ]
		#res.append('\t\t<div style="font-size:6">')
		lvotelist = [ ]
		for gn in sorted(gnv.items()):
			lvotelist.append("<span>%s:<i>%s</i></span>" % gn)
		self.votelist = " ".join(lvotelist)
		#res.append("</div></div>\n")
		#self.parafout = "".join(res)
		self.typ = "vote"

	def writeblock(self, fout):
		fout.write("\n")
		fout.write('<div class="recvote">\n')
		fout.write('\t<div class="motiontext">%s</div>\n' % self.motiontext)
		fout.write('\t<div class="votecount">%s</div>\n' % self.votecount)
		fout.write('\t<div class="votelist">%s</div>\n' % self.votelist)
		fout.write('</div>\n')

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


def GroupParas(tlcall, undocname, sdate):
	res = [ ]
	i = 0
	currentspeaker = None
	while i < len(tlcall):
		tlc = tlcall[i]
		if re.match(recvoterequest, tlc.paratext):
			voteblock = VoteBlock(tlcall, i, undocname, sdate)
			voteblocks.append(voteblock)
			res.append(voteblock)
			i = voteblock.i

		# non-voting line to be processed
		else:
			speechblock = SpeechBlock(tlcall, i, undocname, sdate)
			res.append(speechblock)
			i = speechblock.i

	return res


