import os
import re
import sys
from nations import FixNationName, nonnations
from unmisc import unexception, IsNotQuiet, MarkupLinks, paranumC
from unglue import GlueUnfile
from speechblock import SpeechBlock
from voteblock import VoteBlock, recvoterequest


def GroupParas(tlcall, undocname, sdate):
	res = [ ]
	i = 0
	currentspeaker = None
	while i < len(tlcall):
		tlc = tlcall[i]
		if re.match(recvoterequest, tlc.paratext):
			lblock = VoteBlock(tlcall, i, undocname, sdate)
			i = lblock.i

		# non-voting line to be processed
		else:
			speakerbeforetookchair = ""
			if (len(res) > 2) and (res[-1].typ == "italicline-tookchair") and (res[-2].typ == "spoken"):
				speakerbeforetookchair = res[-2].speaker
			lblock = SpeechBlock(tlcall, i, undocname, sdate, speakerbeforetookchair)
			i = lblock.i

		if res and res[-1].paranum.pageno == lblock.paranum.pageno:
			lblock.paranum.blockno = res[-1].paranum.blockno + 1
		else:
			lblock.paranum.blockno = 1
		res.append(lblock)

	return res



def ParsetoHTML(stem, pdfxmldir, htmldir, bforceparse):
	undocnames = [ ]
	for undoc in os.listdir(pdfxmldir):
		undocname = os.path.splitext(undoc)[0]
		if not re.match(stem, undocname):
			continue
		if re.search("Corr", undocname): # skip corregendas
			continue
		if not bforceparse:
			undochtml = os.path.join(htmldir, undocname + ".html")
			if os.path.isfile(undochtml):
				continue
		undocnames.append(undocname)

	undocnames.sort()
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
				os.system('"C:\Program Files\ConTEXT\ConTEXT" %s /g00:%d' % (undocpdfxml, ln + 2))
		if not gparas:
			continue

		# actually write the file
		tmpfile = undochtml + "--temp"
		fout = open(tmpfile, "w")
		fout.write('<html>\n<head>\n')
		fout.write('<link href="unview.css" type="text/css" rel="stylesheet" media="all">\n')
		fout.write('</head>\n<body>\n')
		fout.write("<h1>%s  date=%s</h1>\n" % (undocname, sdate))
		for gpara in gparas:
			gpara.writeblock(fout)
		fout.write('</body>\n</html>\n')
		fout.close()
		if os.path.isfile(undochtml):
			os.remove(undochtml)
		os.rename(tmpfile, undochtml)



