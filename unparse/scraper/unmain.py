import os
import re
import sys
from unparse import ParsetoHTML
from optparse import OptionParser
from unscrape import ScrapeContentsPageFromStem, ConvertXML
from unmisc import unexception, IsNotQuiet, SetQuiet, SetCallScrape, pdfdir, pdfxmldir, htmldir
from nations import PrintNonnationOccurrances
from unindex import MiscIndexFiles

parser = OptionParser()
parser.set_usage("""

Parses and scrapes UN verbatim reports of General Assembly and Security Council
  scrape  do the downloads
  cxml    do the pdf conversion
  parse   do the parsing
  index   generate miscelaneous index files

--stem selects what is processed.
  scrape --stem=S-[YEAR]-PV
""")


if not os.path.isdir(pdfdir):
    print "\nplease create the directory:", pdfdir
    sys.exit(0)
if not os.path.isdir(pdfxmldir):
    print "\nplease create the directory:", pdfxmldir
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

#print options, args
SetQuiet(options.quiet)
SetCallScrape(options.scrapelinks)
bScrape = "scrape" in args
bConvertXML = "cxml" in args
bParse = "parse" in args
bIndexfiles = "index" in args
if not (bScrape or bConvertXML or bParse or bIndexfiles):
    parser.print_help()
    sys.exit(1)

# lack of stem means we do special daily update
if bScrape:
    # we could use current date to generate these figures
    if not stem:
        ScrapeContentsPageFromStem("A-61-PV")
        ScrapeContentsPageFromStem("S-2007-PV")
    else:
        ScrapeContentsPageFromStem(stem)

if bConvertXML:
    if not stem:
        ConvertXML("S-PV-5", pdfdir, pdfxmldir)
        ConvertXML("A-61-PV", pdfdir, pdfxmldir)
    elif re.match("A-(?:49|[56]\d)-PV", stem):  # year 48 is not parsable
        ConvertXML(stem, pdfdir, pdfxmldir)
    elif re.match("S-PV", stem):  # make sure it can't do too many at once
        ConvertXML(stem, pdfdir, pdfxmldir)
    else:
        print "Stem should be set, eg --stem=A-49-PV"
        print "  (Can't parse 48, so won't do)"

if bParse:
    if not stem:
        ParsetoHTML("A-61-PV", pdfxmldir, htmldir, options.forceparse, options.editparse)
        ParsetoHTML("S-PV-50", pdfxmldir, htmldir, options.forceparse, options.editparse)
    else:
        ParsetoHTML(stem, pdfxmldir, htmldir, options.forceparse, options.editparse)
    PrintNonnationOccurrances()

if bIndexfiles:
    MiscIndexFiles(htmldir)
