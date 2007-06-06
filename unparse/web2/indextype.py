#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import basehref, htmldir, pdfdir, indexstuffdir, currentgasession, currentscyear
from basicbits import EncodeHref
from xapsearch import XapLookup

class SecRecord:
    def __init__(self, stext):
        self.bGA, self.bSC = False, True
        for sp, val in re.findall('<span class="([^"]*)">([^<]*)</span>', stext):
            if sp == "documentid":
                self.docid = val
            elif sp == "date":
                self.sdate = val
            elif sp == "sctopic":
                self.topic = val
            elif sp == "numvotes":
                self.numvotes = int(val)
    
    def GetHref(self):
        return '%s?code=%s' % (basehref, self.docid)
    
    def GetDesc(self):
        vs = (self.numvotes >= 1) and " (vote)" or ""
        return '%s <a href="%s?code=%s">%s</a>%s' % (self.sdate, basehref, self.docid, self.topic, vs)

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
            elif sp == "subheadingid":
                self.gid = val
            elif sp == "date":
                self.sdate = val
            elif sp == "agendanum":
                self.agnum = val
                self.sess = re.search("-(\d+)", self.agnum).group(1)
            elif sp == "agtitle":
                self.agtitle = val
            elif sp == "aggrouptitle":
                self.aggrouptitle = val
            elif sp == "agcategory":
                self.agcategory = val
            # could pull in vote counts if we know what to do with them

    def GetHref(self):
        return '%s?code=%s&select=%s#%s' % (basehref, self.docid, self.gid, self.gid)

    def GetDesc(self):
        return '%s <a href="%s?code=%s&select=%s#%s">%s</a>' % (self.sdate, basehref, self.docid, self.gid, self.gid, self.agtitle)


def LoadAgendaNames():
    agendanamesf = os.path.join(indexstuffdir, "agendanames.html")
    res = [ ]
    fin = open(agendanamesf)
    for ln in fin.readlines():
        if re.match("\s*<p>", ln):
            agrecord = AgRecord(ln)
            res.append(agrecord)
    fin.close()
    return res

def FilterAgendaListRecent(aglist, num):
    sl = [ (agrecord.sdate, agrecord)  for agrecord in aglist ]
    sl.sort()
    sl.reverse()
    return [ agrecord  for sdate, agrecord in sl[:num] ]


def WriteAgendaList(aglist):
    print '<ul class="aglist">'
    for agrecord in aglist:
        print '<li>%s</li>' % agrecord.GetDesc()
    print '</ul>'



def WriteCollapsedAgendaList(aglist):
    aggroupm = { }
    for agrecord in aglist:
        aggroupm.setdefault(agrecord.agnum, [ ]).append(agrecord)
    aggtitles = [ (ag[0].aggrouptitle, ag[0].agnum)  for ag in aggroupm.values() ]
    aggtitles.sort()

    print '<ul class="aglistgroup">'
    for aggt, agnum in aggtitles:
        print '<li>',
        print '<a href="%s?agnum=%s" class="aggroup">%s</a>' % (basehref, agnum, aggt)
        print '<ul>',
        aggl = { }
        for agrecord in aggroupm[agnum]:
            aggl.setdefault((agrecord.sdate, agrecord.docid), [ ]).append((agrecord.gid, agrecord))
        agglks = aggl.keys()
        agglks.sort()
        for agglk in agglks:
            agrecord = min(aggl[agglk])[1]
            print '<a href="%s">%s</a>' % (agrecord.GetHref(), agrecord.sdate),
        print '</ul>'
        print '</li>'



def WriteIndexStuff(sess):
    allags = LoadAgendaNames()

    nsess = int(sess)
    WriteGenHTMLhead("General Assembly Session %s (%d-%d)" % (sess, nsess + 1945, nsess + 1946))

    print '<p>'
    if nsess > 49:
        print '<a href="%s?sess=%d">Session %d</a>' % (basehref, nsess - 1, nsess - 1)
    print '<a href="%s">All sessions</a>' % (basehref)
    if nsess < currentgasession:
        print '<a href="%s?sess=%d">Session %d</a>' % (basehref, nsess + 1, nsess + 1)

    ags = [ agrecord  for agrecord in allags  if agrecord.sess == sess ]
    print '<h3>Full list of topics discussed</h3>'
    print '<p>Several topics may be discussed on each day, and each topic may be discussed over several days.</p>'
    WriteCollapsedAgendaList(ags)
    return True


def WriteCollapsedSec(sclist):
    sctopicm = { }
    for screcord in sclist:
        sctopicm.setdefault(screcord.topic, [ ]).append((screcord.sdate, screcord))
    sctopics = sctopicm.keys()
    sctopics.sort()
    print '<ul>'
    for sctopic in sctopics:
        scgroup = sctopicm[sctopic]
        scgroup.sort()
        print '<li>%s<ul>' % sctopic,
        for sdate, screcord in scgroup:
            print '<a href="%s">%s</a>' % (screcord.GetHref(), sdate),
        print '</ul></li>'



