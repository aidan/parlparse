import os
import re

page1bit = '<page number="1" position="absolute" top="0" left="0" height="1188" width="918">(?:\s*<fontspec[^>]*>|\s)*$'
pageibit = '<page number="(\d+)" position="absolute" top="0" left="0" height="1188" width="918">(?:\s*<fontspec[^>]*>|\s)*(?=<text)'
footertext = '<i><b>\*\d+v?n?\*\s*</b></i>|\*\d+\*|<i><b>\*</b></i>|<i><b>\d</b></i>|(?:\d* )?\d*-\d*S? \(E\)|`````````'

def StripPageTags(xfil):
	xpages = re.findall("(<page.*\s[\s\S]*?)</page>", xfil)
	mpage1head = re.match("([\s\S]*?)(?=<text)", xpages[0])
	#print len(xpages), undoc
	assert re.match(page1bit, mpage1head.group(1)) # fails for bitmap type pdfs
	res = [ xpages[0][mpage1head.end(0):] ]

	for i in range(1, len(xpages)):
		mpageihead = re.match(pageibit, xpages[i])
		assert int(mpageihead.group(1)) == i + 1
		res.append(xpages[i][mpageihead.end(0):])
	return res


textlinefixes = { 		# fix case in A-58-PV.84
	('A-53-PV.4', '<text top="181" left="481" width="179" height="14" font="1">prices and the Russian crisis.</text>'): ("top", -18),
	('A-53-PV.26', '<text top="253" left="516" width="281" height="14" font="1">take up arms, even traditional weapons --</text>'): ("left", -4),
	('A-53-PV.28', '<text top="604" left="159" width="290" height="17" font="6"><b> alovski </b>(the former Yugoslav Republic of</text>'): ("top", +3),  # overflowing line of poetry
	('A-53-PV.41', '<text top="628" left="547" width="281" height="17" font="6"><b> alovski </b>(The former Yugoslav Republic of</text>'): ("top", +3),  # overflowing line of poetry

	('A-54-PV.9', '<text top="613" left="95" width="52" height="14" font="1">response</text>'): ("left", -5),
	('A-54-PV.26', '<text top="955" left="522" width="55" height="14" font="1">too hard.</text>'): ("top", -18),  # overflowing line of poetry
	('A-54-PV.35', '<text top="268" left="159" width="290" height="17" font="5"><b> alovski </b>(the former Yugoslav Republic of</text>'): ("top", +3),  # overflowing line of poetry

	('A-55-PV.3', '<text top="943" left="110" width="67" height="14" font="3">* A/55/150.</text>'): "remove",
	('A-55-PV.4', '<text top="352" left="575" width="251" height="17" font="2">(President of the Republic of Namibia)</text>'): ("top", +2),
	('A-55-PV.5', '<text top="352" left="575" width="251" height="17" font="2">(President of the Republic of Namibia)</text>'): ("top", +2),
	('A-55-PV.6', '<text top="336" left="333" width="228" height="14" font="3">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</text>'): ("top", -2),
	('A-55-PV.6', '<text top="354" left="325" width="235" height="14" font="3">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</text>'): ("top", -2),
	('A-55-PV.7', '<text top="354" left="333" width="220" height="14" font="3">. . . . . . . . . . . . . . . . . . . . . . . . . . . . .</text>'): ("top", -2),
	('A-55-PV.8', '<text top="360" left="310" width="228" height="14" font="3">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</text>'): ("top", -2),
	('A-55-PV.10', '<text top="506" left="386" width="8" height="11" font="8">th</text>'): ("top", +1),
	('A-55-PV.25', '<text top="336" left="271" width="375" height="14" font="3">. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .</text>'): ("top", -2),
	('A-55-PV.28', '<text top="868" left="226" width="224" height="18" font="9">International Committee of the</text>'): ("top", +2),
	('A-55-PV.28', '<text top="886" left="90" width="133" height="18" font="9">Red Cross (ICRC)</text>'): ("top", +2),
	('A-55-PV.50', '<text top="605" left="332" width="8" height="11" font="12">th</text>'): ("top", +1),
	('A-55-PV.69', '<text top="537" left="126" width="324" height="17" font="2">Albania, Algeria, Andorra, Angola, Antigua and</text>'): ("left", -3),
	('A-55-PV.69', '<text top="429" left="126" width="324" height="17" font="2">Albania, Andorra, Angola, Antigua and Barbuda,</text>'): ("left", -3),
	('A-55-PV.69', '<text top="726" left="504" width="324" height="17" font="2">Algeria, Bahrain, China, Democratic People\'s</text>'): ("left", -2),
	('A-55-PV.73', '<text top="832" left="90" width="311" height="18" font="8">International Committee of the Red Cross </text>'): ("top", +2),
	('A-55-PV.81', '<text top="371" left="185" width="1" height="2" font="7">3</text>'): "remove",

	('A-56-PV.79', '<text top="532" left="301" width="76" height="12" font="9">together</text>'): ("top", -4),
	('A-56-PV.79', '<text top="550" left="369" width="76" height="12" font="9">together</text>'): ("top", -4),
	('A-56-PV.62', '<text top="371" left="268" width="4" height="2" font="7">*   *   *</text>'): "remove",

	('A-57-PV.66', '<text top="654" left="126" width="324" height="17" font="2">Albania, Andorra, Argentina, Australia, Austria,</text>'): ("left", -1),
	('A-57-PV.79', '<text top="491" left="546" width="9" height="17" font="11"><b>ø</b></text>'): ("top", +1),

	('A-58-PV.84', '<text top="988" left="571" width="67" height="17" font="10">Ecuador</text>'): ("top", -1),
	('A-58-PV.54', '<text top="889" left="275" width="174" height="15" font="9">Economic Commission for</text>'): ("top", -1),
	('A-58-PV.54', '<text top="907" left="90" width="273" height="15" font="9">Latin America and the Caribbean (ECLAC)</text>'): ("top", -1),
	('A-58-PV.16', '<text top="187" left="90" width="218" height="17" font="10">Saint Kitts and Nevis</text>'): ("top", -1),
	('A-58-PV.20', '<text top="1017" left="469" width="349" height="14" font="10"><i>Note</i>: Solomon Islands pidgin for: "Thank you for helping your</text>'): "remove",
	('A-58-PV.20', '<text top="1031" left="502" width="42" height="14" font="3">friend".</text>'): "remove",

	# these ones happen on multiple pages
	('A-59-PV.38', '<text top="511" left="303" width="146" height="15" font="9">Economic and Social</text>'): ("top", -1),
	('A-59-PV.38', '<text top="529" left="90" width="239" height="15" font="9">Commission for Asia and the Pacific</text>'): ("top", -1),
	('A-59-PV.58', '<text top="970" left="411" width="7" height="15" font="9">. </text>'): ("top", -1),
	('A-59-PV.60', '<text top="745" left="530" width="9" height="17" font="9">,</text>'): ("top", -1),
	('A-59-PV.65', '<text top="648" left="248" width="202" height="20" font="8"> General Assembly the reports</text>'): ("top", +3),
	('A-59-PV.69', '<text top="185" left="691" width="16" height="17" font="9">  (</text>'): ("top", +1),
	('A-59-PV.115', '<text top="1084" left="788" width="43" height="12" font="14">05-43909 </text>'): "remove",
	('A-59-PV.115', '<text top="1084" left="90" width="43" height="12" font="14">05-43909 </text>'): "remove",
				}

