import os
import re
from nations import FixNationName
from unmisc import unexception, paranumC

page1bit = '<page number="1" position="absolute" top="0" left="0" height="1188" width="918">(?:\s*<fontspec[^>]*>|\s)*$'
pageibit = '<page number="(\d+)" position="absolute" top="0" left="0" height="1188" width="918">(?:\s*<fontspec[^>]*>|\s)*(?=<text)'
pagebitmap = '<page number="(\d+)" position="absolute" top="0" left="0" height="1141" width="852">\s*$'
footertext = '<i><b>\*\d+v?n?\*\s*</b></i>|\*\d+\*|<i><b>\*</b></i>|<i><b>\d</b></i>|(?:\d* )?\d*-\d*S? \(E\)|`````````'
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def StripPageTags(xfil):
	xpages = re.findall("(<page.*\s[\s\S]*?)</page>", xfil)
	mpage1head = re.match("([\s\S]*?)(?=<text)", xpages[0])
	#print len(xpages), undoc
	if not mpage1head:
		print " -- bitmap type"
		for xpage in xpages:
			assert re.match(pagebitmap, xpage)
		return False
	if not re.match(page1bit, mpage1head.group(1)):
		print "Probably is a bitmap type"
		print mpage1head.group(1)
		assert False
	res = [ xpages[0][mpage1head.end(0):] ]

	for i in range(1, len(xpages)):
		mpageihead = re.match(pageibit, xpages[i])
		assert int(mpageihead.group(1)) == i + 1
		res.append(xpages[i][mpageihead.end(0):])
	return res



#<text top="1062" left="342" width="486" height="11" font="2">xxxx</text>
class TextLine:
	def __init__(self, txline, lundocname, lpageno, textcountnumber):
		mxline = re.match('<text top="(\d+)" left="(\d+)" width="-?(\d+)" height="(\d+)" font="(\d+)">(.*?)</text>', txline)
		if not mxline:
			print txline
		self.top = int(mxline.group(1))
		self.left = int(mxline.group(2))
		self.width = int(mxline.group(3))
		self.height = int(mxline.group(4))
		self.font = int(mxline.group(5))
		self.pageno = lpageno
		self.undocname = lundocname
		self.textcountnumber = textcountnumber
		self.ltext = mxline.group(6).strip()

		if re.match("<[ib]>\s*</[ib]>$", self.ltext):
			self.ltext = ""

		# will be removed
		if not self.ltext:
			return

		self.bfootertype = (self.left < 459 and self.left + self.width > 459) or re.match(footertext, self.ltext)
		#if self.bfootertype:
		#	print self.ltext

		# move on any short bits that are like 13^(th)
		if self.height == 11 and not self.bfootertype and self.width <= 10:
			#print self.left, self.width, "'%s'" % self.ltext
			assert self.width <= 10
			assert self.ltext in ["th", "rd", "st", "nd"]
			self.top += 2  # push the step down from 16 to 18

def TextLineTopKey(textline):
	return (textline.top, textline.left)


class TextLineCluster:
	def __init__(self, ltxl):
		if ltxl:
			self.txls = [ ltxl ]
			self.indents = [ [ltxl.indent, 1] ]

	def AddLine(self, ltxl):
		if ltxl.vgap != 0:
			if self.indents[-1][0] != ltxl.indent:
				self.indents.append([ltxl.indent, 1])
			else:
				self.indents[-1][1] += 1
		self.txls.append(ltxl)

