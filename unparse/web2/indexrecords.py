#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import indexstuffdir, EncodeHref


class SecRecord:
    def __init__(self, stext):
        self.bGA, self.bSC = False, True
        for sp, val in re.findall('<span class="([^"]*)">([^<]*)</span>', stext):
            if sp == "documentid":
                self.docid = val
                mdec = re.match("S-PV-(\d+)(?:-(Resu|Part)\.(\d))?$", self.docid)
                self.nmeeting = int(mdec.group(1))
                self.meetingsuffix = mdec.group(2) and ("_%s_%s" % (mdec.group(2), mdec.group(3))) or ""
            elif sp == "date":
                self.sdate = val
            elif sp == "sctopic":
                self.topic = val
            elif sp == "numvotes":
                self.numvotes = int(val)

    def GetHref(self, highlight = None):
        params = {"pagefunc":"scmeeting", "scmeeting":self.nmeeting, "scmeetingsuffix":self.meetingsuffix}
        if highlight:
            params['highlightdoclink'] = highlight
        return EncodeHref(params)

    def GetDesc(self, highlight = None):
        vs = (self.numvotes >= 1) and " (vote)" or ""
        return '%s <a href="%s">%s</a>%s' % (self.sdate, self.GetHref(highlight), self.topic, vs)


def LoadSecRecords():
    scsummariesf = os.path.join(indexstuffdir, "scsummaries.html")
    res = [ ]
    fin = open(scsummariesf)
    for ln in fin.readlines():
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

    def GetHref(self, highlight = None):
        params = {"pagefunc":"gameeting", "gasession":self.nsess, "gameeting":self.nmeeting, "gid":self.gid}
        if highlight:
            params['highlightdoclink'] = highlight
        return EncodeHref(params)

    def GetDesc(self, highlight = None):
        return '%s <a href="%s">%s</a>' % (self.sdate, self.GetHref(highlight), self.agtitle)


def LoadAgendaNames(agendaname):
    agendanamesf = None
    if agendaname:
        agendanamesf = os.path.join(indexstuffdir, "agendaindexes", agendaname + ".html")
        b = False
    if not agendanamesf or not os.path.isfile(agendanamesf):
        agendanamesf = os.path.join(indexstuffdir, "agendanames.html")
        return [ ]#b = True
    res = [ ]
    fin = open(agendanamesf)
    for ln in fin.readlines():
        if re.match("\s*<p>", ln):
            agrecord = AgRecord(ln)
            res.append(agrecord)
    fin.close()
    
    if not b:
        res.append(res[-1])
    return res