#<text top="1062" left="342" width="486" height="11" font="2">xxxx</text>
class TextLine:
	def __init__(self, txline, lundocname, lpageno):
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
		self.ltext = mxline.group(6).strip()

		if re.match("<[ib]>\s*</[ib]>$", self.ltext):
			self.ltext = ""

		# will be removed
		if not self.ltext:
			return
		if re.search("recorded vote", self.ltext):
			print self.ltext

		textlinefix = textlinefixes.get((self.undocname, txline))
		if not textlinefix:
			pass
		elif textlinefix == "remove":
			print textlinefix, txline
			self.ltext = ""
			return
		elif textlinefix[0] == "left":
			print textlinefix, txline
			self.left += textlinefix[1]
		elif textlinefix[0] == "top":
			print textlinefix, txline
			self.top += textlinefix[1]
		else:
			assert not textlinefix

		self.bfootertype = (self.left < 459 and self.left + self.width > 459) or re.match(footertext, self.ltext)

		# move on any short bits that are like 13^(th)
		if self.height == 11 and not self.bfootertype and self.width <= 10:
			print self.left, self.width, "'%s'" % self.ltext
			assert self.width <= 10
			assert self.ltext in ["th", "rd", "st", "nd"]
			self.top += 2  # push the step down from 16 to 18

