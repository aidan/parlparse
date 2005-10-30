#!/usr/bin/python
# vim:sw=4:ts=4:noet:nowrap

# fulldepage.py - download HTML of acts, top and tail and concatenate

# Copyright (C) 2005 Francis Davey and Julian Todd, part of lawparse

# lawparse is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# lawparse is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with lawparse; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA  02110-1301  USA

#import urllib1
import urllib
import urlparse
import re
import sys
import os
import optparse
import traceback
import logging

import miscfun
import options

# starting point for scraping
iurl = "http://www.opsi.gov.uk/acts.htm"

# helpful debugging match stuff
def HeadMatch(exp, txt):
	m = re.match(exp, txt)
	if not m:
		raise StandardError, "failed to match expression:\n\t%s\nonto:%s\n%s\n%s\n%s" % (exp, txt[:1000], 
			re.match('\s*<TR><TD align=center>&nbsp;<br><FONT SIZE=5>ABSTRACT<BR>', txt),
			re.match('\s*<TR><TD align=center>&nbsp;<br>', txt),
			re.match('\s*<TR><TD', txt))
		raise StandardError, ""


	return txt[m.end(0):]

# helpful debugging match stuff
def TailMatch(exp, txt):
	m = re.search(exp, txt)
	if not m:
		raise StandardError, "failed to match expression:\n\t%s\nending with:\n%s" % (exp, txt[-2000:])

	mm = re.search(exp, txt[m.start(0) + 1:])  # should not have an early match
	if mm:
		raise StandardError, "had an early match of:\n\t%s\nTail match: %s\nEarly match: %s" % (exp, m.group(0), mm.group(0))
	return txt[:m.start(0)], m


# main top and tail of the pages
def TrimPages(urlpages, year, chapter):
	explanation = None

	res = [ ]
	for i in range(len(urlpages)):
		try:
			(url, page) = urlpages[i]
			res.append('<pageurl page="%d" url="%s"/>\n' % (i, url))

			# trim off heading bits
			if i != 0:
				# trim off the head in stages
				page = HeadMatch('[\s\S]*?<tr[^>]*>\s*<td colspan="?2"?>\s*<hr>\s*</td>\s*</tr>(?i)', page)
				if re.match('\s*<TR><TD width=120', page):
					page = HeadMatch('\s*<tr><td width=120 align=center valign=bottom><img src="/img/ra-col.gif"></td><td valign=top>&nbsp;(?i)', page)
				elif re.match('\s*<TR><TD align=center>&nbsp;<br><FONT SIZE=5>ABSTRACT<BR>', page):
					print "Trimming out ABSTRACT OF SCHEDULES"
					page = HeadMatch('[\s\S]*<HR width=40%>\s*<HR width=40%>\s*', page)
				else:
					page = HeadMatch('\s*<tr[^>]*>\s*<td colspan="?2"? align="?right"?>\s*<a href=[^>]*>back to previous (?:page|text)</a>(?i)', page)

				page = HeadMatch('\s*</td>\s*</tr>\s*(?:<p>)?(?i)', page)

			# trim the tail different cases

			# single page
			if len(urlpages) == 1:
				page, mobj = TailMatch('<tr>\s*<td valign="?top"?>(?:&nbsp;|\s*)</td>\s*<td (?:colspan="?2"?|valign=(?:"?2"?|"?top"?)(?: colspan="?2"?)?)>\s*(?:(?:<a name="end"[^>]*>)?\s*(?:<A HREF="([\.\den/]+\.htm)"><IMG border=0 align=top src="/img/nav-exnt\.gif" alt="Explanatory Note"></A>)?(?:\s*</a>)?)?(?:\s*<a name="end">)?\s*<hr[^>]*>\s*</td>\s*</tr>\s*<tr>(?i)', page)
				if mobj.lastgroup:
					explanation = mobj.lastgroup

			# first page
			elif i == 0:
				if (year, chapter) == ("1996", "45"):
					page, mobj = TailMatch('<TR><TD></TD><TD>\s*<A HREF="96045--a.htm"><IMG border=0 align=top src="/img/nav-conu.gif"(?i)', page)
				else:
					page, mobj = TailMatch('<tr>\s*<td[^>]*>(?:&nbsp;)?</td>\s*<td[^>]*>\s*<a href=[^>]*>\s*<img(?: border=0 align=top)? src="/img/nav-conu\.gif"(?i)', page)

			# middle page
			elif i != len(urlpages) - 1:
				if (year, chapter) == ("1996", "45"):
					page, mobj = TailMatch('<TR><TD>(?:</TD><TD>)?\s*<A HREF="[^"]*"><IMG border=0 align=top src="/img/navprev2.gif"(?i)', page)
				else:
					page, mobj = TailMatch('(?:</table>\s*<table width="100%">\s*)?<td(?: valign=(?:"2"|"?top"?))?(?: colspan="?2"?)?>\s*<a href=[^>]*><img(?: src="/img/nav-conu\.gif"| align="?top"?| alt="continue"| border=(?:0|"0"|"right")| width="25%")+></a>(?i)', page)

			# last page
			else:
				if (year, chapter) == ("1997", "19"):  # special case
					page, mobj = TailMatch('</TABLE></TD></TR>\s*<TR><TD colspan=2>\s*</TD></TR><TR><TD valign=top>&nbsp;</TD><TD valign=top colspan=2>\s*<A name="end"><HR>(?i)', page)
				else:
					page, mobj = TailMatch('(?:</table>\s*<table width="100%">\s*)?<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=(?:"?2"?|"?top"?)(?: colspan="?2"?)?>\s*<a href=[^>]*>\s*<img(?: align="?top"?| alt="previous section"| border="?0"?| src="/img/navprev2\.gif")+>(?i)', page)

			res.append(page)
		except StandardError, e:
			print "\nInner URL %s" % url
			raise 

	if explanation:
		res.append('<explanation href="%s" />' % explanation)
	return res



