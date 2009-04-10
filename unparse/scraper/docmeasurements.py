#!/usr/bin/python

import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs, IsNotQuiet, RomanToDecimal
from pdfinfo import PdfInfo
import datetime

# most of the code in this file will become redundant
import unpylons.model as model   

# Main file
def WriteDocMeasurements(stem, bforcedocmeasurements, htmldir, pdfdir, pdfinfodir, indexstuffdir):
    
    # make full list of parsed and non-parsed documents (due to bad svn update on unparse)
    docids = set()
    for pdf in os.listdir(pdfdir):
        mdocid = re.match("([AS].*?)\.pdf$", pdf)
        if mdocid:
            docids.add(mdocid.group(1))
    for html in os.listdir(htmldir):
        mdocid = re.match("([AS].*?)\.html", html)
        if mdocid:
            docids.add(mdocid.group(1))
    
    # respect the stem and don't reprocess anything that has numpages already set
    # (we could do it by last modified date on the file)
    for docid in reversed(sorted(list(docids))):
        if stem and not re.match(stem, docid):
            continue
        model.ProcessDocumentPylon(docid, pdfdir, htmldir, bforcedocmeasurements)
    print "Quitting after doing the pylons loading"


