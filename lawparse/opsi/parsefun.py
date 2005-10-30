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


class ParseError(Exception):
	"""Exception class for parse errors"""
	pass

class TableBalanceError(Exception):
	pass

def gettext(right):
	'''Splits a string at the next significant tag.'''

	m=re.search('<(?!a|/a|format|/format|hint:|/hint:)',right)
	if m:
		s=right[:m.start()]
		rest=right[m.start():]
		m2=re.match('<font size=-4>(\S*)</font>',rest)
		if m2:
			s=s+'<hint:fraction>'+m2.group(1)+'</hint:fraction>'
			(one,rest)=gettext(rest[m2.end():])
			s=s+one
		return(s,rest)
	else:
		return(right,'')	


def TableBalance(tablestring):
	logger=logging.getLogger('')
	s=tablestring
	pos=0
	total=0
	m=re.match('<table(?i)',s)
	if not m:
		logger.error("failed to find first table in:\n%s" % tablestring)
		raise TableBalanceError, 'First table not found'
	t=1
	total=m.end()

	while t>0:
		if total>=len(tablestring):
			logger.error("error balancing table (t=%s):\n%s" % (t,tablestring))
			raise TableBalanceError, 'Balancing failed'
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