# work backwards looking for paragraph heads
def AppendToCluster(txlcol, txl):
	if not txlcol:
		txlcol.append(TextLineCluster(txl))
		return
	txl.vgap = txl.top - txlcol[-1].txls[-1].top
	#print txlcol[-1].txls[-1].ltext
	#print txl.vgap, txl.width, txl.height, txl.top,  txl.ltext  # zzzz
	if not txl.vgap in (0, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 43, 45, 48, 53, 54, 55, 63, 72, 83):
		print "vgap=", txl.vgap, txl.width, txl.height, txl.top,  txl.ltext  # zzzz
		raise unexception("vgap not familiar", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
	if txl.vgap in (0, 17, 18, 19) or txl.vgap == 0:
		txlcol[-1].AddLine(txl)
	else:
		txlcol.append(TextLineCluster(txl))

def AppendCluster(res, tlc, sclusttype):
	# check if we should merge to the next paragraph
	assert sclusttype in ["gapcluster", "newpage", "newcolumn"]

	if res and sclusttype != "gapcluster":
		# likely continuation of paragraph
		if len(tlc.indents) == 1 and tlc.indents[0][0] == res[-1].indents[-1][0]:
			td0 = res[-1].txls[-1].ltext[:3]
			td1 = tlc.txls[0].ltext[:3]
			if not re.match("<[ib]>", td0):
				td0 = ""
			if not re.match("<[ib]>", td1):
				td1 = ""
			if td0 == td1:
				res[-1].txls.extend(tlc.txls)
				return
			#else:
			#	print "----", tlc.txls[0].ltext


	# new cluster; check the indenting pattern is good
	if len(tlc.indents) == 2:
		if tlc.indents[0] <= tlc.indents[1]:
			#print tlc.indents, tlc.txls[0].ltext
			#assert re.match("<[ib]>.*?</[ib]>", tlc.txls[0].ltext) # <i>In favour:</i>
			pass

	# two paragraphs may have been merged, try to separate them out
	elif len(tlc.indents) == 4 and tlc.indents[0][0] == tlc.indents[2][0] and tlc.indents[1][0] == tlc.indents[3][0]:
		#print tlc.indents
		#print tlc.txls[0].ltext
		assert tlc.indents[0][0] == tlc.indents[2][0]
		assert tlc.indents[1][0] == tlc.indents[3][0]
		si = tlc.indents[2][1]
		tlcf = TextLineCluster(None)
		tlcf.txls = tlc.txls[:si]
		del tlc.txls[:si]
		tlcf.indents = tlc.indents[:2]
		del tlc.indents[:2]
		res.append(tlcf)
		#print tlcf.indents, tlc.indents

	elif len(tlc.indents) != 1:
		print tlc.indents
		prevtop = -1
		for txl in tlc.txls:
			if prevtop == txl.top:
				print " ",
			print txl.indent, txl.ltext
			prevtop = txl.top
		raise unexception("unrecognized indent pattern", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
		assert False
	res.append(tlc)
	return


# maybe shouldn't be a class
class TextPage:
	def ExtractDotLineChair(self, txlines, ih):
		assert self.pageno == 1
		#<text top="334" left="185" width="584" height="17" font="2">Mr.  Kavan  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . (Czech Republic)</text>
		while True:
			#print "------" + txlines[ih].ltext
			mchair = re.search("([^>]*?)\s*\. \. \. \. \.", txlines[ih].ltext)
			if mchair:
				break

			# fix missing year date
			if self.undocname == "A-55-PV.44" and txlines[ih].ltext == "Monday, 30 October, 10 a.m.":
				txlines[ih].ltext = "Monday, 30 October 2000, 10 a.m."

			# extract the date out if poss
			mdate = re.match("\w+\s*, (\d+)\s+(\w+)\s+(\d+),\s*(?:at )?(\d+)\.?(\d*)(?: ([ap])\.?m\.?)?(?: \(closed\))?$", txlines[ih].ltext)
			if mdate:  #Tuesday, 3 December 2002, 10 a.m.
				#print txlines[ih].ltext
				iday = int(mdate.group(1))
				imonth = mdate.group(2) == "Octoberr" and 9 or months.index(mdate.group(2))
				syear = mdate.group(3)
				ihour = int(mdate.group(4))
				imin = mdate.group(5) and int(mdate.group(5)) or 0
				if mdate.group(6) and mdate.group(6) == "p":
					ihour += 12
				if self.date:
					raise unexception("date redefined", paranumC(txlines[ih].undocname, None, 0, -1, txlines[ih].textcountnumber))
				self.date = "%s-%02d-%02d %02d:%02d" % (syear, imonth + 1, iday, ihour, imin)
			ih += 1
			if ih == len(txlines):
				return -1

		if not self.date:
			for i in range(ih):
				print "--%s--" % txlines[i].ltext
			raise unexception("dotlinechair date problem", paranumC(txlines[ih].undocname, None, 0, -1, txlines[ih].textcountnumber))
			assert False

		# when country name for the president . . . . is not on same line
		mcountry = re.search("\((.*?)\)$", txlines[ih].ltext)
		if not mcountry:
			ih += 1
			#print txlines[ih].ltext
			mcountry = re.match("\((.*?)\)$", txlines[ih].ltext)
			if not mcountry:
				print txlines[ih].ltext
				raise unexception("unable to extract country from  ...-line", paranumC(txlines[ih].undocname, None, 0, -1, txlines[ih].textcountnumber))
		ih += 1
		self.chairs.append((mchair.group(1), FixNationName(mcountry.group(1), self.date)))
		return ih

	def ExtractDotLineChairHead(self, txlines):
		self.date = None
		self.chairs = [ ]
		ih = self.ExtractDotLineChair(txlines, 0)
		ihcochair = self.ExtractDotLineChair(txlines, ih)

		if ihcochair != -1:
			return ihcochair
		return ih


	def __init__(self, xpage, lundocname, lpageno, textcountnumber):
		self.pageno = lpageno
		self.undocname = lundocname
		self.textcountnumber = textcountnumber

		leftcolstart = 90
		rightcolstart = re.match("A-5[1234]", lundocname) and 481 or 468
		rightcolstartindentincrement = re.match("A-5[12]", lundocname) and 1 or 0  # adds an offset to non-zero values

		# generate the list of lines, sorted by vertical position
		ftxlines = re.findall("<text.*?</text>", xpage)

		txlines = [ ]
		for txline in ftxlines:
			txl = TextLine(txline, lundocname, lpageno, self.textcountnumber)
			self.textcountnumber += 1
			if txl.ltext:
				if txlines and txlines[-1].bfootertype and txlines[-1].top == txl.top:
					txl.bfootertype = True
				txlines.append(txl)
		txlines.sort(key=TextLineTopKey)

		# the half divider is at 459

		# try to separate out the header and footers
		if self.pageno == 1:
			ih = self.ExtractDotLineChairHead(txlines)
			#for Dtxl in txlines[-10:]:
			#	print Dtxl.top, Dtxl.left, Dtxl.ltext

			ie = len(txlines) - 1
			while txlines[ie].bfootertype:
				#print "FOOTER:", txlines[ie].ltext
				ie -= 1
			#print "**NON-FOOTER:", txlines[ie].ltext
			ie += 1

		else:
			if re.match("<b>\w/\d+/PV.\d+\s*</b>", txlines[0].ltext):
				ih = 1
			else:
				#print txlines[2].ltext
				assert re.match("General Assembly", txlines[0].ltext)
				assert re.match("\d+(?:th|st|nd|rd) (?:plenary )?meeting", txlines[1].ltext)
				assert re.match("\S+ [Ss]ession", txlines[2].ltext)
				assert re.match("\d+ \w+ \d\d\d\d", txlines[3].ltext)
				ih = 4;
			ie = len(txlines) - 1
			if re.match("\d\d\-\d\d\d\d\d", txlines[ie].ltext):
				ie -= 1
			pagenumtext = re.sub("<..?>", "", txlines[ie].ltext).strip()
			if re.match("\d\d\-\d\d\d\d\d", txlines[ie - 1].ltext):
				ie -= 1
			if not re.match("\d+$", pagenumtext):
				print "jjjj", pagenumtext
				raise unexception("pagenum error not a number", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))
			if int(pagenumtext) != self.pageno:
				raise unexception("pagenum error of speaker-intro", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))

		# separate out the header and footers
		self.txlheader = txlines[:ih]
		self.txlfooter = txlines[ie:]

		# separate the body into the two columns
		self.txlcol1 = [ ]
		self.txlcol2 = [ ]
		self.minindentleft = 9999
		self.minindentright = 9999
		for txl in txlines[ih:ie]:
			if txl.left < 459:
				#print txl.bfootertype, txl.left, txl.width, txl.top, txl.ltext  # zzzz
				# there's a bit of spilling out where the region is larger than it should be for the words as in A-56-PV.64
				if not (txl.left + txl.width <= 459):
					if txl.left + txl.width > 501:
						print txl.left, txl.width, txl.left + txl.width
						print txl.ltext
						raise unexception("right-hand extension excessive", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
					if not (txl.left <= 165):
						bc = -1
						while True:
							assert self.txlcol1[-1].txls[bc].top == txl.top  # in-line but shorter
							if (self.txlcol1[-1].txls[bc].left <= 165):
								break
							bc -= 1

				txl.indent = txl.left - leftcolstart
				assert txl.indent >= 0
				self.minindentleft = min(txl.indent, self.minindentleft)
				txl.brightcol = False
				AppendToCluster(self.txlcol1, txl)

			else:
				txl.indent = txl.left - rightcolstart
				if txl.indent:
					txl.indent += rightcolstartindentincrement
				if txl.indent < 0:
					print txl.indent
					print txl.ltext
					raise unexception("negative indent on righthand column", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
				self.minindentright = min(txl.indent, self.minindentright)
				txl.brightcol = True
				AppendToCluster(self.txlcol2, txl)

		#if self.txlcol1 and self.minindentleft != 0:
		#	print "minindentleft", self.minindentleft
		#if self.txlcol2 and self.minindentright != 0:
		#	print "minindentright", self.minindentright

# clusters are paragraphs after the lines have been clustered together
def GlueUnfile(xfil, undocname):
	xpages = StripPageTags(xfil)
	if not xpages:
		return None, None, None  # bitmap type encountered
	txpages = [ ]
	tlcall = [ ]
	for i in range(len(xpages)):
		txpage = TextPage(xpages[i], undocname, i + 1, (txpages or 0) and txpages[-1].textcountnumber)
		txpages.append(txpage)
		if txpage.txlcol1:
			AppendCluster(tlcall, txpage.txlcol1[0], "newpage")
			for tlc in txpage.txlcol1[1:]:
				AppendCluster(tlcall, tlc, "gapcluster")
		else:
			assert i == len(xpages) - 1

		# have had a case where the first column was the blank one
		if txpage.txlcol2:
			AppendCluster(tlcall, txpage.txlcol2[0], "newcolumn")
			for tlc in txpage.txlcol2[1:]:
				AppendCluster(tlcall, tlc, "gapcluster")
		else:
			assert i == len(xpages) - 1

	# assign ids to the clusters
	sdate = txpages[0].date
	paranumlast = paranumC(undocname, sdate, 0, -1, tlc.txls[0].textcountnumber)
	for tlc in tlcall:
		if tlc.txls[0].pageno == paranumlast.pageno:
			paranumlast = paranumC(undocname, sdate, paranumlast.pageno, paranumlast.paragraphno + 1, tlc.txls[0].textcountnumber)
		else:
			paranumlast = paranumC(undocname, sdate, tlc.txls[0].pageno, 1, tlc.txls[0].textcountnumber)
		tlc.paranum = paranumlast


	# merge the lines together and remove double bold/italics that happen across lines
	for tlc in tlcall:
		jparatext = [ ]  # don't insert spaces where there is a hyphen
		for txl in tlc.txls:
			if jparatext and not (re.search("\w-$", jparatext[-1]) and re.match("\w", txl.ltext)):
				jparatext.append(" ")
			jparatext.append(txl.ltext)
		tlc.paratext = "".join(jparatext)
		tlc.paratext = re.sub("-</i> <i>", "-", tlc.paratext)
		tlc.paratext = re.sub("\s*(?:</i>\s*<i>|</b>\s*<b>|<b>\s*</b>|<i>\s*</i>|<b>\s*<i>\s*</b>\s*</i>)\s*", " ", tlc.paratext)
		tlc.paratext = tlc.paratext.strip()
		tlc.paratext = re.sub("^<b>(The(?: Acting)? Co-Chairperson) \(([^\)]*)\)\s*(?:</b>\s*:|:\s*</b>)", "<b>\\1</b> (\\2):", tlc.paratext)
		tlc.lastindent = tlc.indents[-1][0]

	return sdate, txpages[0].chairs, tlcall




