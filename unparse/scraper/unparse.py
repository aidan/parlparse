import os
import re
import sys
from nations import FixNationName, nonnations
from unmisc import unexception, IsNotQuiet, MarkupLinks, paranumC
from unglue import GlueUnfile
from speechblock import SpeechBlock
from voteblock import VoteBlock, recvoterequest

def GroupParas(tlcall, undocname, sdate, seccouncilmembers):
	res = [ ]
	i = 0
	currentspeaker = None
	while i < len(tlcall):
		tlc = tlcall[i]
		if re.match(recvoterequest, tlc.paratext):
			lblock = VoteBlock(tlcall, i, undocname, sdate, seccouncilmembers)
			i = lblock.i

		# non-voting line to be processed
		else:
			speakerbeforetookchair = ""
			if (len(res) > 2) and (res[-1].typ in ["italicline-tookchair", "italicline-spokein"]) and (res[-2].typ == "spoken"):
				speakerbeforetookchair = res[-2].speaker
				if res[-1].typ == "italicline-spokein":
					assert len(res[-1].paragraphs) == 1
					mspokein = re.search("spoke in (\w+)", res[-1].paragraphs[0][1])
					if not mspokein:
						print "unrecognized spokein", res[-1].paragraphs
					#print "converting spokein", speakerbeforetookchair[2], mspokein.group(1)
					speakerbeforetookchair = (speakerbeforetookchair[0], speakerbeforetookchair[1], mspokein.group(1), speakerbeforetookchair[3])
			lblock = SpeechBlock(tlcall, i, undocname, sdate, speakerbeforetookchair)
			i = lblock.i

		if res and res[-1].paranum.pageno == lblock.paranum.pageno:
			lblock.paranum.blockno = res[-1].paranum.blockno + 1
		else:
			lblock.paranum.blockno = 1
		res.append(lblock)

	return res



def ParsetoHTML(stem, pdfxmldir, htmldir, bforceparse, beditparse):
	undocnames = [ ]
	for undoc in os.listdir(pdfxmldir):
		undocname = os.path.splitext(undoc)[0]
		if not re.match(stem, undocname):
			continue
		if re.search("Corr", undocname): # skip corregendas
			continue
		if not bforceparse:
			undochtml = os.path.join(htmldir, undocname + ".html")
			undochtmlunindexed = os.path.join(htmldir, undocname + ".unindexed.html")
			if os.path.isfile(undochtml) or os.path.isfile(undochtmlunindexed):
				continue
		undocnames.append(undocname)

	undocnames.sort()
	if IsNotQuiet():
		print "Preparing to parse %d files" % len(undocnames)

	for undocname in undocnames:
		undocpdfxml = os.path.join(pdfxmldir, undocname + ".xml")
		undochtml = os.path.join(htmldir, undocname + ".unindexed.html")

		gparas = None
		lbeditparse = beditparse
		while not gparas:
			fin = open(undocpdfxml)
			xfil = fin.read()
			fin.close()

			print "parsing:", undocname,
			try:
				if lbeditparse:
					lbeditparse = False
					raise unexception("editparse", None)
				glueunfile = GlueUnfile(xfil, undocname)
				if not glueunfile.tlcall:
					break   # happens when it's a bitmap type, or communique
				print glueunfile.sdate#, chairs
				gparas = GroupParas(glueunfile.tlcall, undocname, glueunfile.sdate, glueunfile.seccouncilmembers)
			except unexception, ux:
				assert not gparas
				if ux.description != "editparse":
					print "\n\nError: %s on page %s textcounter %s" % (ux.description, ux.paranum.pageno, ux.paranum.textcountnumber)
				print "\nHit RETURN to launch your editor on the psdxml (or type 's' to skip, or 't' to throw)"
				rl = sys.stdin.readline()
				if rl[0] == "s":
					break
				if rl[0] == "t":
					raise

				if ux.description != "editparse":
					fin = open(undocpdfxml, "r")
					finlines = fin.read()
					fin.close()
					mfinlines = re.match("(?s)(.*?<text ){%d}" % ux.paranum.textcountnumber, finlines)
					ln = mfinlines.group(0).count("\n")
				else:
					ln = 1
				# must look for using vim in unix version
				os.system('"C:\Program Files\ConTEXT\ConTEXT" %s /g00:%d' % (undocpdfxml, ln + 2))
		if not gparas:
			continue

		# actually write the file
		tmpfile = undochtml + "--temp"
		fout = open(tmpfile, "w")
		fout.write('<html>\n<head>\n')
		fout.write('<link href="unview.css" type="text/css" rel="stylesheet" media="all">\n')
		fout.write('</head>\n<body>\n')

		fout.write('<div class="heading">\n')
		fout.write('\t<span class="code">%s</span> <span class="date">%s</span> <span class="time">%s</span>\n' % (undocname, glueunfile.sdate[:10], glueunfile.sdate[10:].strip()))
		fout.write('</div>\n')

		if glueunfile.bSecurityCouncil:
			fout.write('\n<div class="boldline-agenda">\n<p class="boldline-agenda">%s</p>\n</div>\n' % glueunfile.agenda)
			fout.write('<div class="council-attendees">\n')
			for chair in glueunfile.chairs:
				fout.write('\t<p><span class="name">%s</span> <span class="nation">%s</span> <span class="place">%s</span></p>\n' % (chair[0], chair[1], chair[2]))
			fout.write('</div>')

		if glueunfile.bGeneralAssembly:
			fout.write('\n<div class="assembly-chairs">\n')
			for chair in glueunfile.chairs:
				fout.write('\t<p><span class="name">%s</span> <span class="nation">%s</span> <span class="place">president</span></p>\n' % (chair[0], chair[1]))
			fout.write('</div>')

		for gpara in gparas:
			gpara.writeblock(fout)

		fout.write('</body>\n</html>\n')
		fout.close()
		if os.path.isfile(undochtml):
			os.remove(undochtml)
		os.rename(tmpfile, undochtml)



