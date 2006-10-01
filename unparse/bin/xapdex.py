#!/usr/bin/python2.4 
import sys
import re
import os
import xapian

# Index Julian's UN HTML in Xapian

# TODO: 
# Make it replace the database
# Add the sorting parameters
# Work out what format document content should be in 
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

def process_file(input_file, xapian_db):
    content = open(input_file).read()
    document_id = os.path.splitext(os.path.basename(input_file))[0]
    document_date = re.search('<h1>.*date=(\d\d\d\d-\d\d-\d\d) ', content).group(1)

    print document_id, document_date

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

        # Add to Xapian database
        #print terms
        xapian_doc = xapian.Document()
        doc_content = "%s|%s|%s" % (os.path.basename(input_file), off_from, off_to)
        xapian_doc.set_data(doc_content)
        for term in terms:
            term = term.replace(" ", "")
            xapian_doc.add_term(term)
        n = 0
        for word in words:
            if word == '':
                continue
            if re.search("^\d{1,2}$", word):
                continue
            n = n + 1
            xapian_doc.add_posting(word.lower(), n)
        xapian_db.add_document(xapian_doc)

# Entry point
xapian_file = "/home/francis/toobig/undata/xapdex.db"
xapian_db = xapian.WritableDatabase(xapian_file, xapian.DB_CREATE_OR_OPEN)
input = sys.argv[1]
if os.path.isfile(input):
    process_file(input, xapian_db)
elif os.path.isdir(input):
    for d in os.listdir(input):
        p = os.path.join(input, d)
        if re.search(".html$", p):
            process_file(p, xapian_db)


