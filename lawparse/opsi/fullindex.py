#!/usr/bin/python

import urllib
import urlparse
import re
import sys

# starting point for directories
actdir = "C:/pwhip/parldata/acts"
iurl = "http://www.opsi.gov.uk/acts.htm"


# set of heading matches, broken down to make it easier to
# discover where the failure is
headlines = [ ('first',  '<table(?:cellpadding=2|width=95%|\s)*>\s+(?i)'),
			  ('middle', '<tr>\s*<td\s*align=center\s*valign=bottom>\s*(?i)'),
			  ('middle', '<img\s*src="/img/royalarm.gif"\s*alt="Royal\ Arms">\s*</td>\s+(?i)'),
			  ('middle', '<td\s*valign="?bottom"?>(?:&nbsp;<br>)?\s+(?i)'),
			  ('name',   '<font\s*size="?\+3"?><b>([\s\S]{1,250}?)</b></font>\s+(?i)'),
			  ('chapt',  '<p>(?:</p>)?<font\s*size="?\+1"?>(?:<b>)?([^<]*)(?:</b>)?</font>\s+(?i)'),
			  ('middle', '</td>\s*</tr>\s+(?i)'),
			  ('middle', '<tr(?:\s*xml\S*)*>\s*<td\s*colspan="?2"?>\s*<hr></td>\s*</tr>\s+(?i)'),
			  ('middle', '<tr>\s*<td\s*valign="?top"?>&nbsp;</td>\s+(?i)'),
			  ('middle', '<td\s*valign="?top"?>\s+(?i)'),
			  ('cright', '<p>&copy;\ Crown\ Copyright\ (\d+<?)</p>\s+(?i)'),
			  ('middle', "<P>\s*Acts of Parliament printed from this website are printed under the superintendence and authority of the Controller of HMSO being the Queen's Printer of Acts of Parliament.\s*"),
			  ('middle', '<P>\s*The legislation contained on this web site is subject to Crown Copyright protection. It may be reproduced free of charge provided that it is reproduced accurately and that the source and copyright status of the material is made evident to users.\s*'),
			  ('middle', "<P>\s*It should be noted that the right to reproduce the text of Acts of Parliament does not extend to the Queen's Printer imprints which should be removed from any copies of the Act which are issued or made available to the public. This includes reproduction of the Act on the Internet and on intranet sites. The Royal Arms may be reproduced only where they are an integral part of the original document.\s*"),
			  ('middle', '<p>The text of this Internet version of the Act is published by the Queen\'s Printer of Acts of Parliament and has been prepared to reflect the text as it received Royal Assent.\s*'),
			  ('name2',  'A print version is also available and is published by The Stationery Office Limited as the <b>(.{0,100}?)\s*</b>,\s*'),
			  ('isbn',   'ISBN 0(?:&nbsp;|\s+)(\d\d)(?:&nbsp;|\s+)(\d{6})(?:&nbsp;|\s+)(\d|X)\.\s*'),
			  ('middle', 'The print version may be purchased by clicking\s*'),
			  ('middle', '<A HREF="/bookstore.htm\?AF=A10075&FO=38383&ACTION=AddItem&'),
			  ('prodid', 'ProductID=(\d{9}(?:\d|X))\.?">\s*here</A>.\s*'),
			  ('middle', 'Braille copies of this Act can also be purchased at the same price as the print edition by contacting\s*'),
			  ('middle', 'TSO Customer Services on 0870 600 5522 or '),
			  ('middle', 'e-mail:\s*<A HREF="mailto:customer.services?@tso.co.uk">customer.services?@tso.co.uk</A>.</p>\s*'),
			  ('middle', '<P>\s*Further information about the publication of legislation on this website can be found by referring to the <A HREF="http://www.hmso.gov.uk/faqs.htm">Frequently Asked Questions</a>.\s*<P>\s*'),
			  ('middle', 'To ensure fast access over slow connections, large documents have been segmented into "chunks". Where you see a "continue" button at the bottom of the page of text, this indicates that there is another chunk of text available.\s*'),
			  ('middle', '</td>\s*</tr>\s*(?i)'),
]

'''
(next set of lines, which has repeated info that's worth cross-checking)

<TR><TD colspan=2><HR></TD></TR>

<TR><TD valign=top>&nbsp;</TD>
<TD align=center>&nbsp;<BR><A name="aofs"></a><font size=+2><b>Appropriation Act 2005</b></font>
<p><b>2005 Chapter 3</b>
</TD></TR>

<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col.gif"></TD><TD valign=top>&nbsp;</TD></TR>


<TR valign=top><TD valign=top>&nbsp;</TD><TD valign=top><TABLE width=100%>
'''

def ScrapeAct(aurl):
	tpg = urllib.urlopen(aurl).read()
	print aurl

	for hline in headlines:
		if hline[0] == 'first':
			mline = re.search(hline[1], tpg)
		else:
			mline = re.match(hline[1], tpg)
		if not mline:
			print 'failed at:', hline
			print 'on:'
			print tpg[:1000]
			# drop through to create exit error

		# extract any strings
		# (perhaps make a class that has all these fields in it)
		if hline[0] == 'name':
			name = mline.group(1)
		elif hline[0] == 'chapt':
			chapt = mline.group(1)
			# decode the chapter number here
		elif hline[0] == 'cright':
			cright = mline.group(1)
		elif hline[0] == 'name2':
			name2 = mline.group(1)
		elif hline[0] == 'isbn':
			isbn = "%s %s %s" % (mline.group(1), mline.group(2), mline.group(3))
		elif hline[0] == 'prodid':
			prodid = mline.group(1)

		# move on
		tpg = tpg[mline.end(0):]

	if name != name2:
		print "--------------------mismatching names, /%s/ <> /%s/" % (name, name2)
	print chapt, name, prodid
	return (cright, chapt, name, aurl)


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
#yiurl = yiurl[2:8]
for yiur in yiurl:
	allacts.extend(GetActsFromYear(yiur))
print "lenlen", len(allacts)
fout = open("listacts1.xml", "w")
i = 0    # numbering helps work out where to restart for error examining
for aurl in allacts[0:]:  # start in middle when chasing an error
	res = ScrapeAct(aurl)
	print i, res
	fout.write('<act year="%s" chapter="%s"\tname="%s" url="%s">\n' % res)
	fout.flush()
	i += 1
fout.close()