# recurse through all the links and make a set of strings for each url
def GetAllPages(url, options):
	res = [ ]
	while True:
		if options.verbose >= 2:
			print "getting %s" % url
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
	try:
		assert chnum == range(1, len(chnum) + 1)
	except AssertionError:
		print chnum, len(chnum), yiurl
		# should put a sys.exit() here

	# Noten 1988c44 is not in the alphabetical list!

	return res


# main running part
if __name__ == '__main__':

	logger=logging.getLogger('')

	# read command line parameters
#	parser = optparse.OptionParser()
	parser = options.OpsiOptionParser()
	parser.set_usage("""
Crawls the OPSI website downloading acts of parliament. Concatenates
the HTML files of each act into one file, and saves it in lawdata/acts.""")
	parser.add_option("--force",
						action="store_true", dest="force", default=False,
						help="forces redownloading of all acts")

	parser.add_option("--verbose", dest="verbose", type="int", metavar="level", default="1",
						help="how verbose, level: 0 quiet, 1 useful (default), 2 debug")

	parser.add_option("--from", dest="yearfrom", metavar="year", default="1000",
						help="year to process from, default is start of time")
	parser.add_option("--to", dest="yearto", metavar="year", default="9999",
						help="year to process to, default is present day")
	parser.add_option("--year", dest="year", metavar="year", default=None,
						help="year to process (overrides --from and --to)")

	(options, args) = parser.parse_args()
	if (options.year):
		options.yearfrom = options.year
		options.yearto = options.year

	# setup paths

	miscfun.setpaths(options)

	# just collects links to all the first pages
	yiurl = GetYearIndexes(iurl)

	# go through the years
	for yiur in yiurl:
		if yiur[0] < options.yearfrom or yiur[0] > options.yearto:
			continue

		if options.verbose >= 1:
			print "---- Year:", yiur[0]

		yacts = GetActsFromYear(yiur)
		for url, name, chapter in yacts:
			try:
				# build the name for this
				fact = os.path.join(options.actdirhtml, "ukgpa%sc%s.html" % (yiur[0], chapter))
				if not options.force and os.path.isfile(fact):
					continue
				if (yiur[0], chapter) in (("1996", "45"), ("1996", "23")) or (yiur[0] == "1996"):
					print "  Skipping too hard %sc%s" % (yiur[0], chapter)
					continue

				# scrape the act
				if options.verbose >= 1:
					print "scraping ch", chapter, ":", name,
				actpages = GetAllPages(url, options)  # this ends the contact with the internet.

				# trim and tail it
				trimmedpages = TrimPages(actpages, yiur[0], chapter)

				# write it out
				ftemp = "temp.html"
				fout = open(ftemp, "w")
				fout.writelines(trimmedpages)
				fout.close()
				print "******"
				#print "cwdir=%s\nftemp=%s\nfact=%s" % (os.getcwd(),ftemp,fact)
				
				os.rename(ftemp, fact)

			except StandardError, e:
				print ""
				traceback.print_exc()
				print "\nAct being parsed ch %s : %s\nFirst URL: %s\n" % (chapter, name, url)
				sys.exit()

