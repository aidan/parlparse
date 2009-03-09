import os
import re
import sys
sys.path.append("../pylib")
from unparse import ParsetoHTML
from optparse import OptionParser
from unscrape import ScrapeContentsPageFromStem, ScrapePDF, ConvertXML
from unmisc import unexception, IsNotQuiet, SetQuiet, SetCallScrape, undatadir, pdfdir, pdfxmldir, htmldir, xapdir, commentsdir, pdfpreviewdir, pdfinfodir, indexstuffdir, tmppdfpreviewdir
from nations import PrintNonnationOccurrances
from unindex import MiscIndexFiles
from xapdex import GoXapdex
from pdfimgmake import GenerateDocimages
from votedistances import WriteVoteDistances
from docmeasurements import WriteDocMeasurements
from agendanames import WriteAgendaSummaries
from scsummaries import ScrapeSCSummaries, WriteSCSummaries
from gasummaries import ScrapeGASummaries, ParseScrapeGASummaries
from wpediaget import FetchWikiBacklinks
from gennatdata import GenerateNationData
from nationdatasucker import ScrapePermMissions, NationDataSucker
from dbfill import DBfill

parser = OptionParser()
parser.set_usage("""

Parses and scrapes UN verbatim reports of General Assembly and Security Council
  scrape  do the downloads
  cxml    do the pdf conversion
  parse   do the parsing
  dbfill  upload the parsed headings etc into database
  xapdex  call the xapian indexing system
  votedistances generate voting distances table for java applet
  docmeasurements generate measurements of quantities of documents;
            created as a set of tables in docmeasurements.html in undata
            used for inserting into the webpage
  agendanames generate page containing agenda summaries
  scsummaries scrape and generate summary index for security council
  nationdata generates speeches/urls about nations
  docimages generate document images in undata/pdfpreview

--stem selects what is processed.
  scrape --stem=S-[YEAR]-PV
""")

#  index   generate miscellaneous index files
#  wpscrape  scrape for UN translocutions from wikipedia

# the quiet cronjob should be
# unmain.py --quiet --scrape-links --continue-on-error scrape cxml parse xapdex docmeasurements agendanames scsummaries nationdata

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
                  help="Don't skip files when parsing")
parser.add_option("--force-cxml",
                  action="store_true", dest="forcecxml", default=False,
                  help="Don't skip files when converting xml")
parser.add_option("--edit",
                  action="store_true", dest="editparse", default=False,
                  help="Edit the file before parsing")
parser.add_option("--scrape-links",
                  action="store_true", dest="scrapelinks", default=False,
                  help="Causes cited documents to be scraped during parsing")
parser.add_option("--doc",
                  dest="scrapedoc", metavar="scrapedoc", default="",
                  help="Causes a single document to be scraped")
parser.add_option("--force-dbfill", action="store_true", dest="forcedbfill", default=False,
                  help="Erases existing valies and adds them to table again")
parser.add_option("--force-docmeasurements", action="store_true", dest="forcedocmeasurements", default=False,
                  help="Causes all docmeasurements to be run again")
parser.add_option("--force-xap", action="store_true", dest="forcexap", default=False,
                  help="Erases existing database, and indexes all .html files")
parser.add_option("--limit", dest="limit", default=None, type="int",
                  help="Stop after processing this many files, used for debugging testing")
parser.add_option("--continue-on-error", action="store_true", dest="continueonerror", default=False,
                  help="Continues with next file when there is an error, rather than stopping")
parser.add_option("--force-docimg", action="store_true", dest="forcedocimg", default=False,
                  help="Don't skip files when applying docimages")

(options, args) = parser.parse_args()

stem = re.sub("\.", "\.", options.stem)

#print options, args
SetQuiet(options.quiet)
SetCallScrape(options.scrapelinks)
bScrape = "scrape" in args
bConvertXML = "cxml" in args
bParse = "parse" in args
bXapdex = "xapdex" in args
bDBfill = "dbfill" in args
bDocMeasurements = "docmeasurements" in args
bAgendanames = "agendanames" in args
bDocimages = "docimages" in args
bIndexfiles = "index" in args
bScrapewp = "wpscrape" in args
bSCsummaries = "scsummaries" in args
bGAsummaries = "gasummaries" in args
bNationData = "nationdata" in args
bVoteDistances = "votedistances" in args

