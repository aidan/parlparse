
import re
import sys


patches=[('ukgpa1997c16',[('&rsquo;\)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt cols="c3"}"></a></TD></TR>(?i)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18pt}"></a></TD></TR>(?i)',''),
		('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt in relation to accounting periods beginning after 5th March 1997\."></a></TD></TR>(?i)','')]),
		]


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
					print re.search('<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="sch18ptt cols="c3"}"',act.txt)
					sys.exit()
				act.txt=re.sub(pattern,replacement,act.txt)
	