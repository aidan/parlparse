# parsehead.py - parsing of the head of acts

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

import urllib
import urlparse
import re
import sys
import logging

import miscfun
actdirhtml = miscfun.actdirhtml

headlines1 = [('middle', '[\s\S]*?<table(?:cellpadding="?2"?|width="?95%"?|\s)*>\s*<tr>(?i)'),  # first one
			  ('middle', '(?:<tr(?:\s*xml\S*)*>)*\s*<td\s*align="?center"?\s*valign="?bottom"?>\s*(?i)'),
			  ('middle', '<img\s*src="/img/royalarm.gif"\s*alt="Royal\ Arms">\s*</td>\s+(?i)'),
			  ('middle', '<td\s*valign="?bottom"?>(?:&nbsp;<br>)?\s+(?i)'),
			  ('name',   '<font\s*size="?\+3"?><b>([\s\S]{1,250}?)</b></font>\s+(?i)'),
			  ('year',   '<p>(?:</p>)?<font\s*size="?\+1"?>(?:<b>)?(\d{4})'),
			  ('chapter','\s*(?:ch?\s*\.|chapter)?\s*(\d+)(?:</b>)?</font>\s+(?i)'),
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
			  ('preisbn',   'ISBN ((?:0(?:&nbsp;|\s*)(\d\d)(?:&nbsp;|\s*)(\d{6})?(?:&nbsp;|\s*)(\d|X))?)\s*\.\s*'),
			  ('middle', 'The print version may be purchased by clicking\s*'),
			  ('middle', '<A HREF="(?:/bookstore.htm\?AF=A10075(?:&amp;|&)FO=38383(?:&|&amp;)ACTION=AddItem(?:&amp;|&)|http://www.clicktso.com/portal.asp\?DT=ADDITEM&amp;|http://www.ukstate.com/portal.asp\?CH=YourLife&amp;PR=BookItem&amp;)'),
			  ('prodid', '(?:BI|DI|ProductID)=(?:(\d{9}(?:\d|X)?)\.?)?\s*">\s*here</A>.\s*'),
			  ('middle', 'Braille copies of this Act can also be purchased at the same price as the print edition by contacting\s*'),
			  ('middle', 'TSO Customer Services on 0870 600 5522 or '),
			  ('middle', 'e-mail:\s*<A HREF="mailto:customer.services?@tso.co.uk">customer.services?@tso.co.uk</A>.</p>\s*'),
			  ('middle', '<p>\s*Further information about the publication of legislation on this website can be found by referring to the <a href="http://www.hmso.gov.uk/faqs.htm">Frequently Asked Questions</a>.\s*<p>\s*(?i)'),
			  ('middle', 'To ensure fast access over slow connections, large documents have been segmented into "chunks". Where you see a "continue" button at the bottom of the page of text, this indicates that there is another chunk of text available.\s*(?i)'),
			  ('middle', '</td>\s*</tr>\s*(?i)'),
			  ('middle', '\s*<tr><td colspan="?2"?>\s*<hr></td></tr>\s*(?i)'),
			  ('middle', '\s*(?:<a name="[^"]*"></a>)?<tr>\s*(?:<a name="tcon"><td width="20%">|<td valign=top>)\&nbsp;</td>(?i)'),
			  ('middle', '\s*<td align="?center"?>\s*(?i)'),
			  ('middle', '(?:\&nbsp;<br><a name="aofs"></a>)?(?:<b>\s*|<font size="?\+2"?>){2}(?i)'),
			  ('name3', '([\s\S]{1,250}?)(?:</b>\s*|</font>\s*){2}(?i)'),
			  ('middle', '(?:</a>|<td>|</td>|</tr>|<tr>|<td width="20%">\&nbsp;</td>|\s)*\s*(?i)'),
			  ('chapt2', '<p(?: align="center")?>\s*(?:<font size="4">|<b>)([\s\S]{1,250}?)(</font>|</b>)(?i)'),
			  ('middle', '\s*(?:</p>)?\s*</td>\s*</tr>\s*(?i)')
]