if not (bScrape or bConvertXML or bParse or bVoteDistances or bDBfill or bXapdex or bIndexfiles or bDocMeasurements or bDocimages or bScrapewp or bAgendanames or bSCsummaries or bNationData or bGAsummaries):
    parser.print_help()
    sys.exit(1)

# lack of stem means we do special daily update
if bScrape:
    if not options.stem and not options.scrapedoc:  # default case
        ScrapeContentsPageFromStem("A-62-PV")
        ScrapeContentsPageFromStem("A-63-PV")
        ScrapeContentsPageFromStem("S-2008-PV")
    if options.scrapedoc:
        ScrapePDF(options.scrapedoc, bforce=False)
    if options.stem:
        ScrapeContentsPageFromStem(options.stem)

if bConvertXML:
    if not stem:
        ConvertXML("S-PV.[56]\d\d\d", pdfdir, pdfxmldir, False)
        ConvertXML("A-6[23]-PV", pdfdir, pdfxmldir, False)
    elif re.match("A-(?:49|[56]\d)-PV", stem):  # year 48 is not parsable
        ConvertXML(stem, pdfdir, pdfxmldir, options.forcecxml)
    elif re.match("S-PV", stem):  # make sure it can't do too many at once
        ConvertXML(stem, pdfdir, pdfxmldir, options.forcecxml)
    else:
        print "Stem should be set, eg --stem=A-49-PV"
        print "  (Can't parse 48, so won't do)"

if bParse:
    if not stem:
        ParsetoHTML("A-63-PV", pdfxmldir, htmldir, options.forceparse, options.editparse, options.continueonerror)
        ParsetoHTML("S-PV.6\d\d\d", pdfxmldir, htmldir, options.forceparse, options.editparse, options.continueonerror)
    else:
        ParsetoHTML(stem, pdfxmldir, htmldir, options.forceparse, options.editparse, options.continueonerror)
    PrintNonnationOccurrances()

if bDBfill:
    DBfill(stem, options.forcedbfill, options.limit, options.continueonerror, htmldir)

if bXapdex:
    GoXapdex(stem, options.forcexap, options.limit, options.continueonerror, htmldir, xapdir)


if bSCsummaries:
    scsummariesdir = os.path.join(indexstuffdir, "scsummariesdir")
    #ScrapeSCSummaries(scsummariesdir)  # scrapes copies of the annual lists of security council meetings
    WriteSCSummaries(stem, scsummariesdir, htmldir, pdfdir)  # number of documents in each year of each type

# makes docmeasurements.html, docyears/ and backpointers in pdfinfo/
if bDocMeasurements:
    WriteDocMeasurements(stem, options.forcedocmeasurements, htmldir, pdfdir, pdfinfodir, indexstuffdir)  # number of documents in each year of each type

if bAgendanames:
    WriteAgendaSummaries(stem, htmldir)  # number of documents in each year of each type


# I think this is a new one just for early sessions where they list summary names for all the resolutions
if bGAsummaries:
    agsummariesdir = os.path.join(indexstuffdir, "gasummariesdir")
    if not os.path.isdir(agsummariesdir):
        os.mkdir(agsummariesdir)
    ScrapeGASummaries(agsummariesdir)
    sess = 1
    ParseScrapeGASummaries(agsummariesdir, pdfinfodir, sess)

if bNationData:
    ScrapePermMissions()
    NationDataSucker()
    nationactivitydir = os.path.join(indexstuffdir, "nationactivity")
    if not os.path.isdir(nationactivitydir):
        os.mkdir(nationactivitydir)
    GenerateNationData(nationactivitydir, htmldir)

if bVoteDistances:
    f = os.path.join(indexstuffdir, "votetable.txt")
    if IsNotQuiet():
        print "Writing vote distance to file:", f
    fout = open(f, "w")
    WriteVoteDistances(stem, htmldir, fout)
    fout.close()

if bDocimages:
    GenerateDocimages(stem, options.forcedocimg, options.limit, pdfdir, pdfpreviewdir, pdfinfodir, tmppdfpreviewdir)

# this may be out-dated
if bScrapewp:
    FetchWikiBacklinks(commentsdir)

if bIndexfiles:  # just for making the big index.html pages used in preview
    MiscIndexFiles(htmldir)

