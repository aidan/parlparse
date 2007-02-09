# vim:sw=8:ts=8:et:nowrap

import sys
import os
import urllib
import urlparse
import string
import re
import xml.sax

import mx.DateTime

import miscfuncs
from standingutils import construct_shortname

toppath = miscfuncs.toppath

# Creates an xml with the links into the index files for the Standing Committees.

# url with the alldays thing on it.
urlalldays = 'http://www.publications.parliament.uk/pa/ld199900/ldhansrd/pdvn/allddays.htm'

urlstandingbillsyears = "http://www.publications.parliament.uk/pa/cm/stand.htm"
urlstandingothersyears = "http://www.publications.parliament.uk/pa/cm/othstn.htm"
pwsdantingindex = os.path.join(toppath, "standingindex.xml")

def GetLinksTitles(urlpage):
	res = [ ]
	uin = urllib.urlopen(urlpage)
	s = uin.read()
	uin.close()
	vdat = re.search("(?s)page title and static information follows(.*?)(end of variable data|$)", s).group(1)
	vdat = re.sub("(?s)<!--.*?-->", "", vdat)
	for lk in re.findall('<a href\s*=\s*"([^"]*)">([^<]*)</a>(?i)', vdat):
		lklk = re.sub('\s', '', lk[0])
		lkname = re.sub("(?:\s|&nbsp;)+", " ", lk[1]).strip()
		res.append((urlparse.urljoin(urlpage, lklk), lkname))
		#print res[-1]
	return res

romanconvmap = { "I":1, "II":2, "III":3, "IV":4, "V":5, "VI":6, "VII":7, "1":1, "2":2, }


