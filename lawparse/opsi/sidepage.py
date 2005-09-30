#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import os

import miscfun

# starting point for directories
sidirhtml = miscfun.sidirhtml

# starting point for scraping
iurl = "http://www.opsi.gov.uk/stat.htm"

# helpful debugging match stuff
def HeadMatch(exp, txt):
	m = re.match(exp, txt)
	if not m:
		print "failed to match expression:\n\t", exp
		print "onto:"
		print txt[:1000]
		print re.match('\s*<TR><TD align=center>&nbsp;<br><FONT SIZE=5>ABSTRACT<BR>', txt)
		print re.match('\s*<TR><TD align=center>&nbsp;<br>', txt)
		print re.match('\s*<TR><TD', txt)
		raise Exception


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

	res = [ ]
	print "****len urlpages=", len(urlpages)
	for i in range(len(urlpages)):
		(url, page) = urlpages[i]
		print url, i
		res.append('<pageurl page="%d" url="%s"/>\n' % (i, url))

		# trim off heading bits
		if i != 0:
			print "page", i
			m=re.search('<P align =right><A HREF="[^"]*">Back to previous page</A></P></TD></TR></TABLE>\s*<TABLE width=100%>(?i)',page)
			if m:
				page=page[m.end():]
			else:
				print "Can't find page start", m
				print page[:250]
				sys.ext()

		# trim off tail bits

		# single page
		if len(urlpages) == 1:
			page, mobj = TailMatch('<TABLE width="?95%"? align="?right"?>\s*<TR><TD colspan="?3"?>\s*(?:<p><center>)?\s*<A HREF="/stat\.htm">Other UK SIs</A>(?i)',page)

		# first page
		elif i == 0:
			page, mobj = TailMatch('<TABLE width=95%>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>\s*(?:<p><center>)?\s*<A HREF="[^"]*"><IMG border=0 align=top src="/img/nav-conu\.gif" Alt="continue"></A>(?i)',page)

		# middle page
		elif i != len(urlpages) - 1:
			page, mobj = TailMatch('<TABLE width=95%>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>\s*(?:<p><center>)?\s*<A HREF="[^"]*"><IMG border=0 align=top src="/img/nav-conu\.gif" Alt="continue"></A>(?i)',page)
	
		# last page
		else:
			page, mobj = TailMatch('<TABLE width=95% align=right>\s*<TR><TD colspan="?3"?>\s*(?:<p><center>)?\s*<A HREF="/stat\.htm">Other UK SIs</A>',page)

		res.append(page)
	
	return res



# recurse through all the links and make a set of strings for each url
def GetAllPages(url):
	res = [ ]
	while True:
		page = urllib.urlopen(url).read()
		res.append((url, page))
		contbutton = re.search('<TR>(?:<TD valign=top>&nbsp;</TD>)?<TD(?: valign=top)?>\s*<A HREF="([^">]*)"><IMG border=0 align=top src="/img/nav-conu.gif" Alt="continue"></A>(?:<BR>|&nbsp;|\s)*</TD></TR>(?i)', page)
		if not contbutton:
			if re.search('Alt="?continue"?',page):
				print "****problem seems to be an undetected continue."
				sys.exit()
			else:
				break
		url = urlparse.urljoin(url, contbutton.group(1))

	return res


# get all the links to the starts of the page
def SIIndexes(iurl):
	pg = urllib.urlopen(iurl).read()
	siindexes = re.findall('<a href="(/si/si(\d{4})\d(2).htm)">Nos\s*(\d{4}-\d{4})</a>', pg )

	res = [ ]
	for index in siindexes:
		#assert re.search('\d{4}', yact[0]).group(0) == yact[1]
		res.append((index[1], index[3], urlparse.urljoin(iurl, index[0])))
		print index
	return res

def SIfromindex(index):
	pg = urllib.urlopen(index[2]).read()
	#msi = re.search("<h4>Alphabetical List</h4>([\s\S]*?)<h4>Numerical List</h4>", pg)
	#alphacts = mpubact.group(1)
	eachsi = re.findall('<a href="(si[^"]*)">([^<]*)</a>', pg)
	res = [ ]
	for esi in eachsi:
		simatch=re.match("si(\d{4})/(\d{4})(\d{4}).htm$", esi[0])
		if simatch:
			#mtitch = re.match("([\w\d\s\.,'\-()]*?)\s*(\d{4})\s*\(?c\.?\s*(\d+)\s*\)?$", eact[1])
			#assert mtitch.group(2) == yiurl[0]
			url = urlparse.urljoin(index[2], esi[0])
			v = (url, esi[1], simatch.group(2), simatch.group(3))
			if v not in res:  # 1988 has an act listed twice
				res.append(v)
		else:
			pass
			#assert re.match("\#num|.*\.pdf", eact[0])

	# check all the numbered chapters are here
	#chnum = [ int(x[2])  for x in res ]
	#chnum.sort()
	#assert chnum == range(1, len(chnum) + 1)

	return res


# main running part
if __name__ == '__main__':
	# just collects links to all the first pages
	siurl = SIIndexes(iurl)
	#yiurl = yiurl[-7:]  # just two years

	# go through the years
	for index in siurl:
		print "SI:", index
		sis = SIfromindex(index)
		for url, name, year, number in sis:
			# build the name for this
			fis = os.path.join(sidirhtml, "uksi%sno%s.html" % (year,number))
			if os.path.isfile(fis):
				#print "  skip ch", chapter, ":", name
				continue
			#if (yiur[0], chapter) in (("1996", "45"), ("1996", "23")) or (yiur[0] == "1996"):
			#	print "  Skipping too hard %sc%s" % (yiur[0], chapter)
				continue

			print "scraping SI", year, ":", number, ":" , name
			sipages = GetAllPages(url)  # this ends the contact with the internet.
			print "pages", len(sipages)
			if len(sipages) > 1:
				print "***********pages more than 1"
				#sys.exit()
			trimmedpages = TrimPages(sipages, year, number)
			ftemp = "temp.html"
			fout = open(ftemp, "w")
			fout.writelines(trimmedpages)
			fout.close()
			os.rename(ftemp, fis)



