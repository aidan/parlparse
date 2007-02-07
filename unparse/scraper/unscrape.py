
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


def GetFromNet(undocname, purl, plenaryurl):
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
		if re.search("This document is under EMBARGO", plenrefererforward):
			print "*** EMBARGOED ***"
			return False
		if re.search("The distribution of the document is to hight", plenrefererforward):
			print "*** TO HIGHT ***"
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

	return plenarypdf


def ScrapePDF(undocname, plenaryurl="http://www.un.org/ga/59/documentation/list0.html", purl=None):
	pdfname = undocname + ".pdf"
	pdffile = os.path.join(pdfdir, pdfname)
	if os.path.isfile(pdffile):
		if IsNotQuiet():
			print "  skipping", pdffile, pdfname
		return True

	if not purl:
		mares = re.match("A-RES-(\d+)-(\d+)$", undocname)
		meres = re.match("E-RES-(\d\d\d\d)-(\d+)$", undocname)  # don't know what the code is
		madoc = re.match("A-(\d\d)-((?:L\.|CRP\.)?\d+)([\w\.\-]*)$", undocname)
		msres = re.match("S-RES-(\d+)\((\d+)\)$", undocname)
		mapv  = re.match("A-(\d\d)-PV.(\d+)(-Corr.\d|)$", undocname)
		mspv = re.match("S-PV.(\d+)", undocname)
		scdoc = re.match("S-(\d\d\d\d)-(\d+)(-Corr.\d|)(\(SUPP\)|)$", undocname)
		munknown = re.match("(?:ECESA/1/Rev.1|S-26-2)$", undocname)

		if mares:
			if int(mares.group(1)) < 1:  # limit the sessions we take these resolutions from
				return False
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=A/RES/%s/%s&Lang=E" % (mares.group(1), mares.group(2))
		#if meres:
		#	purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=E/RES/%s/%s&Lang=E" % (meres.group(1), meres.group(2))
		elif madoc:
			if int(madoc.group(1)) < 1:  # limit the sessions we take these resolutions from
				return False
			tail = re.sub("-", "/", madoc.group(3))
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=A/%s/%s%s&Lang=E" % (madoc.group(1), madoc.group(2), tail)
			#print purl
		elif scdoc:
			tail = re.sub("-", "/", scdoc.group(3))
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/%s/%s%s%s&Lang=E" % (scdoc.group(1), scdoc.group(2), tail, scdoc.group(4))
		elif msres:
			sarea = int(msres.group(1)) <= 766 and "RESOLUTION" or "UNDOC"
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/RES/%s%%20(%s)&Lang=E&Area=%s" % (msres.group(1), msres.group(2), sarea)
			plenaryurl = "http://www.un.org/Docs/scres/2002/sc2002.htm"
		elif mspv:
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/PV.%s&Lang=E" % mspv.group(1)
			plenaryurl = "http://www.un.org/Docs/scres/2002/sc2002.htm"
		elif mapv:
			if int(mapv.group(1)) < 40:  # limit the sessions we take these resolutions from
				return False
			tail = re.sub("-", "/", mapv.group(3))
			purl = "http://daccess-ods.un.org/access.nsf/Get?Open&DS=A/%s/PV.%s%s&Lang=E" % (mapv.group(1), mapv.group(2), tail)
		elif meres or munknown:
			print "Unknown undocname", undocname
			return False
		else:
			print "Unrecognized undocname", undocname
			return False
	else:
		purl = re.sub("\s", "", purl)
		purl = re.sub("&amp;", "&", purl)

	#print "$$%s$$" % purl
	print " scraping", undocname,
	if not purl:
		print "*** Need to make"
		return False

	##return False

	# first go through the forwarding blocker
	purl = urlparse.urljoin(plenaryurl, purl)

	try:
		plenarypdf = GetFromNet(undocname, purl, plenaryurl)
	except Exception, e:
		print "Exception", e
		return False

	if not plenarypdf:
		return False
	fout = open(pdffile, "wb")
	fout.write(plenarypdf)
	fout.close()
	return True


# works for general assembly pages, and not much more
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


