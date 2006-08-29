import os
import re
import sys
from nations import FixNationName, nonnations, GenerateNationsVoteList
from paranum import paranum
from unmisc import unexception, IsNotQuiet, MarkupLinks
from unglue import GlueUnfile
from speechblock import SpeechBlock
from voteblock import VoteBlock, recvoterequest

voteblocks = [ ]




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



def ParsetoHTML(stem, pdfxmldir, htmldir, bforceparse):
	undocnames = [ ]
	for undoc in os.listdir(pdfxmldir):
		undocname = os.path.splitext(undoc)[0]

		# too hard.  too many indent problems (usually secret ballot announcementing)
		if undocname in ["A-53-PV.39", "A-53-PV.52",
						 "A-54-PV.34", "A-54-PV.45",
						 "A-55-PV.33", "A-55-PV.99",
						 "A-56-PV.32", "A-56-PV.81"]:
			continue
		if not re.match(stem, undocname):
			continue
		if not bforceparse:
			undochtml = os.path.join(htmldir, undocname + ".html")
			if os.path.isfile(undochtml):
				continue
		undocnames.append(undocname)

	if IsNotQuiet():
		print "Preparing to parse %d files" % len(undocnames)

	for undocname in undocnames:
		undocpdfxml = os.path.join(pdfxmldir, undocname + ".xml")
		undochtml = os.path.join(htmldir, undocname + ".html")


		gparas = None
		while not gparas:
			fin = open(undocpdfxml)
			xfil = fin.read()
			fin.close()

			print "parsing:", undocname,
			try:
				sdate, chairs, tlcall = GlueUnfile(xfil, undocname)
				print sdate#, chairs
				gparas = GroupParas(tlcall, undocname, sdate)
			except unexception, ux:
				assert not gparas
				print "\n\nError: %s on page %s textcounter %s" % (ux.description, ux.paranum.pageno, ux.paranum.textcountnumber)
				print "\nHit RETURN to launch your editor on the psdxml (or type 's' to skip, or 't' to throw)"
				rl = sys.stdin.readline()
				if rl[0] == "s":
					break
				if rl[0] == "t":
					raise

				fin = open(undocpdfxml, "r")
				finlines = fin.read()
				fin.close()
				mfinlines = re.match("(?s)(.*?<text ){%d}" % ux.paranum.textcountnumber, finlines)
				ln = mfinlines.group(0).count("\n")
				print ln
				os.system('"C:\Program Files\ConTEXT\ConTEXT" %s /g00:%d' % (undocpdfxml, ln + 2))
		if not gparas:
			continue

		fout = open(undochtml, "w")
		fout.write('<html>\n<head>\n')
		fout.write('<link href="unhtml.css" type="text/css" rel="stylesheet" media="all">\n')
		fout.write('</head>\n<body>\n')
		fout.write("<h1>%s  date=%s</h1>\n" % (undocname, sdate))
		for gpara in gparas:
			gpara.writeblock(fout)
		fout.write('</body>\n</html>\n')
		fout.close()


