#!/usr/bin/python


import sys, os, stat, re
import datetime
import urllib

def WriteNotfound(code):
    WriteGenHTMLhead("not found")
    a, b = GetFcodes(code)
    print "<h2>:: %s</h2>" % code
    print "<h2>--%s-- --%s--</h2>" % (a, b)


# more efficient to print out as we go through
def MarkupLinks(ftext, highlightdoclink):
    res = [ ]
    for ft in re.split('(<a href="../pdf/[^"]*?\.pdf"[^>]*>)', ftext):
        ma = re.match('<a href="../pdf/([^"]*?)\.pdf"([^>]*)>', ft)
        if ma:
            res.append('<a href="%s?code=%s&pdfpage=all"' % (basehref, ma.group(1)))
            if highlightdoclink and ma.group(1) == highlightdoclink:
                res.append(' class="highlight"')
            else:
                res.append(ma.group(2))
            res.append('>')
        else:
            res.append(ft)
    return "".join(res)


def WriteSpoken(gid, dtext, bGA):
    print '<div class="spoken" id="%s">' % gid
    mspek = re.search('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(nation|non-nation)">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>', dtext)
    assert mspek, dtext[:200]
    name, nationtype, nation, language = mspek.group(1), mspek.group(2), mspek.group(3), mspek.group(4)
    print '<h3 class="speaker">',
    print '<div onclick="linkere(this);" class="unclickedlink">link to this</div>',

    flagnation = nation
    if flagnation and re.match("United Nations", flagnation):
        flagnation = "United Nations"
    if not flagnation and re.match("The Secretary-General$", name):
        flagnation = "United Nations"
    if not flagnation and bGA and re.match("The(?: Acting)? President$", name):
        flagnation = "United Nations"

    if flagnation:
        flagimg = '../flagimg100/Flag_of_' + re.sub(" ", "_", flagnation) + ".png"
        if os.path.isfile(flagimg):
            print '<img class="smallflag" src="%s">' % flagimg,
    print '<span class="name">%s</span>' % name,
    if nation:
        print '<a class="nation" href="%s?nation=%s">%s</a>' % (basehref, urllib.quote(nation), nation)
    print '</h3>'

    print dtext[mspek.end(0):]

    print '</div>'

def WriteAgenda(gid, agnum, dtext):
    print '<div class="subheading" id="%s">' % gid
    print '<div onclick="linkere(this);" class="unclickedlink">link to this</div>'
    if agnum:
        print '<div class="otheraglink"><a href="%s?agnum=%s&highlightag=%s">Other discussions<br>on this topic</a></div>' % (basehref, agnum, gid)
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


def WriteAssemblyChair(dclass, gid, dtext):
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
    print '</div>'
    return longdate

def WriteHTML(fhtml, pdfinfo, highlightdoclink):
    WriteGenHTMLhead(pdfinfo.desc)  # this will be the place the date gets extracted from

    fin = open(fhtml)
    ftext = fin.read()
    fin.close()

    for mdiv in re.finditer('<div class="([^"]*)"(?: id="([^"]*)")?(?: agendanum="([^"]*)")?>(.*?)</div>(?s)', ftext):
        dclass = mdiv.group(1)
        gid = mdiv.group(2)
        agendanum = mdiv.group(3)
        dtext = MarkupLinks(mdiv.group(4).strip(), highlightdoclink)
        if dclass == "spoken":
            WriteSpoken(gid, dtext, pdfinfo.bGA)
        elif dclass == "subheading":
            WriteAgenda(gid, agendanum, dtext)
        elif dclass == "recvote":
            WriteVote(gid, dtext, pdfinfo.bSC)
        elif dclass == 'heading':
            longdate = WriteDataHeading(gid, dtext)
        elif dclass == "assembly-chairs":
            WriteAssemblyChair(dclass, gid, dtext)
        else: #dclass == "assembly-chairs":
            print '<div class="%s" id="%s">' % (dclass, gid)
            if re.match("assembly|italicline", dclass):
                dtext = re.sub('</?p[^>]*>', ' ', dtext)
                dtext = re.sub('class="([^"]*)"', 'class="\\1chair"', dtext)
            print dtext
            print '</div>'