def TextLineTopKey(textline):
	return (textline.top, textline.left)


class TextLineCluster:
	def __init__(self, ltxl):
		if ltxl:
			self.txls = [ ltxl ]
			self.indents = [ (ltxl.indent, 0) ]

	def AddLine(self, ltxl):
		if ltxl.vgap != 0:
			if self.indents[-1][0] != ltxl.indent:
				self.indents.append((ltxl.indent, len(self.txls)))
		self.txls.append(ltxl)

# work backwards looking for paragraph heads
def AppendToCluster(txlcol, txl):
	if not txlcol:
		txlcol.append(TextLineCluster(txl))
		return
	txl.vgap = txl.top - txlcol[-1].txls[-1].top
	#print txlcol[-1].txls[-1].ltext
	#print txl.vgap, txl.width, txl.height, txl.top,  txl.ltext  # zzzz
	if not txl.vgap in (0, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 31, 34, 35, 36, 37, 43, 45, 48, 53, 54, 55, 63, 72):
		print txl.vgap, txl.width, txl.height, txl.top,  txl.ltext  # zzzz
		assert False
	if txl.vgap in (0, 17, 18, 19) or txl.vgap == 0:
		txlcol[-1].AddLine(txl)
	else:
		txlcol.append(TextLineCluster(txl))

def AppendCluster(res, tlc, sclusttype):
	# check if we should merge to the next paragraph
	if res and sclusttype != "gapcluster":

		# likely continuation of paragraph
		if len(res[-1].indents) == 2:
			if len(tlc.indents) == 1 and tlc.indents[0][0] == res[-1].indents[-1][0]:
				res[-1].txls.extend(tlc.txls)
				return
		# possible continuation of blocked-type paragraph
		else:
			assert len(res[-1].indents) == 1
			if len(tlc.indents) == 1 and res[-1].indents[0][0] == tlc.indents[0][0]:
				res[-1].txls.extend(tlc.txls)
				return

	# new cluster; check the indenting pattern is good
	if len(tlc.indents) == 2:
		if tlc.indents[0] <= tlc.indents[1]:
			#print tlc.indents, tlc.txls[0].ltext
			#assert re.match("<[ib]>.*?</[ib]>", tlc.txls[0].ltext) # <i>In favour:</i>
			pass

	# two paragraphs may have been merged, try to separate them out
	elif len(tlc.indents) == 4:
		print tlc.indents
		print tlc.txls[0].ltext
		assert tlc.indents[0][0] == tlc.indents[2][0]
		assert tlc.indents[1][0] == tlc.indents[3][0]
		si = tlc.indents[2][1]
		tlcf = TextLineCluster(None)
		tlcf.txls = tlc.txls[:si]
		del tlc.txls[:si]
		tlcf.indents = tlc.indents[:2]
		del tlc.indents[:2]
		tlcf.bindent = (tlcf.indents[-1][0] != 0)
		res.append(tlcf)
		#print tlcf.indents, tlc.indents

	elif len(tlc.indents) != 1:
		print tlc.indents
		for txl in tlc.txls:
			print txl.indent, txl.ltext
		assert False
	tlc.bindent = (tlc.indents[-1][0] != 0)
	res.append(tlc)
	return


