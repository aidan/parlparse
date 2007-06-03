#!/usr/bin/python

import sys, os, stat, re
import cgi, cgitb
import datetime
cgitb.enable()

from basicbits import WriteGenHTMLhead
from basicbits import htmldir, pdfdir, pdfinfodir, pdfpreviewdir, pdfpreviewpagedir

sys.path.append('/home/undemocracy/unparse/scraper')
from pdfinfo import PdfInfo


def WritePDF(fpdf):
    print "Content-type: application/pdf\n"
    fin = open(fpdf)
    print fin.read()
    fin.close()

def SubParen(f):
    f = re.sub("\(", "\(", f)
    f = re.sub("\)", "\)", f)
    return f

def WritePDFpreviewpage(basehref, pdfinfo, npage):
    WriteGenHTMLhead("%s page %d" % (pdfinfo.desc, npage))
    code = pdfinfo.pdfc

    print '<p>'
    if npage != 1:
        print '<a href="%s?code=%s&pdfpage=%d">Page %d</a>' % (basehref, code, npage - 1, npage - 1)
    print '<a href="%s?code=%s&pdfpage=all">Full doc</a>' % (basehref, code)
    print '<a href="%s?code=%s&pdfpage=%d">Page %d</a>' % (basehref, code, npage + 1, npage + 1)
    print '</p>'

    fpageimg = os.path.join(pdfpreviewpagedir, "%spage%d.png" % (code, npage))
    fpdf = os.path.join(pdfdir, "%s.pdf" % code)
    if os.path.isfile(fpdf) and not os.path.isfile(fpageimg):
        imgpixwidth = 800
        cmd = 'convert -quiet -density 192 %s[%d] -resize %d -bordercolor black -border 3 %s > /dev/null 2>&1' % (SubParen(fpdf), npage - 1, imgpixwidth, SubParen(fpageimg))
        #print cmd
        os.system(cmd)

    if os.path.isfile(fpageimg):
        print '<img src="../undata/pdfpreviewpage/%spage%d.png">' % (code, npage)
    else:
        print '<p>No image</p>'

    print '</body>'
    print '</html>'


def WritePDFpreview(basehref, pdfinfo):
    WriteGenHTMLhead('<div style="float:right; font-size:20; vertical-align:text-bottom;">%s</div> %s' % (pdfinfo.pdfc, pdfinfo.desc))
    
    code = pdfinfo.pdfc

    if pdfinfo.pvrefs:
        print '<h3>Meetings that refer to this document</h3>'
        print '<ul>'
        for pvrefk in sorted(pdfinfo.pvrefsing.keys()):
            mcode = pvrefk[1]
            print '<li>%s <a href="%s?code=%s&highlightdoclink=%s#%s">%s</a></li>' % (pvrefk[0], basehref, mcode, code, min(pdfinfo.pvrefsing[pvrefk]), mcode)
        print '</ul>'

    if pdfinfo.mgapv or pdfinfo.mscpv:
        print '<p>Return to <a href="%s?code=%s">Parsed document</a></p>' % (basehref, code)
    
    print '<h3><a href="%s?code=%s&pdfpage=inline">native pdf</a></h3>' % (basehref, code)

    print '<h3>Link to pages</h3>'
    if pdfinfo.pages != -1:
        print '<p>',
        for n in range(pdfinfo.pages):
            print '<a href="%s?code=%s&pdfpage=%d">Page %d</a>' % (basehref, code, n + 1, n + 1),
        print '</p>'
    else:
        print '<p>We don\'t know how many pages.  <a href="%s?code=%s&pdfpage=1">Page 1</a></p>' % (basehref, code)

    pdfpreviewf = os.path.join(pdfpreviewdir, code + ".jpg")
    if os.path.isfile(pdfpreviewf):
        print '<img src="../undata/pdfpreview/%s.jpg">' % code


    print '</body>'
    print '</html>'



