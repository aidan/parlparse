#!/usr/bin/python

import sys, os, stat, re
import datetime
import cgi

from basicbits import WriteGenHTMLhead
from basicbits import htmldir, pdfdir, indexstuffdir, currentgasession, currentscyear, undata
from basicbits import EncodeHref, MarkupLinks, SplitHighlight
from xapsearch import XapLookup

from indexrecords import LoadSecRecords, LoadAgendaNames, ReadWikipediaReferrers

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
        print '<li><b>%s</b><ul>' % sctopic,
        for sdate, screcord in scgroup:
            patype = (not screcord.bparsed) and ' class="unparsed"' or '' 
            print '<a href="%s"%s>%s</a>' % (screcord.GetHref(), patype, sdate),
        print '</ul></li>'



def WriteIndexStuffSec():
    allsc = LoadSecRecords("all")
    WriteGenHTMLhead("Security Council Meetings by topic")
    WriteCollapsedSec(allsc)
    return True


def WriteIndexStuffSecYear(scyear):
    WriteGenHTMLhead("Security Council Meetings of %s" % scyear)
    allsc = LoadSecRecords("all")
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

    print '<div id="sectors">'
    print '<div id="securitycouncil">'
    print '<h2>Security Council</h2>'
    print '<h3>Recent meetings</h3>'
    recentsc = LoadSecRecords("recent")[:10]
    print '<ul class="cslist">'
    for screcord in recentsc:
        print '<li>%s</li>' % screcord.GetDesc()
    print '</ul>'

    print '<h3 class="browse">Browse</h3>'
    print '<p><a href="/securitycouncil">Meetings by topic</a></p>'
    print '<p><a href="/securitycouncil/documents">All Security Council documents</a></p>'
    print '</div>'

    print '<div id="generalassembly">'
    print '<h2>General Assembly</h2>'
    print '<h3>Recent meetings</h3>'

    recentags = LoadAgendaNames("recent")[:8]
    print '<ul class="cslist">'
    for agrecord in recentags:
        print '<li>%s</li>' % agrecord.GetDesc()
    print '</ul>'

    print '<h3 class="browse">Browse</h3>'
    print '<p><a href="/generalassembly">Meetings by topic</a></p>'
    print '<p><a href="/generalassembly/documents">All General Assembly documents</a></p>'
    print '</div>'

    print """<div id="about">
    <h2>About Us</h2>
    <p>Thirteen years of official <a href="http://en.wikipedia.org/wiki/United_Nations">United Nations</a>
    meetings of the <a href="http://en.wikipedia.org/wiki/United_Nations_General_Assembly">General Assembly</a>
    and the <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council">Security Council</a>
    including many supporting documents are available for browsing and linking to on this site.
    You can see every publically reported members' vote
    and resolution (both passed and vetoed) in this time period.</p>

    <p>This is for use as a tool to facilitate public cited research
    in articles in such places as wikipedia and on blogs.</p>

    <p>This project has been created by the people behind
    <a href="http://www.publicwhip.org.uk">Public whip</a> using
    screen scraping and PDF text parsing <a href="http://www.python.org">technology</a>.
    Email <i>team@undemocracy.com</i> for details.
    Patchy reports about how this was built can be found on the <a href="http://www.freesteel.co.uk/wpblog">Freesteel blog</a>.
    The computer source code, which is the physical embodiment of this project,
    can be found on <a href="http://project.knowledgeforge.net/ukparse/svn/trunk/unparse/">knowledgeforge-ukparse</a>.</p>

    </div>"""

    wprefs = ReadWikipediaReferrers(6)
    print '<div id="wplinks">'
    print '<h3>Wikipedia articles referring to hosted documents</h3>'
    print '<ul class="cslist">'
    for wpref in wprefs:
        print '<li><a href="%s">%s</a></li>' % wpref
    print '</ul>'
    print '</div>'


def WriteIndexStuffAgnum(agnum):
    msess = re.search("-(\d+)$", agnum) # derive the session if there is one
    nsess = msess and int(msess.group(1)) or 0

    allags = LoadAgendaNames(agnum)

    if nsess:
        agnumlist = agnum.split(",")
        ags = [ agrecord  for agrecord in allags  if agrecord.agnum in agnumlist ]
    else:
        # assert agnum in ["condolence", "recent" ]
        ags = [ agrecord  for agrecord in allags  if re.match(agnum, agrecord.agnum) ]

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
        for a in allags[:89]:
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

    allsc = LoadSecRecords("all")
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





