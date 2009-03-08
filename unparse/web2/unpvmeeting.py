#!/usr/bin/python


import sys, os, stat, re
import datetime
import urllib
from basicbits import WriteGenHTMLhead, EncodeHref, monthnames, MarkupLinks, LongDate, GenWDocLink, basehref, nowdatetime
from indexrecords import LoadAgendaNames
from quickskins import WebcastLink

def WriteSpoken(gid, dtext, councilpresidentnation):
    print '<div class="speech" id="%s">' % gid
    respek = '<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(nation|non-nation)">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>'
    mspek = re.search(respek, dtext)
    if not mspek:
        dtext = re.sub('<span class="search-highlight">(.*?)</span>', '\\1', dtext)
        mspek = re.search(respek, dtext)
    assert mspek, dtext[:300]
    name, nationtype, nation, language = mspek.group(1), mspek.group(2), mspek.group(3), mspek.group(4)
    print '<cite>',


    # build up the components of the speaker
    nationlink = nation and EncodeHref({"pagefunc":"nation", "nation":nation})
    if nationlink:
        nationblock = '<a class="nation" href="%s">(%s)</a>' % (nationlink, nation)
    elif nation:
        nationblock = '<span class="nation">(%s)</span>' % nation
    else:
        nationblock = ""

    # the country links still go from the flag
    flagnation = nation
    if councilpresidentnation:
        if name == "The President":
            nation = councilpresidentnation
            flagnation = nation
    if not flagnation:
        if re.match("The(?: Deputy)? Secretary-General", name):
            flagnation = "United Nations"
            nation = name
        elif not councilpresidentnation and re.match("The(?: Acting)? President", name):
            flagnation = "%s of the General Assembly" % name
    if not flagnation:
        flagnation = "Unknown"
    if re.search("for General Assembly", flagnation):
        flagnation = "Secretariat"
    
    flagimg = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":flagnation})
    flaglink = nation and EncodeHref({"pagefunc":"nation", "nation":nation})

    if nation and name and not re.search("President", name):
        personlink = EncodeHref({"pagefunc":"nationperson", "nation":nation, "person":name})
    else:
        personlink = ""

    if flaglink:
        print '<a href="%s">' % flaglink,
    print '<img class="smallflag" src="%s">' % flagimg,
    if flaglink:
        print '</a>',

    if personlink:
        print '<a class="name" href="%s">%s</a>' % (personlink, name),
    else:
        print '<span class="name">%s</span>' % name

    print nationblock
    print '</cite>'

    print dtext[mspek.end(0):]

    print '</div>'

def WriteAgenda(gid, agnum, dtext, docid):
    print '<div class="agendaitem" id="%s">' % gid
    if agnum:
        lkothdisc = '<a href="%s">More on this topic</a>' % EncodeHref({"pagefunc":"agendanum", "agendanum":agnum})
        flippedhcode = '%s_%s' % (docid, gid)
        lkflipagenda = '<a href="%s#%s">Flip</a>' % (EncodeHref({"pagefunc":"agendanumexpanded", "agendanum":agnum}), flippedhcode)
        #print '<div class="otheraglink">%s %s</div>' % (lkothdisc, lkflipagenda)
        print '<div class="otheraglink">%s</div>' % lkothdisc
    
    print dtext
    print '</div>'

def WriteAgendaFlipped(gid, agnum, dtext, docid):
    print '<div class="subheading" id="%s_%s">' % (docid, gid)
    if agnum:
        lkflap = '<a href="%s">Flap</a>' % (EncodeHref({"pagefunc":"meeting", "docid":docid, "gid":gid}))
        print '<div class="otheraglink">%s</div>' % lkflap

    print dtext
    print '</div>'


def WriteVote(gid, dtext, bSC):
    print '<div class="recvote" id="%s">' % gid

    print '<table class="votekey">'
    print '<tr><td><span class="favourul" onclick="chvotekey(this);">favour</span></td>'
    if not bSC:
        print '</tr><tr>'
    print '<td><span class="againstul" onclick="chvotekey(this);">against</span></td></tr>'
    print '<tr><td><span class="abstainul" onclick="chvotekey(this);">abstain</span></td>'
    if not bSC:
        print '</tr><tr>'
    print '<td><span class="absentul" onclick="chvotekey(this);">absent</span></td></tr>'
    print '</table>'

    print dtext
    print '</div>'


