import urllib2
import cookielib
import urlparse
import re
import sys
import os
import shutil
from optparse import OptionParser
from unexception import unexception

docindex = "http://www.un.org/documents/"

def ScrapePlenaryPDF(plenaryurl, purl, pdfname, undocname):
	# first go through the forwarding blocker
	purl = urlparse.urljoin(plenaryurl, purl)
	req = urllib2.Request(purl)
	req.add_header('Referer', plenaryurl)
	fin = urllib2.urlopen(req)
	plenrefererforward = fin.read()
	fin.close()
	mfore = re.search('URL=([^"]*)', plenrefererforward)
	if not mfore:
		if undocname == "A-55-PV.26":
			print "broken", pdfname
        	return
		print plenrefererforward
	turl = urlparse.urljoin(purl, mfore.group(1))

	# pull in the login url, containing another forward, and a page which gives the cookies
	fin = urllib2.urlopen(turl)
	plenarycookielink = fin.read()
	fin.close()

	#<META HTTP-EQUIV="refresh" CONTENT="1; URL=http://daccessdds.un.org/doc/UNDOC/GEN/N02/596/08/PDF/N0259608.pdf?OpenElement">
	#<frame name="footer" scrolling="no" noresize target="main" src="http://daccessdds.un.org/prod/ods_mother.nsf?Login&Username=freeods2&Password=1234" marginwidth="0" marginheight="0">

	# extract pdf link
	mpdf = re.search('URL=([^"]*)', plenarycookielink)
	if not mpdf:
		print plenarycookielink
	plenarypdfurl = urlparse.urljoin(turl, mpdf.group(1))

	# extract cookie link
	mcook = re.search('src="(http://daccessdds.un.org/[^"]*)', plenarycookielink)
	if not mcook:
		print plenarycookielink
	plenarycookurl = urlparse.urljoin(turl, mcook.group(1))

	# take the cookies from the cookie link
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
	fin = opener.open(plenarycookurl)
	fin.close()

	print "scraping", plenarypdfurl[-30:], pdfname

	# put them into the pdf link
	fin = opener.open(plenarypdfurl)
	plenarypdf = fin.read()
	fin.close()

	fout = open(pdfname, "wb")
	fout.write(plenarypdf)
	fout.close()


def ScrapePlenary(pdfdir, plenaryurl):
	if not os.path.isdir(pdfdir):
		print "Please create directory", pdfdir
		sys.exit(0)

	fin = urllib2.urlopen(plenaryurl)
	plenaryindex = fin.read()
	fin.close()
	# <a href="http://daccess-ods.un.org/access.nsf/Get?OpenAgent&DS=A/57/PV.1&Lang=E" target="_blank">A/57/PV.1</a>
	plenaryindexlist = re.findall('<a href="(http://daccess[^"]*)" target="_blank">([^<]*)</a>(?i)', plenaryindex)
	for plenary in plenaryindexlist[:]:
		undocname = re.sub("/", "-", plenary[1])
		undocname = re.sub("\s", "", undocname)
		pdfname = undocname + ".pdf"
		pdffile = os.path.join(pdfdir, pdfname)
		if not os.path.isfile(pdffile):  # or re.match("Corr", pdfname)
			ScrapePlenaryPDF(plenaryurl, plenary[0], pdffile, undocname)
		else:
			print "skipping", pdfname



scrapeurlmap = {
	"A-53":"http://www.un.org/ga/53/session/pv53.htm",
	"A-54":"http://www.un.org/ga/54/pv54e.htm",
	"A-55":"http://www.un.org/ga/55/pvlista55.htm",  # A/55/PV.26 is missing
	"A-56":"http://www.un.org/ga/56/pv.htm",   # number 63 and 110 are disappeared
	"A-57":"http://www.un.org/ga/57/pv.html", # note that A/57/PV.90 is under embargo
	"A-58":"http://www.un.org/ga/58/pv.html",
	"A-59":"http://www.un.org/ga/59/pv.html",
				}

pdfdir = "pdf"
def ScrapePDF(stem, pdfdir):
	for st in scrapeurlmap:
		if stem and not re.match(stem, st):
			continue
		ScrapePlenary(pdfdir, scrapeurlmap[st])

def ConvertXML(stem, pdfdir, pdfxmldir):
	for sd in os.listdir(pdfdir):
		if stem and not re.match(stem, sd):
			continue
		pdf = os.path.join(pdfdir, sd)
		pdfdest = os.path.join(pdfxmldir, sd)
		xmldest = os.path.splitext(pdfdest)[0] + ".xml"
		if not os.path.isfile(xmldest):
			shutil.copyfile(pdf, pdfdest)
			print "pdftohtml -xml", sd
			os.spawnl(os.P_WAIT, 'pdftohtml', 'pdftohtml', '-xml', pdfdest)
			os.remove(pdfdest)
			assert os.path.isfile(xmldest)





