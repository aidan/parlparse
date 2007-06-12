#!/usr/bin/python


import sys, os, stat, re
import cgi, cgitb
import datetime
import urllib
cgitb.enable()

from basicbits import DecodeHref, EncodeHref

from pdfview import WritePDF, WritePDFpreview, WritePDFpreviewpage
from indextype import WriteFrontPage, WriteFrontPageError
from indextype import WriteIndexStuff, WriteIndexStuffDocuments, WriteIndexStuffSec, WriteIndexStuffSecYear, WriteIndexStuffAgnum, WriteIndexStuffNation, WriteIndexSearch
from unpvmeeting import WriteHTML
from highlightimg import WritePNGpage


# the main section that interprets the fields
if __name__ == "__main__":

    form = cgi.FieldStorage()
    searchvalue = form.has_key("search") and form["search"].value or ""  # returned by the search form
    pathpartstr = (os.getenv("PATH_INFO") or '').strip('/')
    pathparts = [ s  for s in pathpartstr.split('/')  if s ]
    hmap = DecodeHref(pathparts)

    # should be done with one of those apache settings
    if re.search("\.png", pathpartstr):
        fin = open(pathpartstr)
        print "Content-type: image/png\n"
        print fin.read()
        fin.close()
        sys.exit(0)

    if searchvalue:
        WriteIndexSearch(searchvalue)
    elif hmap["pagefunc"] == "front":
        WriteFrontPage()
    elif hmap["pagefunc"] == "gasession":
        WriteIndexStuff(hmap["gasession"])
    elif hmap["pagefunc"] == "agendanum":
        WriteIndexStuffAgnum(hmap["agendanum"])
    elif hmap["pagefunc"] == "gadocuments":
        WriteIndexStuffDocuments(hmap["docyearfile"])
    elif hmap["pagefunc"] == "gameeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "")
    elif hmap["pagefunc"] == "scmeeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "")
    elif hmap["pagefunc"] == "sctopics":
        WriteIndexStuffSec()
    elif hmap["pagefunc"] == "scyear":
        WriteIndexStuffSecYear(hmap["scyear"])
    elif hmap["pagefunc"] == "scdocuments":
        WriteIndexStuffDocuments(hmap["docyearfile"])
    elif hmap["pagefunc"] == "pdf":
        WritePDF(hmap["pdffile"])
    elif hmap["pagefunc"] == "document":
        WritePDFpreview(hmap["docid"], hmap["pdfinfo"])
    elif hmap["pagefunc"] == "pdfpage":  # this is the html doc containing the page
        WritePDFpreviewpage(hmap["pdfinfo"], hmap["page"], hmap["highlightrects"], hmap["highlightedit"])
    elif hmap["pagefunc"] == "nation":
        WriteIndexStuffNation(hmap["nation"], "")
    elif hmap["pagefunc"] == "nationperson":
        WriteIndexStuffNation(hmap["nation"], hmap["person"])
    elif hmap["pagefunc"] == "pagepng":  # this is the bitmap of the page
        WritePNGpage(hmap["pdffile"], hmap["page"], hmap["width"], hmap["pngfile"], hmap["highlightrects"])
        sys.exit(0)
    else:
        WriteFrontPageError(pathpartstr, hmap)
    print "</body>"
    print '</html>'


