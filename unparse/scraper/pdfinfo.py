import os
import re
import sys

# this class encapsulates all the info we know of one pdf file
# the slow data is the number of pages of the file, which we don't destroy
class PdfInfo:

    def __init__(self, lpdfc):
        self.pdfc = lpdfc
        self.pages = -1
        self.pvrefs = set()
        self.pdfcB = lpdfc
        if re.search("[()]", self.pdfcB):
            self.pdfcB = re.sub("\(", "\(", self.pdfcB)
            self.pdfcB = re.sub("\)", "\)", self.pdfcB)

    def UpdateInfo(self, pdfinfodir):
        pdfinfofile = os.path.join(pdfinfodir, self.pdfc + ".txt")
        if not os.path.isfile(pdfinfofile):
            return

        fin = open(pdfinfofile, "r")
        for ln in fin.readlines():
            param, val = ln.strip().split(" = ")
            if param == "pages":
                self.pages = int(val)
            if param == "pvref":
                self.pvrefs.add(val)

    def AddDocRef(self, docid, gid, sdate):
        self.pvrefs.add("%s|%s|%s" % (sdate, docid, gid))

    def WriteInfo(self, pdfinfodir):
        pdfinfofile = os.path.join(pdfinfodir, self.pdfc + ".txt")
        fout = open(pdfinfofile, "w")
        fout.write("pdfc = %s\n" % self.pdfc)
        if self.pages != -1:
            fout.write("pages = %d\n" % self.pages)
        for pvref in self.pvrefs:
            fout.write("pvref = %s\n" % pvref)


