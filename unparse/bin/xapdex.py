#!/usr/bin/python2.4

# unparse/bin/xapdex.py - Index Julian's UN HTML in Xapian. Run with --help
# for command line options.

import sys
import re
import os
import os.path
import xapian
import distutils.dir_util
import traceback

# TODO: 
# Get list of days with stuff in them
# Decide what to do properly with spaces in names etc.
# Index votes themselves (still needed?  This is now in a mysql database)
# A-50-PV.61.html breaks xapdex.py
# Unicode

# Fields are:
# I identifier (e.g. docA61PV4-pg001-bk01)
# J subsidiary identifier (e.g. docA61PV4-pg001-bk02-pa03)
# C class (e.g. italicline boldline)
# S speaker name (with spaces and dots removed XXX remove all punctuation)
# N nation
# L language
# D document id (e.g. A-57-PV.57)
# R referenced document (e.g. A-57-PV.57)
# E date (e.g. 2002-10-01)
# H heading identifier, if speech in a heading section (e.g. docA61PV4-pg001-bk01)
# A agenda number-session number

# Example set of identifiers for a document:
# Cspoken E2006-07-20 RA-60-L.49 Smrbodini Ipg017-bk01 Nsanmarino Hpg001-bk05 L DA-60-PV.94 Jpg017-bk01-pa01 Jpg017-bk01-pa02 Jpg017-bk01-pa03


######################################################################
# Parse command line parameters

from optparse import OptionParser
parser = OptionParser()
#def option_error(self, msg): # XXX how do we make a member function?
#    self.print_help(sys.stderr) # more informative, instead of default print_usage
#    self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))
#parser.error = option_error
parser.set_usage("""
./xapdex.py DIRECTORY_OR_FILE ...

DIRECTORY_OR_FILE are Julian's structured HTML files to index, specified using
paths relative to the UN data directory. At the moment, replaces whole database
with a new one indexing the given files.

Example command lines:
./xapdex.py --undata=/home/undemocracy/undata/ --xapdb=xapdex.db
./xapdex.py --stem=A-53-PV""")
parser.add_option("--undata", dest="undata", default=None,
      help="UN data directory; if not specified searches for it in current directory, up to 3 parent directories, and home directory")
parser.add_option("--stem", dest="stem", default=None,
      help="Restricts the files scanned within the directory similar to the parser feature")
parser.add_option("--xapdb", dest="xapdb", default="xapdex.db",
      help="Xapian database as path relative to UN data directory; defaults to xapdex.db")
parser.add_option("--force", action="store_true", dest="force", default=False,
                  help="Erases existing database, and indexes all .html files")
parser.add_option("--limit", dest="limit", default=None, type="int",
      help="Stop after processing this many files, used for debugging testing")
parser.add_option("--continue-on-error", action="store_true", dest="continueonerror", default=False,
                  help="Continues with next file when there is an error, rather than stopping")
parser.add_option("--verbose", dest="verbose", default=1, type="int",
      help="Ranges from 0 for no output, to 2 for lots, default 1")
(options, args) = parser.parse_args()
if not options.undata:
    options.undata = "undata"
    if not os.path.isdir(options.undata):
        options.undata = "../undata"
    if not os.path.isdir(options.undata):
        options.undata = "../../undata"
    if not os.path.isdir(options.undata):
        options.undata = "../../../undata"
    if not os.path.isdir(options.undata):
        options.undata = "%s/undata" % os.getenv('HOME')
    if not os.path.isdir(options.undata):
        parser.error("Please specify UN data directory with --undata=, or run script with undata in current directory, in parent directory (up to 3 levels), or directly in your home directory")
if len(args) != 0:
    print "No args used by this function; see --stem"
    parser.print_help()
    sys.exit(0)


######################################################################
# Main indexing routines

# TODO can't be bothered right now:
#   "There's an extra refinement to avoid the race condition gap between
#   committing the Xapian database change and moving the file. And another
#   refinement so it doesn't get tricked by the parser atlering the
#   unindexed file while it is updating the index from it. But those
#   refinements only affect the indexer, I think."
# I think the frist refinement needs some cleverness in Drupal's use of the
# index as well.


