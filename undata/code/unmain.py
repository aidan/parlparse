import os
import re
import sys
from unglue import GlueUnfile
from unparse import GroupParas
from optparse import OptionParser
from unscrape import ScrapePDF, ConvertXML
from unexception import unexception

parser = OptionParser()
parser.set_usage("""Parses and scrapes UN verbatim reports from General Assembly and Security Council
scrape  do the downloads
cxml    do the conversion
parse   do the parsing""")


pdfdir = os.path.join("..", "pdf")
pdfxmldir = os.path.join("..", "pdfxml")

if not os.path.isdir(pdfdir):
	print "please create the directory:", pdfdir
	sys.exit(0)
if not os.path.isdir(pdfxmldir):
	print "please create the directory:", pdfxmldir
	sys.exit(0)


parser.add_option("--stem", dest="stem", metavar="stem", default="",
                  help="stem of documents to be parsed")
parser.add_option("--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="low volume messages")
(options, args) = parser.parse_args()

stem = ""
if options.stem:
	stem = re.sub("\.", "\.", options.stem)
if not stem:  # make it anyway if you don't do the stem command properly
	for a in args:
		if re.match("A-", a):
			stem = a

#print options, args
bQuiet = options.quiet
bScrape = "scrape" in args
bConvertXML = "cxml" in args
bParse = "parse" in args
if not (bScrape or bConvertXML or bParse):
	parser.print_help()
	sys.exit(1)

if bScrape:
	ScrapePDF(stem, pdfdir)
if bConvertXML:
	ConvertXML(stem, pdfdir, pdfxmldir)
if not bParse:
	sys.exit(0)

# The rest of this module runs the parser.

# the main function
undocnames = [ ]
for undoc in os.listdir("pdfxml"):
	undocname = os.path.splitext(undoc)[0]

	# too hard.  too many indent problems (usually secret ballot announcementing)
	if undocname in ["A-53-PV.39", "A-53-PV.52",
					 "A-54-PV.34", "A-54-PV.45",
					 "A-55-PV.33", "A-55-PV.99",
					 "A-56-PV.32", "A-56-PV.81"]:
		continue

	if re.match(stem, undocname):
		undocnames.append(undocname)
if not bQuiet:
	print "Preparing to parse %d files" % len(undocnames)

for undocname in undocnames:
	undochtml = os.path.join("html", undocname + ".html")
	undocpdfxml = os.path.join("pdfxml", undocname + ".xml")
	print "parsing:", undocname,

	fin = open(undocpdfxml)
	xfil = fin.read()
	fin.close()

	gparas = None
	while not gparas:
		try:
			sdate, chairs, tlcall = GlueUnfile(xfil, undocname)
			print sdate#, chairs
			gparas = GroupParas(tlcall, undocname, sdate)
		except unexception, ux:
			assert not gparas
			print "\nHit RETURN to launch your editor on the psdxml (or type 's' to skip)"
			rl = sys.stdin.readline()
			if rl[0] == "s":
				break
			os.system('"C:\Program Files\ConTEXT\ConTEXT" %s' % (undocpdfxml,))
	if not gparas:
		continue

	fout = open(undochtml, "w")
	fout.write('<html>\n<head>\n')
	fout.write('<link href="unhtml.css" type="text/css" rel="stylesheet" media="all">\n')
	fout.write('</head>\n<body>\n')
	fout.write("<h1>%s  date=%s</h1>\n" % (undocname, sdate))
	for gpara in gparas:
		gpara.writeblock(fout)
	fout.write('</body>\n</html>\n')
	fout.close()


