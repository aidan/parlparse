#!/usr/bin/python

import sys, os, re
from cStringIO import StringIO


def SubParen(f):
    f = re.sub("\(", "\(", f)
    f = re.sub("\)", "\)", f)
    return f

def WritePNGpage(pdffile, npage, imgpixwidth, pngfile, highlightrects):
    #print 'Content-type: text/html\n\n<h1>%s</h1><p>pdffile %s' % (pngfile, pdffile); sys.exit(0)
    if not os.path.isfile(pngfile):
        cmd = 'convert -quiet -density 192 %s[%d] -resize %d %s > /dev/null 2>&1' % (SubParen(pdffile), npage - 1, imgpixwidth, SubParen(pngfile))
        os.system(cmd)
    if not highlightrects or not os.path.isfile(pngfile):
        fin = open(os.path.isfile(pngfile) and pngfile or "pngnotfound.png")
        print "Content-type: image/png\n"
        print fin.read()
        fin.close()
        return


    # large libraries.  load only if necessary
    import Image, ImageDraw, ImageEnhance, ImageChops

    dkpercent = 70

    p1 = Image.new("RGB", (500, 500))
    ff = StringIO()

    pfp = Image.open(pngfile)
    swid, shig = pfp.getbbox()[2:]

    dpfp = ImageEnhance.Brightness(pfp).enhance(dkpercent / 100.0)
    ddpfp = ImageDraw.Draw(dpfp)
    for rect in highlightrects:
        srect = (rect[0] * swid / 1000, rect[1] * swid / 1000, rect[2] * swid / 1000, rect[3] * swid / 1000)
        ddpfp.rectangle(srect, (255, 255, 255))

    cpfp = ImageChops.darker(pfp, dpfp)

    ff = StringIO()
    cpfp.save(ff, "png")
    print "Content-type: image/png\n"
    print ff.getvalue()
    ff.close()




