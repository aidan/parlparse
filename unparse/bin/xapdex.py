#!/usr/bin/python2.4 

# unparse/bin/xapdex.py - Index Julian's UN HTML in Xapian. Run with --help
# for command line options.

import sys
import re
import os
import os.path
import xapian
import distutils.dir_util

# TODO: 
# Get list of days with stuff in them
# Decide what to do properly with spaces in names etc.
# Index votes themselves
# A-50-PV.61.html breaks xapdex.py
# Unicode
# Make sure the chamber (general assembly, security council) is in metadata
# Finish check_removed_docs

# Fields are:
# I identifier (e.g. pg001-bk01)
# J subsidiary identifier (e.g. pg001-bk01-pa01)
# C class (e.g. italicline boldline)
# S speaker name (with spaces and dots removed XXX remove all punctuation)
# N nation
# L language
# D document id (e.g. A-57-PV.57)
# R referenced document (e.g. A-57-PV.57)
# E date (e.g. 2002-10-01)
# H heading identifier, if speech in a heading section (e.g. pg001-bk02, with - removed)

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
./xapdex.py html/A-53-PV.63.html
./xapdex.py --undata=~/devel/undata --xapdb=xapdex.db html""")
parser.add_option("--undata", dest="undata", default=None,
      help="UN data directory; if not specified searches for it in current directory, up to 3 parent directories, and home directory")
parser.add_option("--xapdb", dest="xapdb", default="xapdex.db",
      help="Xapian database as path relative to UN data directory; defaults to xapdex.db")
parser.add_option("--first-time",
                  action="store_true", dest="firsttime", default=False,
                  help="erases existing database, and indexes all .html files")
parser.add_option("--limit", dest="limit", default=None, type="int",
      help="Stop after processing this many files, used for debugging testing")
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
if len(args) == 0:
    parser.print_help()
    sys.exit(0)

######################################################################
# These munge functions convert codes into format for Xapian.

# e.g. A/57/PV.57 or A-57-PV.57
def munge_un_document_id(doc_id):
    doc_id = doc_id.replace("/", "-")
    return doc_id
   
# e.g. pg001-bk01
def munge_julian_id(id):
    return id

# e.g. 2006-11-18
def munge_date(date):
    return date

# e.g. United States
def munge_nation(nation):
    return nation.lower()

# e.g. ?
def munge_language(language):
    return language.lower()

# e.g. italicline
def munge_cls(cls):
    return cls.lower()

# e.g. Mr. Zarif
def munge_speaker_name(name):
    # XXX remove all punctuation
    return name.replace(".", "").lower()

######################################################################
# Reindex one file

# TODO can't be bothered right now:
#   "There's an extra refinement to avoid the race condition gap between
#   committing the Xapian database change and moving the file. And another
#   refinement so it doesn't get tricked by the parser atlering the
#   unindexed file while it is updating the index from it. But those
#   refinements only affect the indexer, I think."
# I think the frist refinement needs some cleverness in Drupal's use of the
# index as well.

process_count = 0
def process_file(input_dir, input_file_rel, xapian_db):
    global process_count, options
    process_count = process_count + 1
    if options.limit and process_count > options.limit:
        return

    input_file = os.path.join(input_dir, input_file_rel)
    input_file_rel_use = input_file_rel.replace(".unindexed", "")
    input_file_use = os.path.join(input_dir, input_file_rel_use)
    newindex = False 
    if ".unindexed" in input_file_rel:
        newindex = True

    content = open(input_file).read()
    document_id = os.path.splitext(os.path.basename(input_file))[0]
    document_date = re.search('<h1>.*date=(\d\d\d\d-\d\d-\d\d) ', content).group(1)

    if options.verbose:
        if newindex:
            print "indexing (again): %s %s" % (document_id, document_date)
        else:
            print "indexing: %s %s" % (document_id, document_date)

    # Delete existing items for the document
    xapian_enquire = xapian.Enquire(xapian_db)
    xapian_query = xapian.QueryParser()
    xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
    xapian_query.set_default_op(xapian.Query.OP_AND)
    xapian_query.add_prefix("document", "D")
    query = "document:%s" % munge_un_document_id(document_id)
    parsed_query = xapian_query.parse_query(query)
    if options.verbose > 1:
        print "\tdelete query: %s" % parsed_query.get_description()
    xapian_enquire.set_query(parsed_query)
    matches = xapian_enquire.get_mset(0, 999999, 999999) # XXX 999999 enough to ensure we get 'em all?
    for match in matches:
        if options.verbose > 1:
            print "\tdeleting existing Xapian doc: %s" % match[0]
        xapian_db.delete_document(match[0]) # Xapian's document id

    # Loop through each speech
    pos_in_file = 0
    heading = None
    divs = re.finditer("^<div .*?^</div>", content, re.S + re.M)
    for div in divs:
        # Document content
        off_from = div.start()
        off_to = div.end()
        div_content = div.group(0)
        #print div_content

        # Look up all the data
        id = re.search('^<div [^>]*id="([^">]+)"', div_content).group(1)
        ids = re.findall('<div [^>]*id="([^">]+)"', div_content)
        cls = re.search('^<div [^>]*class="([^">]+)"', div_content).group(1)
        if cls == 'spoken':
            #print "----\n"
            #print div_content
            name = re.search('<span class="speaker" [^>]*name="([^">]*)"', div_content).group(1)
            nation = re.search('<span class="speaker" [^>]*nation="([^">]*)"', div_content).group(1)
            language = re.search('<span class="speaker" [^>]*language="([^">]*)"', div_content).group(1)
        if cls == 'boldline':
            heading = id
        ref_docs = re.findall('<a href="../pdf/([^>]+).pdf">', div_content)

        # Generate terms
        terms = set()
        terms.add("D%s" % munge_un_document_id(document_id))
        terms.add("E%s" % munge_date(document_date))
        for ref_doc in ref_docs:
            terms.add("R%s" % munge_un_document_id(ref_doc))
        terms.add("I%s" % munge_julian_id(id))
        for a_id in ids:
            if a_id != id:
                terms.add("J%s" % munge_julian_id(a_id))
        terms.add("C%s" % munge_cls(cls))
        if cls == 'spoken':
            terms.add("S%s" % munge_speaker_name(name))
            terms.add("N%s" % munge_nation(nation))
            terms.add("L%s" % munge_language(language))
        if heading:
            terms.add("H%s" % munge_julian_id(heading))

        # Generate words
        word_content = div_content
        word_content = re.sub("<[^>]+>", "", word_content)
        word_content = re.sub("&#\d+;", " ", word_content)
        word_content = re.sub("(\d),(\d)", "$1$2", word_content)
        word_content = re.sub("[^A-Za-z0-9]", " ", word_content)
        words = re.split("\s+",word_content)

        # Add item to Xapian database
        xapian_doc = xapian.Document()
        doc_content = "%s|%s|%s" % (input_file_rel_use, off_from, off_to - off_from)
        # ... terms (unplaced keywords, i.e. all the meta data like speaker, country)
        xapian_doc.set_data(doc_content)
        for term in terms:
            term = term.replace(" ", "")
            if options.verbose > 1:
                print "\t\tterm: %s" % term
            xapian_doc.add_term(term)
        # ... postings (keywords with placement, so can be in phrase search; the bulk of text)
        n = 0
        for word in words:
            if word == '':
                continue
            if re.search("^\d{1,2}$", word):
                continue
            n = n + 1
            if options.verbose > 1:
                print "\t\tposting: %s" % word
            xapian_doc.add_posting(word.lower(), n)
        # ... values (for sorting by)
        # XXX we use date, position in file. Should probably include type (i.e.
        # general assembly, security council) as well. Note must be lexicographically
        # sortable field, i.e. probably fixed width (hence padding on the pos).
        xapian_doc.add_value(0, "%s%06d" % (document_date.replace("-", ""), pos_in_file))
        pos_in_file = pos_in_file + 1
        # ... and add to the database
        new_doc_id = xapian_db.add_document(xapian_doc)
        if options.verbose > 1:
            print "\tadded Xapian doc: %s" % new_doc_id

    # Note that the document has been indexed
    xapian_db.flush()
    if newindex:
        os.unlink(input_file)
        os.rename(input_file_use, input_file)

# XXX finish this off, it checks for docs that are no longer there
def check_removed_docs(xapian_db):
    print xapian_db.allterms_end()
    t = xapian_db.allterms_begin()

    docs_in_xap = set()
    while t != xapian_db.allterms_end():
        term = t.get_term()
        t.next()
        g = re.search("^D(.*)$", term)
        if g:
            print g.group(1)

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

#check_removed_docs(xapian_db)
#sys.exit()

# Process files / directory trees
if options.verbose > 1:
    print "files/directories to process are", args
for input_rel in args:
    input_rel = input_rel.rstrip()
    input = os.path.join(undata_dir, input_rel)
    if os.path.isfile(input):
        process_file(undata_dir, input_rel, xapian_db)
    elif os.path.isdir(input):
        filelist = os.listdir(input)
        filelist.sort(reverse = True)
        for d in filelist:
            p = os.path.join(input_rel, d)
            if re.search(".unindexed.html$", p) \
                or (options.firsttime and re.search(".html$", p)):
                process_file(undata_dir, p, xapian_db)
    else:
        raise Exception, "Directory/file %s doesn't exist" % input

# Flush and close
xapian_db.flush()
del xapian_db



