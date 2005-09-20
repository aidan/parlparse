#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import os

import miscfun

# starting point for directories
actdirhtml = miscfun.actdirhtml

# starting point for scraping
iurl = "http://www.opsi.gov.uk/acts.htm"


# helpful debugging match stuff
def HeadMatch(exp, txt, rtrnMobj=False):
	m = re.match(exp, txt)
	if not m:
		print "failed to match expression:\n\t", exp
		print "onto:"
		print txt[:1000]
		raise Exception
	if rtrnMobj:
		return(m, txt[m:end(0)])
	else:
		return txt[m.end(0):]

# helpful debugging match stuff
def TailMatch(exp, txt):
	m = re.search(exp, txt)
	if not m:
		print "failed to match expression:\n\t", exp
		print "ending with:\n"
		print txt[-2000:]
		raise Exception

	assert not re.search(exp, txt[m.start(0) + 1:])  # should not have an early match
	return txt[:m.start(0)], m


# main top and tail of the pages
def TrimPages(urlpages, year, chapter):

	explanation = None

	res = [ ]
	for i in range(len(urlpages)):
		(url, page) = urlpages[i]
		res.append('<pageurl page="%d" url="%s"/>\n' % (i, url))

		# trim off heading bits
		if i != 0:
			# trim off the head in stages
			page = HeadMatch('[\s\S]*?<tr[^>]*>\s*<td colspan="?2"?>\s*<hr>\s*</td>\s*</tr>(?i)', page)
			if re.match('\s*<TR><TD width=120', page):
				page = HeadMatch('\s*<tr><td width=120 align=center valign=bottom><img src="/img/ra-col.gif"></td><td valign=top>&nbsp;(?i)', page)
			else:
				page = HeadMatch('\s*<tr[^>]*>\s*<td colspan="?2"? align="?right"?>\s*<a href=[^>]*>back to previous (?:page|text)</a>(?i)', page)
			page = HeadMatch('</td>\s*</tr>\s*(?:<p>)?(?i)', page)

		# trim the tail different cases
		if len(urlpages) == 1:  # single page
			page, mobj = TailMatch('<tr>\s*<td valign="?top"?>(?:&nbsp;|\s*)</td>\s*<td (?:colspan="?2"?|valign=(?:"?2"?|"?top"?)(?: colspan="?2"?)?)>\s*(?:(?:<a name="end"[^>]*>)?\s*(?:<A HREF="([\.\den/]+\.htm)"><IMG border=0 align=top src="/img/nav-exnt\.gif" alt="Explanatory Note"></A>)?(?:\s*</a>)?)?(?:\s*<a name="end">)?\s*<hr[^>]*>\s*</td>\s*</tr>\s*<tr>(?i)', page)
			if mobj.lastgroup:
				explanation = mobj.lastgroup

		elif i == 0:		# first page
			page, mobj = TailMatch('<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=("?2"?|"?top"?)(?: colspan="?2"?)?>\s*<a href=[^>]*>\s*<img(?: border=0 align=top)? src="/img/nav-conu\.gif"(?i)', page)
		elif i != len(urlpages) - 1:  # middle page
			page, mobj = TailMatch('(?:</table>\s*<table width="100%">\s*)?<td(?: valign=(?:"2"|"?top"?))?(?: colspan="?2"?)?>\s*<a href=[^>]*><img(?: src="/img/nav-conu\.gif"| align="?top"?| alt="continue"| border=(?:0|"0"|"right")| width="25%")+></a>(?i)', page)
		# last page
		else:
			if (year, chapter) == ("1997", "19"):  # special case
				page, mobj = TailMatch('</TABLE></TD></TR>\s*<TR><TD colspan=2>\s*</TD></TR><TR><TD valign=top>&nbsp;</TD><TD valign=top colspan=2>\s*<A name="end"><HR>(?i)', page)
			else:
				page, mobj = TailMatch('(?:</table>\s*<table width="100%">\s*)?<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=(?:"?2"?|"?top"?)(?: colspan="?2"?)?>\s*<a href=[^>]*>\s*<img(?: align="?top"?| alt="previous section"| border="?0"?| src="/img/navprev2\.gif")+>(?i)', page)

		res.append(page)
	if explanation:
		res.append('<explanation href="%s" />' % explanation)
	return res



# recurse through all the links and make a set of strings for each url
def GetAllPages(url):
	res = [ ]
	while True:
		page = urllib.urlopen(url).read()
		res.append((url, page))
		contbutton = re.search('<a href="(\S*.htm)"(?:\s*xml\S*)*>\s*<img (?:\s*(?:border="?0"?|align="?top"?|src="/img/nav-conu.gif"|alt="continue")){4}(?i)', page)
		if not contbutton:
			break
		url = urlparse.urljoin(url, contbutton.group(1))

	return res


# get all the links to the starts of the page
def GetYearIndexes(iurl):
	pg = urllib.urlopen(iurl).read()
	mpubact = re.search("<h3>Full text Public Acts</h3>([\s\S]*?)<h3>Full text\s*Local Acts</h3>", pg)
	pubacts = mpubact.group(1)
	yearacts = re.findall('<a href="(acts/acts\d{4}.htm)">(\d{4})\s*</a>', pubacts)

	res = [ ]
	for yact in yearacts:
		assert re.search('\d{4}', yact[0]).group(0) == yact[1]
		res.append((yact[1], urlparse.urljoin(iurl, yact[0])))
	return res

def GetActsFromYear(yiurl):
	pg = urllib.urlopen(yiurl[1]).read()
	mpubact = re.search("<h4>Alphabetical List</h4>([\s\S]*?)<h4>Numerical List</h4>", pg)
	alphacts = mpubact.group(1)
	eachacts = re.findall('<a href="([^"]*)">([^<]*)</a>', alphacts)
	res = [ ]
	for eact in eachacts:
		if re.match("acts\d{4}/[\d\-_\w]*\.htm$", eact[0]):
			mtitch = re.match("([\w\d\s\.,'\-()]*?)\s*(\d{4})\s*\(?c\.?\s*(\d+)\s*\)?$", eact[1])
			assert mtitch.group(2) == yiurl[0]
			url = urlparse.urljoin(yiurl[1], eact[0])
			v = (url, mtitch.group(1), mtitch.group(3))
			if v not in res:  # 1988 has an act listed twice
				res.append(v)
		else:
			assert re.match("\#num|.*\.pdf", eact[0])

	# check all the numbered chapters are here
	chnum = [ int(x[2])  for x in res ]
	chnum.sort()
	assert chnum == range(1, len(chnum) + 1)

	return res


# main running part
if __name__ == '__main__':
	# just collects links to all the first pages
	yiurl = GetYearIndexes(iurl)
	#yiurl = yiurl[-7:]  # just two years

	# go through the years
	for yiur in yiurl:
		print "---- Year:", yiur[0]
		yacts = GetActsFromYear(yiur)
		for url, name, chapter in yacts:
			# build the name for this
			fact = os.path.join(actdirhtml, "ukgpa%sc%s.html" % (yiur[0], chapter))
			if os.path.isfile(fact):
				#print "  skip ch", chapter, ":", name
				continue

			print "scraping ch", chapter, ":", name,
			actpages = GetAllPages(url)  # this ends the contact with the internet.
			print "pages", len(actpages)
			trimmedpages = TrimPages(actpages, yiur[0], chapter)
			ftemp = "temp.html"
			fout = open(ftemp, "w")
			fout.writelines(trimmedpages)
			fout.close()
			os.rename(ftemp, fact)