def WriteAssemblyChair(gid, dtext):
    ppres = re.findall('<p[^>]*>(.*?)</p>', dtext)
    print '<div class="assembly-chairs" id="%s">' % gid
    if len(ppres) == 1:
        print "The President:"
    else:
        print "The Co-Presidents:"
    for pres in ppres:
        masschname = re.search('<span class="name">([^<]*)</span>', pres)
        masschnation = re.search('<span class="nation">([^<]*)</span>', pres)
        if masschname:
            print masschname.group(1)
        if masschnation:
            print '(%s)' % masschnation.group(1)
    print '</div>'


def WriteCouncilAttendees(gid, dtext):
    pcatt = re.findall('<p[^>]*>(.*?)</p>', dtext)
    assert len(pcatt) == 15, dtext
    rows = [ [ "President:", [ ] ], [ "Members:", [ ] ] ]
    res = None
    for catt in pcatt:
        name, nation, place = None, None, None
        for cl, val in re.findall('<span class="([^"]*)">([^<]*)</span>', catt):
            if cl == "nation":
                nation = val
            elif cl == "place":
                place = val
            elif cl == "name" and not name: # sometimes we get two names here
                name = val
        assert name and nation and place, dtext
        
        if place == "president":
            res = nation
            rows[0][1].append((name, nation))
        else:
            rows[1][1].append((name, nation))
    assert res, dtext

    # line-wrap the rows (in future we'll have speaking and non-speaking rows)
    while len(rows[-1][1]) > 3:
        rows.append([ "", rows[-1][1][3:] ])
        del rows[-2][1][3:]

    print '<div class="council-attendees" id="%s">' % gid
    print '<table>'
    for rowlab, rowcont in rows:
        print '<tr>'
        print '<th>%s</th>' % rowlab
        for name, nation in rowcont:
            hrefflag = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":nation})
            print '<td><img class="smallflag_sca" src="%s"></td>' % hrefflag,
            hrefname = EncodeHref({"pagefunc":"nationperson", "nation":nation, "person":name})
            print '<td><a class="name" href="%s">%s</a>' % (hrefname, name),
            print '<br>'
            hrefnation = EncodeHref({"pagefunc":"nation", "nation":nation})
            print '<a class="nation" href="%s">%s</a></td>' % (hrefnation, nation)
        if rowlab == "President:":
            print '<td></td>'
            print '<td colspan="3">(The Presidency changes each month to the next member in alphabetical order)</td>'
        print '</tr>'
    print '</table>'
    print '</div>'
    return res

# convert paragraphs to less damaging spans (keeping the ids that might be marking them)
def WriteItalicLine(gid, dclass, dtext):
    print '<div class="act" id="%s">' % gid # dclass
    print re.sub("<(/?)p([^>]*)>", "<\\1span\\2>", dtext)
    print '</div>'

# this creates the data that the javascript can look up
def WriteDataHeading(gid, dtext):
    mdata = re.search('<span class="code">([^<]*)</span>\s*<span class="date">([^<]*)</span>\s*<span class="time">([^<]*)</span>', dtext)
    print '<div class="cdocattr" id="%s">' % gid  # always pg000-bk00
    print '<span class="docid">%s</span>' % mdata.group(1)
    sdate = mdata.group(2)
    print '<span class="date">%s</span>' % sdate
    print '<span class="time">%s</span>' % mdata.group(3)
    ndate = int(sdate[8:10])
    nmonth = int(sdate[5:7])
    longdate = '%d %s %s' % (ndate, monthnames[nmonth - 1], sdate[:4])
    print '<span class="longdate">%s</span>' % longdate
    print '<span class="wikidate">[[%d %s]] [[%s]]</span>' % (ndate, monthnames[nmonth - 1], sdate[:4])
    print '<span class="basehref">%s</span>' % "/" # XXX is this needed any more in the js?
    print '</div>'
    return longdate

