#!/usr/bin/python

# !!!!!!!! Class shared between scraper and web2 !!!!!!!!

import os
import re
import sys

# this class encapsulates all the info we know of one pdf file
# the slow data is the number of pages of the file, which we don't destroy
class PdfInfo:

    # extracts what you can from the name
    def __init__(self, lpdfc):
        self.pdfc = lpdfc
        self.pvrefs = set()  # back pointers
        self.pvrefsing = { } # map from pair date, code to list

        self.pdfcB = lpdfc
        if re.search("[()]", self.pdfcB):
            self.pdfcB = re.sub("\(", "\(", self.pdfcB)
            self.pdfcB = re.sub("\)", "\)", self.pdfcB)

        mgadoc = re.match("A-(\d\d)-([L\d].*)", self.pdfc)
        self.mgapv = re.match("A-(\d\d)-PV\.(\d+)", self.pdfc)
        mscdoc = re.match("S-(\d\d\d\d)-(\d.*)", self.pdfc)
        self.mscpv = re.match("S-PV.(\d+\S*)", self.pdfc)
        mgares = re.match("A-RES-(\d\d)-(\d+)", self.pdfc)
        mscprst = re.match("S-PRST-(\d\d\d\d)-(.+)", self.pdfc)
        mscres = re.match("S-RES-(\d+)\((\d\d\d\d)\)", self.pdfc)
        
        mrgares = re.match("A-RES-(\d+)\(([IVXL]+)\)", self.pdfc)
        mogadoc = re.match("A-(\d+.*)", self.pdfc)
        moscdoc = re.match("S-(\d+.*)", self.pdfc)

        self.bSC, self.bGA = False, False
        self.nsess, self.nscyear = 0, 0
        self.sortkey = self.pdfc

        self.pages = -1
        self.sdaterefs = [ ]  # dates of meetings that refer to this one
        self.sdate = None   # this data is used for access when we are rendering the associated html
        self.nextmeetingdetails = None
        self.prevmeetingdetails = None
        self.time = None
        self.title = None
        self.agendascontained = [ ] # (gid, agnum, title)
        
        if mgadoc:
            self.desc = "General Assembly Session %s document" % mgadoc.group(1)
            self.dtype = "Document"
            self.nsess = int(mgadoc.group(1))
            self.nmeeting = None
            self.bGA = True
            self.document_number = mgadoc.group(2)
        elif self.mgapv:
            self.desc = "General Assembly Session %s meeting %s" % (self.mgapv.group(1), self.mgapv.group(2))
            self.dtype = "Verbatim Report"
            self.nsess = int(self.mgapv.group(1))
            self.nmeeting = int(self.mgapv.group(2))
            self.sortkey = (self.nsess, self.nmeeting)
            self.bGA = True
        elif mscdoc:
            self.desc = "Security Council %s document" % mscdoc.group(1)
            self.dtype = "Document"
            self.nscyear = int(mscdoc.group(1))
            self.scmeeting = None
            self.document_number = mscdoc.group(2)
            self.bSC = True
        elif self.mscpv:
            self.desc = "Security Council meeting %s" % self.mscpv.group(1)
            self.dtype = "Verbatim Report"
            self.scmeeting = self.mscpv.group(1)
            self.bSC = True
        elif mgares:
            self.desc = "General Assembly Resolution %s/%s" % (mgares.group(1), mgares.group(2))
            self.dtype = "Resolution"
            self.nsess = int(mgares.group(1))
            self.nmeeting = None
            self.bGA = True
            self.resolution_number = mgares.group(2)
        elif mscprst:
            self.nscyear = int(mscprst.group(1))
            self.desc = "Security Council Presidential Statement %d" % self.nscyear
            self.dtype = "Presidental Statement"
            self.scmeeting = None # although it could be obtained through the indexes
            self.document_number = mscprst.group(2)
            self.bSC = True
        elif mscres:
            self.nscyear = int(mscres.group(2))
            self.desc = "Security Council Resolution %s (%d)" % (mscres.group(1), self.nscyear)
            self.dtype = "Resolution"
            self.scmeeting = None # although it could be obtained through the indexes
            self.bSC = True
            self.resolution_number = mscres.group(1)
        
        elif mrgares:
            self.desc = "General Assembly Resolution %s" % mrgares.group(1)
            self.dtype = "Resolution"
            self.nsess = -1 # should decode the roman numeral
            self.nmeeting = None
            self.bGA = True
            self.resolution_number = mrgares.group(1)

        elif mogadoc:
            self.desc = "General Assembly Document %s" % mogadoc.group(1)
            self.dtype = "Document"
            self.document_number = mogadoc.group(1)
            self.nmeeting = None
            self.nsess = None
            self.bGA = True
        elif moscdoc:
            self.desc = "Security Council Document %s" % moscdoc.group(1)
            self.dtype = "Document"
            self.nscyear = -1
            self.scmeeting = None
            self.document_number = moscdoc.group(1)
            self.bSC = True
        
        else:
            self.desc = "UNKNOWN"
            self.dtype = None


    def GetAgnum(self, cgid):
        for (gid, agnum, title) in self.agendascontained:
            if gid == cgid:
                return agnum
        return None

    # called while we are scanning through all the files
    # should look up the agenda title or something
    def AddDocRef(self, docid, gid, sdate):
        self.pvrefs.add("%s|%s|%s" % (sdate, docid, gid))
        refsingkey = (sdate, docid)
        self.pvrefsing.setdefault(refsingkey, [ ]).append(gid)
        self.sdaterefs.append(sdate)

    def AddPrevMeetingDetails(self, prevpdfinfo):
        if prevpdfinfo:
            prevpdfinfo.nextmeetingdetails = (self.pdfc, self.sdate, self.time)
            self.prevmeetingdetails = (prevpdfinfo.pdfc, prevpdfinfo.sdate, self.rosetime)

    # loads the data in from the file
    def UpdateInfo(self, pdfinfodir):

        # in future we'll record the wikibacklinks

        pdfinfofile = os.path.join(pdfinfodir, self.pdfc + ".txt")
        if not os.path.isfile(pdfinfofile):
            return

        fin = open(pdfinfofile, "r")
        for ln in fin.readlines():
            mln = re.match("(.*?) = (.*)$", ln)
            assert mln, ln + " " + pdfinfofile
            param, val = mln.group(1).strip(), mln.group(2).strip()

            if param == "pages":
                self.pages = int(val)
            elif param == "pvref":
                # this is used in some of the decoding of first links
                vals = val.split('|')
                if len(vals) == 3:
                    self.AddDocRef(vals[1], vals[2], vals[0])
            elif param == "daterangerefs":
                self.sdaterefs.extend(val.split())
            elif param == "date":
                self.sdate = val
            elif param == "time":
                self.time = val
            elif param == "rosetime":
                self.rosetime = val
            elif param == "prevmeeting":
                self.prevmeetingdetails = tuple(val.split())
            elif param == "nextmeeting":
                self.nextmeetingdetails = tuple(val.split())
                assert len(self.nextmeetingdetails) == 3, val
            elif param == "agendacontained":
                magcon = re.match("(\S+)\s+(\S+)\s+(.+)$", val)
                self.agendascontained.append((magcon.group(1), magcon.group(2), magcon.group(3).strip()))

    def ResetDocmeasureData(self):
        self.sdaterefs = [ ]  # dates of meetings that refer to this one
        self.sdate = None   # this data is used for access when we are rendering the associated html
        self.nextmeetingdetails = None
        self.prevmeetingdetails = None
        self.time = None

    def WriteInfo(self, pdfinfodir):
        pdfinfofile = os.path.join(pdfinfodir, self.pdfc + ".txt")
        fout = open(pdfinfofile, "w")
        fout.write("pdfc = %s\n" % self.pdfc)
        if self.sdate:
            fout.write("date = %s\n" % self.sdate)
        if self.time:
            fout.write("time = %s\n" % self.time)
            fout.write("rosetime = %s\n" % self.rosetime)
        if self.pages != -1:
            fout.write("pages = %d\n" % self.pages)
        for pvref in self.pvrefs:
            fout.write("pvref = %s\n" % pvref)
        if self.sdaterefs:
            fout.write("daterangerefs = %s %s\n" % (min(self.sdaterefs), max(self.sdaterefs)))
        if self.nextmeetingdetails:
            fout.write("nextmeeting = %s %s %s\n" % self.nextmeetingdetails)
        if self.prevmeetingdetails:
            fout.write("prevmeeting = %s %s %s\n" % self.prevmeetingdetails)
        for agcontained in self.agendascontained:
            fout.write("agendacontained = %s %s %s\n" % agcontained)