# get the standing committee parsing to work, output XML
# res = [ (urllink, date, sitting number, sitting part, morning|afternoon) ]
def GetReportProcedings(urlpage, year):
	res = [ ]
	firstdate = ""
	uin = urllib.urlopen(urlpage)
	s = uin.read()
	uin.close()
	vdat = re.search("(?s)Report of proceedings(.*?)(Associated Memoranda|start of footer|$)", s).group(1)
	vdat = re.sub("(?s)<!--.*?-->", "", vdat)

	# correct a few typos
	if year == "2005":
		vdat = re.sub('(/pa/cm200506/cmstand/e/st050705/am/50705s01.htm">1st  sitting</A></FONT></TD><TD><FONT size=\+1><A\s*href="/pa/cm200506/cmstand/)b/st050621(/am/50705s01.htm">5 July 2005)', '\g<1>e/st050705\g<2>', vdat)
		vdat = re.sub('(/pa/cm200506/cmstand/b/st060713/am/60713s01.htm">3rd sitting</A></FONT></TD><TD><FONT size=\+1><A href="/pa/cm200506/cmstand/b/st06071)1(/am/60713s01.htm">13 July 2006)', '\g<1>3\g<2>', vdat)
	if year == "2002":
		vdat = re.sub('(<A href="st030225/)a(m/30225s01.htm">10th sitting</A></FONT></TD><TD><FONT size=\+1><A href="st030225/pm/30225s01.htm">25th February 2003 \(afternoon\))', '\g<1>p\g<2>', vdat)
		vdat = re.sub('(st03061)7/30618(s01.htm">2nd\s*sitting</A></FONT></TD>\s*<TD><FONT size=\+1><A href="st030618/30618s01.htm">18th June 2003)', '\g<1>8/30618\g<2>', vdat)
	if year == "2001":
		vdat = re.sub('(st011127/)a(m/11127s01.htm">6th sitting</A></FONT></TD>\s*<TD nowrap><FONT size=\+1><A href="st011127/pm/11127s01.htm">27th November 2001 \(afternoon\))', '\g<1>p\g<2>', vdat)
	if year == "1997":
		vdat = re.sub('(st980512/pm/pt)1(/80512s01.htm">3rd sitting </A></FONT></TD>\s*<TD><FONT size=\+1><A href="st980512/pm/pt2/80512s01.htm">12 May 1998)', '\g<1>2\g<2>', vdat)

	lks = re.findall('(?si)<a\s+href\s*=\s*"([^"]*)">(.*?)(?:</a>|<tr>)(?i)', vdat)
	for lk in lks:
		lklk = re.sub("\s", "", lk[0])
		lklk = re.sub("/+", "/", lklk)
		lklk = urlparse.urljoin(urlpage, lklk)

		lkname = re.sub("(?:\s|&nbsp;|<br>|</?[iI]>)+", " ", lk[1]).strip()
		mprevdebates = re.match("Debates on.*?Bill in Session \d\d\d\d-\d\d", lkname)

		if (not res or res[-1][0] != lklk) and not mprevdebates:
			 res.append([lklk, "", 0, 0, ""])  # urllink, date, sitting number, sitting part, morning|afternoon

		msecreading = re.match("Second Reading Committee$|Standing Committee B$", lkname)
		mothmem = re.match("Other Memorand(?:ums|a) and Letters [Ss]ubmitted to the Committee$", lkname)
		msitting = re.match("(\d+)(?:st|nd|rd|th)\s+[Ss]itting(?: \((cont)'d\))?(?: \(Part ([I]*)\))?$", lkname)
		mdate = re.match("(?:<b>)?(\d+(?:st|nd|rd|th)? (?:January|February|March|April|May|June|July|August|September|October|November|December)(?: \d\d\d\d)?)(?:</b>)?(?: ?\(([Mm]orning|[Aa]fternoon|evening)\)?)?(?: [\[\(\-]?\s*[Pp]art ([IViv\d]*)\s*[\]\)]?)?(?: ?\((morning|[Aa]fternoon)\)?)?$", lkname)

		# from this we can assembly the components of the result
		if mothmem:
			assert not res[-1][1]
			assert res[-1][3] == 0
			res[-1][3] = 99999
		elif msecreading:
			pass # print lkname
		elif msitting:
			assert res[-1][2] == 0 or res[-1][2] == int(msitting.group(1))
			res[-1][2] = int(msitting.group(1)) # sitting
			if msitting.group(3): # part
				assert res[-1][3] == 0
				res[-1][3] = romanconvmap[msitting.group(3).upper()]
		elif mdate:
			sdate = mdate.group(1)
			if year == "2003" and not re.match(".*?\d$", sdate):
				if re.search("st04012[02]/[ap]m/4012[02]s01.htm$", res[-1][0]):
					sdate = sdate + " 2004"
				else:
					print year, mdate.group(0), res[-1][0]
					assert False
			if year == "1999":
				sdate = re.sub("February 1999", "February 2000", sdate)
			if year == "2004":
				sdate = re.sub("January 2004", "January 2005", sdate)
			if year == "2003" and re.match(".*?41111s01.htm$", res[-1][0]):
				sdate = re.sub("[34] November 2004", "11 November 2004", sdate)
			if year == "1999" and re.match(".*?00118s01.htm$", res[-1][0]):
				sdate = re.sub("7 February 2000", "18 January 2000", sdate)
			if year == "2005" and re.match(".*?6062\ds01.htm$", res[-1][0]):
				sdate = re.sub("2005", "2006", sdate)
			res[-1][1] = mx.DateTime.DateTimeFrom(sdate).date
			# firstdate is used to label the committee
			if not firstdate or firstdate > res[-1][1]:
				firstdate = res[-1][1]

			if mdate.group(2): # morning|afternoon
				assert not res[-1][4]
				res[-1][4] = mdate.group(2).lower()
			if mdate.group(4): # morning|afternoon
				assert not res[-1][4]
				res[-1][4] = mdate.group(4).lower()
			if mdate.group(3): # part
				assert res[-1][3] == 0
				res[-1][3] = romanconvmap[mdate.group(3).upper()]
		elif mprevdebates:
			print "skipping  ****%s*" % lkname
		elif lkname:
			print "  ****%s*" % lkname

	# check the numbering of the parts is good
	#for r in res:
	#	print r[1:]

	# single sitting, set it up
	if len(res) == 1:
		assert (res[0][2] == 0 or res[0][2] == 1) and res[0][3] == 0
		res[0][2] = 1

	# now check the numbering of the parts is consistent (requires sorting them)
	parts = [ [r[2], r[3], r[1], r]  for r in res  if r[3] != 99999 ]  # sitting, part, date, whole
	parts.sort()
	prev = None
	for p in parts:
		assert int(p[2][:4]) - int(year) in [0, 1]
		if prev:
			if prev[0] == p[0]:
				if prev[1] == 0 and p[1] == 2:
					prev[1] = 1
					prev[3][3] = 1 # blank case, give it sitting number 1
				else:
					assert prev[1] + 1 == p[1] and prev[1] != 0
			else:
				assert prev[0] + 1 == p[0]

			assert prev[2] <= p[2] # date
		else:
			if year == "2001" and re.match(".*?/pa/cm200102/cmstand/special/cmadopt.htm$", urlpage):
				assert p[0] == 2  # 1st meeting held in private
			elif year == "1998" and re.match(".*?/pa/cm199899/cmstand/special/special.htm$", urlpage):
				assert p[0] == 2  # 1st meeting held in private
			elif year == "1999" and re.match(".*?/pa/cm199900/cmstand/a/cmserv.htm$", urlpage):
				assert p[0] == 25  # 1st 24 meeting ommitted
			else:
				if p[0] != 1:
					print "starting at %s" % p[0]
				#	print vdat
				#assert p[0] == 1
		prev = p
	return res, firstdate