def WritePrevNext(pdfinfo, gadice):
    if not pdfinfo.prevmeetingdetails and not pdfinfo.nextmeetingdetails:
        return
    #print '<div class="prevnexmeeting">'
    #thislink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.pdfc})
    #print '<p><a href="%s">This meeting held on %s from %s to %s</a></p>' % (pdfinfo.sdate, pdfinfo.time, pdfinfo.rosetime)
    print '<table>'
    print '<tr class="meeting-date"><th>Date</th><td><b>%s</b></td></tr>' % LongDate(pdfinfo.sdate)
    if not gadice:
        print '<tr class="meeting-time"><th>Started</th><td>%s</td></tr>' % pdfinfo.time
        print '<tr class="meeting-rosetime"><th>Ended</th><td>%s</td></tr>' % pdfinfo.rosetime
    print '</table>'

    
    if not (pdfinfo.prevmeetingdetails or pdfinfo.nextmeetingdetails or gadice):
        return
    
    print '<ul>'
    if gadice:
        currlink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.pdfc, "gid":gadice})
        print '<li><a href="%s" title="Full meeting"><b>Full meeting</b></a></li>' % currlink
    if not gadice and pdfinfo.prevmeetingdetails:
        prevlink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.prevmeetingdetails[0]})
        print '<li><a href="%s" title="Previous meeting: finished %s %s">Previous meeting</a></li>' % (prevlink, pdfinfo.prevmeetingdetails[1], pdfinfo.prevmeetingdetails[2])
    if not gadice and pdfinfo.nextmeetingdetails:
        nextlink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.nextmeetingdetails[0]})
        print '<li><a href="%s" title="Next meeting: started %s %s">Next meeting</a></li>' % (nextlink, pdfinfo.nextmeetingdetails[1], pdfinfo.nextmeetingdetails[2])
    webcastlink = WebcastLink(pdfinfo.bSC and "securitycouncil" or "generalassembly", pdfinfo.sdate)
    if webcastlink:
        print '<li><a href="%s" title="Goto entry in list of webcasts">Webcast Video</a></li>' % (webcastlink)
    
    print '<li>&nbsp;</li>'
    if pdfinfo.bGA:
        print '<li><a href="%s">Entire session</a></li>' % (EncodeHref({"pagefunc":"gasession", "gasession":pdfinfo.nsess}))
    if pdfinfo.bSC:
        print '<li><a href="/securitycouncil">All meetings</a></li>'

    print '</ul>'


def WriteInstructions():
    print """<div id="metainstructions">
             <h3>Instructions</h3>
             <p><b>Click</b> on the <span class="unclickedlink">Link to this</span> button beside the speech or 
             paragraph to expand it to a useful panel 
             containing: 
             <ul>
             <li>The date of the speech</li>
             <li>A link to the original page of the PDF document</li>
             <li>A URL that can be used in most blogs</li>
             <li>A structured <a href="http://en.wikipedia.org/wiki/Template:UN_document#Usage">Citation template</a> 
             suitable for use in a Wikipedia article.</li>
             </ul>
             <p><b>Those</b> last two rows ("URL" and "wiki") use textboxes to hide most of the text.</p>

             <p class="secline"><b>To access</b> this text, right-click in the textbox with your mouse and choose "Select All", 
             then right-click again and choose "Copy".  
             Now you can right-click into another window and choose 
             "Paste" to get the text.</p>
             </div>"""


rdivspl = '<div class="([^"]*)"(?: id="([^"]*)")?(?: agendanum="([^"]*)")?>(.*?)</div>(?s)'


