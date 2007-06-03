import os
import sys
import re


currentgasession = 61
currentscyear = 2007

basehref = 'unjgt.py'
htmldir = '/home/undemocracy/undata/html'
pdfdir = '/home/undemocracy/undata/pdf'
pdfinfodir = '/home/undemocracy/undata/pdfinfo'
pdfpreviewdir = '/home/undemocracy/undata/pdfpreview'
pdfpreviewpagedir = '/home/undemocracy/undata/pdfpreviewpage'
indexstuffdir = '/home/undemocracy/undata/indexstuff'


def WriteGenHTMLhead(title):
    print "Content-type: text/html\n"
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
    print '<html>'
    print '<head>'
    print '<title>JGT backup site</title>'
    print '<link href="../css/unview.css" type="text/css" rel="stylesheet" media="all">'
    print '<script language="JavaScript" type="text/javascript" src="../js/unjava.js"></script>'
    print '</head>'
    print '<body>'
    print '<h1 class="tophead">UNdemocracy.com</h1>'
    print '<h1 class="topheadspec">%s</h1>' % title


def GetFcodes(code):
    scode = re.sub("/", "-", code)
    scode = re.sub("\.html$|\.pdf$", "", scode)

    fhtml = os.path.join(htmldir, scode + ".html")
    if not os.path.isfile(fhtml):  # only use unindexed types during development, since no searcher is running
        fhtml = ""

    fpdf = os.path.join(pdfdir, scode + ".pdf")
    if not os.path.isfile(fpdf):
        fpdf = ""

    return fhtml, fpdf

