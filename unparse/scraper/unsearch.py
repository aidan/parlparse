import os
import re
import sys
from unmisc import pdfdir, pdfxmldir, htmldir

import cgi, cgitb
import datetime
cgitb.enable()

webdocurl = "http://www.freesteel.co.uk/cgi-bin/unview.py?code="

stylehack = """
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
"""

htmldir = "/home/undemocracy/undata/html"
htmldir = "..\\..\\undata\\html"
pdfdir = "/home/undemocracy/undata/pdf"

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


def WriteFileSearch(searchstring, code):
	fhtmlfile = os.path.join(htmldir, code + ".unindexed.html")
	if not os.path.isfile(fhtmlfile):
		return

	fin = open(fhtmlfile)
	fd = fin.read()
	fin.close()

	mdate = re.search('<span class="date">([^<]*)</span>', fd)
	bSecurityCouncil = re.search("S-PV", fhtmlfile)
	sagenda = ""
	if bSecurityCouncil:
		magenda = re.search('<div class="boldline-agenda">(.*?)</div>', fd)
		if magenda:
			sagenda = magenda.group(1)

	#<div class="motiontext">The draft resolution was adopted by 90 votes to 48, with 21 abstentions (<a href="../pdf/A-RES-57-54.pdf" class="pdf">resolution 57/54</a>).</div>
	parasc = [ p  for p in re.findall('<(?:p|blockquote) id="([^"]*)">(.*?)</(?:p|blockquote)>', fd)  if re.search(searchstring, p[1]) ]
	if not parasc:
		return

	# do the layout
	print '<h2 class="%s">%s %s</h2>' % (bSecurityCouncil and "sc" or "", mdate.group(1), bSecurityCouncil and "Security Council" or "General Assembly")
	for p in parasc:
		mdec = re.search("pg(\d+)-bk(\d+)-pa(\d+)", p[0])
		print '<p><a href="%s%s#%s">Page %d, speech %d, para %d</a> - ' % (webdocurl, code, p[0], int(mdec.group(1)), int(mdec.group(2)), int(mdec.group(3)))
		print ShortPara(p[1], searchstring)
		print '</p>'


# sort out the index/unindexed repeats
def WriteSearch(searchstring, year):
	fin = open(os.path.join(htmldir, "index.html"))
	dxfile = fin.read()
	fin.close()

	print "Content-type: text/html\n"
	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
	print '<html>'
	print '<head>'
	print '<title>version 0</title>'
	print '<link href="http://seagrass.goatchurch.org.uk/~undemocracy/undata/html/unview.css" type="text/css" rel="stylesheet" media="all">'
	print '<style type="text/css">%s</style>' % stylehack
	print '</head>'
	print '<h1>Searching for: "%s" in %s</h1>' % (searchstring, year)

	sdate = ""
	for doc in re.findall('<td rowspan="\d+">(\d\d\d\d-\d\d-\d\d)</td>|code=[^"#]*">([^<]+)</td>', dxfile):
		if doc[0]:
			sdate = doc[0]
			continue
		if sdate[:4] != year:
			continue

		WriteFileSearch(searchstring, doc[1])

	print "</body>"
	print '</html>'


# the main section that interprets the fields
if __name__ == "__main__":
	#form = cgi.FieldStorage()

	#year = form.has_key("year") and form["year"].value or ""
	#searchstring = form.has_key("search") and form["search"].value or ""

	searchstring = "nuclear"
	year = "2006"
	WriteSearch(searchstring, year)




