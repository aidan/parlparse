#!/usr/bin/python

import sys, os, stat, re
import datetime
import cgi

from basicbits import WriteGenHTMLhead
from basicbits import htmldir, pdfdir, indexstuffdir, currentgasession, currentscyear, undata
from basicbits import EncodeHref, MarkupLinks, SplitHighlight
from xapsearch import XapLookup

from indexrecords import LoadSecRecords, LoadAgendaNames


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



def WriteCollapsedAgendaList(aglist, bDiced):
    aggroupm = { }
    for agrecord in aglist:
        aggroupm.setdefault(agrecord.agnum, [ ]).append(agrecord)
    aggtitles = [ (ag[0].aggrouptitle, ag[0].agnum)  for ag in aggroupm.values() ]
    aggtitles.sort()

    print '<ul class="aglistgroup">'

    print '<li><a href="%s" class="aggroup">Condolences</a></li>' % EncodeHref({"pagefunc":"agendanum", "agendanum":"condolence"}) # special case

    if bDiced:
        for aggt, agnum in aggtitles:
            aggl = { }
            for agrecord in aggroupm[agnum]:
                aggl.setdefault((agrecord.sdate, agrecord.docid), [ ]).append((agrecord.gid, agrecord))
            agglks = aggl.keys()
            agglks.sort()
            agglk = min(agglks)
            agrecord = min(aggl[agglk])[1]
            href = EncodeHref({"pagefunc":"meeting", "docid":agrecord.docid, "gadice":agrecord.gid})
            print '<li>%d %s <a href="%s" class="aggroup">%s</a></li>' % (len(agglks), agrecord.sdate, href, aggt)
        print '</ul>'
        return        

    for aggt, agnum in aggtitles:
        print '<li>',
        print '<a href="%s" class="aggroup">%s</a>' % (EncodeHref({"pagefunc":"agendanum", "agendanum":agnum}), aggt)
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


def GetSessionLink(nsess, bdocuments):
    if nsess < 49:
        bdocuments = True
    if bdocuments:
        return '<a href="%s">Session %d</a>' % (EncodeHref({"pagefunc":"gasession", "gasession":nsess}), nsess)
    return '<a href="%s">Session %d documents</a>' % (EncodeHref({"pagefunc":"gadocuments", "gasession":nsess}), nsess)


def WriteIndexStuff(nsess):
    WriteGenHTMLhead("General Assembly Session %d (%d-%d)" % (nsess, nsess + 1945, nsess + 1946))
    allags = LoadAgendaNames(None)

    print '<p>',
    tlinks = [ ]
    if nsess > 1:
        tlinks.append(GetSessionLink(nsess - 1, False))
    tlinks.append('<a href="%s">All sessions</a>' % (EncodeHref({"pagefunc":"gatopics"})))
    tlinks.append(GetSessionLink(nsess, True))  # documents
    if nsess < currentgasession:
        tlinks.append(GetSessionLink(nsess + 1, False))
    print ' | '.join(tlinks),
    print '</p>'

    ags = [ agrecord  for agrecord in allags  if agrecord.nsess == nsess ]
    print '<h3>Full list of topics discussed</h3>'
    print '<p>Several topics may be discussed on each day, and each topic may be discussed over several days.</p>'
    WriteCollapsedAgendaList(ags, True)


def WriteIndexStuffGA():
    WriteGenHTMLhead("All General Assembly Topics")
   
    print '<p><a href="%s">Security Council Topics</a></p>' % EncodeHref({"pagefunc":"sctopics"})
    print '<h3>Topics that span more than one year</h3>'
    print '<ul class="aglistgroup">'
    print '<li><a href="%s" class="aggroup">Condolences</a></li>' % EncodeHref({"pagefunc":"agendanum", "agendanum":"condolence"}) # special case
    print '</ul>'

    print '<h3>General Assembly Sessions topics by year</h3>'
    print '<ul>'
    for nsess in range(49, currentgasession + 1):
        print '<li>',
        print GetSessionLink(nsess, True),
        print '(%d-%d)' % (nsess + 1945, nsess + 1946)
        print '</li>',
    print '</ul>'
    return


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
    WriteGenHTMLhead("Something is wrong", frontpage=False) # deliberately false, as bad URLs go here
    print "<h1>Did not recognize pathpartstr: '%s'</h1>" % pathpartstr
    print "<h3>hmap:"
    print hmap
    print "</h3>"


