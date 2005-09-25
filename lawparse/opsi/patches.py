
import re
import sys


patches=[('ukgpa1997c16',
		[('''<TR><TD valign=top>&nbsp;</TD><TD valign=top><TABLE>\s*<TR><TD valign=top><IMG SRC="/img/amdt-col\.gif"></TD>\s*<TD valign=top><UL>"\(a\) "the higher rate" shall be construed in accordance with section 51 above;"</UL></TD></TR>\s*</TABLE></TD></TR>\s*<TR><TD valign=top><IMG SRC="/img/amdt\-col\.gif"></TD>\s*<TD valign=top><UL>"\(b\) "the standard rate" shall be construed in accordance with section 51 above;"\.</UL></TD></TR>''','''<TR><TD valign=top>&nbsp;</TD><TD valign=top><TABLE>
<TR><TD valign=top><IMG SRC="/img/amdt-col.gif"></TD>
<TD valign=top><UL>"(a) "the higher rate" shall be construed in accordance with section 51 above;"</UL></TD></TR>

<TR><TD valign=top><IMG SRC="/img/amdt-col.gif"></TD>
<TD valign=top><UL>"(b) "the standard rate" shall be construed in accordance with section 51 above;".</UL></TD></TR>
</TABLE></TD></TR>''')])]


def ActApplyPatches(act):
	
	name=act.ShortID()

	print "****Checking for patches to %s" % name

	for (n,l) in patches:
		if n==name:
			print "****Patching %s" % n
			for (pattern,replacement) in l:
				print "***applying pattern",pattern 
				if not re.search(pattern,act.txt):
					print "***error, failed to find substitution text"
					sys.exit()
				act.txt=re.sub(pattern,replacement,act.txt)
	