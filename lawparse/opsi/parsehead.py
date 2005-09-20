#!/usr/bin/python

import urllib
import urlparse
import re
import sys

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
			  ('isbn',   'ISBN ((?:0(?:&nbsp;|\s*)(\d\d)(?:&nbsp;|\s*)(\d{6})?(?:&nbsp;|\s*)(\d|X))?)\s*\.\s*'),
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

headlinestoc = [('middle', '(?:<sup><a name="fnf1"></a><a href="#tfnf1">\[1\]</a></sup>)?<br><a name="aofr"></a>\s*<tr>(?i)'),
			  ('middle', '\s*<td width="20%">&nbsp;</td>\s*<td>\s*<center>\s*<font size="\+1">(?i)'),
			  ('middle', '\s*<br><br>ARRANGEMENT OF (?:SECTIONS|PARTS|CLAUSES)</font>\s*</center>(?i)'),
			  ('middle','\s*<br>\s*<center>\s*(?=<table)'),
			 ]

preamblepattern='((?:An )?\s*(?:\[A\.D\.\s*\S*\])?\s*Act(, as respects Scotland,)? to ([^<]|</?i>)*)'

headlines2 = [  ('middle','\s*(?:<pageurl[^>]*>\s*)?<tr(?: valign="top")?>\s*<td(?: width="10%"| width=120 align=center valign=bottom)>(?i)'),
				('middle', '(?:<img src="/img/ra-col\.gif">)?\s*(?:<br>|&nbsp;)?\s*</td>(?i)'),
				('middle', '\s*(?:<td valign=top>&nbsp;</td>)?\s*'),
				('middle', '(\s*</tr>\s*<pageurl[^>]*>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*)?(?i)'),
				('middle', '<td(?: valign=top)?>(?i)'),
				('middle', '\s*(?:<br>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;</td></tr>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>)(?i)'),
				('preamble','(?:' + preamblepattern + '</td>\s*</tr>\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td |\s*<p>' + preamblepattern +'\s*<p)(?i)'),
				('date',   '\s*align="?right"?>\s*\[(\d+\w*\s*\w+\s*\d{4})\]?\s*(?:<br><br>)?(?i)'),
				('middle', '(?:\s*</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;|\s*<p>)(?i)'),
				('consideration','\s*(Whereas [a-zA-Z ;,&\(\)0-9\']*:)?'),
				('petition1','(Most Gracious Sovereign,\s*(?:</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?\s*(?:<p>)?WE, Your Majesty\'s most dutiful and loyal subjects,? the Commons of the United Kingdom in Parliament assembled, (towards making good the supply which we have cheerfully granted to Your Majesty in this Session of Parliament,? have resolved to grant unto Your Majesty the sums? hereinafter mentioned|towards raising the necessary supplies to defray Your Majesty\'s public expenses, and making an addition to the public revenue, have freely and voluntarily resolved to give and grant unto Your Majesty the several duties hereinafter mentioned); and do therefore most humbly beseech Your Majesty that it may be enacted,? and )?\s*(?i)'),
				('middle', '(</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?(?i)') ]



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
	#print "****tablestring ending with:"
	#print tablestring[total-16:total]
	#print "****next begins with:"
	#print tablestring[total:total+32]
	#print
	return total


# this is outside of the class to keep it simple
def ActParseHead(act):
	for headline in headlines1:
		act.NibbleHead(headline[0], headline[1])

	btocexists = re.search('(?:<center>|<td colspan=2 align=center>).*ARRANGEMENT OF (?:SECTIONS|PARTS|CLAUSES).*(?:</center>|</td>)(?si)', act.txt)
	if btocexists:
		print "TOCTOC"
		for headline in headlinestoc:
			act.NibbleHead(headline[0], headline[1])
		act.NibbleHead("checkfront", "<table")

		# look for last open table on first page
		print len(act.txt)
		act.txt = act.txt[TableBalance(act.txt):]
		act.NibbleHead("middle", '\s*</center>')

		print "ttttt", len(act.txt)

	if re.match('\s*<center>\s*(?=<table)', act.txt):
		print "*****additional tables of contents"
		act.NibbleHead("middle", '\s*<center>\s*')
		act.txt = act.txt[TableBalance(act.txt):]
		act.NibbleHead("middle", '\s*</center>')

	if btocexists:
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




	for headline in headlines2:
		act.NibbleHead(headline[0], headline[1])

	if re.match("Whereas the government of the Commonwealth of Australia", act.txt):
		act.NibbleHead("middle", "Whereas the government of the Commonwealth of Australia has requested that the record copy of the Commonwealth of Australia Constitution Act 1900 which is at present on loan to the Commonwealth should remain permanently in the keeping of the Commonwealth;</td>")
		act.NibbleHead("middle", '\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>')
		act.NibbleHead("middle", '\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;And whereas the government of the United Kingdom is willing to advise Her Majesty to accede to that request subject to the approval by Parliament of legislation releasing that copy from the provisions of the Public Records Act 1958;</td>')
		act.NibbleHead("middle", '\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;')

	if re.match("WE", act.txt):
		print "the WE IT ENACTED misspelling", act.ShortID()
	if re.match("Most Gracious Sovereign,", act.txt):
		act.NibbleHead('middle', 'Most Gracious Sovereign,')
		if re.match("<font", act.txt):
			act.NibbleHead('enact', '(<font size="-1">We(?:, )?</font>\s*,?\s*Your Majesty\'s most dutiful and loyal subjects.*? as follows):&#151;</td>\s*</tr>\s*(?:<p>)?')
		else:
			act.NibbleHead('middle', '</td>\s*</tr>\s*<tr valign="top">')
			act.NibbleHead('middle', '\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;\s*(?i)')
			act.NibbleHead('enact',  '(WE Your Majesty\'s most dutiful and loyal subjects, .*? as follows):&#151;</td>\s*</tr>(?i)')
	else:
		if re.match('<font size=\+3><B>B</B></font><font size=-1>E IT ENACTED</font>(?i)',act.txt):
			act.NibbleHead('enact', '<font size=\+3><B>B</B></font><font size=-1>E IT ENACTED</font>( by the Queen\'s most Excellent Majesty, by and with the advice and consent of the Lords Spiritual and Temporal, and Commons, in this present Parliament assembled, and by the authority of the same, as follows:- )<BR>&nbsp;</TD></TR>(?i)')
		else:		
			act.NibbleHead('enact',  '((?:Be it (?:therefore )?enacted|WE IT ENACTED)\s+by the Queen\'s most Excellent Majesty[\s\S]*? as\s+follows)(?:<br>|&nbsp;|:|\.|-|&#151;|\s)*</td>\s*</tr>(?i)')