headlinestoc1 = [('middle', '(?:<sup><a name="fnf1"></a><a href="#tfnf1">\[1\]</a></sup>)?<br><a name="aofr"></a>\s*<tr>(?i)'),
			  ('middle', '\s*<td width="20%">&nbsp;</td>\s*<td>\s*<center>\s*<font size="\+1">(?i)'),
			  ('middle', '\s*<br><br>(ARRANGEMENT OF (?:SECTIONS|PARTS|CLAUSES))</font>\s*</center>(?i)'),
			  ('middle','\s*<br>\s*<center>\s*(?=<table)'),
			 ]

headlinestoc2 = [('middle', '<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col.gif"></TD><TD valign=top>&nbsp;</TD></TR>\s*'),
		('middle','\s*<TR valign=top><TD valign=top>&nbsp;</TD><TD valign=top>(?=<TABLE(?: width="?100%"?)?>)(?i)')]


headlines2 = [  ('pageurl2','\s*(?:<pageurl[^>]*>\s*)?<tr(?: valign="top")?>\s*<td(?: width="10%"| width=120 align=center valign=bottom| valign=top)>(?i)'),
	('middle', '(?:<img src="/img/ra-col\.gif">)?\s*(?:<br>|&nbsp;)?\s*</td>(?i)'),
	('middle', '\s*(?:<td valign=top>&nbsp;</td>)?\s*'),
	('pageurl3', '(\s*</tr>\s*<pageurl[^>]*>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*)?(?i)'),
	('middle', '<td(?: valign=top)?>(?i)'),
	('middle', '\s*(?:<br>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;</td></tr>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>)?(?i)')]


headlines3 = [ ('middle', '(?:<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col\.gif"></TD><TD\s*valign=top>&nbsp;</TD></TR>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>)?(?i)') ]

frontmatter = [
	('middle','(<tr valign="?top"?>\s*<td width="?10%"?>\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;|<p>)?(?i)'),
	('longtitle','\s*(?:<p>)?((?:An )?\s*(?:\[A\.D\.\s*\S*\])?\s*Act(, as respects Scotland,)? to ([^<]|</?i>)*)(?:\s*<p|</td>\s*</tr>\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td)(?i)'),
	('date',   '\s*align="?right"?>\s*\[(\d+\w*\s*\w+\s*\d{4})\]?\s*(?:<br><br>)?(?i)'),
	('middle', '(?:\s*</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;|\s*<p>)(?i)'),
	('whereas','\s*(Whereas [a-zA-Z ;,&\(\)0-9\']*:)?')]
#,
#	('petition1','(Most Gracious Sovereign,\s*(?:</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?\s*(?:<p>)?WE, Your Majesty\'s most dutiful and loyal subjects,? the Commons of the United Kingdom in Parliament assembled, (towards making good the supply which we have cheerfully granted to Your Majesty in this Session of Parliament,? have resolved to grant unto Your Majesty the sums? hereinafter mentioned|towards raising the necessary supplies to defray Your Majesty\'s public expenses, and making an addition to the public revenue, have freely and voluntarily resolved to give and grant unto Your Majesty the several duties hereinafter mentioned); and do therefore most humbly beseech Your Majesty that it may be enacted,? and )?\s*(?i)'),
#	('middle', '(</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?(?i)') ]


consolidated=[('apply','(?:<p>)?(Apply a sum out of the Consolidated Fund to the service of the year ending on\s*(\d+(?:st|th|nd|rd)\s*(\w*)\s*(\d+)); to appropriate the supplies granted in this Session of Parliament; and to repeal certain Consolidated Fund and Appropriation Acts\.)(?i)'),
		('middle','(?:\s*<p align=right>)?(?i)'),
		('consoldate','\[(.*?)\]\s*(?i)')]



