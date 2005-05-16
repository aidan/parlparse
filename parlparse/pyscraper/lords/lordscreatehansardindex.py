#! /usr/bin/python2.3
import sys
import os
import urllib
import urlparse
import string
import re
import xml.sax

# In Debian package python2.3-egenix-mxdatetime
import mx.DateTime

import miscfuncs

toppath = miscfuncs.toppath

# Creates an xml with the links into the index files for the Lords.
# From here we get links into the Main Pages, the Grand Committee,
# the Written Statements, and the Written Answers, which are all
# linked across using the Next Section button (which will really
# screw things up) and all have independent column numbering systems.



# url with the alldays thing on it.
urlalldays = 'http://www.publications.parliament.uk/pa/ld199900/ldhansrd/pdvn/allddays.htm'

# url with bound volumes
# we don't yet scrape across these, as it will be complex.
# deep in here are days which overlap the ones listed in urlalldays,
# but they have different urls even though appearing to be the same text.
# Probably, vols should over-ride the days one.
urlbndvols = 'http://www.publications.parliament.uk/pa/ld199900/ldhansrd/pdvn/home.htm'

pwlordindex = os.path.join(toppath, "lordindex.xml")

# scrape limit date
earliestdate = '2001-11-25'
#earliestdate = '1994-05-01'

def LordsIndexFromAll(urlalldays):
    urlinkpage = urllib.urlopen(urlalldays)
    srlinkpage = urlinkpage.read()
    urlinkpage.close()

    # remove comments because they sometimes contain wrong links
    srlinkpage = re.sub('<!--[\s\S]*?-->', ' ', srlinkpage)

    # Find lines of the form:
    # <p><a href="lds04/index/40129-x.htm">29 Jan 2004</a></p>
    realldayslinks = re.compile('<p><a href="([^"]*)">([^<]*)</a></p>(?i)')
    datelinks = realldayslinks.findall(srlinkpage)

    res = []
    for link in datelinks:
        sdate = mx.DateTime.DateTimeFrom(link[1]).date
        uind = urlparse.urljoin(urlalldays, re.sub('\s', '', link[0]))
        res.append((sdate, '1', uind))

    return res

def LordsIndexFromVolMenu(urlbndvols):
	print urlbndvols
	urvipage = urllib.urlopen(urlbndvols)
	srvipage = urvipage.read()
	urvipage.close()

	# this gets in reverse order
	volnos = [ ]

	# <a href="/pa/ld/ldse0203.htm">Session 2002-03</a>
	ursessh = re.findall('<a href="\s*([^"]*?)\s*">Session \d*-\d*</a>', srvipage)
	for ses in ursessh:
		if not ses:
			continue
		uses = urlparse.urljoin(urlbndvols, ses)

		print uses
		ursepage = urllib.urlopen(uses)
		srsepage = ursepage.read()
		ursepage.close()

		#<A href="ldvol650.htm" TITLE="Link to Volume 650"><B>Volume 650</B></td><td width=70%><B><A href="ldvol650.htm" TITLE="Link to Volume 650">Monday 23 June 2003&nbsp;-
		urse = re.findall('<a href="([^"]*)"[^>]*><b>volume (\d*)</b>(?i)', srsepage)
		for u in urse:
			volnos.append((-string.atoi(u[1]), urlparse.urljoin(uses, u[0])))

	res = []

	# order and check numbering
	volnos.sort()

	# go through each page of volumes and create the date and link
	prevol = None
	for vol in volnos:
		print vol
		if prevol and (prevol + 1 != vol[0]):
			print "Mis-order on vol %d " % prevol
		prevol = vol[0]

		urvopage = urllib.urlopen(vol[1])
		srvopage = urvopage.read()
		urvopage.close()

		#<TR valign=top><TD><IMG src="/pa/img/diamdrd.gif" alt="*"></A></TD><TD></TD><TD
		#colspan=2><B>Thursday 7 November 2002</B></TD></TR>
		#<TR valign=top><TD>&nbsp;</TD><TD></TD><TD><B><A
		#href="../ld200102/ldhansrd/vo021107/index/21107-
		#x.htm">Debates</A></B></B>&nbsp;</TD><TD>&nbsp;&nbsp;&nbsp;</TD>
		sdl = re.findall('<b>([^<]*)</b>(?:\s|<[^a][^>]*>|&nbsp;)*?<a\s*href="([^"]*)">([^<]*)</a>(?i)', srvopage)
		#print "    ", sss

		for sss in sdl:
			if re.match("publications(?i)", sss[2]):
				continue
			if not (sss[2] == "Debates"):
				print "awooga " + sss[2]
				continue
			sdate = mx.DateTime.DateTimeFrom(sss[0]).date
	        uind = urlparse.urljoin(vol[1], re.sub('\s', '', sss[1]))
	        res.append((sdate, '2', uind))

	return res



def WriteXML(fout, urllist):
	fout.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
	fout.write("<publicwhip>\n\n")

	# avoid printing duplicates
	for i in range(len(urllist)):
		r = urllist[i]
		if (i == 0) or (r != urllist[i-1]):
			fout.write('<lordsdaydeb date="%s" type="%s" url="%s"/>\n' % (r[0], r[1], r[2]))

	fout.write("\n</publicwhip>\n")


# gets the old file so we can compare the head values
class LoadOldLIndex(xml.sax.handler.ContentHandler):
	def __init__(self, pwlordindex):
		self.res = []
		if not os.path.isfile(pwlordindex):
			return
		parser = xml.sax.make_parser()
		parser.setContentHandler(self)
		parser.parse(pwlordindex)

	def startElement(self, name, attr):
		if name == "lordsdaydeb":
			ddr = (attr["date"], attr["type"], attr["url"])
			self.res.append(ddr)

	def CompareHeading(self, urllisthead):
		if not self.res:
			return False

		for i in range(min(20, len(urllisthead))):
			if (i >= len(self.res)) or (self.res[i] != urllisthead[i]):
				print "failed match", i
				if i < len(self.res):
					print self.res[i], urllisthead[i]
				return False
		return True


###############
# main function
###############
def UpdateLordsHansardIndex(bforce):
	urllisth = LordsIndexFromAll(urlalldays)
	urllisth.sort()
	urllisth.reverse()

	oldindex = LoadOldLIndex(pwlordindex)
	if oldindex.CompareHeading(urllisth) and not bforce:
		#print "head the same, no new list"
		return

	# get front page (which we will compare against)
	urllistv = LordsIndexFromVolMenu(urlbndvols)

	urlall = urllisth[:]
	urlall.extend(urllistv)

	# compare the above with a loading of the head of the lordindex
	# if not match, take it, and properly deal with urlbndvols

	urlall.sort()
	urlall.reverse()

	urldupl = [ ]

	uuprev = None
	for uu in urlall:
		if (not uuprev) or (uuprev[0] != uu[0]):
			urldupl.append(uu)

	# we need to extend it to the volumes, but this will do for now.
	fpwlordindex = open(pwlordindex, "w");
	WriteXML(fpwlordindex, urlall)
	fpwlordindex.close()



