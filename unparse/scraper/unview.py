#!/usr/bin/python2.3

# this is the start of a cgi script that will view the html files we've got
# it works on seagrass and should be able to be hosted anywhere because it
# references to the data files using absolute paths

import sys, os, stat, re
import cgi, cgitb
import datetime
cgitb.enable()

htmldir = "/home/undemocracy/undata/html"
pdfdir = "/home/undemocracy/undata/pdf"

stylehack = """
body
{
	width:100%;
}
div.stripe-1,
div.stripe-1 div.main,
div.stripe-1 div.sidebar
{
	background: #E8CBFD;
	margin-top: 0px;
    margin-bottom: 0px;
	padding-top: 0px;
    padding-bottom: 0px;
	margin: 0;
	padding: 0;
}
div.stripe-2,
div.stripe-2 div.main,
div.stripe-2 div.sidebar
{
	background: #C5CDEA;
	margin-top: 0px;
    margin-bottom: 0px;
	padding-top: 0px;
    padding-bottom: 0px;
	padding-left: 0px;
	margin-left: 0px;
	margin-right: 0px;
	margin: 0 0 0 0;
	padding: 0 0 0 0;
}
div.main
{
	float: left;
	width: 60%;
}
div.sidebar
{
	float: right;
	width: 39.5%;
}
div.break
{
	clear: both;
	height: 1px;
	font-size: 1px;
	background: #fff;
}
li.wikiref
{
	font-size: 10;
    padding-bottom: 10px;
}
"""

def GetFcodes(code):
	scode = re.sub("/", "-", code)
	scode = re.sub("\.html$|\.pdf$", "", scode)

	fhtml = os.path.join(htmldir, scode + ".html")
	if True or not os.path.isfile(fhtml):  # only use unindexed types during development, since no searcher is running
		fhtml = os.path.join(htmldir, scode + ".unindexed.html")
		if not os.path.isfile(fhtml):
			fhtml = ""

	fpdf = os.path.join(pdfdir, scode + ".pdf")
	if not os.path.isfile(fpdf):
		fpdf = ""

	return fhtml, fpdf


def WritePDF(fpdf):
	print "Content-type: application/pdf\n"
	fin = open(fpdf)
	print fin.read()
	fin.close()


def WriteNotfound(code):
	print "Content-type: text/html\n"
	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
	print '<html>'
	print '<head>'
	print '<title>version 0</title>'
	print '<link href="http://seagrass.goatchurch.org.uk/~undemocracy/undata/html/unview.css" type="text/css" rel="stylesheet" media="all">'
	print '</head>'
	print '<body>'
	a, b = GetFcodes(code)
	print "<h1>Not found: --%s--</h1>" % code
	print "<h2>--%s-- --%s--</h2>" % (a, b)
	print "</body>"
	print '</html>'

accessdate = datetime.date.today().isoformat()
def WikiRef(code, date, time):
	res = [ ]
	res.append("&lt;ref&gt;")
	res.append("{{")
	res.append("UN document")
	mgenass = re.match("A[/\-](\d+)[/\-]PV\.(\d+)$", code)
	mseccou = re.match("S[/\-]PV[/\-](\d+)$", code)
	mscres = re.match("S/RES/(\d+)\((\d+)\)$", code)
	res.append("|code=%s" % code)

	if mgenass:
		res.append("|body=A")
		res.append("|type=PV")
		res.append("|session=%s" % mgenass.group(1))
		res.append("|meeting=%s" mgenass.group(2))
	elif mseccou:
		res.append("|body=S")
		res.append("|type=PV")
		res.append("|meeting=%s" % mseccou.group(1))
	elif mscres:
		res.append("|body=S")
		res.append("|type=RES")
		res.append("|number=%s" % mscres.group(1))
		res.append("|year=%s" % mscres.group(2))
	else:
		res.append("|decription=Document whose code is %s" % code)

	if date:
		res.append("|date=%s" % date)
	if time:
		res.append("|time=%s" % time)
	res.append("|accessdate=%s" % accessdate)
	res.append("}}")
	res.append("&lt;/ref&gt;")

	return " ".join(res)