def TableBalance(tablestring):
	s=tablestring
	pos=0
	total=0
	m=re.match('<table(?i)',s)
	if not m:
		print "failed to find first table in:"
		print tablestring
		sys.exit()
	t=1
	total=m.end()

	while t>0:
		if total>=len(tablestring):
			print "error balancing table (t=%s):" % t
			print tablestring
			sys.exit()
		s=tablestring[total:]
		m=re.search('(<table|</table>)(?i)',s)
		if m:
			#print m.group(1),pos,t,total
			if re.match('<table(?i)',m.groups(1)[0]):
				t=t+1
			else:
				t=t-1
			pos=m.end()

		#print t,pos
		total=total+pos
	return total


# this is outside of the class to keep it simple


def ActParseHead(act):
	logger=logging.getLogger('opsi.parsehead')

	for headline in headlines1:
		act.NibbleHead(headline[0], headline[1])

	btoc1exists = re.search('<center>.*ARRANGEMENT OF (?:SECTIONS|PARTS|CLAUSES).*</center>(?si)', act.txt)
	if btoc1exists:
		logger.debug("***** Table of contents TYPE 1 (external heading)")
		for headline in headlinestoc1:
			act.NibbleHead(headline[0], headline[1])
		act.NibbleHead("checkfront", "<table(?i)")

		# look for last open table on first page
		logger.debug("Length of act=%s" % len(act.txt))
		act.txt = act.txt[TableBalance(act.txt):]
		act.NibbleHead("middle", '\s*</center>')

		logger.debug("ttttt", len(act.txt))

	btoc2exists = re.search('<td colspan="?2"? align="?center"?>.*(ARRANGEMENT OF (?:SECTIONS|PARTS|CLAUSES)|CONTENTS).*</td>(?si)', act.txt)
	if btoc2exists:
		logger.debug("***** Table of contents TYPE 2 (internal heading)")
		for headline in headlinestoc2:
			act.NibbleHead(headline[0], headline[1])
		act.NibbleHead("checkfront", "<table(?i)")

		# look for last open table on first page
		logger.debug("Length of act is %s" % len(act.txt))
		act.txt = act.txt[TableBalance(act.txt):]
		act.NibbleHead("middle", '\s*</TD></TR>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top><BR>\s*<HR width=70% align=left>\s*<BR></TD></TR>(?i)')
		act.NibbleHead("pageurl1",'(\s*<pageurl[^>]*>)?(?i)')
		act.NibbleHead("middle", '\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>\s*(?:<BR>&nbsp;<BR>&nbsp;</TD></TR>\s*<TR><TD colspan=2>\s*</TD></TR>|<P>)(?i)')

		logger.debug("ttttt", len(act.txt))



	if re.match('\s*<center>\s*(?=<table)', act.txt):
		print "*****additional tables of contents"
		act.NibbleHead("middle", '\s*<center>\s*')
		act.txt = act.txt[TableBalance(act.txt):]
		act.NibbleHead("middle", '\s*</center>')

	if btoc1exists:
		act.NibbleHead("middle", '\s*<br><br><br><br>\s*</td>\s*</tr>\s*')

	if re.search('<i>notes:</i>(?i)', act.txt):
		print "****suspected footnote"
		#(x1,x2)=ScrapeTool([('first','<tr>\s*<td WIDTH="20%">&nbsp;</td>(?i)'),
		#('middle','\s*<td>\s*<br>\s*<hr>\s*<i>notes:</i><br><br>\s*<p>\s*(?i)'),
		#('middle','<a name="t(?P<ref>cnc1|fnf1)">\[1\]</a>(<b>)?(\[)?([a-zA-Z\.,;\s]*)(\])?\s*(</b>)?\s*<a href="#(?P=ref)">back</a>(?i)'),
		#('middle','\s*</p>\s*</td>\s*</tr>\s*(<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>)(?i)')],tpg)

	m=re.search('<tr>\s*<td WIDTH="20%">&nbsp;</td>\s*<td>\s*<br>\s*<hr>\s*<i>notes:</i><br><br>\s*<p>\s*<a name="t[cf]n[cf]1">\[1\]</a>(<b>)?(\[)?([a-zA-Z\.,;\s]*)(\])?\s*(</b>)?\s*<a href="#[cf]n[cf]1">back</a>\s*</p>\s*</td>\s*</tr>\s*(<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>)(?i)', act.txt)
	if m:
		act.txt = act.txt[:m.start()] + act.txt[m.end():]
		print "****footnote found"

