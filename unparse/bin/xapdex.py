#!/usr/bin/python2.4 
import sys
import re
import os
import xapian

# Index Julian's UN HTML in Xapian

# TODO: 
# Sort out the x's in document ids
# Make it iterate through all the documents
# Make it replace the database
# Add the sorting parameters

# Fields are:
# I identifier (e.g. pg001-bk01)
# J subsidiary identifier (e.g. pg001-bk01-pa01)
# C class (e.g. italicline boldline)
# S speaker name
# N nation
# L language
# D document id (e.g. A/57/PV.57)
# R referenced document (e.g. A/57/PV.57)

def process_file(input_file, xapian_db):
    content = open(input_file).read()
    document_id = os.path.splitext(os.path.basename(input_file))[0].replace("-","x")

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
        ref_docs = re.findall('<a href="../pdf/([^>]+).pdf">', div_content)

        # Generate terms
        terms = []
        terms.append("D%s" % document_id.lower())
        for ref_doc in ref_docs:
            terms.append("R%s" % ref_doc.replace("-","x").lower())
        terms.append("I%s" % id.lower())
        for a_id in ids:
            if a_id != id:
                terms.append("J%s" % a_id.lower())
        terms.append("C%s" % cls.lower())
        if cls == 'spoken':
            terms.append("S%s" % name.lower())
            terms.append("N%s" % nation.lower())
            terms.append("L%s" % language.lower())

        # Generate words
        word_content = div_content
        word_content = re.sub("<[^>]+>", "", word_content)
        word_content = re.sub("&#\d+;", " ", word_content)
        word_content = re.sub("(\d),(\d)", "$1$2", word_content)
        word_content = re.sub("[^A-Za-z0-9]", " ", word_content)
        words = re.split("\s+",div_content)

        # Add to Xapian database
        print terms
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
            xapian_doc.add_term(word.lower(), n)
        xapian_db.add_document(xapian_doc)

# Entry point
xapian_file = "/home/francis/toobig/undata/xapdex.db"
xapian_db = xapian.WritableDatabase(xapian_file, xapian.DB_CREATE_OR_OPEN)
input_file = sys.argv[1]
process_file(input_file, xapian_db)

