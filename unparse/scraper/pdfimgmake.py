import sys
import os
import re
import Image

from pdfinfo import PdfInfo

def GetAllPdfDocs(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir):
    filelist = os.listdir(pdfdir)
    filelist.sort()
    filelist.reverse()
    pdfinfos = { }

    for pdf in filelist:
        if not re.search("\.pdf$", pdf):
            continue
        pdfc = pdf[:-4]
        if stem and not re.match(stem, pdfc):
            continue
        pdfinfo = PdfInfo(pdfc)
        pdfinfo.UpdateInfo(pdfinfodir)
        pdfpreviewfile = os.path.join(pdfpreviewdir, pdfc + ".jpg")
        if bforcedocimg or pdfinfo.pages == -1 or not os.path.isfile(pdfpreviewfile):
            pdfinfos[pdfc] = pdfinfo
            if nlimit and len(pdfinfos) >= nlimit:
                break
    return pdfinfos


pwidth = 700
pheight = 400
def GenerateDocImage(pdfinfo, pdfdir, pdfpreviewdir, pdfinfodir, tmppdfpreviewdir):
    destpdfpng1 = os.path.join(tmppdfpreviewdir, "a.png")
    destpdfpngA = os.path.join(tmppdfpreviewdir, "a%03d.png")
    for d in os.listdir(tmppdfpreviewdir):
        os.remove(os.path.join(tmppdfpreviewdir, d))

    pdffile = os.path.join(pdfdir, pdfinfo.pdfc + ".pdf")
    jpgfile = os.path.join(pdfpreviewdir, pdfinfo.pdfc + ".jpg")

    cmd1 = "convert -density 192 %s[0] -resize %d -bordercolor black -border 3 %s" % (pdffile, pwidth * 2, destpdfpng1)
    cmd1r = "convert  -background skyblue -rotate 5 %s %s" % (destpdfpng1, destpdfpng1)
    cmdA = 'convert -density 72 %s -resize %d -bordercolor black -border 3 %s' % (pdffile, pwidth / 2, destpdfpngA)

    print cmdA
    os.system(cmdA)

    print cmd1
    os.system(cmd1)
    print cmd1r
    os.system(cmd1r)

    bbox = Image.open(destpdfpng1).getbbox()
    #print bbox

    respng = os.path.join(tmppdfpreviewdir, "res.png")
    tmppng = os.path.join(tmppdfpreviewdir, "tmp.png")
    resjpg = os.path.join(tmppdfpreviewdir, "res.jpg")

    pgs = [ os.path.join(tmppdfpreviewdir, pg)  for pg in os.listdir(tmppdfpreviewdir)  if re.match("a\d\d\d\.png$", pg) ]
    pgs.sort()

    pdfinfo.pages = len(pgs)  # this is where the number of pages is set

    nrows = max(1, min(3, (len(pgs) - 1) / 5))
    nperrow = (len(pgs) - 1) / nrows
    if nperrow * nrows < (len(pgs) - 1):
        nperrow += 1

    os.system("convert %s %s" % (destpdfpng1, respng))
    for irow in range(nrows - 1, -1, -1):
        for inn in range(nperrow - 1, -1, -1):
            npg = irow * nperrow + inn + 1
            if npg >= len(pgs):
                continue
            #print irow, inn, npg, len(pgs)

            cmdS = 'convert %s -background none -rotate 20 %s' % (pgs[npg], tmppng)
            print cmdS
            os.system(cmdS)
            #sys.exit(0)
            cmd2 = 'composite -geometry +%d+%d %s %s %s' % (bbox[2] * inn / (nperrow + 1), int(bbox[3] * (0.5 + 0.4 * irow / nrows)), tmppng, respng, respng)
            print cmd2
            os.system(cmd2)
            #sys.exit(0)

    respng2 = os.path.join(tmppdfpreviewdir, "res2.png")
    cmdC = "convert %s -crop %dx%d+0+%d -resize %dx%d %s" % (respng, bbox[2], bbox[3] * 3 / 5, bbox[3] / 5, pwidth, pheight, respng2)
    print cmdC
    os.system(cmdC)
    os.system("convert %s %s" % (respng2, jpgfile))


def GenerateDocimages(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir, tmppdfpreviewdir):
    pdfinfos = GetAllPdfDocs(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir)
    for pdfinfo in pdfinfos.values():
        print pdfinfo.pdfc
        GenerateDocImage(pdfinfo, pdfdir, pdfpreviewdir, pdfinfodir, tmppdfpreviewdir)
        pdfinfo.WriteInfo(pdfinfodir)
        break

"""import Image
import PngImagePlugin
info = PngImagePlugin.PngInfo()
info.add_text("key", "value")

im = Image.open("a.png")
print im.info

im.save("anew.png", pnginfo=info)
"""

