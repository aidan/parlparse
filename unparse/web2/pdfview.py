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

def WritePDFpreviewpage(basehref, pdfinfo, npage, highlight, highlightedit):
    WriteGenHTMLhead("%s page %d" % (pdfinfo.desc, npage))
    code = pdfinfo.pdfc

    print '<h3>Other pages</h3>'
    print '<p>'
    if npage != 1:
        print '<a href="%s?code=%s&pdfpage=%d">Page %d</a>' % (basehref, code, npage - 1, npage - 1)
    print '<a href="%s?code=%s&pdfpage=all">Full doc</a>' % (basehref, code)
    if pdfinfo.pages == -1 or npage + 1 < pdfinfo.pages:
        print '<a href="%s?code=%s&pdfpage=%d">Page %d</a>' % (basehref, code, npage + 1, npage + 1)
    print '</p>'

    print '<h3>Links</h3>'
    ivl = [ '<a href="' ]
    ivl.append("%s?code=%s" % (basehref, pdfinfo.pdfc))
    ivl.append('&pdfpage=%d' % npage)
    if highlight:
        ivl.append('&highlight=%s' % highlight)
    ivl.append('">Document %s</a>' % pdfinfo.pdfc)
    print '<p>URL: <input style="text" readonly value=\'%s\'></p>' % "".join(ivl)
    
    ivw = [ '<ref>{{ UN document |code=%s' % pdfinfo.pdfc ]
    ivw.append('body=General Assembly |session=60')
    ivw.append(' |page=%d' % npage)
    if highlight:
        ivw.append(' |highlight=%s' % highlight)
    ivw.append(' |accessdate=1999-99-99 }}</ref>')
    print '<p>wiki: <input style="text" readonly value=\'%s\'></p>' % "".join(ivw)


    print '<h3>Editing highlight</h3>'
    highlights = [ lhl  for lhl in highlight.split("|")  if lhl ]
    if highlights:
        print '<p><a href="%s?code=%s&pdfpage=%d">no highlight</a>' % (basehref, code, npage),
        if len(highlights) > 1:
            for ih in range(len(highlights)):
                mhighlight = highlights[:]
                del mhighlight[ih]
                print '<a href="%s?code=%s&pdfpage=%d&highlight=%s">withough highlight %d</a>' % (basehref, code, npage, "|".join(mhighlight), ih),
        print '</p>'

    phighlight = highlight and ("&highlight=%s" % highlight) or ""
    if highlightedit:
        print '<script src="../js/cropper/lib/prototype.js" type="text/javascript"></script>'
        print '<script src="../js/cropper/lib/scriptaculous.js?load=builder,dragdrop" type="text/javascript"></script>'
        print '<script src="../js/cropper/cropper.js" type="text/javascript"></script>'
        print """<script type="text/javascript">
                    Event.observe(window, 'load',
                              function() { new Cropper.Img('pdfpageid', { onEndCrop: onEndCrop }); } );

                function onEndCrop( coords, dimensions )
                {
                    var achl = document.getElementById('consdhighlight');
                    var imgl = document.getElementById('pdfpageid');
                    lhref = achl.href.substring(0, achl.href.lastIndexOf('|') + 1);
                    ix1 = Math.ceil(coords.x1 * 1000 / imgl.width);
                    iy1 = Math.ceil(coords.y1 * 1000 / imgl.height);
                    ix2 = Math.ceil(coords.x2 * 1000 / imgl.width); 
                    iy2 = Math.ceil(coords.y2 * 1000 / imgl.height);
                    rs = "rect" + ix1 + "," + iy1 + "," + ix2 + "," + iy2; 
                    achl.href = lhref + rs; 
                };
                </script>"""

        print '<p>Click and drag a box to highlight the text you want.'
        print '<a href="%s?code=%s&pdfpage=%d%s">leave editing mode</a>' % (basehref, code, npage, phighlight)
        print '<a id="consdhighlight" href="%s?code=%s&pdfpage=%d&highlight=%s|"><b>consolidate highlight</b></a>' % (basehref, code, npage, highlight)
        print '</p>'
    else:
        print '<p><a href="%s?code=%s&pdfpage=%d%s&highlightedit=yes"><b>add new highlight</b></a></p>' % (basehref, code, npage, phighlight)
    print '<p></p>'


    fpageimg = os.path.join(pdfpreviewpagedir, "%spage%d.png" % (code, npage))
    fpdf = os.path.join(pdfdir, "%s.pdf" % code)
    if os.path.isfile(fpdf) and not os.path.isfile(fpageimg):
        imgpixwidth = 800
        cmd = 'convert -quiet -density 192 %s[%d] -resize %d %s > /dev/null 2>&1' % (SubParen(fpdf), npage - 1, imgpixwidth, SubParen(fpageimg))
        #print cmd
        os.system(cmd)

    # now is the place we iterate through the highlights and render that there
    # Import Image, ImageDraw
    # a = image.open(dpdf)
    # d = ImageDraw.ImageDraw(a)
    # d.rectangle(sx, sy, wx, wy)
    # etc

    if os.path.isfile(fpageimg):
        print '<div class="pdfpagediv">'
        if highlight:
            sdark = highlightedit and "|darken20" or ""
            print '<img id="pdfpageid" src="highlightimg.py?code=%s&pdfpage=%d&highlight=%s%s">' % (code, npage, highlight, sdark)
        else:
            print '<img id="pdfpageid" src="../undata/pdfpreviewpage/%spage%d.png">' % (code, npage)
        print '</div>'
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