def WriteIndexStuffSec():
    allsc = LoadSecRecords()
    WriteGenHTMLhead("Security Council Meetings by topic")
    WriteCollapsedSec(allsc)
    return True


def WriteIndexStuffSecYear(scyear):
    WriteGenHTMLhead("Security Council Meetings of %s" % scyear)
    allsc = LoadSecRecords()
    sl = [ (screcord.sdate, screcord)  for screcord in allsc  if (screcord.sdate[:4] == scyear) ]
    sl.sort()
    WriteAgendaList([screcord  for sdate, screcord in sl ])
    return True

def WriteFrontPageError(pathpartstr, hmap):
    WriteGenHTMLhead("Front page")
    print "<h1>Did not recognize pathpartstr: '%s'</h1>" % pathpartstr
    print "<h3>hmap:"
    print hmap
    print "</h3>"


def WriteFrontPage():
    WriteGenHTMLhead("Front page")
    fin = open("frontpage.html")
    print fin.read()

    print '<h3>Search feature</h3>'
    print '<form action="%s" method="get">' % basehref
    print 'Search:'
    print '<input type="text" name="search" value="">'
    print '<input type="submit" value="GO">'
    print '</form>'

    allags = LoadAgendaNames()
    print '<h3>General Assembly Sessions</h3>'
    print '<p>',
    for ns in range(49, currentgasession + 1):
        href = EncodeHref({"pagefunc":"gasession", "gasession":ns})
        print '<a href="%s">Session %d</a> (%d-%d)</a>' % (href, ns, ns + 1945, ns + 1946),
    print '</p>'

    print '<h3>Security Council meetings</h3>'
    print '<p><b><a href="%s">Meetings by topic</a></b></p>' % EncodeHref({"pagefunc":"sctopics"})
    print '<p>By year:',
    for ny in range(1994, currentscyear + 1):
        href = EncodeHref({"pagefunc":"scyear", "scyear":ny})
        print '<a href="%s">%d</a>' % (href, ny),
    print '</p>'

    allags = LoadAgendaNames()
    print '<h3>Some recent General Assembly meetings</h3>'
    WriteAgendaList(FilterAgendaListRecent(allags, 10))

    allsc = LoadSecRecords()
    print '<h3>Some recent Security Council meetings</h3>'
    WriteAgendaList(FilterAgendaListRecent(allsc, 10))  # functions apply here
    return True


def WriteIndexStuffAgnum(agnum):
    msess = re.search("-(\d+)$", agnum)
    if not msess:
        return False
    sess = msess.group(1)
    nsess = int(sess)

    allags = LoadAgendaNames()

    agnumlist = agnum.split(",")
    ags = [ agrecord for agrecord in allags  if agrecord.agnum in agnumlist ]
    if not ags:
        return False
    
    agtitle ="Topic of General Assembly Session %s" % sess
    WriteGenHTMLhead(agtitle)
    
    print '<p><a href="%s?sess=%s">Whole of session %s</a></p>' % (basehref, sess, sess)
    
    print '<h3>%s</h3>' % ags[0].aggrouptitle
    WriteAgendaList(ags)

    return True


# under construction
def WriteIndexSearch(search):
    WriteGenHTMLhead("search")
    print '<h3>Searching for: %s</h3>' % search
    recs = XapLookup(search)
    if not recs:
        print '<p>No results found</p>'
        return True

    allags = LoadAgendaNames()  # very inefficient, but get it done
    aglookup = { }
    for agrecord in allags:
        aglookup[(agrecord.docid, agrecord.gid)] = agrecord

    allsc = LoadSecRecords()
    sclookup = { }
    for screcord in allsc:
        sclookup[screcord.docid] = screcord

    print '<ul>'
    for rec in recs:
        srec = rec.split("|")
        gidspeech = srec[0]
        docid = srec[1]
        gidsubhead = srec[4]
        if re.match("A", docid):
            agrecord = aglookup.get((docid, gidsubhead), None)
            if agrecord:
                print '<li><b>AG</b> %s <a href="%s?code=%s#%s">%s</a></li>' % (agrecord.sdate, basehref, agrecord.docid, gidspeech, agrecord.agtitle)
        if re.match("S", docid):
            screcord = sclookup.get(docid, None)
            if screcord:
                print '<li><b>SC</b> %s <a href="%s?code=%s#%s">%s</a></li>' % (screcord.sdate, basehref, screcord.docid, gidspeech, screcord.topic)


    print '</ul>'

    return True


# not written
def WriteIndexStuffNation(nation):
    WriteGenHTMLhead('nation= ' + nation)
    return True




