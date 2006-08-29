import os
import re
import sys
from unglue import GlueUnfile
from unparse import ParsetoHTML
from optparse import OptionParser
from unscrape import ScrapePDF, ConvertXML
from unmisc import unexception, IsNotQuiet, SetQuiet

parser = OptionParser()
parser.set_usage("""Parses and scrapes UN verbatim reports from General Assembly and Security Council
scrape  do the downloads
cxml    do the conversion
parse   do the parsing""")


pdfdir = os.path.join("..", "pdf")
pdfxmldir = os.path.join("..", "pdfxml")
htmldir = os.path.join("..", "html")

if not os.path.isdir(pdfdir):
	print "please create the directory:", pdfdir
	sys.exit(0)
if not os.path.isdir(pdfxmldir):
	print "please create the directory:", pdfxmldir
	sys.exit(0)


parser.add_option("--stem", dest="stem", metavar="stem", default="",
                  help="stem of documents to be parsed (eg A-59-PV)")
parser.add_option("--quiet",
                  action="store_true", dest="quiet", default=False,
                  help="low volume messages")
parser.add_option("--force-parse",
				  action="store_true", dest="forceparse", default=False,
				  help="Don't skip any files when parsing")
(options, args) = parser.parse_args()

stem = ""
if options.stem:
	stem = re.sub("\.", "\.", options.stem)
if not stem:  # make it anyway if you don't do the stem command properly
	for a in args:
		if re.match("A-", a):
			stem = a

#print options, args
SetQuiet(options.quiet)
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
if bParse:
	ParsetoHTML(stem, pdfxmldir, htmldir, options.forceparse)



