#!/usr/bin/python


import sys, os, stat, re
import datetime
import urllib
from basicbits import WriteGenHTMLhead, EncodeHref, monthnames
from indexrecords import LoadAgendaNames

# more efficient to print out as we go through
rpdlk = '<a href="../pdf/[^"]*?\.pdf"[^>]*>'
rpdlkp = '<a href="../pdf/([^"]*?)\.pdf"([^>]*)>'
def MarkupLinks(ftext, highlights):
    res = [ ]
    if highlights[1]:
        rspl = '(%s|%s)' % (rpdlk, highlights[1])
    else:
        rspl = '(%s)' % rpdlk
    for ft in re.split(rspl, ftext):
        ma = re.match(rpdlkp, ft)
        if ma:
            res.append('<a href="%s"' % (EncodeHref({"pagefunc":"document", "docid":ma.group(1)})))
            if highlights[0] and ma.group(1) == highlights[0]:
                res.append(' class="highlight"')
            res.append(ma.group(2))
            res.append('>')
        elif highlights[1] and re.match(highlights[1], ft):
            res.append('<span class="search-highlight">')
            res.append(ft)
            res.append('</span>')
        else:
            res.append(ft)
    return "".join(res)


def WriteSpoken(gid, dtext, councilpresidentnation):
    print '<div class="spoken" id="%s">' % gid
    mspek = re.search('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(nation|non-nation)">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>', dtext)
    assert mspek, dtext[:200]
    name, nationtype, nation, language = mspek.group(1), mspek.group(2), mspek.group(3), mspek.group(4)
    print '<h3 class="speaker">',


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
        if re.match("The Secretary-General", name):
            flagnation = "United Nations"
            nation = name
        elif not councilpresidentnation and re.match("The(?: Acting)? President", name):
            flagnation = "%s of the General Assembly" % name
        else:
            flagnation = "Unknown"
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
    print '</h3>'

    print dtext[mspek.end(0):]

    print '</div>'

def WriteAgenda(gid, agnum, dtext, docid):
    print '<div class="discussion" id="%s">' % gid
    if agnum:
        lkothdisc = '<a href="%s">Other discussions<br>on this topic</a>' % EncodeHref({"pagefunc":"agendanum", "agendanum":agnum})
        flippedhcode = '%s_%s' % (docid, gid)
        lkflipagenda = '<a href="%s#%s">Flip</a>' % (EncodeHref({"pagefunc":"agendanumexpanded", "agendanum":agnum}), flippedhcode)
        print '<div class="otheraglink">%s %s</div>' % (lkothdisc, lkflipagenda)
    
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
        print '</tr>'
    print '</table>'
    print '</div>'
    return res

# convert paragraphs to less damaging spans (keeping the ids that might be marking them)
def WriteItalicLine(gid, dclass, dtext):
    print '<div class="event" id="%s">' % gid # dclass
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

def WritePrevNext(pdfinfo):
    if not pdfinfo.prevmeetingdetails and not pdfinfo.nextmeetingdetails:
        return
    print '<table class="prevnextmeeting">'
    print '<tr>'
    if pdfinfo.prevmeetingdetails:
        prevlink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.prevmeetingdetails[0]})
        print '<td><a href="%s">Previous meeting<br>finished %s %s</a></td>' % (prevlink, pdfinfo.prevmeetingdetails[1], pdfinfo.prevmeetingdetails[2])
    else:
        print '<td></td>'
    thislink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.pdfc})
    print '<td><a href="%s">This meeting on %s from %s to %s</a></td>' % (thislink, pdfinfo.sdate, pdfinfo.time, pdfinfo.rosetime)
    if pdfinfo.nextmeetingdetails:
        nextlink = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.nextmeetingdetails[0]})
        print '<td><a href="%s">Next meeting started %s %s</a></td>' % (nextlink, pdfinfo.nextmeetingdetails[1], pdfinfo.nextmeetingdetails[2])
    else:
        print '<td></td>'
    print '</table>'




rdivspl = '<div class="([^"]*)"(?: id="([^"]*)")?(?: agendanum="([^"]*)")?>(.*?)</div>(?s)'


def WriteHTML(fhtml, pdfinfo, highlightth):
    WriteGenHTMLhead(pdfinfo.desc)  # this will be the place the date gets extracted from
    print '<div style="display: none;"><img id="hrefimg"></div>'
    #print '<input id="hrefimgi"></input>'
    print '<script type="text/javascript">document.getElementById("hrefimg").src = HrefImgReport(location.href);</script>'
    WritePrevNext(pdfinfo)

    fin = open(fhtml)
    ftext = fin.read()
    fin.close()
    councilpresidentnation = None  # gets set if we have a council-attendees

    if not highlightth:
        highlights = ("", "")
    elif re.match("[AS]-", highlightth):
        highlights = (highlightth, "")
    else:
        hls = [ hl.lower()  for hl in highlightth.split()  if hl ]
        if hls:
            rhls = [ ]
            for hl in hls:
                if rhls:
                    rhls.append('|')
                rhls.append(hl)
                rhls.append('(?![a-z])')
            rhls.append('(?i)')
            highlights = ("", "".join(rhls))
        else:
            highlights = ("", "")

    for mdiv in re.finditer(rdivspl, ftext):
        dclass, gid, agendanum = mdiv.group(1), mdiv.group(2), mdiv.group(3)
        dtext = MarkupLinks(mdiv.group(4).strip(), highlights)
        if dclass == "spoken":
            WriteSpoken(gid, dtext, councilpresidentnation)
        elif dclass == "subheading":
            WriteAgenda(gid, agendanum, dtext, pdfinfo.pdfc)
        elif dclass == "recvote":
            WriteVote(gid, dtext, pdfinfo.bSC)
        elif dclass == 'heading':
            longdate = WriteDataHeading(gid, dtext)
        elif dclass == "assembly-chairs":
            WriteAssemblyChair(gid, dtext)
        elif dclass == "council-attendees":
            councilpresidentnation = WriteCouncilAttendees(gid, dtext)  # value used to dereference "The President" in the Security Council
        elif re.match("italicline", dclass):
            WriteItalicLine(gid, dclass, dtext)
        else:  # all cases should have been handled
            print '<div class="%s" id="%s">' % (dclass, gid)
            print dtext, '</div>'


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

