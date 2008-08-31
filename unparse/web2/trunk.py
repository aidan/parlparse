#!/usr/bin/python

# Copyright (c) 2008 Julian Todd. This file is part of UNDemocracy.
# 
# UNDemocracy is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
# 
# UNDemocracy is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
# 
# There is a copy of the GNU Affero General Public License in LICENSE.txt at
# the top of the directory tree. Or see <http://www.gnu.org/licenses/>.

import sys, os, stat, re
import cgi, cgitb
import datetime
import urllib
cgitb.enable()

from basicbits import DecodeHref, EncodeHref, LogIncomingDoc, SetBodyID, WriteGenHTMLfoot
from db import LogIncomingDB

from pdfview import WritePDF, WritePDFpreview, WritePDFpreviewpage, WritePdfPreviewJpg
from indextype import WriteFrontPage, WriteFrontPageError, WriteAboutPage, WriteWikiPage
from indextype import WriteIndexStuff, WriteIndexStuffGA, WriteIndexStuffSec, WriteIndexStuffSecYear, WriteIndexStuffAgnum, WriteIndexSearch
from unpvmeeting import WriteHTML, WriteHTMLagnum
from highlightimg import WritePNGpage
from nationpage import WriteIndexStuffNation, WriteAllNations
from doclisting import WriteIndexStuffDocumentsYear, WriteDocumentListing, WriteDocumentListingEarly

from indexrecords import LoadAgendaNames
from quickskins import WriteWebcastIndexPage

# the main section that interprets the fields
if __name__ == "__main__":

    form = cgi.FieldStorage()
    pathpartstr = (os.getenv("PATH_INFO") or '').strip('/')
    pathparts = [ s  for s in pathpartstr.split('/')  if s ]
    referrer = os.getenv("HTTP_REFERER") or ''
    ipaddress = os.getenv("REMOTE_ADDR") or ''
    useragent = os.getenv("HTTP_USER_AGENT") or ''

    if False: # on strike condition
        print "Content-type: text/html\n"; 
        print "<h1>UNDEMOCRACY.COM is on strike</h1>"
        print '<h2>For the official source of documents, go <a href="http://www.un.org/documents/">here</a></h2>'
        print '<h2>For the scraped and parsed data, go <a href="http://seagrass.goatchurch.org.uk/~undemocracy/undata/">here</a></h2>'
        print '<h2>For the explanation, go <a href="http://www.freesteel.co.uk/wpblog/2007/11/undemocracycom-goes-on-strike/">here</a></h2>'
        print '<p>Thank you.  (2007-11-20)</p>'
        sys.exit()

    hmap = DecodeHref(pathparts, form)

    # used to spot what anchor tag the user was sent to
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
        if re.search("meeting_", pathpartstr) and not re.match("meeting_", remadeurl):
            print "Status: 302 Moved Temporarily"
        else:
            print "Status: 301 Moved Permanently"
        print "Location: %s\n" % remadeurl
        sys.exit()

    pagefunc = hmap["pagefunc"]
    SetBodyID(hmap["pagefunc"])

    if pagefunc == "front":
        LogIncomingDB("front", "", referrer, ipaddress, useragent, remadeurl)
        WriteFrontPage()
    elif pagefunc == "about": # no longer exists
        WriteAboutPage()
    elif pagefunc == "incoming":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteWikiPage()
    elif pagefunc == "search":
        LogIncomingDB(pagefunc, hmap["searchvalue"], referrer, ipaddress, useragent, remadeurl)
        WriteIndexSearch(hmap["searchvalue"])
    elif pagefunc == "nationlist":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteAllNations()
    
    elif pagefunc == "gasession":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuff(hmap["gasession"])
    elif pagefunc == "gatopics":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffGA()
    elif pagefunc == "agendanum":
        LogIncomingDB(pagefunc, hmap["agendanum"], referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffAgnum(hmap["agendanum"])
    elif pagefunc == "gadocuments":
        LogIncomingDB(pagefunc, hmap["docyearfile"], referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffDocumentsYear(hmap["docyearfile"])
    
    elif pagefunc == "gameeting":
        LogIncomingDB(hmap["docid"], hmap["gadice"] or "0", referrer, ipaddress, useragent, remadeurl)
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], hmap["gadice"], hmap["highlightdoclink"])
    elif pagefunc == "agendanumexpanded":
        LogIncomingDB(pagefunc, hmap["agendanum"], referrer, ipaddress, useragent, remadeurl)
        aglist = LoadAgendaNames(hmap["agendanum"])
        WriteHTMLagnum(hmap["agendanum"], aglist)
    elif pagefunc == "scmeeting":
        LogIncomingDB(hmap["docid"], "0", referrer, ipaddress, useragent, remadeurl)
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "", hmap["highlightdoclink"])
    
    elif pagefunc == "sctopics":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffSec()
    elif pagefunc == "scyear":
        LogIncomingDB(pagefunc, hmap["scyear"], referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffSecYear(hmap["scyear"])
    elif pagefunc == "scyearearly":
        LogIncomingDB(pagefunc, "early", referrer, ipaddress, useragent, remadeurl)
        WriteDocumentListingEarly("securitycouncil")
    elif pagefunc == "scdocuments":
        LogIncomingDB(pagefunc, hmap["docyearfile"], referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffDocumentsYear(hmap["docyearfile"])
    elif pagefunc == "pdf":
        LogIncomingDB(pagefunc, "pdf", referrer, ipaddress, useragent, remadeurl)
        WritePDF(hmap["pdffile"])
    elif pagefunc == "document":
        rfr = LogIncomingDB(hmap["docid"], "0", referrer, ipaddress, useragent, remadeurl)
        WritePDFpreview(hmap["docid"], hmap["pdfinfo"], rfr, hmap.get("scrapedoc"))
    elif pagefunc == "documentlist":
        LogIncomingDB(pagefunc, "", referrer, ipaddress, useragent, remadeurl)
        WriteDocumentListing(hmap["body"])
    
    elif pagefunc == "pdfpage":  # this is the html doc containing the page
        LogIncomingDB(hmap["docid"], "page_%s" % hmap["page"], referrer, ipaddress, useragent, remadeurl)
        WritePDFpreviewpage(hmap["pdfinfo"], hmap["page"], hmap["highlightrects"], hmap["highlightedit"])
        #LogIncomingDoc(hmap["docid"], "page_" + str(hmap["page"]), referrer, ipaddress, useragent)
    
    elif pagefunc == "nation":
        LogIncomingDB(pagefunc, hmap["nation"],  referrer, ipaddress, useragent, remadeurl)
        WriteIndexStuffNation(hmap["nation"], "")
    elif pagefunc == "nationperson":
        LogIncomingDB(pagefunc, "%s/%s" % (hmap["nation"],hmap["person"]), referrer,ipaddress,useragent, remadeurl)
        WriteIndexStuffNation(hmap["nation"], hmap["person"])
    
    elif hmap["pagefunc"] == "pagepng":  # this is the actual image bitmap of the page
        #print 'Content-type: text/html\n\n<h1>%s</h1>' % hmap["pngfile"]
        #sys.exit(0)
        WritePNGpage(hmap["pdffile"], hmap["page"], hmap["width"], hmap["pngfile"], hmap["highlightrects"])
        sys.exit(0)

    elif hmap["pagefunc"] == "webcastindex":
        WriteWebcastIndexPage(hmap["body"], hmap["date"])

    else:
        WriteFrontPageError(pathpartstr, hmap)

    WriteGenHTMLfoot()