def SpecWikiRef(wikiref, gid, speakername, speakernation):
	res = [ ]
	if gid:
		res.append("|anchor=%s" % gid)
		mpg = re.search("pg(\d+)(?:-bk(\d+))?(?:-pa(\d+))?", gid)
		if mpg:
			res.append("|page=%d" % int(mpg.group(1)))
	if speakername:
		res.append("|speakername=%s" % speakername)
	if speakernation:
		res.append("|speakernation=%s" % speakernation)
	res.append("}}")
	return re.sub("}}", " ".join(res), wikiref)

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December" ]
def Prettydate(sdate):
	return "[[%d %s]] [[%s]]" % (int(sdate[8:]), months[int(sdate[5:7]) - 1], sdate[:4])

def ExtractFixDocLinks(dtext):
	res = [ ]
	wlinks = [ ]
	for lk in re.split('(<a[^>]*>[^<]*</a>)', dtext):
		mlk = re.match('<a href="../pdf/(.*?).pdf"([^>]*)>(.*?)</a>', lk)
		if not mlk:
			res.append(lk)
			continue
		code = re.sub("-", "/", mlk.group(1))
		res.append('<a href="unview.py?code=%s"%s>%s</a>' % (code, mlk.group(2), mlk.group(3)))
		wlinks.append(code)
	return "".join(res), wlinks


def WriteHTML(fhtml, code):
	print "Content-type: text/html\n"
	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
	print '<html>'
	print '<head>'
	print '<title>version 0</title>'
	print '<link href="http://seagrass.goatchurch.org.uk/~undemocracy/undata/html/unview.css" type="text/css" rel="stylesheet" media="all">'
	print '<style type="text/css">%s</style>' % stylehack
	print '</head>'

	fin = open(fhtml)
	ftext = fin.read()
	fin.close()

	fdivs = re.findall('<div class="([^"]*)"(?: id="([^"]*)")?>(.*?)</div>(?s)', ftext)
	s = 1
	date, time = "", ""
	docwikiref = WikiRef(code, date, time)
	for (dclass, gid, dtext) in fdivs:
		speakername, speakernation = "", ""  # always set to nothing at the start
		if dclass == "heading" or dclass == "spoken":
			for pp in re.findall('<span class="([^"]*)">(.*?)</span>', dtext):
				if pp[0] == "date":
					date = Prettydate(pp[1])
				if pp[0] == "time":
					time = pp[1]
				if pp[0] == "name":
					speakername = pp[1]
				if pp[0] == "nation":
					speakernation = pp[1]
			if dclass == "heading":  # recalculate
				docwikiref = WikiRef(code, date, time)

		print '<div class="stripe-%d"%s>' % (s, gid and ' id="%s"' % gid or '')
		print '<div class="main">'
		stext, wlinks = ExtractFixDocLinks(dtext)
		print '<div class="%s">%s</div>' % (dclass, stext)
		print '</div>'
		print '<div class="sidebar">'
		print '<ul>'
		print '<li class="wikiref">%s</li>' % SpecWikiRef(docwikiref, gid, speakername, speakernation)
		for wlink in wlinks:
			print '<li class="wikiref">%s</li>' % WikiRef(wlink, "", "")
		print '</ul>'
		print '</div>'
		print '</div>'
		print '<div class="break"></div>'
		s = 3 - s

	print "</body>"
	print '</html>'


# the main section that interprets the fields
if __name__ == "__main__":
	form = cgi.FieldStorage()

	code = form.has_key("code") and form["code"].value or ""
	bforcepdf = form.has_key("forcepdf") and (form["forcepdf"].value == "yes")
	fhtml, fpdf = GetFcodes(code)

	if fhtml and not bforcepdf:
		WriteHTML(fhtml, code)
	elif fpdf:
		WritePDF(fpdf)
	else:
		WriteNotfound(code)