# Reindex one file
def delete_all_for_doc(document_id, xapian_db):
    xapian_enquire = xapian.Enquire(xapian_db)
    xapian_query = xapian.QueryParser()
    xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
    xapian_query.set_default_op(xapian.Query.OP_AND)
    xapian_query.add_boolean_prefix("document", "D")
    query = "document:%s" % document_id
    parsed_query = xapian_query.parse_query(query)
    if options.verbose > 1:
        print "\tdelete query: %s" % parsed_query.get_description()
    xapian_enquire.set_query(parsed_query)
    xapian_enquire.set_weighting_scheme(xapian.BoolWeight())
    mset = xapian_enquire.get_mset(0, 999999, 999999) # XXX 999999 enough to ensure we get 'em all?
    nmset = 0
    for mdoc in mset:
        if options.verbose > 1:
            print "\tdeleting existing Xapian doc: %s" % mdoc[4].get_value(0)
        xapian_db.delete_document(mdoc[0]) # Xapian's document id
        nmset += 1
    return nmset

def thinned_docid(document_id):
    mgass = re.match("A-(\d+)-PV\.(\d+)$", document_id)
    if mgass:
        return "APV%03d%04d" % (int(mgass.group(1)), int(mgass.group(2))), mgass.group(1)
    msecc = re.match("S-PV-(\d+)(?:-Resu\.(\d+))?$", document_id)
    if msecc:
        return "SPV%05d%02d" % (int(msecc.group(1)), (msecc.group(2) and int(msecc.group(2)) or 0)), None
    assert False, "Cannot parse docid: %s" % document_id


#mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)" agendasess="([^"]*)")?[^>]*>(.*?)^</div>', doccontent, re.S + re.M)
def MakeBaseXapianDoc(mdiv, tdocument_id, document_date, nationterms):
    div_class = mdiv.group(1)
    div_id = mdiv.group(2)
    div_agendanum = mdiv.group(3)
    div_agendasess = mdiv.group(4)
    div_text = mdiv.group(5)

    terms = [ ]
    terms.append("C%s" % div_class)

    mblockid = re.match("pg(\d+)-bk(\d+)$", div_id)
    assert mblockid, "unable to decode blockid:%s" % div_id
    terms.append("I%s" % mblockid.group(0))

    for ref_doc in re.findall('<a href="../(?:pdf|html)/([^"]+).(?:pdf|html)"', div_text):
        terms.append("R%s" % ref_doc)

    if div_class in ['spoken', 'council-attendees']:
        for spclass in re.findall('<span class="([^"]*)">([^>]*)</span>', div_text):
            if spclass[0] == "name":
                terms.append("S%s" % re.sub("[\.\s]", "", spclass[1]).lower())
            if spclass[0] == "language":
                terms.append("L%s" % re.sub("[\.\s]", "", spclass[1]).lower())
            if spclass[0] == "nation":
                nationterm = "N%s" % re.sub("[\.\s]", "", spclass[1]).lower()
                terms.append(nationterm)
                if div_class == 'spoken':
                    nationterms.append(nationterm)

    if div_agendanum:
        for agnum in re.split("(\d+)", div_agendanum): # sometimes it's a comma separated list
            terms.append("A%ss%s" % (div_agendanum, div_agendasess))

    # in the future we may break everything down to the paragraph level, and have 3 levels of heading backpointers
    textspl = [ ] # all the text broken into words
    for mpara in re.finditer('<(?:p|blockquote)(?: class="([^"]*)")? id="(pg(\d+)-bk(\d+)-pa(\d+))">(.*?)</(?:p|blockquote)>', div_text):
        assert mpara.group(3) == mblockid.group(1) and mpara.group(4) == mblockid.group(2), "paraid disagrees with blockid: %s %s" % (div_id, mpara.group(0))
        terms.append("J%s" % mpara.group(2))
        paraclass = mpara.group(1)
        if not paraclass or paraclass in ['boldline-p', 'boldline-indent']:
            textspl.extend(re.findall("\w+", mpara.group(6)))

        elif paraclass == 'votelist':
            for mvote in re.finditer('<span class="([^"\-]*)([^"])*">([^<]*)</span>', mpara.group(6)):
                vnation = re.sub("[\.\s]", "", mvote.group(3)).lower()
                vvote = mvote.group(2) or mvote.group(1)
                terms.append("V%s-%s" % (vnation, vvote))  # could also add vetos?

        else:
            assert paraclass in ['boldline-agenda', 'motiontext', 'votecount'], "Unrecognized paraclass:%s" % paraclass

    # date, docid, page, blockno
    value0 = "%s%sp%04d%03d" % (re.sub("-", "", document_date), tdocument_id, int(mblockid.group(1)), int(mblockid.group(2)))
    assert len(value0) == 26, len(value0) # nice and tidy; we're generating a value that gives a total global sort

    if options.verbose > 1:
        print "value0", value0, "words:", len(textspl), " terms:", terms

    # assemble the document
    xapian_doc = xapian.Document()
    xapian_doc.add_value(0, value0)  # it's poss to have more than one value tagged on, but I think sorting is done only on one value

    for term in terms:
        xapian_doc.add_term(term)

    nspl = 0
    for tspl in textspl:
        if not re.match("\d\d?$", tspl):
            xapian_doc.add_posting(tspl.lower(), nspl)
        nspl += 1

    return xapian_doc  # still need to set the data



