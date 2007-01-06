import os
import re
import sys
from unmisc import pdfdir, pdfxmldir, htmldir

searchterm = sys.argv[1]

htmlfiles = os.listdir(htmldir)
htmlfiles.sort()

ispread = 76
def ShortPara(ptext, searchterm):
	mg = re.search(searchterm, ptext)
	fs = lfs = max(0, mg.start(0) - ispread)
	fe = lfe = min(len(ptext), mg.end(0) + ispread)
	while fs != 0 and fs < mg.start(0) and ptext[fs - 1] != " ":
		fs += 1
	while fe != len(ptext) and fe > mg.end(0) and ptext[fe] != " ":
		fe -= 1
	res = ptext[fs:fe]
	res = re.sub("<", "&lt;", res)
	res = re.sub(">", "&gt;", res)
	res = re.sub(searchterm, "<b>%s</b>" % searchterm, res)
	return "%s%s%s" % (fs != 0 and "..." or "", res, fe != len(ptext) and "..." or "")

print """<html>
<head>
<title>Search %s</title>
<style type="text/css">
body
{
	width:600px;
}
h2
{
	color: #08601f;
	padding-top:10px;
	font-size: 120%%;
    margin-bottom: 10px;
}
h2.sc
{
	color: #60081f;
	padding-top:10px;
	font-size: 120%%;
    margin-bottom: 10px;
}
p
{
    margin-top: 0px;
    margin-bottom: 0px;
	padding-left:20px;
	font-size: 90%%;
}
</style>
</head>
<body>
<h1>Searching for '%s'</h1>
""" % (searchterm, searchterm)

cc = 2000
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
		magenda = re.search('<div class="boldline-agenda">(.*?)</div>', fd)
		if magenda:
			sagenda = magenda.group(1)

	#<div class="motiontext">The draft resolution was adopted by 90 votes to 48, with 21 abstentions (<a href="../pdf/A-RES-57-54.pdf" class="pdf">resolution 57/54</a>).</div>
	parasc = [ p  for p in re.findall('<(?:p|blockquote) id="([^"]*)">(.*?)</(?:p|blockquote)>', fd)  if re.search(searchterm, p[1]) ]
	if not parasc:
		continue

	# do the layout
	print '<h2 class="%s">%s %s</h2>' % (bSecurityCouncil and "sc" or "", mdate.group(2), bSecurityCouncil and "Security Council" or "General Assembly")
	for p in parasc:
		mdec = re.search("pg(\d+)-bk(\d+)-pa(\d+)", p[0])
		print '<p><a href="%s/%s#%s">Page %d, speech %d, para %d</a> - ' % (htmldir, htmlfile, p[0], int(mdec.group(1)), int(mdec.group(2)), int(mdec.group(3)))
		print ShortPara(p[1], searchterm)
		print '</p>'

	cc -= 1
	if cc == 0:
		break
print """
</body>
</html>
"""