def WriteFrontPage():
    WriteGenHTMLhead("Front page", frontpage=True)
    
    fin = open("frontpage.html")
    print fin.read()
    
    return
    print '<h3>Search feature</h3>'
    print '<form action="/" method="get">' 
    print 'Search:'
    print '<input type="text" name="search" value="">'
    print '<input type="submit" value="GO">'
    print '</form>'

    print '<p><a href="%s">List all nations</a></p>' % EncodeHref({"pagefunc":"nationlist"})

    print '<h3>General Assembly Sessions</h3>'
    print '<p><a href="%s">All condolences</a>' % EncodeHref({"pagefunc":"agendanum", "agendanum":"condolence"})
    print '<a href="%s">All documents</a></p>' % EncodeHref({"pagefunc":"documentlist", "body":"generalassembly"})

    print '<p>',
    for ns in range(49, currentgasession + 1):
        href = EncodeHref({"pagefunc":"gasession", "gasession":ns})
        print '<a href="%s">Session %d</a> (%d-%d)</a>' % (href, ns, ns + 1945, ns + 1946),
    print '</p>'

    print '<h3>Security Council meetings</h3>'
    print '<p><b><a href="%s">Meetings by topic</a></b>' % EncodeHref({"pagefunc":"sctopics"})
    print '<a href="%s">All documents</a></p>' % EncodeHref({"pagefunc":"documentlist", "body":"securitycouncil"})
    print '<p>By year:',
    for ny in range(1994, currentscyear + 1):
        href = EncodeHref({"pagefunc":"scdocuments", "scyear":ny})
        print '<a href="%s">%d</a>' % (href, ny),
    print '</p>'

    allags = LoadAgendaNames("recent")
    print '<h3>Some recent General Assembly meetings</h3>'
    WriteAgendaList(FilterAgendaListRecent(allags, 10))

    allsc = LoadSecRecords()
    print '<h3>Some recent Security Council meetings</h3>'
    WriteAgendaList(FilterAgendaListRecent(allsc, 10))  # functions apply here
    return True


def WriteIndexStuffAgnum(agnum):
    msess = re.search("-(\d+)$", agnum)
    nsess = msess and int(msess.group(1)) or 0

    allags = LoadAgendaNames(agnum)

    if nsess:
        agnumlist = agnum.split(",")
        ags = [ agrecord  for agrecord in allags  if agrecord.agnum in agnumlist ]
    else:
        # assert agnum == "condolence"
        ags = [ agrecord  for agrecord in allags  if re.match("condolence", agrecord.agnum) ]

    agtitle = "Topic of General Assembly"
    WriteGenHTMLhead(agtitle)

    if agnum == "condolence":
        print '<p>According to the rules of the General Assembly, when there has been a major disaster only '
        print 'the president is permitted to offer condolences to the victims at the start of the meeting.'
        print 'This is probably to avoid the entire day being taken up with every ambassador in turn offering '
        print 'their own expression of sympathy.  This timeline of disasters is incomplete owing to the '
        print 'General Assembly not always being in session.'
    
    if nsess:
        print '<p><a href="%s">Whole of session %d</a></p>' % (EncodeHref({"pagefunc":"gasession", "gasession":nsess}), nsess)
    
    print '<h2><a href="%s">See this agenda all unrolled</a></h2>' % EncodeHref({"pagefunc":"agendanumexpanded", "agendanum":agnum})

    if ags:
        print '<h3>%s</h3>' % ags[0].aggrouptitle
        WriteAgendaList(ags)
    else:
        print '<h3>List appears empty</h3>'
        print len(allags)
        for a in allags[:99]:
            print '<p>' + a.agnum

    return True


# under construction
def WriteIndexSearch(search):
    WriteGenHTMLhead("Searching for '%s'" % search)
    recs = XapLookup(search)
    if not recs:
        print '<p>No results found</p>'
        return True

    allags = LoadAgendaNames(None)  # very inefficient, but get it done
    aglookup = { }
    for agrecord in allags:
        aglookup[(agrecord.docid, agrecord.gid)] = agrecord

    allsc = LoadSecRecords()
    sclookup = { }
    for screcord in allsc:
        sclookup[screcord.docid] = screcord

    highlights = SplitHighlight(search)

    print '<div id="search-results">';
    for rec in recs:
        # id of para, document number, byte offset start, byte length, heading id
        srec = rec.split("|")
        #print "xap records", srec
        gidspeech = srec[0]
        docid = srec[1]
        byte_start = int(srec[2])
        byte_len = int(srec[3])
        gidsubhead = srec[4]

        # extract record using byte offset
        fullfilename = os.path.join(undata, "html", docid + '.html')
        f = open(fullfilename)
        f.seek(byte_start)
        content = f.read(byte_len)
        f.close()

        # really nasty search highlighting
        words = re.split("<[^>]*>|</[^>]*>|(\S+)", content)
        words = [ x for x in words if x ]
        firstword = 0
        for i in range(len(words)):
            word = words[i]
            if re.match(highlights[1], word) and not firstword:
                firstword = i
        roundwords = words[firstword-50:firstword+50]
        extract_text = " ".join(roundwords)
        extract_text = extract_text.replace("</p>", "") # XXX why does split not cover this?
        extract_text = MarkupLinks(extract_text, search)

        if re.match("A", docid):
            agrecord = aglookup.get((docid, gidsubhead), None)
            if agrecord:
                print '<h2>General Assembly: %s</h2>' % (agrecord.GetDesc(search, gidspeech))
                print extract_text
                del aglookup[(docid, gidsubhead)]  # quick hack to avoid repeats
        if re.match("S", docid):
            screcord = sclookup.get(docid, None)
            if screcord:
                print '<h2>Security Council: %s</h2>' % (screcord.GetDesc(search, gidspeech))
                print '<p>'+extract_text+'</p>'
                del sclookup[docid]
    print '</div>';





