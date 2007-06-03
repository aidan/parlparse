#!/usr/bin/python

# this is the start of a cgi script that will view the html files we've got
# it works on seagrass and should be able to be hosted anywhere because it
# references to the data files using absolute paths

import sys, os, stat, re
import cgi, cgitb
import datetime
import urllib
cgitb.enable()

from basicbits import WriteGenHTMLhead, GetFcodes
from basicbits import basehref, htmldir, pdfdir, pdfinfodir

sys.path.append('/home/undemocracy/unparse/scraper')
from pdfinfo import PdfInfo 

from pdfview import WritePDF, WritePDFpreview, WritePDFpreviewpage
from indextype import WriteFrontPage, WriteIndexStuff, WriteIndexStuffSec, WriteIndexStuffSecYear, WriteIndexStuffAgnum, WriteIndexStuffNation, WriteIndexSearch


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
    if not flagnation and bGA and re.match("The President$", name):
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

    print dtext
    print '</div>'

def WriteHTML(fhtml, pdfinfo, highlightdoclink):
    WriteGenHTMLhead(pdfinfo.desc)

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
        else: #dclass == "assembly-chairs":
            print '<div class="%s" id="%s">' % (dclass, gid)
            if re.match("assembly|italicline", dclass):
                dtext = re.sub('</?p[^>]*>', ' ', dtext)
                dtext = re.sub('class="([^"]*)"', 'class="\\1chair"', dtext)
            print dtext
            print '</div>'



# the main section that interprets the fields
if __name__ == "__main__":
    form = cgi.FieldStorage()

    code = form.has_key("code") and form["code"].value or ""
    pdfpage = form.has_key("pdfpage") and form["pdfpage"].value or ""
    search = form.has_key("search") and form["search"].value or ""


    if not code:
        nation = form.has_key("nation") and form["nation"].value or ""
        agnum = form.has_key("agnum") and form["agnum"].value or ""
        sess = form.has_key("sess") and form["sess"].value or ""
        if search:
            bsucc = WriteIndexSearch(search)
        elif nation:
            bsucc = WriteIndexStuffNation(nation)
        elif agnum:
            bsucc = WriteIndexStuffAgnum(agnum)
        elif sess:
            if sess[:2] == "sc":
                scyear = sess[2:]
                if scyear:
                    bsucc = WriteIndexStuffSecYear(scyear)
                else:
                    bsucc = WriteIndexStuffSec()
            else:
                bsucc = WriteIndexStuff(sess)
        else:
            bsucc = WriteFrontPage()
        if not bsucc:
            WriteGenHTMLhead("Bad data")

    else:
        fhtml, fpdf = GetFcodes(code)
        pdfinfo = PdfInfo(code)
        pdfinfo.UpdateInfo(pdfinfodir)

        if fhtml and not pdfpage:
            highlightdoclink = form.has_key("highlightdoclink") and form["highlightdoclink"].value or ""
            WriteHTML(fhtml, pdfinfo, highlightdoclink)
        elif pdfpage == "inline":
            WritePDF(fpdf)
        elif re.match("\d+$", pdfpage):
            WritePDFpreviewpage(basehref, pdfinfo, int(pdfpage))
        elif fpdf:
            WritePDFpreview(basehref, pdfinfo)
        else:
            WriteNotfound(code)

    print "</body>"
    print '</html>'


