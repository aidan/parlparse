#!/usr/bin/python2.4 
import sys
import re
import os
import os.path
import xapian
import distutils.dir_util

# Index Julian's UN HTML in Xapian

# Usage:
# ./xapdex.py UNDATA_DIR XAPIAN_DATABASE_NAME HTML_DIRECTORY_OR_FILE
# XAPIAN_DATABASE_NAME and HTML_DIRECTORY_OR_FILE are relative to UNDATA_DIR.
# At the moment, replaces whole database with a new one indexing the given
# HTML_DIRECTORY_OR_FILE. 
# e.g. 
# ./xapdex.py ~/devel/undata xapdex.db html/A-53-PV.63.html
# ./xapdex.py ~/devel/undata xapdex.db html

# TODO: 
# Get list of days
# Decide what to do properly with spaces in names etc.

# Fields are:
# I identifier (e.g. pg001-bk01, with x for -)
# J subsidiary identifier (e.g. pg001-bk01-pa01, with x for -)
# C class (e.g. italicline boldline)
# S speaker name
# N nation
# L language
# D document id (e.g. A/57/PV.57)
# R referenced document (e.g. A/57/PV.57)
# E date (e.g. 2002-10-01, without -)
# H heading identifier, if speech in a heading section

def process_file(input_dir, input_file_rel, xapian_db):
    input_file = os.path.join(input_dir, input_file_rel)

    content = open(input_file).read()
    document_id = os.path.splitext(os.path.basename(input_file))[0]
    document_date = re.search('<h1>.*date=(\d\d\d\d-\d\d-\d\d) ', content).group(1)

    print document_id, document_date

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
            name = re.search('<span class="speaker" [^>]*name="([^">]*)"', div_content).group(1)
            nation = re.search('<span class="speaker" [^>]*nation="([^">]*)"', div_content).group(1)
            language = re.search('<span class="speaker" [^>]*language="([^">]*)"', div_content).group(1)
        if cls == 'boldline':
            heading = id
        ref_docs = re.findall('<a href="../pdf/([^>]+).pdf">', div_content)

        # Generate terms
        terms = []
        terms.append("D%s" % document_id.replace("-","x").lower())
        terms.append("E%s" % document_date.replace("-", ""))
        for ref_doc in ref_docs:
            terms.append("R%s" % ref_doc.replace("-","x").lower())
        terms.append("I%s" % id.replace("-", ""))
        for a_id in ids:
            if a_id != id:
                terms.append("J%s" % a_id.replace("-", ""))
        terms.append("C%s" % cls.lower())
        if cls == 'spoken':
            terms.append("S%s" % name.lower())
            terms.append("N%s" % nation.lower())
            terms.append("L%s" % language.lower())
        if heading:
            terms.append("H%s" % heading.replace("-", ""))

        # Generate words
        word_content = div_content
        word_content = re.sub("<[^>]+>", "", word_content)
        word_content = re.sub("&#\d+;", " ", word_content)
        word_content = re.sub("(\d),(\d)", "$1$2", word_content)
        word_content = re.sub("[^A-Za-z0-9]", " ", word_content)
        words = re.split("\s+",word_content)

        # Add item to Xapian database
        xapian_doc = xapian.Document()
        doc_content = "%s|%s|%s" % (input_file_rel, off_from, off_to - off_from)
        # ... terms (unplaced keywords, i.e. all the meta data like speaker, country)
        xapian_doc.set_data(doc_content)
        for term in terms:
            term = term.replace(" ", "")
            xapian_doc.add_term(term)
        # ... postings (keywords with placement, so can be in phrase search; the bulk of text)
        n = 0
        for word in words:
            if word == '':
                continue
            if re.search("^\d{1,2}$", word):
                continue
            n = n + 1
            xapian_doc.add_posting(word.lower(), n)
        # ... values (for sorting by)
        # XXX we use date, position in file. Should probably include type (i.e.
        # general assembly, security council) as well. Note must be lexicographically
        # sortable field, i.e. probably fixed width (hence padding on the pos).
        xapian_doc.add_value(0, "%s%06d" % (document_date.replace("-", ""), pos_in_file))
        pos_in_file = pos_in_file + 1
        # ... and commit to the database
        xapian_db.add_document(xapian_doc)

# Get directory where we keep data
undata_dir = sys.argv[1].rstrip()
if not os.path.exists(undata_dir):
    raise Exception, "Could not find undata directory %s" % undata_dir

# Work out where Xapian database is, and name of temporary new one
xapian_file = os.path.join(undata_dir, sys.argv[2]).rstrip()
xapian_file_new = xapian_file + ".new"
# Erase existing temporary new one, that may be left over
if os.path.exists(xapian_file_new):
    if os.path.exists(os.path.join(xapian_file_new, "iamflint")):
        distutils.dir_util.remove_tree(xapian_file_new)
    else:
        raise Exception, "Path %s exists but doesn't contain Xapian database" % xapian_file_new
# Create new database
os.environ['XAPIAN_PREFER_FLINT'] = '1' # use newer/faster Flint backend
xapian_db = xapian.WritableDatabase(xapian_file_new, xapian.DB_CREATE_OR_OPEN)

# Find file / directory tree to read in
input_rel = sys.argv[3].rstrip()
input = os.path.join(undata_dir, input_rel)
if os.path.isfile(input):
    process_file(undata_dir, input_rel, xapian_db)
elif os.path.isdir(input):
    for d in os.listdir(input):
        p = os.path.join(input_rel, d)
        if re.search(".html$", p):
            process_file(undata_dir, p, xapian_db)
else:
    raise Exception, "Directory/file %s doesn't exist" % input

# Close new database, so flushed
del xapian_db

# Move new database into place with name of main database
if os.path.exists(xapian_file):
    if os.path.exists(os.path.join(xapian_file, "iamflint")):
        distutils.dir_util.remove_tree(xapian_file)
    else:
        raise Exception, "Path %s exists but doesn't contain Xapian database" % xapian_file
os.rename(xapian_file_new, xapian_file)


