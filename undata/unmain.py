import os
import re
from unglue import GlueUnfile
from unparse import SingleParaProcess
from unparse import countryvotes

# the main function
for undoc in os.listdir("pdfxml"):
	undocname = os.path.splitext(undoc)[0]
	undochtml = os.path.join("html", undocname + ".html")
	undocpdf = os.path.join("pdfxml", undoc)

	# too hard.  too many indent problems (usually secret ballot announcementing)
	if undocname in ["A-53-PV.39", "A-53-PV.52",
					 "A-54-PV.34", "A-54-PV.45",
					 "A-55-PV.33", "A-55-PV.99",
					 "A-56-PV.32", "A-56-PV.81"]:
		continue

	if not re.match("A-53-PV.", undoc):
		continue
	print "parsing:", undocname,

	fin = open(undocpdf)
	xfil = fin.read()
	fin.close()

	date, tlcall = GlueUnfile(xfil, undocname)

	# merge the lines together
	for tlc in tlcall:
		SingleParaProcess(tlc)

	print date
	#votes, unparas = GlueUnfile(undocname, date, tlcall)
	#print votes,

	h = open(undochtml, "w")
	for tlc in tlcall:
		h.write(tlc.paraembed[0])
		h.write(tlc.paratext)
		h.write(tlc.paraembed[1])
	h.close()

for c in sorted(countryvotes.keys()):
	print c, countryvotes[c]