# It turns out to be simpler to treat acts that were a single page differently
# from the others. Not unreasonable I think.

	if re.match('An Act',act.txt):
		pass
	elif re.search('<pageurl', act.txt):
		for headline in headlines2:
			act.NibbleHead(headline[0], headline[1])
	else:
		for headline in headlines3:
			act.NibbleHead(headline[0], headline[1])

	if re.match('(?:<p>)?Apply a sum out of the Consolidated Fund(?i)', act.txt):
		print "****Consolidated Fund"
		for headline in consolidated:
			act.NibbleHead(headline[0], headline[1])

	else:
		for headline in frontmatter:
			act.NibbleHead(headline[0], headline[1])
	

	if re.match("Whereas the government of the Commonwealth of Australia", act.txt):
		act.NibbleHead("whereas", "Whereas the government of the Commonwealth of Australia has requested that the record copy of the Commonwealth of Australia Constitution Act 1900 which is at present on loan to the Commonwealth should remain permanently in the keeping of the Commonwealth;</td>")
		act.NibbleHead("middle", '\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>')
		act.NibbleHead("middle", '\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;And whereas the government of the United Kingdom is willing to advise Her Majesty to accede to that request subject to the approval by Parliament of legislation releasing that copy from the provisions of the Public Records Act 1958;</td>')
		act.NibbleHead("middle", '\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;')

	if re.match("WE", act.txt):
		print "the WE IT ENACTED misspelling", act.ShortID()

	if re.match("(<p>)?Most Gracious Sovereign,(?i)", act.txt):
		print "****money act"
		act.NibbleHead('petition2', '(?:<p>)?(Most Gracious Sovereign,)\s*(?:<p>)?(?i)')
		if re.match("\s*(<P>)?(<font|WE,)(?i)", act.txt):
			act.NibbleHead('enact', '\s*(?:<P>)?(?P<font><font size="-1">)?We(?:, )?(?(font)</font>|)\s*,?\s*(Your Majesty\'s most dutiful and loyal subjects.*? as follows):(?:&#151;|-)(?i)')
			act.NibbleHead('middle','(?:<br>|&nbsp;|\s)*</td>\s*</tr>\s*(?:<p>)?(?i)')
		else:
			act.NibbleHead('middle', '</td>\s*</tr>\s*<tr valign="top">')
			act.NibbleHead('middle', '\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;\s*(?i)')
			act.NibbleHead('enact',  '(WE,? Your Majesty\'s most dutiful and loyal subjects,? .*? as follows):(?:&#151|-);</td>\s*</tr>(?i)')
	else:
		if re.match('(?:<font size=\+3><B>)?(?:<p>)?B(?:</B></font>)?<font size=-1>E IT ENACTED</font>(?i)',act.txt):
			act.NibbleHead('enact', '(?:<font size=\+3><B>)?(?:<p>)?(B(?:</B></font>)?<font size=-1>E IT ENACTED</font>\s*by the Queen\'s most Excellent Majesty, by and with the advice and consent of the Lords Spiritual and Temporal, and Commons, in this present Parliament assembled, and by the authority of the same, as follows:-\s*)(?:<BR>&nbsp;</TD></TR>)?(?i)')
		else:		
			act.NibbleHead('enact',  '((?:Be it (?:therefore )?enacted|WE IT ENACTED)\s+by the Queen\'s most Excellent Majesty[\s\S]*? as\s+follows)(?:<br>|&nbsp;|:|\.|-|&#151;|\s)*</td>\s*</tr>(?i)')



