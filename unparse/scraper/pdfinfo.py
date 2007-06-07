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
        self.pvrefsing = { } # map from pair date, code to list

        self.pdfcB = lpdfc
        if re.search("[()]", self.pdfcB):
            self.pdfcB = re.sub("\(", "\(", self.pdfcB)
            self.pdfcB = re.sub("\)", "\)", self.pdfcB)

        mgadoc = re.match("A-(\d\d)-[L\d]", self.pdfc)
        self.mgapv = re.match("A-(\d\d)-PV\.(\d+)", self.pdfc)
        mscdoc = re.match("S-(\d\d\d\d)-\d", self.pdfc)
        self.mscpv = re.match("S-PV-(\d+)", self.pdfc)
        mgares = re.match("A-RES-(\d\d)-(\d+)", self.pdfc)
        mscprst = re.match("S-PRST-(\d\d\d\d)", self.pdfc)
        mscres = re.match("S-RES-(\d+)\((\d\d\d\d)\)", self.pdfc)
        
        self.bSC, self.bGA, self.sess = False, False, ""

        if mgadoc:
            self.desc = "General Assembly Session %s document" % mgadoc.group(1)
            self.bSC = True
        elif self.mgapv:
            self.desc = "General Assembly Session %s meeting %s" % (self.mgapv.group(1), self.mgapv.group(2))
            self.bGA, self.sess = True, self.mgapv.group(1)
        elif mscdoc:
            self.desc = "Security Council %s document" % mscdoc.group(1)
            self.bSC = True
        elif self.mscpv:
            self.desc = "Security Council meeting %s" % self.mscpv.group(1)
            self.bSC = True
        elif mgares:
            self.desc = "General Assembly Resolution %s/%s" % (mgares.group(1), mgares.group(2))
            self.bGA, self.sess = True, mgares.group(1)
        elif mscprst:
            self.desc = "Security Council Presidential Statement %s" % mscprst
            self.bSC = True
        elif mscres:
            self.desc = "Security Council Resolution %s (%s)" % (mscres.group(1), mscres.group(2))
            self.bSC = True
        else:
            self.desc = "UNKNOWN"


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
                vals = val.split('|')
                if len(vals) == 3:
                    self.pvrefsing.setdefault((vals[0], vals[1]), [ ]).append(vals[2])

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


