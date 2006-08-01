import os
import re
from nations import FixNationName, GenerateNationsVoteList


#	<blockquote><i>A recorded vote was taken.</i></blockquote>
#	<blockquote><i>In favour:</i> Algeria, Andorra, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bangladesh, Belarus, Belgium, Brazil, Brunei Darussalam, Bulgaria, Burkina Faso, Cameroon, Canada, Cape Verde, Chad, Chile, Colombia, Costa Rica, Côte d'Ivoire, Cuba, Cyprus, Czech Republic, Denmark, Djibouti, Dominican Republic, Ecuador, Egypt, El Salvador, Estonia, Ethiopia, Finland, France, Georgia, Germany, Ghana, Greece, Guinea, Guinea-Bissau, Guyana, Hungary, Indonesia, Iran (Islamic Republic of), Ireland, Israel, Italy, Jamaica, Japan, Kazakhstan, Kuwait, Latvia, Libyan Arab Jamahiriya, Liechtenstein, Lithuania, Luxembourg, Malaysia, Maldives, Mali, Malta, Mauritius, Mexico, Micronesia (Federated States of), Monaco, Mongolia, Morocco, Mozambique, Myanmar, Namibia, Netherlands, New Zealand, Nicaragua, Niger, Norway, Oman, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Republic of Korea, Republic of Moldova, Romania, San Marino, Saudi Arabia, Senegal, Singapore, Slovakia, Slovenia, South Africa, Spain, Sri Lanka, Sudan, Suriname, Swaziland, Sweden, Thailand, the former Yugoslav Republic of Macedonia, Togo, Tunisia, Turkey, Ukraine, United Arab Emirates, United Kingdom of Great Britain and Northern Ireland, United Republic of Tanzania, United States of America, Uruguay, Vanuatu, Venezuela, Yemen</blockquote>
#	<blockquote><i>Against:</i> Democratic People's Republic of Korea</blockquote>
#	<blockquote><i>Abstaining:</i> Bhutan, Botswana, China, India, Lao People's Democratic Republic, Pakistan, Syrian Arab Republic, Viet Nam</blockquote>

voteblocks = [ ]

class VoteBlock:

	# problem is overflowing paragraphs across pages, where double barrelled country names can get split
	def DetectNationList(self, ptext, fromlast):
		bforce = (not not fromlast)
		if fromlast and fromlast != "FIRST":
			print "carryingforward $%s$" % fromlast
			ptext = "%s %s" % (fromlast, ptext)
		if ptext == "None":
			return "presentcomplete", [ ], None
		ptext = re.sub("</?i>", "", ptext)
		votelist = [ c.strip()  for c in re.split("[,\.]", ptext)  if not re.match("\s*$", c) ]
		if re.match("<i>", ptext):
			if bforce:
				print fromlast, bforce, ptext
				assert False
			return "nothingmore", -1, -1

		if votelist and not FixNationName(votelist[-1], self.sdate) and (ptext[-1] != ","):
			carryforward = votelist[-1]
			votelist = votelist[:-1]
		else:
			carryforward = None

		res = [ ]
		fres = [ ]
		for lnation in votelist:
			nation = FixNationName(lnation, self.sdate)
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
		self.motiontext = adtext
		self.i += 1

	def DetectSubsequentVoteChange(self):
		adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
		msubseq = re.match("\[Subsequently,? (.*?)\.\]", adtext)
		if not msubseq:
			print adtext
			assert not re.search("Subsequently", adtext)
			self.votechange = ""
			return

		for sadtext in re.split(";\s*", msubseq.group(1)):
			if not sadtext:
				continue
			msadtext = re.match("the delegations? of (.*?) (?:informed|advised) the Secretariat that (?:it|they) had intended to (vote in favour|vote against|abstain)$", sadtext)
			if not msadtext:
				msadtext = re.match("the delegation of (.*?) had (not) intended to participate$", sadtext)
			if not msadtext:
				print "------", sadtext
				assert False
		self.votechange = adtext
		self.i += 1

	def __init__(self, tlcall, i, lundocname, lsdate):
		self.tlcall = tlcall
		self.i = i
		self.sdate = lsdate
		self.undocname = lundocname
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
		votecount = "favour=%d against=%d abstain=%d absent=%d" % (len(self.vlfavour), len(self.vlagainst), len(self.vlabstain), len(self.vlabsent))
		print votecount
		self.DetectAdoption()
		self.DetectSubsequentVoteChange()

		res = [ "\t\t<h1>VOTE ", votecount, "</h1>\t\t" ]
		res.append("<p>")
		for gn in gnv:
			res.append("<span>%s: %s</span>" % gn)
		res.append("</p>\n")
		self.parafout = "".join(res)


def FindVoteTriplets(tlcall, undocname, sdate):
	i = 0
	while i < len(tlcall):
		tlc = tlcall[i]
		if re.match("A recorded vote has been requested|(?:<i>)?A recorded vote was taken|<i>In favour", tlc.paratext):
			voteblock = VoteBlock(tlcall, i, undocname, sdate)
			voteblocks.append(voteblock)
			tlc.parafout = voteblock.parafout

			# erase the lines which have been rolled into the voteblock
			i += 1
			while i < voteblock.i:
				tlcall[i].parafout = ""
				i += 1

		# non-voting line to be processed
		else:
			if re.match("<i>(?:In favour|Against|Abstaining)", tlc.paratext): # should be part of a voteblock
				print tlc.paratext
				print tlcall[i - 1].paratext
				assert False
			lastindent = tlc.indents[-1][0]
			if lastindent:
				tlc.parafout = '\t<blockquote indent="%d">%s</blockquote>\n' % (lastindent, tlc.paratext)
			else:
				tlc.parafout = '<p>%s</p>\n' % (tlc.paratext)
			i += 1

def ParseUnfile(undocname, sdate, tlcall):
	FindVoteTriplets(tlcall, undocname, sdate)

