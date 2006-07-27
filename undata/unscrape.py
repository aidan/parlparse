import urllib2
import cookielib
import urlparse
import re
import sys
import os

"""With votes: http://www.un.org/ga/59/pv.html"""
docindex = "http://www.un.org/documents/"


def ScrapePlenaryPDF(plenaryurl, purl, pdfname):
	# first go through the forwarding blocker
	purl = urlparse.urljoin(plenaryurl, purl)
	req = urllib2.Request(purl)
	req.add_header('Referer', plenaryurl)
	fin = urllib2.urlopen(req)
	plenrefererforward = fin.read()
	fin.close()
	mfore = re.search('URL=([^"]*)', plenrefererforward)
	if not mfore:
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

	print plenarypdfurl[-30:], pdfname

	# put them into the pdf link
	fin = opener.open(plenarypdfurl)
	plenarypdf = fin.read()
	fin.close()

	fout = open(pdfname, "wb")
	fout.write(plenarypdf)
	fout.close()

def ScrapePlenary(plenaryurl, outdir):
	fin = urllib2.urlopen(plenaryurl)
	plenaryindex = fin.read()
	fin.close()
	# <a href="http://daccess-ods.un.org/access.nsf/Get?OpenAgent&DS=A/57/PV.1&Lang=E" target="_blank">A/57/PV.1</a>
	plenaryindexlist = re.findall('<a href="(http://daccess[^"]*)" target="_blank">([^<]*)</a>(?i)', plenaryindex)
	for plenary in plenaryindexlist[:]:
		fname = os.path.join(outdir, re.sub("/", "-", plenary[1]) + ".pdf")
		fname = re.sub("\s", "", fname)
		ScrapePlenaryPDF(plenaryurl, plenary[0], fname)

#ScrapePlenary("http://www.un.org/ga/57/pv.html", "plenary57")  # note that A/57/PV.90 is under embargo
#ScrapePlenary("http://www.un.org/ga/58/pv.html", "plenary58")
#ScrapePlenary("http://www.un.org/ga/59/pv.html", "plenary59")
#ScrapePlenary("http://www.un.org/ga/56/pv.htm", "plenary56")   # number 63 and 110 are disappeared
#ScrapePlenary("http://www.un.org/ga/55/pvlista55.htm", "plenary55")  # A/55/PV.26 is missing
#ScrapePlenary("http://www.un.org/ga/54/pv54e.htm", "plenary54")
ScrapePlenary("http://www.un.org/ga/53/session/pv53.htm", "plenary53")






