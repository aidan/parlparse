#!/usr/bin/python

import urllib
import urlparse
import re
import sys

# starting point for directories
actdir = "C:/pwhip/parldata/acts"
iurl = "http://www.opsi.gov.uk/acts.htm"


def ScrapeAct(aurl):
	tpg = urllib.urlopen(aurl).read()
	print aurl

	mtpg = re.search('''(?ix)#<table(?:cellpadding=2|width=95%|\s)*>\s*
						#<tr>\s*<td\s*align=center\s*valign=bottom>\s*
						<img\s*src="/img/royalarm.gif"\s*alt="Royal\ Arms">\s*</td>\s*
						<td\s*valign="?bottom"?>(?:&nbsp;<br>)?\s*
						<font\s*size="?\+3"?><b>([\s\S]{1,250}?)</b></font>\s*
						<p>(?:</p>)?<font\s*size="?\+1"?>(?:<b>)?([^<]*)(?:</b>)?</font>\s*
						</td>\s*</tr>\s*
						<tr(?:\s*xml\S*)*>\s*<td\s*colspan="?2"?>\s*<hr></td>\s*</tr>\s*
						<tr>\s*<td\s*valign="?top"?>&nbsp;</td>\s*
						<td\s*valign="?top"?>\s*
						<p>&copy;\ Crown\ Copyright\ (\d+<?)</p>''',
						tpg)

#	mtpg = re.search("<p>&copy; Crown Copyright (\d+)</p>", tpg)
	if not mtpg:
		print tpg[:2000]
	print mtpg.group(2), mtpg.group(1)
	return (mtpg.group(3), mtpg.group(2), mtpg.group(1), aurl)


def GetActsFromYear(iyurl):
	pg = urllib.urlopen(iyurl).read()
	mpubact = re.search("<h4>Alphabetical List</h4>([\s\S]*?)<h4>Numerical List</h4>", pg)
	alphacts = mpubact.group(1)
	eachacts = re.findall('<a href="([^"]*)">([^<]*)</a>', alphacts)
	res = [ ]
	for eact in eachacts:
		if re.match("acts\d{4}/[\d\-_\w]*\.htm$", eact[0]):
			assert re.match("[\w\d\s\.,'\-()]*$", eact[1])
			res.append(urlparse.urljoin(iyurl, eact[0]))
		else:
			assert re.match("\#num|.*\.pdf", eact[0])
	return res



def GetYearIndexes(iurl):
	pg = urllib.urlopen(iurl).read()
	mpubact = re.search("<h3>Full text Public Acts</h3>([\s\S]*?)<h3>Full text\s*Local Acts</h3>", pg)
	pubacts = mpubact.group(1)
	yearacts = re.findall('<a href="(acts/acts\d{4}.htm)">(\d{4})\s*</a>', pubacts)

	res = [ ]
	for yact in yearacts:
		assert re.search('\d{4}', yact[0]).group(0) == yact[1]
		res.append(urlparse.urljoin(iurl, yact[0]))
	return res


# main running part
# just collects links to all the first pages
# then extracts name and chapter from the page itself
yiurl = GetYearIndexes(iurl)
allacts = [ ]
#yiurl = yiurl[-1:]
#yiurl = yiurl[15:]
for yiur in yiurl:
	allacts.extend(GetActsFromYear(yiur))
print "lenlen", len(allacts)
fout = open("listacts1.xml", "w")
for aurl in allacts:
	res = ScrapeAct(aurl)
	print res
	fout.write('<act year="%s" chapter="%s"\tname="%s" url="%s">\n' % res)
	fout.flush()
fout.close()


