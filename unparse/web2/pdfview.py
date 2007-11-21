#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead, EncodeHref
from basicbits import htmldir, pdfdir, pdfinfodir, pdfpreviewdir, pdfpreviewpagedir, nowdatetime, basehref
from basicbits import LookupAgendaTitle, GenWDocLink


def WritePDF(fpdf):
    print "Content-type: application/pdf\n"
    fin = open(fpdf)
    print fin.read()
    fin.close()

def SubParen(f):
    f = re.sub("\(", "\(", f)
    f = re.sub("\)", "\)", f)
    return f

def WritePdfPreviewJpg(docid):
    fname = os.path.join(pdfpreviewdir, docid + ".jpg")
    if os.path.isfile(fname):
        print "Content-type: image/png\n"
    else:
        fname = "pngnotfound.png"
        print "Content-type: image/png\n"
    
    fin = open(fname)
    print fin.read()
    fin.close()


def WritePDFpreviewpage(pdfinfo, npage, highlightrects, highlightedit):
    WriteGenHTMLhead("%s page %d" % (pdfinfo.desc, npage))
    code = pdfinfo.pdfc

    hmap = {"pagefunc":"pdfpage", "docid":code}
    resurl, reswref = GenWDocLink(pdfinfo, npage, highlightrects)
    print '<div id="docpagespecs">'
    
    print '<p><i>This</i> is page <b>%s</b>' % npage
    fulldoc = EncodeHref({"pagefunc":"document", "docid":code})
    if pdfinfo.pages == -1:
        print ' of a <a href="%s"><b>Document</b></a> with an unknown number of pages.</p>' % fulldoc
    else:
        print ' of a <b>%d</b> page <a href="%s"><b>Document</b></a>.</p>' % (pdfinfo.pages, fulldoc)

    lpages = [ ]
    lpages.append('Go to')
    if npage != 1:
        hmap["page"] = npage - 1
        lpages.append(' <a href="%s">previous page</a>' % EncodeHref(hmap))
    else:
        lpages.append(' <a href="%s">full document</a>' % fulldoc)
    if pdfinfo.pages == -1 or npage + 1 <= pdfinfo.pages:
        hmap["page"] = npage + 1
        lpages.append(' or <a href="%s">next page</a>' % EncodeHref(hmap))
    print '<p>%s</p>' % "".join(lpages)
    
    hmap["page"] = npage
    hmap["highlightrects"] = highlightrects
    hmap["highlightedit"] = False

    print '</div>'

    print '<div id="highlightcontrols">'
    print '<p><span class="linktabfleft">URL:</span> <input style="text" readonly value="%s">' % resurl
    print '<span class="linktabfleft">wiki:</span> <input style="text" readonly value="%s"></p>' % reswref

    if highlightrects:
        hmap["highlightrects"] = [ ]
        print '<a href="%s">Without any highlight</a>.' % EncodeHref(hmap),
        if len(highlightrects) > 1:
            for ih in range(len(highlightrects)):
                hmap["highlightrects"] = highlightrects[:]
                del hmap["highlightrects"][ih]
                print '<a href="%s">Without highlight %d</a>' % (EncodeHref(hmap), ih + 1),

        hmap["highlightrects"] = highlightrects

    if highlightedit:
        print '<script src="/cropper/lib/prototype.js" type="text/javascript"></script>' 
        print '<script src="/cropper/lib/scriptaculous.js?load=builder,dragdrop" type="text/javascript"></script>'
        print '<script src="/cropper/cropper.js" type="text/javascript"></script>'
        print """<script type="text/javascript">
                    Event.observe(window, 'load',
                              function() { new Cropper.Img('pdfpageid', { onEndCrop: onEndCrop }); } );

                function onEndCrop( coords, dimensions )
                {
                    var achl = document.getElementById('consdhighlight');
                    var imgl = document.getElementById('pdfpageid');
                    lhref = achl.href.substring(0, achl.href.lastIndexOf('/') + 1);
                    ix1 = Math.ceil(coords.x1 * 1000 / imgl.width);
                    iy1 = Math.ceil(coords.y1 * 1000 / imgl.width);
                    ix2 = Math.ceil(coords.x2 * 1000 / imgl.width); 
                    iy2 = Math.ceil(coords.y2 * 1000 / imgl.width);
                    rs = "rect_" + ix1 + "," + iy1 + "_" + ix2 + "," + iy2; 
                    achl.href = lhref + rs; 
                };
                </script>"""

        print 'Click and drag with your mouse to highlight the area of text you want.'
        hmap["highlightedit"] = False
        print '<div style="font-size:8;float:right">Thanks to <br><a href="http://www.defusion.org.uk/code/javascript-image-cropper-ui-using-prototype-scriptaculous/">Dave Spurr</a>.</div>'
        print '<br><a href="%s">Leave editing mode</a>' % (EncodeHref(hmap))
        print '<a id="consdhighlight" href="%s/"><b>Consolidate highlight</b></a>' % EncodeHref(hmap)
    else:
        hmap["highlightedit"] = True
        print '<a href="%s"><b>Add new highlight</b></a>' % EncodeHref(hmap)

    del hmap["highlightedit"]
    print '</div>'

    hmap["pagefunc"] = "pagepng"
    hmap["width"] = 800
    print '<div class="pdfpagediv"><img id="pdfpageid" src="%s"></div>' % EncodeHref(hmap)

    print '<p style="clear:both">%s</p>' % "".join(lpages)

