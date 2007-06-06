import os
import sys
import re


currentgasession = 61
currentscyear = 2007
basehref = "http://staging.undemocracy.com/"

# dereferencing for hackability
# this is a very brutal system for breaking it down
def DecodeHref(pathparts, searchvalue):
    if searchvalue:  # may have option to search by country
        return { "pagefunc": "search", "searchvalue": searchvalue }
    if len(pathparts) == 0:
        return { "pagefunc": "front" }

    if pathparts[0] == "generalassembly":
        if len(pathparts) < 2:
            return { "pagefunc": "fronterror" }
        if pathparts[1] == "topicn":
            if len(pathparts) < 3:
                return { "pagefunc": "fronterror" }
            return { "pagefunc": "agendanum", "agendanum":pathparts[2] }
        if not re.match("\d\d$", pathparts[1]):
            return { "pagefunc": "fronterror" }
        nsess = int(pathparts[1])
        if not 49 <= nsess <= currentgasession:
            return { "pagefunc": "fronterror" }
        if len(pathparts) == 2:
            return { "pagefunc": "gasession", "gasession":nsess }
        if pathparts[2] == "topicn":
            if len(pathparts) < 4:
                return { "pagefunc": "fronterror" }
            # agenda num should in theory match session number
            return { "pagefunc": "agendanum", "agendanum":pathparts[3] }
        if pathparts[2] == "documents":
            return { "pagefunc": "fronterror" }  # selected docs for this session (not done yet)
        return { "pagefunc": "fronterror" }

    if pathparts[0] == "securitycouncil":
        if len(pathparts) < 2:
            return { "pagefunc":"sctopics" }
        if not re.match("\d\d\d\d$", pathparts[1]):
            return { "pagefunc":"fronterror" }
        nyear = int(pathparts[1])
        if not 1994 <= nyear <= currentscyear:
            return { "pagefunc":"fronterror" }
        if len(pathparts) == 2:
            return { "pagefunc":"scyear", "scyear":nyear }
        if pathparts[2] == "documents":
            return { "pagefunc":"fronterror" }  # selected docs for this year (not done yet)
        return { "pagefunc":"fronterror" }

    # might be able to lose the "nation" thing as well
    if pathparts[0] == "nation":
        if len(pathparts) < 2:
            # should be list of nations
            return { "pagefunc": "fronterror" }
        nation = pathparts[1]  # to demunge and match
        return { "pagefunc": "nation", "nation":nation }

    # avoid the superfluous "document" leader
    if re.match("[AS]-", pathparts[0]):
        docid = pathparts[0]
        if len(pathparts) == 1:
            return { "pagefunc":"document", "docid":docid }
        mpage = re.match("page(d+)$", pathparts[1])
        if mpage:
            npage = int(mpage.group(1))
            if len(pathparts) >= 3 and pathparts[2] == "highlight" or pathparts[2] == "highlightedit":
                highlights = len(pathparts) >= 4 and pathparts[3] or ""
                return { "pagefunc":"documentpage", "docid":docid, "page":npage, "highlights":highlights, "highlightedit":(pathparts[2] == "highlightedit") }
            return { "pagefunc":"documentpage", "docid":docid, "page":npage, "highlights":"", "highlightedit":False }
        return { "pagefunc":"document", "docid":docid }

    return { "pagefunc": "fronterror" }

def EncodeHref(hmap):
    if hmap["pagefunc"] == "front":
        return "%s" % basehref
    if hmap["pagefunc"] == "document":
        return "%s/%s" % (basehref, hmap["docid"])
    if hmap["pagefunc"] == "documentpage":
        if hmap["highlightedit"]:
            return "%s/%s/page%d/highlightedit/%s" % (basehref, hmap["docid"], hmap["page"], hmap["highlights"])
        if hmap["highlights"]:
            return "%s/%s/page%d/highlight/%s" % (basehref, hmap["docid"], hmap["page"], hmap["highlights"])
        return "%s/%s/page%d" % (basehref, hmap["docid"], hmap["page"])
    if hmap["pagefunc"] == "gasession":
        return "%s/generalassembly/%s" % (basehref, hmap["gasession"])
    if hmap["pagefunc"] == "sctopics":
        return "%s/securitycouncil" % (basehref)
    if hmap["pagefunc"] == "scyear":
        return "%s/securitycouncil/%d" % (basehref, hmap["scyear"])
    if hmap["pagefunc"] == "agendanum":
        magnum = re.match("[^\-]*-(\d\d)$", hmap["agendanum"])
        if magnum:
            return "%s/generalassembly/%s/topicn/%s" % (basehref, magnum.group(1), hmap["agendanum"])
        return "%s/topicn/%s" % (basehref, hmap["agendanum"])



htmldir = '/home/undemocracy/undata/html'
pdfdir = '/home/undemocracy/undata/pdf'
pdfinfodir = '/home/undemocracy/undata/pdfinfo'
pdfpreviewdir = '/home/undemocracy/undata/pdfpreview'
pdfpreviewpagedir = '/home/undemocracy/undata/pdfpreviewpage'
indexstuffdir = '/home/undemocracy/undata/indexstuff'

def WriteGenHTMLhead(title):
    print "Content-Type: text/html\n"
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
    print '<html>'
    print '<head>'
    print '<title>JGT backup site</title>'
    print '<link href="%s/unview.css" type="text/css" rel="stylesheet" media="all">' % basehref
    print '<script language="JavaScript" type="text/javascript" src="%s/unjava.js"></script>' % basehref
    print '</head>'
    print '<body>'
    print '<h1 class="tophead">UNdemocracy.com</h1>'
    print '<h1 class="topheadspec">%s</h1>' % title

def GetFcodes(code):
    scode = re.sub("/", "-", code)
    scode = re.sub("\.html$|\.pdf$", "", scode)

    fhtml = os.path.join(htmldir, scode + ".html")
    if not os.path.isfile(fhtml):  # only use unindexed types during development, since no searcher is running
        fhtml = ""

    fpdf = os.path.join(pdfdir, scode + ".pdf")
    if not os.path.isfile(fpdf):
        fpdf = ""

    return fhtml, fpdf

monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]



