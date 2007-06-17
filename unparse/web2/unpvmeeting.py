#!/usr/bin/python


import sys, os, stat, re
import datetime
import urllib
from basicbits import WriteGenHTMLhead, EncodeHref, monthnames


# more efficient to print out as we go through
def MarkupLinks(ftext, highlightdoclink):
    res = [ ]
    for ft in re.split('(<a href="../pdf/[^"]*?\.pdf"[^>]*>)', ftext):
        ma = re.match('<a href="../pdf/([^"]*?)\.pdf"([^>]*)>', ft)
        if ma:
            res.append('<a href="%s"' % (EncodeHref({"pagefunc":"document", "docid":ma.group(1)})))
            if highlightdoclink and ma.group(1) == highlightdoclink:
                res.append(' class="highlight"')
            else:
                res.append(ma.group(2))
            res.append('>')
        else:
            res.append(ft)
    return "".join(res)


def WriteSpoken(gid, dtext, councilpresidentnation):
    print '<div class="spoken" id="%s">' % gid
    mspek = re.search('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(nation|non-nation)">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>', dtext)
    assert mspek, dtext[:200]
    name, nationtype, nation, language = mspek.group(1), mspek.group(2), mspek.group(3), mspek.group(4)
    print '<h3 class="speaker">',
    print '<div onclick="linkere(this);" class="unclickedlink">link to this</div>',

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

def WriteAgenda(gid, agnum, dtext):
    print '<div class="subheading" id="%s">' % gid
    print '<div onclick="linkere(this);" class="unclickedlink">link to this</div>'
    if agnum:
        print '<div class="otheraglink"><a href="%s">Other discussions<br>on this topic</a></div>' % EncodeHref({"pagefunc":"agendanum", "agendanum":agnum})
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

    print '<div onclick="linkere(this);" class="unclickedlink">link to this</div>'

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
    print '<div class="%s">' % dclass
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



def WriteHTML(fhtml, pdfinfo, highlightdoclink):
    WriteGenHTMLhead(pdfinfo.desc)  # this will be the place the date gets extracted from
    print '<div style="display: none;"><img id="hrefimg"></div>'
    #print '<input id="hrefimgi"></input>'
    print '<script type="text/javascript">document.getElementById("hrefimg").src = HrefImgReport(location.href);</script>'
    WritePrevNext(pdfinfo)

    fin = open(fhtml)
    ftext = fin.read()
    fin.close()
    councilpresidentnation = None  # gets set if we have a council-attendees

    # TODO: Make highlightdoclink work for search results

    for mdiv in re.finditer('<div class="([^"]*)"(?: id="([^"]*)")?(?: agendanum="([^"]*)")?>(.*?)</div>(?s)', ftext):
        dclass = mdiv.group(1)
        gid = mdiv.group(2)
        agendanum = mdiv.group(3)
        dtext = MarkupLinks(mdiv.group(4).strip(), highlightdoclink)
        if dclass == "spoken":
            WriteSpoken(gid, dtext, councilpresidentnation)
        elif dclass == "subheading":
            WriteAgenda(gid, agendanum, dtext)
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
            print dtext

    #print '<div id="footer">'
    #print 'Footer'
    #print '</div>'