def WritePDFpreview(docid, pdfinfo):
    parsed = (pdfinfo.mgapv or pdfinfo.mscpv)

    WriteGenHTMLhead('%s %s' % (pdfinfo.pdfc, pdfinfo.desc))
    
    code = pdfinfo.pdfc

    pdfpreviewf = os.path.join(pdfpreviewdir, code + ".jpg")
    if os.path.isfile(pdfpreviewf):
        print '<img style="float:right" src="/pdfpreviewjpg/%s">' % code

    resurl, reswref = GenWDocLink(pdfinfo, None, None)
    print '<div id="rightdoclinks">'
    print '<p>URL: <input style="text" readonly value="%s"></p>' % resurl
    print '<p><a href="http://en.wikipedia.org/wiki/Help:Footnotes">wiki:</a> '
    print '<input style="text" readonly value="%s"></p>' % reswref
    print '</div>'
    
    
    if pdfinfo.mgapv or pdfinfo.mscpv:
        pfile = os.path.join(htmldir, pdfinfo.pdfc + ".html")
        if os.path.isfile(pfile):
            print '<h3>Go to <a href="%s">HTML version</a> of this transcript</h3>' % (EncodeHref({"pagefunc":"meeting", "docid":code}))
        else:
            print '<p>There is no parsed version for this verbatim report.</p>'


    pdflink = EncodeHref({"pagefunc":"nativepdf", "docid":code})
    print '<p>View entire document as <a href="%s">PDF</a> <a href="%s"><img style="vertical-align: sub" src="/images/pdficon_large.gif" alt="(PDF)" border="0"></a></p>' % (pdflink, pdflink)

    print '<p>Or click on individual pages:'
    npages = pdfinfo.pages == -1 and 5 or pdfinfo.pages
    for n in range(npages):
        print '<a href="%s">Page %d</a>' % (EncodeHref({"pagefunc":"pdfpage", "docid":code, "page":(n+1)}), n + 1),
    if pdfinfo.pages == -1:
        print '(We\'re not sure how many pages there actually are in this file, so click on them to see what you get.)'
    print '</p>'

    if pdfinfo.bGA:
        print '<br><p>See all <a href="/generalassembly/documents">General Assembly documents</a>.</p>'
    if pdfinfo.bSC:
        print '<br><p>See all <a href="/securitycouncil/documents">Security Council documents</a>.</p>'

    if pdfinfo.pvrefs:
        print '<h3>References to this document</h3>'
        print '<p>List of all recent Security Council and General Assembly meetings where this document is mentioned.</p>'
        print '<ul class="docrefs">'
        for pvrefk in sorted(pdfinfo.pvrefsing.keys()):
            mcode = pvrefk[1]
            hmap = { "pagefunc":"meeting", "docid":mcode, "highlightdoclink":code }
            hmap["gid"] = min(pdfinfo.pvrefsing[pvrefk])
            agtitle, sdate = LookupAgendaTitle(mcode, hmap["gid"])
            print '<li>%s <a href="%s">%s</a></li>' % (pvrefk[0], EncodeHref(hmap), (agtitle or mcode))
        print '</ul>'


    print '</body>'
    print '</html>'



