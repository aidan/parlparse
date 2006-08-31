import urllib2
import cookielib
import urlparse
import re
import sys
import os
import shutil
from optparse import OptionParser
from unmisc import unexception, IsNotQuiet, pdfdir

docindex = "http://www.un.org/documents/"

def ScrapePDF(undocname, plenaryurl="http://www.un.org/ga/59/documentation/list0.html", purl=None):
	pdfname = undocname + ".pdf"
	pdffile = os.path.join(pdfdir, pdfname)
	if os.path.isfile(pdffile):
		print "  skipping", pdfname
		return True

	if not purl:
		mares = re.match("A-RES-(\d\d)-(\d+)$", undocname)
		madoc = re.match("A-(\d\d)-((?:L\.)?\d+)([\w\.\-]*)$", undocname)
		msres = re.match("S-RES-(\d+)\((\d+)\)", undocname)
		if mares:
			if int(mares.group(1)) < 53:  # limit the sessions we take these resolutions from
				return False
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=A/RES/%s/%s&Lang=E" % (mares.group(1), mares.group(2))
			print purl
		elif madoc:
			if int(madoc.group(1)) < 53:  # limit the sessions we take these resolutions from
				return False
			tail = re.sub("-", "/", madoc.group(3))
			if tail:
				print "TAIL Part", tail
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=A/%s/%s%s&Lang=E" % (madoc.group(1), madoc.group(2), tail)
			print purl
		elif msres:
			if int(msres.group(2)) < 1997:  # limit older resolutions
				return False
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/RES/%s%%20(%s)&Lang=E" % (msres.group(1), msres.group(2))
			print purl

	print " scraping", undocname,
	if not purl:
		print "*** Need to make"
		return False


	# first go through the forwarding blocker
	purl = urlparse.urljoin(plenaryurl, purl)
	req = urllib2.Request(purl)
	req.add_header('Referer', plenaryurl)
	fin = urllib2.urlopen(req)
	plenrefererforward = fin.read()
	fin.close()
	mfore = re.search('URL=([^"]*)', plenrefererforward)
	if not mfore:
		if undocname == "A-55-PV.26":   # claims to be embargoed
			print "broken", pdfname
			return False
		if re.search("There is no document", plenrefererforward):
			print "no-document"
			return False
		print plenrefererforward
		assert False
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

	print plenarypdfurl[-30:]

	# put them into the pdf link
	fin = opener.open(plenarypdfurl)
	plenarypdf = fin.read()
	fin.close()

	fout = open(pdffile, "wb")
	fout.write(plenarypdf)
	fout.close()
	return True


def ScrapeContentsPage(contentsurl):
	print "URL index:", contentsurl

	fin = urllib2.urlopen(contentsurl)
	plenaryindex = fin.read()
	fin.close()

	# <a href="http://daccess-ods.un.org/access.nsf/Get?OpenAgent&DS=A/57/PV.1&Lang=E" target="_blank">A/57/PV.1</a>

	plenaryindexlist = re.findall('<a\s+href="(http://daccess[^"]*)" target="_blank">(.*?)</a>(?is)', plenaryindex)
	if not plenaryindexlist:
		plenaryindexlist = re.findall('<a target="_blank" href="(http://daccess[^"]*)">(.*?)</a>(?i)', plenaryindex)
	for plenary in plenaryindexlist[:]:
		undocname = re.sub("/", "-", plenary[1])
		undocname = re.sub("\s|<.*?>", "", undocname)
		undocname = re.sub("SecurityCouncilresolution", "S-RES-", undocname)
		assert re.match("(?:A-RES-\d\d-\d+|A-\d\d-PV-\d+|S-RES-\d+\(\d+\))$", undocname)
		ScrapePDF(undocname, contentsurl, plenary[0])



scrapepvurlmap = {
	"A-53-PV":"http://www.un.org/ga/53/session/pv53.htm",
	"A-54-PV":"http://www.un.org/ga/54/pv54e.htm",
	"A-55-PV":"http://www.un.org/ga/55/pvlista55.htm",  # A/55/PV.26 is missing
	"A-56-PV":"http://www.un.org/ga/56/pv.htm",   # number 63 and 110 are disappeared
	"A-57-PV":"http://www.un.org/ga/57/pv.html", # note that A/57/PV.90 is under embargo
	"A-58-PV":"http://www.un.org/ga/58/pv.html",
	"A-59-PV":"http://www.un.org/ga/59/pv.html",

	"A-59":"http://www.un.org/ga/59/documentation/list0.html",
	"A-RES-56":"http://www.un.org/Depts/dhl/resguide/r56.htm",
	"A-RES-56":"http://www.un.org/Depts/dhl/resguide/r56.htm",
	"S-RES-2001":"http://www.un.org/Docs/scres/2001/sc2001.htm",
	"S-RES-2002":"http://www.un.org/Docs/scres/2002/sc2002.htm",

				}
#http://www.un.org/ga/59/documentation/list0.html

def ScrapeContentsPageFromStem(stem):
	if stem not in scrapepvurlmap:
		print "Allowable stems for scraping:\n ", ",\n  ".join(scrapepvurlmap.keys())
		sys.exit(1)

	# could generate some of the pages regularly.
	ScrapeContentsPage(scrapepvurlmap[stem])


def ConvertXML(stem, pdfdir, pdfxmldir):
	for sd in os.listdir(pdfdir):
		if stem and not re.match(stem, sd):
			continue
		pdf = os.path.join(pdfdir, sd)
		if not os.path.isfile(pdf):
			continue
		pdfdest = os.path.join(pdfxmldir, sd)
		xmldest = os.path.splitext(pdfdest)[0] + ".xml"
		if os.path.isfile(xmldest):
			print "skipping", sd
			continue
		shutil.copyfile(pdf, pdfdest)
		print "pdftohtml -xml", sd
		os.spawnl(os.P_WAIT, 'pdftohtml', 'pdftohtml', '-xml', pdfdest)
		os.remove(pdfdest)
		assert os.path.isfile(xmldest)





