import sys
import os
import re
if sys.version[:3] != "2.4":
    import Image


def GetAllPdfDocs(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir):
    filelist = os.listdir(pdfdir)
    filelist.sort()
    filelist.reverse()
    res = [ ]
    for dpdf in filelist:
        if nlimit and len(res) >= nlimit:
            break
        if re.search("(?:\.svn)$", dpdf):
            continue
        if dpdf == "out":
            continue
        if re.search("\(", dpdf):
            dpdf = dpdf.replace("(", "\(")
            dpdf = dpdf.replace(")", "\)")
        if re.search("PV", dpdf):
            continue

        assert dpdf[-4:] == ".pdf", dpdf
        d = dpdf[:-4]
        if stem and not re.match(stem, d):
            continue
        pdffile = os.path.join(pdfdir, dpdf)
        pdfpreviewfile = os.path.join(pdfpreviewdir, d + ".jpg")
        pdfinfofile = os.path.join(pdfinfodir, d + ".txt")
        if bforcedocimg or not os.path.isfile(pdfpreviewfile) or not os.path.isfile(pdfinfofile):
            res.append((pdffile, pdfpreviewfile, pdfinfofile))
    return res


pwidth = 700
pheight = 400
def GenerateDocImage(df, tmppdfpreviewdir):
    destpdfpng1 = os.path.join(tmppdfpreviewdir, "a.png")
    destpdfpngA = os.path.join(tmppdfpreviewdir, "a%03d.png")
    for d in os.listdir(tmppdfpreviewdir):
        os.remove(os.path.join(tmppdfpreviewdir, d))
    cmd1 = "convert -density 192 %s[0] -resize %d -bordercolor black -border 3 %s" % (df[0], pwidth * 2, destpdfpng1)
    cmd1r = "convert  -background skyblue -rotate 5 %s %s" % (destpdfpng1, destpdfpng1)
    cmdA = 'convert -density 72 %s -resize %d -bordercolor black -border 3 %s' % (df[0], pwidth / 2, destpdfpngA)

    print cmdA
    os.system(cmdA)

    print cmd1
    os.system(cmd1)
    print cmd1r
    os.system(cmd1r)

    bbox = Image.open(destpdfpng1).getbbox()
    print bbox

    respng = os.path.join(tmppdfpreviewdir, "res.png")
    tmppng = os.path.join(tmppdfpreviewdir, "tmp.png")
    resjpg = os.path.join(tmppdfpreviewdir, "res.jpg")

    pgs = [ os.path.join(tmppdfpreviewdir, pg)  for pg in os.listdir(tmppdfpreviewdir)  if re.match("a\d\d\d\.png$", pg) ]
    pgs.sort()

    fout = open(df[2], "w")
    fout.write("pages = %d\n" % len(pgs))
    fout.close()

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
            print irow, inn, npg, len(pgs)

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
    os.system("convert %s %s" % (respng2, df[1]))


def GenerateDocimages(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir, tmppdfpreviewdir):
    docfiles = GetAllPdfDocs(stem, bforcedocimg, nlimit, pdfdir, pdfpreviewdir, pdfinfodir)
    for df in docfiles:
        GenerateDocImage(df, tmppdfpreviewdir)
        #break

"""import Image
import PngImagePlugin
info = PngImagePlugin.PngInfo()
info.add_text("key", "value")

im = Image.open("a.png")
print im.info

im.save("anew.png", pnginfo=info)
"""

