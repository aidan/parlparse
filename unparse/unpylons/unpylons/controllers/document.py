import os
import urllib
import logging
import sys
import re

from unpylons.lib.base import *

import unpylons.model as model
htmldir = os.path.join(model.undatadir, "html")
pdfdir = os.path.join(model.undatadir, "pdf")
pngdir = os.path.join(model.undatadir, "docpages")
log = logging.getLogger(__name__)

class DocumentController(BaseController):

    # list of documents by date
    def documentsall(self):
        c.gasessions, c.scyears = model.GetSessionsYears()
        c.documents = model.Document.query.all()
        return render('documentall')

    # list for specific document
    def documentspec(self, docid):
        c.document = model.Document.query.filter_by(docid=docid).first()
        c.docid = c.document.docid
        c.docidq = urllib.quote(c.docid)
        c.meeting = c.document.meetings and c.document.meetings[0]
        #c.message = str([m.meeting1_docidhref  for m in model.DocumentRefDocument.query.filter_by(document2_docid=docid)])
        #c.message = str([m.title  for m in model.Meeting.query.filter_by(docid="A-60-PV.56")])
        #c.message = str(dir(h.truncate))
        return render('documenthold')
        #return str(response.headers["content-type"]) + "ooo" + docid

    def PngFile(self, docid, page):
        pngname = "%s_page_%s.png" % (docid, page)
        return os.path.join(pngdir, pngname)

    def RenderPage(self, docid, page, pngfile):
        pdffile = os.path.join(pdfdir, docid + ".pdf")
        lpdffile = pdffile.replace("(", "\(").replace(")", "\)")
        lpngfile = pngfile.replace("(", "\(").replace(")", "\)")
        imgpixwidth = 800
        cmd = 'convert -quiet -density 192 %s[%d] -resize %d %s > /dev/null 2>&1' % (lpdffile, int(page)-1, imgpixwidth, lpngfile)
        os.system(cmd)

    # list for specific document
    def documentpage(self, docid, page):
        c.document = model.Document.query.filter_by(docid=docid).first()
        c.docid = docid
        c.page = int(page)

        # this makes us render it before we make the image
        pngfile = self.PngFile(docid, c.page)
        if not os.path.exists(pngfile):
            #self.RenderPage(docid, c.page, pngfile)
            #c.message = "page rendered"        
            c.message = "deferred rendering"        
        else:
            c.message = "page already rendered"
        return render('documentpage')
        #return str(response.headers["content-type"]) + "ooo" + docid

    def imagedocumentpage(self, docid, page):
        pngfile = self.PngFile(docid, page)
        self.RenderPage(docid, c.page, pngfile)
        response.headers['Content-type'] = 'image/png'
        fin = open(pngfile, "rb")
        x = fin.read()
        fin.close()
        return x



