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
    hmap = DecodeHref(pathparts)

    if searchvalue:
        WriteIndexSearch(searchvalue)
    elif hmap["pagefunc"] == "front":
        WriteFrontPage()
    elif hmap["pagefunc"] == "gasession":
        WriteIndexStuff(hmap["gasession"])
    elif hmap["pagefunc"] == "agendanum":
        WriteIndexStuffAgnum(hmap["agendanum"])
    elif hmap["pagefunc"] == "gameeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "")
    elif hmap["pagefunc"] == "scmeeting":
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "")
    elif hmap["pagefunc"] == "sctopics":
        WriteIndexStuffSec()
    elif hmap["pagefunc"] == "scyear":
        WriteIndexStuffSecYear(hmap["scyear"])
    elif hmap["pagefunc"] == "pdf":
        WritePDF(hmap["pdffile"])
    elif hmap["pagefunc"] == "document":
        WritePDFpreview(hmap["docid"], hmap["pdfinfo"])
    elif hmap["pagefunc"] == "pdfpage":
        WritePDFpreviewpage(hmap["pdfinfo"], hmap["page"], hmap["highlight"], hmap["highlightedit"])
    else:
        WriteFrontPageError(pathpartstr, hmap)
    print "</body>"
    print '</html>'
    sys.exit(0)

    code = form.has_key("code") and form["code"].value or ""
    pdfpage = form.has_key("pdfpage") and form["pdfpage"].value or ""


    if 0:
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