def WriteHTML(fhtml, pdfinfo, gadice, highlightth):
    WriteGenHTMLhead(pdfinfo.desc)  # this will be the place the date gets extracted from
    print '<div style="display: none;"><img id="hrefimg" src="" alt=""></div>'
    #print '<input id="hrefimgi">%s</input>' % gadice
    print '<script type="text/javascript">document.getElementById("hrefimg").src = HrefImgReport(location.href);</script>'

    agnums = gadice and pdfinfo.GetAgnum(gadice) or ""

    resurl, reswref = GenWDocLink(pdfinfo, None, None)
    print '<div id="upperdoclinks">'
    print '</div>'

    print '<div id="meta">'
   # print gadice, agnums
    WritePrevNext(pdfinfo, gadice)
    
    print '<div id="metadoclinks">'
    print '<h3>Links for full page</h3>'
    print '<p><span class="linktabfleft">URL:</span> <input style="text" readonly value="%s"></p>' % resurl
    print '<p><span class="linktabfleft"><a href="http://en.wikipedia.org/wiki/Help:Footnotes">wiki:</a></span>' 
    print '<input style="text" readonly value="%s"></p>' % reswref
    print '</div>'

    WriteInstructions()
    print '</div>'
    print '<div id="documentwrap">'

    if False and gadice and agnums:
        for agnum in agnums.split(","):
            aglist = LoadAgendaNames(agnum)
            print '<table class="agendatable">'
            print '<caption>agenda %s</caption>' % agnum
            for agrecord in aglist:
                print '<tr><td>'
                if (agrecord.docid, agrecord.gid) != (pdfinfo.pdfc, gadice):
                    href = EncodeHref({"pagefunc":"meeting", "docid":agrecord.docid, "gadice":agrecord.gid})
                    print '%s <a href="%s">%s</a>' % (agrecord.sdate, href, agrecord.agtitle)
                else:
                    print '%s %s' % (agrecord.sdate, agrecord.agtitle)
                print '</td></tr>'
            print '</table>'

    fin = open(fhtml)
    ftext = fin.read().decode('latin-1')
    fin.close()
    councilpresidentnation = None  # gets set if we have a council-attendees

    agendanumcurrent = ""
    agendagidcurrent = ""
    for mdiv in re.finditer(rdivspl, ftext):
        dclass, gid, agendanum = mdiv.group(1), mdiv.group(2), mdiv.group(3)
        dtext = mdiv.group(4).strip()
        dtextmu = MarkupLinks(dtext, highlightth)
        if dclass == "spoken":
            if not gadice or agendagidcurrent == gadice:
                WriteSpoken(gid, dtextmu, councilpresidentnation)
        elif dclass == "subheading":
            if agendagidcurrent and (not gadice or agendagidcurrent == gadice):
                print '</div>\n\n'
            agendagidcurrent = gid
            if agendagidcurrent and (not gadice or agendagidcurrent == gadice):
                print '<div class="discussion">'
            if not gadice or agendagidcurrent == gadice:
                WriteAgenda(gid, agendanum, dtextmu, pdfinfo.pdfc)
        elif dclass == "recvote":
            if not gadice or agendagidcurrent == gadice:
                WriteVote(gid, dtextmu, pdfinfo.bSC)
        elif dclass == 'heading':
            longdate = WriteDataHeading(gid, dtext)
        elif dclass == "assembly-chairs":
            if not gadice:
                WriteAssemblyChair(gid, dtextmu)
        elif dclass == "council-attendees":
            councilpresidentnation = WriteCouncilAttendees(gid, dtext)  # value used to dereference "The President" in the Security Council
        elif dclass == "council-agenda":
            print '<div class="%s" id="%s">' % (dclass, gid)
            print dtextmu
            print '</div>'

        elif re.match("italicline", dclass):
            if not gadice or agendagidcurrent == gadice:
                WriteItalicLine(gid, dclass, dtextmu)
        else:  # all cases should have been handled
            print '<div class="%s" id="%s">' % (dclass, gid)
            print dtext, '</div>'
    if agendagidcurrent and (not gadice or agendagidcurrent == gadice):
        print '</div>'
    print '</div>'

def WriteHTMLagnum(agnum, aglist):
    WriteGenHTMLhead("Unrolled: " + aglist[0].aggrouptitle)
    print '<h3><a href="%s">Rolled back up agenda</a></h3><p></p>' % EncodeHref({"pagefunc":"agendanum", "agendanum":agnum})

    prevfhtml = ""
    for agrecord in aglist:
        if agrecord.fhtml == prevfhtml: # avoid repeating the same document more than once when agendas get re-opened
            continue
        prevfhtml = agrecord.fhtml

        fin = open(agrecord.fhtml)
        ftext = fin.read()
        fin.close()
        
        print '<h1>%s</h1>' % agrecord.sdate
        agendanumcurrent = ""
        #continue
        for mdiv in re.finditer(rdivspl, ftext):
            dclass, gid, agendanum = mdiv.group(1), mdiv.group(2), mdiv.group(3)
            stext = mdiv.group(4).strip()
            if dclass == "assembly-chairs":
                WriteAssemblyChair(gid, ftext)   # could always use this for doing the date band
                continue   
            if dclass == "heading":
                continue   # wot are we going to do about this? needs numbers for the javascript links

            if dclass == "subheading":
                agendanumcurrent = agendanum   # this would do some kind of folding down or up when we get there
            if agnum != agendanumcurrent:
                continue   # only printing that which is in this agenda 
            
            dtext = MarkupLinks(stext, "")
            if dclass == "subheading":
                WriteAgendaFlipped(gid, agendanum, dtext, agrecord.docid)
            elif dclass == "spoken": 
                WriteSpoken("", dtext, "")
            elif dclass == "recvote":
                WriteVote("", dtext, False)
            elif re.match("italicline", dclass):
                WriteItalicLine("", dclass, dtext)
            elif dclass == "end-document":
                pass
            else:
                print '<div>UNEXPECTED Class %s</div>' % dclass

