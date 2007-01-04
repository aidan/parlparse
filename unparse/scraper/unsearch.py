import os
import re
import sys
from unmisc import pdfdir, pdfxmldir, htmldir

searchterm = sys.argv[1]
print "Searching for", searchterm

htmlfiles = os.listdir(htmldir)
htmlfiles.sort()

ispread = 16
def ShortPara(ptext, searchterm):
	mg = re.search(searchterm, ptext)
	fs = lfs = max(0, mg.start(0) - ispread)
	fe = lfe = min(len(ptext), mg.end(0) + ispread)
	while fs != 0 and fs < mg.start(0) and ptext[fs - 1] != " ":
		fs += 1
	while fe != len(ptext) and fe > mg.end(0) and ptext[fe] != " ":
		fe -= 1
	return ptext[fs:fe]


for htmlfile in htmlfiles:
	if not re.search(".html$", htmlfile):
		continue
	if re.search("unindexed", htmlfile) and os.path.isfile(os.path.join(htmldir, re.sub("unindexed\.", "", htmlfile))):
		continue
	fhtmlfile = os.path.join(htmldir, htmlfile)
	if not os.path.isfile(fhtmlfile):
		continue

	fin = open(fhtmlfile)
	fd = fin.read()
	fin.close()

	mdate = re.search("<h1>(\S+)\s+date=([^<]*)</h1>", fd)
	bSecurityCouncil = re.search("S-PV", htmlfile)
	sagenda = ""
	if bSecurityCouncil:
		sagenda = re.search('<div class="boldline-agenda">(.*?)</div>', fd).group(1)

	parasc = [ p  for p in re.findall('<(?:p|blockquote) id="([^"]*)">(.*?)</(?:p|blockquote)>', fd)  if re.search(searchterm, p[1]) ]
	if not parasc:
		continue

	# do the layout
	print len(parasc), ShortPara(parasc[0][1], searchterm)



#	<p id="docSPV4717Resu1-pg002-bk05-pa02">Based on their reports, Japan considers that, even though some progress has been observed recently, Iraqi cooperation is still insufficient and limited, despite the ever-stronger pressure from the international community. We think that there is a common recognition in this regard among the international community, including on the part of the members of the Security Council.</p>
#<h1>S-PV-4717-Resu.1  date=2003-03-12 15:00</h1>
#<div class="boldline-agenda">The situation between Iraq and Kuwait Letter dated 7 March 2003 from the Chargé d'affaires a.i. of the Permanent Mission of Malaysia to the United Nations addressed to the President of the Security Council (S/2003/283).</div>


