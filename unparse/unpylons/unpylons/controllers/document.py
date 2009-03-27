import os
import urllib
import logging
import sys
import re
from cStringIO import StringIO

from unpylons.lib.base import *

import unpylons.model as model
htmldir = os.path.join(model.undatadir, "html")
pdfdir = os.path.join(model.undatadir, "pdf")
pngdir = os.path.join(model.undatadir, "docpages")
log = logging.getLogger(__name__)

class DocumentController(BaseController):

    def setparamsfromdocid(self, docid):    
        mga = re.match("A(-RES)?-(\d\d)(-L)?(?:-PV.(\d+))?", docid)
        msc = re.match("S(?:-PV-(\d+.*))?(?:-RES-(\d+))?", docid)
        if mga:
            c.body, c.longbody = "GA", "General Assembly"
            c.session, c.meeting = mga.group(2), mga.group(4)
            if mga.group(1):
                c.doctype = "Resolution"
            elif mga.group(4):
                c.doctype = "Verbatim Report"
            elif mga.group(3):
                c.doctype = "Document (limited release)"
            else:
                c.doctype = "Document"
        elif msc:
            c.body, c.longbody = "SC", "Security Council"
            c.session, c.meeting = None, msc.group(1)
            if msc.group(1):
                c.doctype = "Verbatim Report"
            elif msc.group(2):
                c.doctype = "Resolution"
                c.resolution_number = msc.group(2)
            else:
                c.doctype = "Document"
                
        else:
            c.body, c.longbody = "UN", "Unknown"
            c.session, c.meeting = None, None

    # list of documents by date
    def documentsall(self):
        c.gasessions, c.scyears = model.GetSessionsYears()
        c.documents = model.Document.query.all()
        return render('documentall')

    # list for specific document
    def documentspec(self, docid):
        referrer = os.getenv("HTTP_REFERER") or ''
        ipaddress = os.getenv("REMOTE_ADDR") or ''
        useragent = os.getenv("HTTP_USER_AGENT") or ''
        print (referrer, ipaddress, useragent)
        
        c.document = model.Document.query.filter_by(docid=docid).first()
        c.docid = docid
        c.docidq = urllib.quote(docid)
        self.setparamsfromdocid(docid)

        c.meeting = c.document and c.document.meetings and c.document.meetings[0]
        return render('documenthold')

    # same as above but with the message set differently
    def documentspecscrape(self, docid):
        c.document = model.Document.query.filter_by(docid=docid).first()
        c.docid = docid
        c.docidq = urllib.quote(docid)
        c.meeting = c.document and c.document.meetings and c.document.meetings[0]
        c.message = "not scraped (feature incomplete)"
        return render('documenthold')

    def RenderPage(self, docid, page, pngfile):
        pdffile = os.path.join(pdfdir, docid + ".pdf")
        lpdffile = pdffile.replace("(", "\(").replace(")", "\)")
        lpngfile = pngfile.replace("(", "\(").replace(")", "\)")
        imgpixwidth = 800
        cmd = 'convert -quiet -density 192 %s[%d] -resize %d %s > /dev/null 2>&1' % (lpdffile, int(page)-1, imgpixwidth, lpngfile)
        os.system(cmd)

    
    def HighlightRects(self, pngfile, highlightrects):
        # large libraries.  load only if necessary
        import Image, ImageDraw, ImageEnhance, ImageChops

        dkpercent = 70

        p1 = Image.new("RGB", (500, 500))
        ff = StringIO()

        pfp = Image.open(pngfile)
        swid, shig = pfp.getbbox()[2:]

        dpfp = ImageEnhance.Brightness(pfp).enhance(dkpercent / 100.0)
        ddpfp = ImageDraw.Draw(dpfp)
        for highlightrect in highlightrects:
            mrect = re.match("rect_(\d+),(\d+)_(\d+),(\d+)$", highlightrect)
            if mrect:
                rect = (int(mrect.group(1)), int(mrect.group(2)), int(mrect.group(3)), int(mrect.group(4)))
                srect = (rect[0] * swid / 1000, rect[1] * swid / 1000, rect[2] * swid / 1000, rect[3] * swid / 1000)
                ddpfp.rectangle(srect, (255, 255, 255))

        cpfp = ImageChops.darker(pfp, dpfp)

        ff = StringIO()
        cpfp.save(ff, "png")
        return ff.getvalue()

    
    # list for specific document
    def documentpage(self, docid, page, highlightrects=""):
        c.document = model.Document.query.filter_by(docid=docid).first()
        c.docid = docid
        c.page = int(page)
        c.highlightrects = [hr  for hr in highlightrects.split("/")  if hr]
        c.pngname = "%s_page_%s" % (docid, page)
        pngfile = os.path.join(pngdir, c.pngname) + ".png"
        if not os.path.exists(pngfile):
            #self.RenderPage(docid, c.page, pngfile)
            #c.message = "page rendered"        
            c.message = "deferred rendering"        
        else:
            c.message = "page already rendered"
        return render('documentpage')
        #return str(response.headers["content-type"]) + "ooo" + docid

    def imagedocumentpage(self, pngname):
        print "mmmmm", pngname
        midp = re.match("(.*?)_page_(\d+)(.*)$", pngname)
        pngfile = os.path.join(pngdir, c.pngname) + ".png"
        docid = midp.group(1)
        c.page = int(midp.group(2))
        highlightrects = re.findall("rect_\d+,\d+_\d+,\d+", midp.group(3))
        self.RenderPage(docid, c.page, pngfile)
        bimgexists = os.path.isfile(pngfile)
        response.headers['Content-type'] = 'image/png'
        if not highlightrects or not bimgexists:
            fin = open(bimgexists and pngfile or "pngnotfound.png", "rb")
            res = fin.read()
            fin.close()
            return res
        
        return self.HighlightRects(pngfile, highlightrects)