# Reindex one file
def process_file(input_dir, input_file_rel, xapian_db):
    mdocid = re.match("(html/)([\-\d\w\.]+?)(\.unindexed)?(\.html)$", input_file_rel)
    assert mdocid, "unable to match:%s" % input_file_rel
    document_id = mdocid.group(2)

    pfnameunindexed = os.path.join(input_dir, input_file_rel)
    fin = open(pfnameunindexed)
    doccontent = fin.read()
    fin.close()

    mdocument_date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', doccontent)
    assert mdocument_date, "not found date in file %s" % input_file_rel
    document_date = mdocument_date.group(1)

    if options.verbose:
        print "indexing %s %s" % (document_id, document_date)

    while delete_all_for_doc(document_id, xapian_db):
        pass   # keep calling delete until all clear

    # Loop through each speech, and batch up the headings so they can be updated with the correct info
    xapian_doc_heading = None
    sdiv_headingdata = None
    xapian_doc_subheading = None
    sdiv_subheadingdata = None
    nationtermsubheading = set()  # list of nations who spoke in the block
    nationtermheading = set()  # list of nations who spoke in the block
    lastend = 0

    tdocument_id, gasssess = thinned_docid(document_id)
    docterms = [ ]
    docterms.append("D%s" % document_id)
    docterms.append("E%s" % document_date)
    docterms.append("E%s" % document_date[:4])
    docterms.append("E%s" % document_date[:7])
    if gasssess:
        docterms.append("Zga")
        docterms.append("Zga%s" % gasssess)
    else:
        docterms.append("Zsc")

    mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)" agendasess="([^"]*)")?[^>]*>(.*?)^</div>', doccontent, re.S + re.M)
    for mdiv in mdivs:
        # used to dereference the string as it is in the file
        div_class = mdiv.group(1)
        div_data = (document_id, mdiv.start(), mdiv.end() - mdiv.start(), mdiv.group(2))

        xapian_doc = MakeBaseXapianDoc(mdiv, tdocument_id, document_date, nationtermsubheading)
        for dterm in docterms:
            xapian_doc.add_term(dterm)

        if div_class == "heading":
            assert not xapian_doc_heading, "Only one heading per document"
            xapian_doc_heading = xapian_doc
            sdiv_headingdata = div_data

        elif div_class in ["subheading", "end-document"]:
            assert xapian_doc_heading
            if xapian_doc_subheading:
                for nterm in nationtermsubheading:
                    xapian_doc_subheading.add_term(nterm)
                dsubheadingdata = "%s|%d|%d|%s|%d" % (sdiv_subheadingdata[0], sdiv_subheadingdata[1], sdiv_subheadingdata[2], sdiv_headingdata[3], lastend - sdiv_subheadingdata[1])
                xapian_doc_subheading.set_data(dsubheadingdata)
                xapian_db.add_document(xapian_doc_subheading)

            nationtermheading.update(nationtermsubheading)
            if div_class == "subheading":
                nationtermsubheading.clear()
                xapian_doc_subheading = xapian_doc
                sdiv_subheadingdata = div_data
            else:
                nationtermsubheading = None
                xapian_doc_subheading = None
                sdiv_subheadingdata = None

            if div_class == "end-document":
                for nterm in nationtermheading:
                    xapian_doc_heading.add_term(nterm)
                dheadingdata = "%s|%d|%d|%s|%d" % (sdiv_headingdata[0], sdiv_headingdata[1], sdiv_headingdata[2], "", lastend - sdiv_headingdata[1])
                xapian_doc_heading.set_data(dheadingdata)
                xapian_db.add_document(xapian_doc_heading)
                xapian_doc_heading = None

        else:
            assert div_class in ["assembly-chairs", "council-agenda", "council-attendees", "spoken", "italicline", "italicline-tookchair", "italicline-spokein", "recvote"], "unknown divclass:%s" % div_class
            assert sdiv_subheadingdata or sdiv_headingdata
            ddata = "%s|%d|%d|%s|" % (div_data[0], div_data[1], div_data[2], (sdiv_subheadingdata or sdiv_headingdata)[3])
            xapian_doc.set_data(ddata)
            xapian_db.add_document(xapian_doc)

        lastend = mdiv.end()

    # the end-document tag helps us close these headings off
    assert not xapian_doc_subheading and not xapian_doc_heading

    # Note that the document has been indexed
    xapian_db.flush()

    if mdocid.group(3): # unindexed
        fnameindexed = "%s%s%s" % (mdocid.group(1), mdocid.group(2), mdocid.group(4))
        pfnameindexed = os.path.join(input_dir, fnameindexed)
        if os.path.exists(pfnameindexed):
            os.unlink(pfnameindexed)
        print pfnameunindexed, pfnameindexed
        os.rename(pfnameunindexed, pfnameindexed)


######################################################################
# Main entry point

# Get directory where we keep data
undata_dir = options.undata.rstrip()
if not os.path.exists(undata_dir):
    raise Exception, "Could not find undata directory %s" % undata_dir

# Work out where Xapian database is, and name of temporary new one
xapian_file = os.path.join(undata_dir, options.xapdb).rstrip()
# Create new database
os.environ['XAPIAN_PREFER_FLINT'] = '1' # use newer/faster Flint backend
xapian_db = xapian.WritableDatabase(xapian_file, xapian.DB_CREATE_OR_OPEN)

# Process files / directory trees
if options.verbose > 1:
    print "files/directories to process are", args

relsm = {}
relsum = {}
if True:
    input_rel = "html"
    inputd = os.path.join(undata_dir, input_rel)
    if os.path.isfile(inputd):
        rels.append(input_rel)
    elif os.path.isdir(inputd):
        filelist = os.listdir(inputd)
        filelist.sort(reverse = True)
        for d in filelist:
            if re.search("(?:\.css|\.svn)$", d):
                continue

            if not options.stem or re.match(options.stem, d):
                p = os.path.join(input_rel, d)
                mux = re.match("(.*?)(\.unindexed)?\.html$", d)
                assert mux, "unmatched file:%s" % d
                if mux.group(2):
                    relsum[mux.group(1)] = p  # with the html/
                elif options.force:
                    relsm[mux.group(1)] = p
    else:
        raise Exception, "Directory/file %s doesn't exist" % input

for r in relsum:
    relsm.pop(r, 1)
rels = relsum.values()
rels.extend(relsm.values())
rels.sort()

# having gone through the list, now load each
if options.limit and len(rels) > options.limit:
    rels = rels[:options.limit]
for rel in rels:
    try:
        process_file(undata_dir, rel, xapian_db)
    except KeyboardInterrupt, e:
        print "  ** Keyboard interrupt"
        sys.exit(1)
    except Exception, e:
        print e
        if options.continueonerror:
            traceback.print_exc()
        else:
            traceback.print_exc()
            sys.exit(1)

# Flush and close
xapian_db.flush()
del xapian_db



