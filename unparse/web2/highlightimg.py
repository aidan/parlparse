#!/usr/bin/python

import sys, os, re
import cgi, cgitb
from cStringIO import StringIO
cgitb.enable()

import Image, ImageDraw, ImageEnhance, ImageChops
from basicbits import pdfpreviewpagedir

if __name__ == "__main__":
    form = cgi.FieldStorage()

    code = form.has_key("code") and form["code"].value or ""
    pdfpage = form.has_key("pdfpage") and form["pdfpage"].value or ""
    highlight = form.has_key("highlight") and form["highlight"].value or ""

    fp = "%spage%d.png" % (code, int(pdfpage))
    rects = [ ]
    dkpercent = 70
    for lhl in highlight.split("|"):
        mrect = re.match("rect(\d+),(\d+),(\d+),(\d+)", lhl)
        mdkpercent = re.match("darken(\d+)", lhl)
        if mrect:
            rects.append((int(mrect.group(1)), int(mrect.group(2)), int(mrect.group(3)), int(mrect.group(4))))
        if mdkpercent:
            dkpercent = 100 - int(mdkpercent.group(1))

    afp = os.path.join(pdfpreviewpagedir, fp)

    p1 = Image.new("RGB", (500, 500))
    ff = StringIO()

    pfp = Image.open(afp)
    swid, shig = pfp.getbbox()[2:]

    dpfp = ImageEnhance.Brightness(pfp).enhance(dkpercent / 100.0)
    ddpfp = ImageDraw.Draw(dpfp)
    for rect in rects:
        srect = (rect[0] * swid / 1000, rect[1] * shig / 1000, rect[2] * swid / 1000, rect[3] * shig / 1000)
        ddpfp.rectangle(srect, (255, 255, 255))

    cpfp = ImageChops.darker(pfp, dpfp)

    ff = StringIO()
    cpfp.save(ff, "png")
    print "Content-type: image/png\n"
    print ff.getvalue()
    ff.close()




