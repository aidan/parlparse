#!/usr/bin/python

import sys, os, stat, re
import datetime
import cgi

from basicbits import WriteGenHTMLhead
from basicbits import htmldir, pdfdir, indexstuffdir, currentgasession, currentscyear, undata
from basicbits import EncodeHref, MarkupLinks, SplitHighlight
from xapsearch import XapLookup

from indexrecords import LoadSecRecords, LoadAgendaNames
from wikitables import ShortWikipediaTable, BigWikipediaTable

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
    for nsess in range(currentgasession, 48, -1):
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
        scgroup.reverse()
        print '<li><b>%s</b><ul>' % sctopic,
        for sdate, screcord in scgroup:
            patype = (not screcord.bparsed) and ' class="unparsed"' or '' 
            print '<a href="%s"%s>%s</a>' % (screcord.GetHref(), patype, re.sub("-", "&#8209;", sdate)),
        print '</ul></li>'



def WriteIndexStuffSec():
    allsc = LoadSecRecords("all")
    WriteGenHTMLhead("Security Council Meetings by topic")
    print '<p><a href="/generalassembly">General Assembly topics</a></p>'
    print '<p><a href="/securitycouncil/documents">Security Council documents</a></p>'
    print '<p><a href="/">Front page</a></p>'
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

def WriteAboutPage():
    WriteGenHTMLhead("About Us")
    fin = open("aboutpage.html")
    print fin.read()
    fin.close()

def WriteWikiPage():
    WriteGenHTMLhead("Wikipedia references")
    bigwikitable = BigWikipediaTable()
    print '<div id="wplinks">'
    print '<h3>Wikipedia table</h3>'
    print '<p>List of incoming links from Wikipedia from wikipedia articles.</p>'
    print '<table class="wpreftab">'
    print '<tr> <th>N</th> <th>Document</th> <th>First</th> <th>Last</th> </tr>'

    for bigwikirow in bigwikitable:
        if re.search("index.php", bigwikirow[4]):
            continue
        print '<tr>',
        print '<td>%d</td>' % bigwikirow[2]
        print '<td><a href="%s">%s</a></td>' % (bigwikirow[3], bigwikirow[4])
        print '<td>%s</td><td>%s</td>' % (bigwikirow[1].strftime("%Y-%m-%d"), bigwikirow[0].strftime("%Y-%m-%d"))
        print '</tr>'
    print '</table>'
    print '</div>'


