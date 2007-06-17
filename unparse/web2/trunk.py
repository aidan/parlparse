#!/usr/bin/python


import sys, os, stat, re
import cgi, cgitb
import datetime
import urllib
cgitb.enable()

from basicbits import DecodeHref, EncodeHref, LogIncomingDoc, SetBodyID, WriteGenHTMLfoot

from pdfview import WritePDF, WritePDFpreview, WritePDFpreviewpage, WritePdfPreviewJpg
from indextype import WriteFrontPage, WriteFrontPageError
from indextype import WriteIndexStuff, WriteIndexStuffSec, WriteIndexStuffSecYear, WriteIndexStuffAgnum, WriteIndexSearch
from unpvmeeting import WriteHTML
from highlightimg import WritePNGpage
from nationpage import WriteIndexStuffNation, WriteAllNations
from doclisting import WriteIndexStuffDocumentsYear, WriteDocumentListing


# the main section that interprets the fields
if __name__ == "__main__":

    form = cgi.FieldStorage()
    pathpartstr = (os.getenv("PATH_INFO") or '').strip('/')
    pathparts = [ s  for s in pathpartstr.split('/')  if s ]
    referrer = os.getenv("HTTP_REFERER") or ''
    ipaddress = os.getenv("REMOTE_ADDR") or ''
    useragent = os.getenv("HTTP_USER_AGENT") or ''

    
    hmap = DecodeHref(pathparts, form)

    if hmap["pagefunc"] == "imghrefrep":
        LogIncomingDoc(hmap["imghrefrep"], "imghrefrep", referrer, ipaddress, useragent)
        sys.exit(0)
    elif hmap["pagefunc"] == "pdfpreviewjpg":
        WritePdfPreviewJpg(hmap["docid"])
        sys.exit(0)

    # Redirect if the URL isn't in its canonical form
    remadeurl = EncodeHref(hmap)
#    print "Content-type: text/html\n"; print hmap; print "ello"; print remadeurl; print pathpartstr; sys.exit()
    if remadeurl != "/" + pathpartstr and not re.match('^/rubbish/', remadeurl):
        #print 'Content-type: text/html\n'
        #print '<h1>%s</h1>\n<h2>%s</h2>' % (pathpartstr, remadeurl)
        
        print "Status: 301 Moved Permanently"
        print "Location: %s\n" % remadeurl
        sys.exit()    

    SetBodyID(hmap["pagefunc"])

    if hmap["pagefunc"] == "front":
        WriteFrontPage()
    elif hmap["pagefunc"] == "search":
        WriteIndexSearch(hmap["searchvalue"])
    elif hmap["pagefunc"] == "nationlist":
        WriteAllNations()
    elif hmap["pagefunc"] == "gasession":
        WriteIndexStuff(hmap["gasession"])
    elif hmap["pagefunc"] == "agendanum":
        WriteIndexStuffAgnum(hmap["agendanum"])
    elif hmap["pagefunc"] == "gadocuments":
        WriteIndexStuffDocumentsYear(hmap["docyearfile"])
    elif hmap["pagefunc"] == "gameeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], hmap["highlightdoclink"])
    elif hmap["pagefunc"] == "scmeeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], hmap["highlightdoclink"])
    elif hmap["pagefunc"] == "sctopics":
        WriteIndexStuffSec()
    elif hmap["pagefunc"] == "scyear":
        WriteIndexStuffSecYear(hmap["scyear"])
    elif hmap["pagefunc"] == "scdocuments":
        WriteIndexStuffDocumentsYear(hmap["docyearfile"])
    elif hmap["pagefunc"] == "pdf":
        WritePDF(hmap["pdffile"])
        LogIncomingDoc(hmap["docid"], "pdf", referrer, ipaddress, useragent)
    elif hmap["pagefunc"] == "document":
        WritePDFpreview(hmap["docid"], hmap["pdfinfo"])
        LogIncomingDoc(hmap["docid"], "0", referrer, ipaddress, useragent)
    elif hmap["pagefunc"] == "documentlist":
        WriteDocumentListing(hmap["body"])
    elif hmap["pagefunc"] == "pdfpage":  # this is the html doc containing the page
        WritePDFpreviewpage(hmap["pdfinfo"], hmap["page"], hmap["highlightrects"], hmap["highlightedit"])
        LogIncomingDoc(hmap["docid"], str(hmap["page"]), referrer, ipaddress, useragent)
    elif hmap["pagefunc"] == "nation":
        WriteIndexStuffNation(hmap["nation"], "")
    elif hmap["pagefunc"] == "nationperson":
        WriteIndexStuffNation(hmap["nation"], hmap["person"])
    elif hmap["pagefunc"] == "pagepng":  # this is the bitmap of the page
        #print 'Content-type: text/html\n\n<h1>%s</h1>' % hmap["pngfile"]
        #sys.exit(0)
        WritePNGpage(hmap["pdffile"], hmap["page"], hmap["width"], hmap["pngfile"], hmap["highlightrects"])
        sys.exit(0)
    else:
        WriteFrontPageError(pathpartstr, hmap)

    WriteGenHTMLfoot()

