# parsefun.py - utility functions for parser

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

import re
import sys
import logging

EXCLTAG='(?!hint:|/hint:)'
TEXTEND='(?=<%s|$)' % EXCLTAG



quotepatterns=[
	('(?P<pre>there shall be inserted&\#151;)\s*(?=<table)','',
	'error'),
	("""
		(?=<table cellpadding="8">
			\s*<tr>
			\s*<td width="10%"(?: valign="top")?>&nbsp;</td>
			\s*<td>
		&quot;)(?ix)""",'',
	'simple'),

#unsatisfactory, see below
	("""
		(?=<table\s*cellpadding="8">
			\s*<tr\s*valign="top">
			\s*<td\s*width="15%">
			\s*<br>)(?ix)""",'',
	'withmargin'),
	("""
		(?=<table\s*cellpadding="8">
			\s*<tr\s*valign="top">\s*<td\s*width="5%">\s*<br>\s*</td>
			\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&nbsp;&nbsp;&nbsp;&nbsp;<b>)(?ix)""",'',
	'section'),
	("""
		(?=<table\s*cellpadding="8">
			\s*<tr\s*valign="top">
			\s*<td\s*width="20%">&nbsp;</td>\s*<td>
			\s*<br><i>\s*<center>)(?ix)""",'',
	'full'),
	("""
		(?=<table\s*cellpadding="8">
			\s*<tr>\s*<td\s*width="10%"\s*valign="top">&nbsp;</td>
			\s*<td align="center">\s*<a name="sdiv1A">)(?ix)""",'',
	'heading'),
# this is probably over-general, we should probably look only for quotes

	('(?=<table\s*cellpadding="8">)','',
	'withmargin2'),
	("""
		(?P<pre><TR><TD valign=top>&nbsp;</TD><TD\s*valign=top>)
		(?=<TABLE>)(?ix)""",'',
	'rightquote')
	]

	
tablepatterns=[
	('(?P<pre><TR><TD valign=top>&nbsp;</TD><TD valign=top align=center>&nbsp;<BR>T<FONT size=-1>ABLE OF </FONT>R<FONT size=-1>ATES OF </FONT>T<FONT size=-1>AX</TD></TR>\s*<TR><TD></TD><TD valign=top>)\s*(?=<table border width=100%>)','\s*(?P<post></td>\s*</tr>)', 'taxtable1997c16'),
	('(?=<TABLE cellpadding=10 border>)','','repealtable1'),
	('(?=<table border>)','','repealtable2'),
	('<center>\s*(?=<table>)','\s*</center>','tableCentered'),
	('(?=<table)','','misctable')]


class ParseError(Exception):
	"""Exception class for parse errors"""
	pass

class TableBalanceError(ParseError):
	pass

def gettext(right):
	'''Splits a string at the next significant tag or entity.'''

	#m=re.search('<(?!a|/a|format|/format|hint:|/hint:)',right)
	m=re.search('<(?!a|/a|format|/format|hint:|/hint:)|&#151;|&nbsp;',right)
	if m:
		s=right[:m.start()]
		rest=right[m.start():]
		m2=re.match('<font size=-4>(\S*)</font>',rest)
		if m2:
			s=s+'<hint:fraction>'+m2.group(1)+'</hint:fraction>'
			(one,rest)=gettext(rest[m2.end():])
			s=s+one
		if False: #re.match('&#151;',rest):
			print rest[:32]
			sys.exit()
		return(s,rest)
	else:
		return(right,'')	


def TableBalance(tablestring):
	"""Returns the position where the table in tablestring ends.

	The tablestring argument must beging with a <table> tag."""

	logger=logging.getLogger('')
	s=tablestring
	pos=0
	total=0
	m=re.match('<table(?i)',s)
	if not m:
		#logger.error("failed to find first table in:\n%s" % tablestring[:255])
		raise TableBalanceError, "First table not found\nFailed to find first table in:\n%s" % tablestring[:32]
	t=1
	total=m.end()

	while t>0:
		if total>=len(tablestring):
			
			raise TableBalanceError, 'Balancing failed\nError balancing table (t=%s):\n%s' % (t,tablestring[:255])
		s=tablestring[total:]
		m=re.search('(<table|</table>)(?i)',s)
		if m:

			if re.match('<table(?i)',m.groups(1)[0]):
				t=t+1
			else:
				t=t-1
			pos=m.end()


		total=total+pos
	return total

