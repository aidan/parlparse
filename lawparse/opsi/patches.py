# patches.py - special patches to particular acts

# Copyright (C) 2005 Francis Davey, part of lawparse

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


patches=[('ukgpa1997c16',[('&rsquo;\)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt cols="c3"}"></a></TD></TR>(?i)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18pt}"></a></TD></TR>(?i)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt in relation to accounting periods beginning after 5th March 1997\."></a></TD></TR>(?i)','')]),
	('ukgpa1997c46',
		[('',''),
		('; or<UL></TD></TR>','; or</UL></TD></TR>'),
		('In Schedule 9, paragraph 5A is amended as follows\.','In Schedule 9, paragraph 5A is amended as follows.</td></tr>\n')]),
	('ukgpa1997c10',
		[('<TD valign=top>"Valuation Office"\.</TD></TR>\s*</TABLE>','<TD valign=top>"Valuation Office"\.</TD></TR>\n</TABLE>\n</td></tr>')]),
	('ukgpa1988c19',
		[('Wages Act 1986 in relation to any deduction from wages paid before the coming into force of this paragraph\.</td>\s*</tr>\s*</p>','Wages Act 1986 in relation to any deduction from wages paid before the coming into force of this paragraph\.</td>\n</tr>')]),
	('ukgpa1988c20',
		[('\(3\)&nbsp;No part of any highway shall be stopped up under this paragraph until the Secretary of State is in possession of all lands abutting on both sides of that part of the highway','<br><br>&nbsp;&nbsp;&nbsp;&nbsp;(3)&nbsp;No part of any highway shall be stopped up under this paragraph until the Secretary of State is in possession of all lands abutting on both sides of that part of the highway')])
		]

def ActApplyPatches(act):
	logger=logging.getLogger('opsi')
	
	name=act.ShortID()

	logger.info("****Checking for patches to %s" % name)

	for (n,l) in patches:
		if n==name:
			logger.info("****Patching %s" % n)
			for (pattern,replacement) in l:
				logger.debug("***applying pattern",pattern)
				if not re.search(pattern,act.txt):
					logging.error("***error, failed to find substitution text")
					print re.search('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt cols="c3"}"',act.txt)
					raise Exception
				m=re.search(pattern,act.txt)
				if m:
					logger.debug("***Before:%s" % act.txt[m.start()-16:m.end()+16])
				act.txt=re.sub(pattern,replacement,act.txt)
				if m:
					logger.debug("***After:%s" % act.txt[m.start()-16:m.end()+16])

	