# breaks down into lists of links
def ScrapeSCContentsPage(year, contentsurl):
	print "URL index:", contentsurl
	fin = urllib2.urlopen(contentsurl)
	scindex = fin.read()
	fin.close()

	reslist = [ ]
	pvlist = [ ]
	prstlist = [ ]
	scdoclist = [ ]
	pvcorrlist = [ ]

	# this gets everything except the press releases in the middle column
	scindexlist = re.findall('<a.[^>]*?href=\s*"(http://daccess[^"]*)"[^>]*>\s*(?:<font size="2">)?(.*?)(?:<br>\s*)?</a>(?is)', scindex)

	for sci in scindexlist:
		#print sci[1]
		# communique for an embargoed verbatim recording
		if re.match("Communiqu.", sci[1]):
			assert sci[0] == pvlist[-1][2]  # same link
			continue

		# security council resolutions
		scres = re.match("S/RES/(\d+)\s*\((\d+)\)\s*$", sci[1])
		if scres:
			reslist.append((-int(scres.group(1)), scres, sci[0]))
			continue

		# verbatim recordings
		scpv = re.match("S/PV\.(\d+)(?:\s*<br>)?(?:\s*\((Resumption|Part)\s*([\dI]*)\))?\s*(?:\(closed\))?$", sci[1])
		if scpv:
			pvlist.append((-int(scpv.group(1) or "1"), scpv, sci[0]))
			#print scpv.group(0)
			continue

		# corrigenda, which happens to the verbatim transcripts
		sccorr = re.match("Corr\.(\d+)\s*", sci[1])
		if sccorr:
			urlwithoutcorr = re.sub("/Corr\.\d+(?i)", "", sci[0])
			if pvlist[-1][2] != urlwithoutcorr:
				print pvlist[-1][2]
				print urlwithoutcorr
				if year == 1998 and re.search("PV\.3896", pvlist[-1][2]) and re.search("PV\.3986", urlwithoutcorr):
					print "  --- known typo"
				elif year == 1995 and re.search("PV\.3528", pvlist[-1][2]) and re.search("PV\.3611", urlwithoutcorr):
					print "  --- known typo"
				else:
					assert False
			pvcorrlist.append((pvlist[-1][1], sccorr.group(1), sci[0]))
			continue

		# presidential statements
		scprst = re.match("S/PRST/(\d+)/(\d+)\s*$", sci[1])
		if scprst:
			assert int(scprst.group(1)) == year
			prstlist.append((-int(scprst.group(2)), scprst, sci[0]))
			continue

		# security council documents (usually a failed resolution)
		scdoc = re.match("\(?S/(\d+)/(\d+)\)?\s*$", sci[1])
		if scdoc:
			assert int(scdoc.group(1)) == year
			scdoclist.append((-int(scdoc.group(2)), scdoc, sci[0]))
			continue

		# known typo link
		if re.match("<a>", sci[1]):
			assert sci[0] == pvlist[-1][2]  # same link
			continue

		print "Unrecognized link type", "$$%s$$" % sci[1]
		assert False

	# sort and scrape all the presidential statements
	prstlist.sort()
	for i in range(1, len(prstlist)):
		if -prstlist[i - 1][0] - 1 != -prstlist[i][0]:
			print "presidential statement missing between ", -prstlist[i - 1][0], "and", -prstlist[i][0]
			if (year, -prstlist[i - 1][0],  -prstlist[i][0]) in [(2000, 28, 26), (1996, 11, 9), (1996, 4, 2), (1995, 57, 55), (1995, 37, 35), (1995, 15, 13), (1995, 4, 2), (1994, 77, 75), (1994, 50, 48), (1994, 42, 39), (1994, 25, 23), (1994, 19, 17), (1994, 4, 2)]:
				print "  -- known missing statement"
			else:
				assert False
	for (i, prst, prsturl) in prstlist:
		ScrapePDF("S-PRST-%s-%s" % (prst.group(1), prst.group(2)), plenaryurl=contentsurl, purl=prsturl)

	# now sort and scrape all the verbatims
	pvlist.sort()
	for i in range(1, len(pvlist)):
		if -pvlist[i - 1][0] == -pvlist[i][0]:
			if pvlist[i - 1][1].group(2) == "Resumption":
				resum = int(pvlist[i][1].group(3) or "0")
				if not pvlist[i - 1][1].group(2):
					print pvlist[i - 1][1].group(0) # there nust be a resumption number
				resumP = int(pvlist[i - 1][1].group(3) or "1")
				assert resumP == resum + 1
			else:
				print pvlist[i - 1][1].group(2), pvlist[i][1].group(2)
		elif -pvlist[i - 1][0] - 1 != -pvlist[i][0]:
			print "verbatim report missing between ", -pvlist[i - 1][0], "and", -pvlist[i][0]
			assert False
	for (i, scpv, scpvurl) in pvlist:
		resumppart = ""
		if scpv.group(2) == "Resumption":
			 resumppart = "-Resu.%s" % scpv.group(3)
		elif scpv.group(2) == "Part":
			if scpv.group(3) == "I":
				pn = "1"
			elif scpv.group(3) == "II":
				pn = "2"
			else:
				print scpv.group(0), scpv.group(3)
			resumppart = "-Part.%s" % pn
		ScrapePDF("S-PV-%s%s" % (scpv.group(1), resumppart), plenaryurl=contentsurl, purl=scpvurl)

	# do corrigendas
	for (scpv, pvcorr, pvcorrurl) in pvcorrlist:
		ScrapePDF("S-PV-%s%s-Corr.%s" % (scpv.group(1), (scpv.group(2) and ("-Resu.%s" % scpv.group(3)) or ""), pvcorr), plenaryurl=contentsurl, purl=pvcorrurl)

	# now sort and scrape all the resolutions
	reslist.sort()
	for i in range(1, len(reslist)):
		if -reslist[i - 1][0] - 1 != -reslist[i][0]:
			print "resolution missing between ", -reslist[i - 1][0], "and", -reslist[i][0]
			assert False
	for (i, scres, scresurl) in reslist:
		ScrapePDF("S-RES-%s(%s)" % (scres.group(1), scres.group(2)), plenaryurl=contentsurl, purl=scresurl)


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
	"S-RES-2001":"http://www.un.org/Docs/scres/2001/sc2001.htm",
	"S-RES-2002":"http://www.un.org/Docs/scres/2002/sc2002.htm",
				}
