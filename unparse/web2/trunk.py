#!/usr/bin/python


import sys, os, stat, re
import cgi, cgitb
import datetime
import urllib
cgitb.enable()

from basicbits import WriteGenHTMLhead, GetFcodes, monthnames
from basicbits import basehref, htmldir, pdfdir, pdfinfodir
from basicbits import DecodeHref, EncodeHref

from pdfinfo import PdfInfo

from pdfview import WritePDF, WritePDFpreview, WritePDFpreviewpage
from indextype import WriteFrontPage, WriteFrontPageError
from indextype import WriteIndexStuff, WriteIndexStuffSec, WriteIndexStuffSecYear, WriteIndexStuffAgnum, WriteIndexStuffNation, WriteIndexSearch
from unpvmeeting import WriteNotfound, WriteHTML


# the main section that interprets the fields
if __name__ == "__main__":

    form = cgi.FieldStorage()
    searchvalue = form.has_key("search") and form["search"].value or ""  # returned by the search form
    pathpartstr = os.getenv("PATH_INFO") or ''
    pathparts = [ s  for s in pathpartstr.strip('/').split('/')  if s ]
    hmap = DecodeHref(pathparts, searchvalue)

    if hmap["pagefunc"] == "front":
        WriteFrontPage()
    WriteFrontPageError(pathpartstr, hmap)
    print "</body>"
    print '</html>'
    sys.exit(0)

    code = form.has_key("code") and form["code"].value or ""
    pdfpage = form.has_key("pdfpage") and form["pdfpage"].value or ""


    if not code:
        nation = form.has_key("nation") and form["nation"].value or ""
        agnum = form.has_key("agnum") and form["agnum"].value or ""
        sess = form.has_key("sess") and form["sess"].value or ""
        if search:
            bsucc = WriteIndexSearch(search)
        elif nation:
            bsucc = WriteIndexStuffNation(nation)
        elif agnum:
            bsucc = WriteIndexStuffAgnum(agnum)
        elif sess:
            if sess[:2] == "sc":
                scyear = sess[2:]
                if scyear:
                    bsucc = WriteIndexStuffSecYear(scyear)
                else:
                    bsucc = WriteIndexStuffSec()
            else:
                bsucc = WriteIndexStuff(sess)
        else:
            bsucc = WriteFrontPage()
        if not bsucc:
            WriteGenHTMLhead("Bad data")

    else:
        fhtml, fpdf = GetFcodes(code)
        pdfinfo = PdfInfo(code)
        pdfinfo.UpdateInfo(pdfinfodir)

        if fhtml and not pdfpage:
            highlightdoclink = form.has_key("highlightdoclink") and form["highlightdoclink"].value or ""
            WriteHTML(fhtml, pdfinfo, highlightdoclink)
        elif pdfpage == "inline":
            WritePDF(fpdf)
        elif re.match("\d+$", pdfpage):
            highlight = form.has_key("highlight") and form["highlight"].value or ""
            highlightedit = form.has_key("highlightedit") and form["highlightedit"] or ""
            WritePDFpreviewpage(basehref, pdfinfo, int(pdfpage), highlight, highlightedit)
        elif fpdf:
            WritePDFpreview(basehref, pdfinfo)
        else:
            WriteNotfound(code)

    print "</body>"
    print '</html>'


