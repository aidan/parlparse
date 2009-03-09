#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import EncodeHref

# put back in for now
from basicbits import indexstuffdir, htmldir
from db import GetDBcursor

class SecRecord:
    def __init__(self, stext):
        self.bGA, self.bSC = False, True
        self.bparsed = True
        self.topic = "Not set"
        for sp, val in re.findall('<span class="([^"]*)">([^<]*)</span>', stext):
            if sp == "documentid":
                self.docid = val
                mdec = re.match("S-PV.(\d+(?:-(?:Resu|Part)\.\d+)?)$", self.docid)
                self.scmeeting = mdec.group(1)
            elif sp == "date":
                self.sdate = val
            elif sp == "sctopic":
                self.topic = val
            elif sp == "numvotes":
                self.numvotes = int(val)
            elif sp == "parsed":
                self.bparsed = (val == "1")

    def GetHref(self, highlight = None, gid = None):
        params = {"pagefunc":"scmeeting", "scmeeting":self.scmeeting}
        if highlight:
            params['highlightdoclink'] = highlight
        if gid:
            params['gid'] = gid
        return EncodeHref(params)

    def GetDesc(self, highlight = None, gid = None):
        vs = (self.numvotes >= 1) and " (vote)" or ""
        if not self.bparsed:
            vs = " (unparsed)"
        return '%s <a href="%s">%s</a>%s' % (self.sdate, self.GetHref(highlight, gid), self.topic, vs)


def LoadSecRecords(secsubj):
    scsummariesf = os.path.join(indexstuffdir, "scsummaries.html")
    res = [ ]
    fin = open(scsummariesf)
    while True:
        ln = fin.readline()
        if not ln:
            break
        if secsubj == "recent" and len(res) > 20:
            break
        if re.match('\s*<span class="scmeeting">', ln):
            res.append(SecRecord(ln))
    fin.close()
    return res


class AgRecord:
    def __init__(self, stext):
        self.bGA, self.bSC = True, False
        for sp, val in re.findall('<span class="([^"]*)">([^<]*)</span>', stext):
            if sp == "documentid":
                self.docid = val
                mdec = re.match("A-(\d\d)-PV\.(\d+)$", self.docid)
                self.sess = mdec.group(1)
                self.nsess = int(self.sess)
                self.nmeeting = int(mdec.group(2))
                self.fhtml = os.path.join(htmldir, self.docid + ".html")

            elif sp == "subheadingid":
                self.gid = val
            elif sp == "date":
                self.sdate = val
            elif sp == "agendanum":
                self.agnum = val
                # assert self.sess == re.search("-(\d+)", self.agnum).group(1)
            elif sp == "agtitle":
                self.agtitle = val
            elif sp == "aggrouptitle":
                self.aggrouptitle = val
            elif sp == "agcategory":
                self.agcategory = val
            # could pull in vote counts if we know what to do with them

    def GetHref(self, highlight = None, gid = None):
        params = {"pagefunc":"gameeting", "gasession":self.nsess, "gameeting":self.nmeeting, "gid":self.gid}
        if highlight:
            params['highlightdoclink'] = highlight
        if gid:
            params['gid'] = gid
            #params['gadice'] = gid  # makes the link do the section ; only works if gid is for the header!
        return EncodeHref(params)

    def GetDesc(self, highlight = None, gid = None):
        return '%s <a href="%s">%s</a>' % (self.sdate, self.GetHref(highlight, gid), self.agtitle)

# this probably goes
def LoadAgendaNames(agendaname):
    agendanamesf = None
    lagendanamesf = [ ]
    agendaindexesdir = os.path.join(indexstuffdir, "agendaindexes")
    if agendaname == None:
        lagendanamesf.append(os.path.join(indexstuffdir, "agendanames.html"))
    elif agendaname == "condolence":
        for ff in os.listdir(agendaindexesdir):
            if re.match("condolence-\d+\.html", ff):
                lagendanamesf.append(os.path.join(agendaindexesdir, ff))
        lagendanamesf.sort()
    else:
        for cagendaname in agendaname.split(","):
            agendanamesf = os.path.join(agendaindexesdir, cagendaname + ".html")
            if os.path.isfile(agendanamesf):
                lagendanamesf.append(agendanamesf)

    res = [ ]
    for agendanamesf in lagendanamesf:
        fin = open(agendanamesf)
        for ln in fin.readlines():
            if re.match("\s*<p>", ln):
                agrecord = AgRecord(ln)
                res.append(agrecord)
        fin.close()

    return res