def WriteFrontPage():
    WriteGenHTMLhead("Front page", frontpage=True)

    print '''
        <div style="padding: 1ex; margin: 3px; background-color:#f9b5b5; border: thin red solid; margin-top:0em; float:right; width:260px">
                        <form method="post" action="http://www.theunsays.com/cgi-bin/emailnotify/singleform.cgi" id="singleform" name="singleform" >                           
                        <strong>Email me when</strong> <input type="text" value="anything" size="9" onclick="this.value=''" name="keyword" /> appears in a press release.      
                        <strong>Email:</strong> <input type="text" size="15" value="your address" onclick="this.value=''" name="email" />                                      
                        <input type="hidden" name="source" value="undemocracy.com" />                                                                                          
                        <input type="submit" onclick=" if ( document.singleform.keyword.value == 'anything' ) {document.singleform.keyword.value = ''; }                       
                                                      if ( document.singleform.email.value == 'your address' ) {alert('email address missing'); return false; }                
                                        " value="signup" />                                                                                                                    
                        </form>  
        </div>

            <p style="margin-top:1em"><b>This website</b> gives easy access to the transcripts (since 1994) of 
             two of the five principal 
             <a href="http://en.wikipedia.org/wiki/United_Nations_System" title="Wikipedia article about the United Nations System"><b>United Nations bodies</b></a>.</p>  
             
             <p style="margin-top:0.5em">The 
             <a href="http://en.wikipedia.org/wiki/United_Nations#Security_Council" title="Wikipedia article describing the Security Council"><b>Security Council</b></a> 
             can authorize war and international sanctions.</p>

             <p style="margin-top:0.5em">The 
             <a href="http://en.wikipedia.org/wiki/United_Nations#General_Assembly" title="Wikipedia article describing the United Nations General Assembly"><b>General Assembly</b></a>
             directs the business of the United Nations and 
             recommends international treaties.
             

             <div style="padding: 1ex; margin: 3px; background-color:#f9b5b5; border: thin red solid; margin-top:0em; float:right; width:260px">Media: 
             <a href="http://www.guardian.co.uk/technology/2008/mar/13/internet.politics">Newspaper article 13 March</a>, 
             <a href="http://video.google.com/videoplay?docid=5811193931753907681&hl=en-GB">4 minute video presentation</a>,
             <a href="http://citizenreporter.org/2008/01/bm241-making-better-use-of-the-united-nations/">Podcast interview</a>.
             <br/>
             Notes on the <a href="http://www.freesteel.co.uk/wpblog/category/whipping/un/">creator's blog</a>.
             <br/>
             <b>New:</b> Links to <a href="http://www.undemocracy.com/generalassembly/webcastindex">webcasts</a>.</div>
             
         <p style="margin-top:0.5em">Find out what <a href="/nations" title="List all nations and their ambassadors who speak"><b>your nation</b></a> has been doing in this international forum.</p>

             <p style="margin-top:1em; margin-bottom:0.5em"><b style="background:#b3f1d7;">The third column</b> lists 
             recent visits from Wikipedia readers.
             <i>This is the best place to start browsing, 
             because only some of documents are very interesting and you are unlikely to get lucky
             if you click at random.</i></p>'''  
    
    print '''<p style="margin-botton:1em"><b>Note</b>: While Security Council meetings are on-line within 
             hours, General Assembly transcripts go on-line three months after
             the meeting (although the videos are up immediately).  The start of the 63rd 
             session is <a href="http://www.un.org/ga/63/meetings63.shtml"><b>here</b></a>.</p>'''
    
    print '<div id="sectors">'
    print '<div id="securitycouncil">'
    print '<h2>Security Council</h2>'
    
    print '<p><a href="/securitycouncil" title="Comprehensive list of meetings by date according to agenda item">Meetings by topic</a></p>'
    print '<p><a href="/securitycouncil/documents" title="Table of documents of the Security Council by year">All documents</a></p>'
    
    print '<h3>Recent meetings</h3>'
    recentsc = LoadSecRecords("recent")[:12]
    print '<ul class="cslist">'
    for screcord in recentsc:
        print '<li>%s</li>' % re.sub("--", " - ", screcord.GetDesc())  # sub to allow word wrapping
    print '</ul>'

    print '</div>'

    print '<div id="generalassembly">'
    print '<h2>General Assembly</h2>'
    
    print '<p><a href="/generalassembly" title="Table of sessions which link to comprehensive lists of agenda items">Meetings by topic</a></p>'
    print '<p><a href="/generalassembly/documents" title="All documents of the General Assembly">All documents</a></p>'
    
    print '<h3>Recent meetings</h3>'

    recentags = LoadAgendaNames("recent")[:8]
    print '<ul class="cslist">'
    for agrecord in recentags:
        print '<li>%s</li>' % agrecord.GetDesc()
    print '</ul>'

    print '</div>'

    txtaboutus = """
    <h2>Information</h2>
    <p><b>This site</b> has nothing to do with the <b><a href="http://www.un.org/english">real UN website</a></b> 
    or any part of the United Nations itself.  It has been supported by no organization. 
    It is merely a citizens' attempt to provide Web 2.0 compliant access to 
    many of the important official UN documents 
    (eg <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council">Security Council Resolutions</a> 
    and <a href="http://en.wikipedia.org/wiki/United_Nations_General_Assembly">General Assembly votes</a>)
    which feature in the news.</p>

    <p><b>For</b> background information about the UN and its structure, as well as the meaning and purpose of these documents, 
    check out <a href="http://en.wikipedia.org/wiki/United_Nations">United Nations on Wikipedia</a>
    and read the related articles.  
    Why not help to <a href="http://en.wikipedia.org/wiki/Wikipedia:WikiProject_United_Nations">improve them</a>?</p>
    
    <p><b>For</b> a quick tour of the sets of documents that are available here, look at
    <a href="http://www.undemocracy.com/United_States/bush">President Bush</a> of
    <a href="http://www.undemocracy.com/United_States">The United States</a>, or
    <a href="http://www.undemocracy.com/Iran/ahmadinejad">President Ahmadinejad</a> of
    <a href="http://www.undemocracy.com/Iran">Iran</a>, as well as
    <a href="http://www.undemocracy.com/S-RES-242(1967)">all speeches</a>
    that refer to <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council_Resolution_242">Resolution 242</a>.</p>

    <p><b>Questions</b> about this website in particular are answered by:
    <a href="http://www.publicwhip.org.uk/faq.php#organisation">Who?</a>
    <a href="http://en.wikipedia.org/wiki/United_Nations_Document_Codes">What?</a>
    <a href="http://www.freesteel.co.uk/wpblog/category/whipping/un/">When?</a>
    <a href="http://www.freesteel.co.uk/wpblog/">Where?</a>
    <a href="http://www.freesteel.co.uk/wpblog/2007/09/the-purpose-of-the-undemocracycom-site/"><b>Why?</b></a>
    <a href="http://www.freesteel.co.uk/wpblog/2007/09/how-does-undemocracycom-work/">How?</a>, and finally
    <a href="http://www.freesteel.co.uk/wpblog/2007/09/undemocracy-needs-your-help/">What can I do to help?</a>.</p>
    
    <p><b>You</b> can leave comments on some of those links, or email <a href="mailto:team@undemocracy.com">team@undemocracy.com</a>.
    Don't be shy.  
    This project is a hobby begun by volunteers who recognized that the accessibility of these vital documents 
    was so limited they had to do something about it themselves, since there was no evidence it was 
    going to happen by itself.</p>"""

    shortwikitable = ShortWikipediaTable(12)
    if True:
        print '<div id="wpblogincoming">'
        print '<h2>Wikipedia referring articles</h2>'
        print '<p><a href="/incoming" title="Wikipedia articles which link to documents available on this website">All incoming citations</a></p>'
        print '<p><i>(<a href="http://en.wikipedia.org/wiki/Portal:United_Nations" title="Wikipedia project: United Nations Portal">Portal:United Nations</a>)</i></p>'
        print '<h3>Recently followed citations</h3>'
        print '<ul class="cslist">'
        for shortwikirow in shortwikitable:
            # shortwikirow[0] date, shortwikirow[1] time, shortwikirow[2] count
            print '<li>%s %s (%s) <a href="%s">%s</a></td> </li>' % (shortwikirow[0], shortwikirow[1], shortwikirow[2], shortwikirow[3], shortwikirow[4])

        print '</ul>'
        print '<p><a href="/incoming" title="Wikipedia articles which link to documents available on this website">more...</a></p>'
        print '</div>'

    print '<div id="aboutfooter">'
    print txtaboutus
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
        print '<p>According to the <a href="http://www.undemocracy.com/A-520-Rev.16/page_97">procedures of the General Assembly</a>, when there has been a major disaster only '
        print 'the president is permitted to offer condolences to the victims at the start of the meeting.'
        print 'This is probably to avoid the entire day being taken up with every ambassador in turn offering '
        print 'their own expression of sympathy.  This timeline of disasters is incomplete owing to the '
        print 'General Assembly not always being in session.'
        ags.reverse()

    if nsess:
        print '<p><a href="%s">Whole of session %d</a></p>' % (EncodeHref({"pagefunc":"gasession", "gasession":nsess}), nsess)
    
    #print '<h2><a href="%s">See this agenda all unrolled</a></h2>' % EncodeHref({"pagefunc":"agendanumexpanded", "agendanum":agnum})

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