# maybe shouldn't be a class
class TextPage:
	def ExtractDotLineChair(self, txlines, ih):
		assert self.pageno == 1
		#<text top="334" left="185" width="584" height="17" font="2">Mr.  Kavan  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . (Czech Republic)</text>
		while not re.search("\. \. \. \. \.", txlines[ih].ltext):
			# extract the date out if poss
			if re.match("\w+, \d+ \w+ \d+, \d+ [ap].m.", txlines[ih].ltext):  #Tuesday, 3 December 2002, 10 a.m.
				self.date = txlines[ih].ltext
				print self.date
			ih += 1
			if ih == len(txlines):
				return -1

		# country name is not on same line
		if not re.search("\(.*?\)$", txlines[ih].ltext):
			ih += 1
			print txlines[ih].ltext
			assert re.match("\(.*?\)$", txlines[ih].ltext)
		ih += 1
		return ih

	def ExtractDotLineChairHead(self, txlines):
		#for ih in range(21):
		#	print txlines[ih].top, txlines[ih].left, txlines[ih].ltext
		ih = self.ExtractDotLineChair(txlines, 0)
		ihcochair = self.ExtractDotLineChair(txlines, ih)
		if ihcochair != -1:
			return ihcochair
		return ih


	def __init__(self, xpage, lundocname, lpageno):
		self.pageno = lpageno
		self.undocname = lundocname

		# generate the list of lines, sorted by vertical position
		ftxlines = re.findall("<text.*?</text>", xpage)

		txlines = [ ]
		for txline in ftxlines:
			txl = TextLine(txline, lundocname, lpageno)
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
				ie -= 1
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
			#print txlines[ie].ltext
			assert int(re.sub("<..?>", "", txlines[ie].ltext)) == self.pageno

		# separate out the header and footers
		self.txlheader = txlines[:ih]
		self.txlfooter = txlines[ie:]

		# separate the body into the two columns
		self.txlcol1 = [ ]
		self.txlcol2 = [ ]
		for txl in txlines[ih:ie]:
			if txl.left < 459:
				#print txl.bfootertype, txl.left, txl.width, txl.top, txl.ltext  # zzzz
				# there's a bit of spilling out where the region is larger than it should be for the words as in A-56-PV.64
				if not (txl.left + txl.width <= 459):
					assert (txl.left + txl.width <= 501)
					if not (txl.left <= 165):
						bc = -1
						while True:
							assert self.txlcol1[-1].txls[bc].top == txl.top  # in-line but shorter
							if (self.txlcol1[-1].txls[bc].left <= 165):
								break
							bc -= 1

				txl.indent = txl.left - 90
				txl.brightcol = False
				AppendToCluster(self.txlcol1, txl)
			else:
				txl.indent = txl.left - 468
				txl.brightcol = True
				AppendToCluster(self.txlcol2, txl)
			assert txl.indent >= 0


def ParseUnfile(xfil, undocname):
	xpages = StripPageTags(xfil)
	txpages = [ ]
	res = [ ]
	for i in range(len(xpages)):
		txpage = TextPage(xpages[i], undocname, i + 1)
		txpages.append(txpage)
		if txpage.txlcol1:
			AppendCluster(res, txpage.txlcol1[0], "newpage")
			for tlc in txpage.txlcol1[1:]:
				AppendCluster(res, tlc, "gapcluster")
		else:
			assert i == len(xpages) - 1

		# have had a case where the first column was the blank one
		if txpage.txlcol2:
			AppendCluster(res, txpage.txlcol2[0], "newcolumn")
			for tlc in txpage.txlcol2[1:]:
				AppendCluster(res, tlc, "gapcluster")
		else:
			assert i == len(xpages) - 1
	return res


# the main function
for undoc in os.listdir("pdfxml"):
	undocname = os.path.splitext(undoc)[0]
	undochtml = os.path.join("html", undocname + ".html")
	undocpdf = os.path.join("pdfxml", undoc)

	# too hard.  too many indent problems (usually secret ballot announcementing)
	if undocname in ["A-53-PV.39", "A-53-PV.52"
					 "A-54-PV.34", "A-54-PV.45",
					 "A-55-PV.33", "A-55-PV.99",
					 "A-56-PV.32", "A-56-PV.81"]:
		continue

	if not re.match("A-53-PV.5", undoc):
		continue
	print "----------------",  undoc

	fin = open(undocpdf)
	xfil = fin.read()
	fin.close()

	res = ParseUnfile(xfil, undocname)

	h = open(undochtml, "w")
	for tlc in res:
		h.write(tlc.bindent and "<blockquote>\n" or "<p>\n")
		h.write("\n".join([txl.ltext  for txl in tlc.txls]))
		h.write(tlc.bindent and "\n</blockquote>\n" or "\n</p>\n")
	h.close()


