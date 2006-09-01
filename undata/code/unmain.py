import os
import re
import sys
from unglue import GlueUnfile
from unparse import ParsetoHTML
from optparse import OptionParser
from unscrape import ScrapeContentsPageFromStem, ConvertXML
from unmisc import unexception, IsNotQuiet, SetQuiet, SetCallScrape, pdfdir, pdfxmldir, htmldir

parser = OptionParser()
parser.set_usage("""Parses and scrapes UN verbatim reports from General Assembly and Security Council
scrape  do the downloads
cxml    do the conversion
parse   do the parsing""")


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
parser.add_option("--edit",
				  action="store_true", dest="editparse", default=False,
				  help="Edit the file before parsing")
parser.add_option("--scrape-links",
				  action="store_true", dest="scrapelinks", default=False,
				  help="Causes cited documents to be scraped during parsing")

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
SetCallScrape(options.scrapelinks)
bScrape = "scrape" in args
bConvertXML = "cxml" in args
bParse = "parse" in args
if not (bScrape or bConvertXML or bParse):
	parser.print_help()
	sys.exit(1)

if bScrape:
	ScrapeContentsPageFromStem(stem)
if bConvertXML:
	ConvertXML(stem, pdfdir, pdfxmldir)
if bParse:
	ParsetoHTML(stem, pdfxmldir, htmldir, options.forceparse, options.editparse)