def GetBillLinks(bforce):
	billyears = GetLinksTitles(urlstandingbillsyears)
	res = [ ]
	if not bforce:
		billyears = billyears[0:1]   # if you don't do --force-index, you just get the current year
		
	for billyear in billyears:
		year = re.match("Session (\d\d\d\d)-\d\d(?:\d\d)?$", billyear[1]).group(1)
		if miscfuncs.IsNotQuiet():
			print "year=", year
		bnks = GetLinksTitles(billyear[0])
		for bnk in bnks:
			mcttee = re.match("(.*? (?:Bill|Dogs|Names))(?:\s?\[Lords\])?\s?(?:\(except clauses.*?\) )?(\((Standing Committee [aA-Z]|Special Standing Committee|Second Reading Committee)\)\s?)?$", bnk[1])
			if not mcttee:
				print "Unrecognized committee or bill name:", bnk
			billtitle = mcttee.group(1)
			if billtitle == "Company & Business Names":
				billtitle = "Company and Business Names (Chamber of Commerce, Etc.) Bill"
			if billtitle == "Breeding and Sale of Dogs":
				billtitle = "Breeding and Sale of Dogs Bill"
			if not re.match(".*? Bill$", billtitle):
				print "Does not end in Bill", billtitle
			assert re.match(".*? Bill$", billtitle)
			committee = mcttee.group(2)
			#res.append((year, billtitle, committee, bnk[0]))
			ps, committeedate = GetReportProcedings(bnk[0], year)
			for p in ps:
				res.append(((year, billtitle, committee, bnk[0], committeedate), p))
	return res

def WriteXML(fout, billinks):
	fout.write('<?xml version="1.0" encoding="ISO-8859-1"?>\n')
	fout.write("<publicwhip>\n\n")

	for billink in billinks:
		(h, p) = billink
		(year, billtitle, committee, indexurl, committeedate) = h
		(urllink, date, sittingnumber, sittingpart, daypart) = p

		# construct short name to use for the pullglued file
		# "P" = Public Bill Committee
		shortcommitteeletter = "P"
		if committee:
			mstandc = re.match("\(?Standing Committee ([aA-Z])\)?", committee)
			if mstandc:
				shortcommitteeletter = mstandc.group(1).upper()
			elif re.match("\(?Special Standing Committee\)?", committee):
				shortcommitteeletter = "S"
			elif re.match("\(?Second Reading Committee\)?", committee):
				shortcommitteeletter = "2"
			else:
				print "Unrecognized committee for short name:", committee
				assert False
		shortname = construct_shortname(committeedate, shortcommitteeletter, sittingnumber, sittingpart, date)
		fout.write('<standingcttee shortname="%s" session="%s" date="%s" sittingnumber="%d" sittingpart="%d" daypart="%s" committeename="%s" billtitle="%s" urlindex="%s" url="%s"/>\n' % (shortname, year, date, sittingnumber, sittingpart, daypart, committee, billtitle, indexurl, urllink))

	fout.write("\n</publicwhip>\n")


###############
# main function
###############
def UpdateStandingHansardIndex(bforce):
	#print "not--UpdateStandingHansardIndex"
	#return
	billinks = GetBillLinks(bforce)

	# we need to extend it to the volumes, but this will do for now.
	fpwsdantingindex = open(pwsdantingindex, "w");
	WriteXML(fpwsdantingindex, billinks)
	fpwsdantingindex.close()