#http://www.un.org/ga/59/documentation/list0.html
def ScrapeContentsPageFromStem(stem):
	# this attempts to scrape PV and corrigenda assembly vertbatims by generating the codes
	# we could lead on from the last known
	mpv = re.match("A-(\d+)-PV$", stem)
	if mpv:
		# these should search for gaps
		repv = re.compile("A-%s-PV.(\d+)(?:-Corr.(\d+))?" % mpv.group(1))
		pvdone = []
		for f in os.listdir(pdfdir):
			mfm = repv.match(f)
			if mfm:
				pvdone.append(int(mfm.group(1)))

		# onwards values
		pvdone.sort()
		print pvdone
		v = (pvdone and pvdone[-1] or 0)
		vn = v + 1
		while ScrapePDF("A-%s-PV.%d" % (mpv.group(1), vn)):
			ScrapePDF("A-%s-PV.%d-Corr.1" % (mpv.group(1), vn))
			vn += 1

		# missing values
		while len(pvdone) >= 2:
			vn = pvdone[-1] - 1
			if pvdone[-2] < vn:
				if ScrapePDF("A-%s-PV.%d" % (mpv.group(1), vn)):
					ScrapePDF("A-%s-PV.%d-Corr.1" % (mpv.group(1), vn))
				pvdone[-1] = vn
			else:
				del pvdone[-1]

		return

	# this works from other contents pages for general assemblies
	if stem in scrapepvurlmap:
		ScrapeContentsPage(scrapepvurlmap[stem])
		return

	# security council scrapage
	mspv = re.match("S-(\d+)-PV", stem)
	if mspv:
		assert 1994 <= int(mspv.group(1)) <= 2007
		ScrapeSCContentsPage(int(mspv.group(1)), "http://www.un.org/Depts/dhl/resguide/scact%s.htm" % mspv.group(1))
		return

	print "Allowable stems for scraping are 'A-\d\d-PV' or 'S-\d\d\d\d(year)-PV', or"
	print ",\n  ".join(scrapepvurlmap.keys())
	assert False



# the other command that converts the files using the exe command
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
			if IsNotQuiet():
				print "skipping", sd
			continue
		#shutil.copyfile(pdf, pdfdest)
		print " ppdftohtml -xml", sd
		res = os.spawnl(os.P_WAIT, 'pdftohtml', 'pdftohtml', '-xml', pdf, "temph")
		assert os.path.isfile("temph.xml")
		os.rename("temph.xml", xmldest)
		#os.remove(pdfdest)
		assert os.path.isfile(xmldest)



