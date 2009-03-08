import os
import sys
import re
import cgi

indexstuffdir = "/home/undemocracy/undata/indexstuff"

from pdfinfo import PdfInfo
from downascii import DownAscii
import datetime

sys.path.append("../pylib")
from config import *  # this must bring in htmldir

nowdatetime = datetime.datetime.now().strftime("%Y-%m-%d;%H:%M")
currentgasession = 63
currentscyear = datetime.datetime.now().year  #2007
basehref = "http://www.undemocracy.com"

scpermanentmembers = ["China", "France", "Russia", "United Kingdom", "United States"]
scelectedmembersyear = { 
2007:["Belgium", "Congo", "Ghana", "Indonesia", "Italy", "Panama", "Peru", "Qatar", "Slovakia", "South Africa"],
2008:["Burkina Faso", "Libya", "South Africa", "Vietnam", "Indonesia", "Costa Rica", "Panama", "Belgium", "Italy", "Croatia"],
}

monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def LongDate(sdate):
    nmonth = int(sdate[5:7])
    return "%d %s %s" % (int(sdate[8:]), monthnames[nmonth - 1], sdate[:4])

def LongDateNB(sdate):
    nmonth = int(sdate[5:7])
    return "%d&nbsp;%s&nbsp;%s" % (int(sdate[8:]), monthnames[nmonth - 1], sdate[:4])

bodyid = None
def SetBodyID(lbodyid):
    global bodyid
    bodyid = lbodyid

def WriteGenHTMLhead(title, frontpage=False):
    print "Content-Type: text/html\n"
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
    print '<html>'
    print '<head>'
    print '<meta http-equiv="content-type" content="text/html; charset=iso-8859-1">'
    print '<title>UNdemocracy - %s</title>' % cgi.escape(title)
    print '<link href="/unview.css" type="text/css" rel="stylesheet" media="all">'
    yuibase = 'http://yui.yahooapis.com/2.3.1'
    yuibase = '/yui/2.3.1'
    print '<script type="text/javascript" src="%s/build/yahoo/yahoo-min.js"></script>' % yuibase
    print '<script type="text/javascript" src="%s/build/dom/dom-min.js"></script>' % yuibase
    print '<script type="text/javascript" src="%s/build/event/event-min.js"></script>' % yuibase
    print '<script language="JavaScript" type="text/javascript" src="/unjava.js"></script>'
    print '</head>'
    print '<body id="%s">' % bodyid

    if os.getenv("HTTP_HOST") != 'www.undemocracy.com':
        if os.getenv("HTTP_HOST") != 'local.undemocracy.com':
            print '''<p style="color:red"><strong>This is a test site - the real site is <a href="http://www.undemocracy.com">over here</a>.</strong> Developers are busy making UNdemocracy better using this page. %s</p>''' % os.getenv("HTTP_HOST")

    print '<div id="identity">'
    if not frontpage:
        print '<a href="/">'
    #print '<img src="/images/site/logobeta.gif" alt="UNdemocracy.com">'
    print '<img src="/images/site/logobetaw.png" alt="UNdemocracy.com">'
    if not frontpage:
        print '</a>'
    print '</div>'
    if not frontpage:
        print '<h1>%s</h1>' % cgi.escape(title)
    else:
        print '<div id="bigsearch">'
        #print '<a href="/nations">List all nations</a>'
        print '<form action="/" method="get">'
        #print '<p>'
        print '<input type="text" name="search">'
        print '<button>Search</button>'
        print '</form>'
        print '<a href="#aboutfooter">About us</a>&nbsp;&nbsp;&nbsp;'
        print '<a href="/nations">List of all nations</a>'
        print '</div>'
    print '<div id="content">'
    #print os.environ

def WriteGenHTMLfoot():
    print '</div>'
    print '<div style="background-color:black;clear:both; color:white; text-align:center">'
    print '<a href="http://project.knowledgeforge.net/ukparse/svn/trunk/unparse/" style="color:#55ffff">Source Code</a>'
    print 'of undemocracy.com protected by <a href="http://www.fsf.org/licensing/licenses/agpl-3.0.html" style="color:#55ffff">AGPL</a>'
    print '<a href="http://okd.okfn.org/"><img src="http://www.publicwhip.org.uk/images/ok_80x23_red_green.png" style="vertical-align:bottom" alt="Open Knowledge"></a></div>'
    print "</body>"
    print '</html>'


def GetPdfInfo(docid):
    res = PdfInfo(docid)
    res.UpdateInfo(pdfinfodir)
    if re.match("A-\d+-PV|S-PV", docid):
        res.htmlfile = os.path.join(htmldir, docid + ".html")
    else:
        res.htmlfile = ""
    res.pdffile = os.path.join(pdfdir, docid + ".pdf")
    return res


def LookupAgendaTitle(docid, gid, c):
    if re.match("S", docid):
        c.execute("SELECT shortheading, ldate FROM un_scheadings WHERE docid='%s'" % docid)
        a = c.fetchone()
        if a:
            return a[0], a[1]

    pdfinfo = GetPdfInfo(docid)
    prevagc = None
    for agc in pdfinfo.agendascontained:
        if agc[0] > gid:
            break
        prevagc = agc
    if not prevagc:
        return None, pdfinfo.sdate
    return prevagc[2], pdfinfo.sdate  # the title


def LogIncomingDoc(docid, page, referrer, ipaddress, useragent):
    lua = re.sub("\s", "_", useragent or "empty")
    logtxt = "docpage = %s %s %s %s %s %s\n" % (docid, page, (referrer or "None"), ipaddress, nowdatetime, lua)

    # log according to user agent
    if re.search("google", useragent):
        fflog = "logpages_google.txt"
    elif re.search("picsearch", useragent):
        fflog = "logpages_picsearch.txt"
    elif re.search("search.msnbot|search.msn.com/msnbot", useragent):
        fflog = "logpages_msn.txt"
    elif re.search("cuill.*?robot", useragent):
        fflog = "logpages_cuill.txt"
    elif re.search("ysearch/slurp", useragent):
        fflog = "logpages_yahoo.txt"
    elif page == "front":
        fflog = "logpages_front.txt"
    else:
        fflog = "logpages_unknown.txt"

    flog = os.path.join(logincomingdir, fflog)
    fout = open(flog, "a")
    fout.write(logtxt)
    fout.close()

    # now log according to referrer
    res = "unknown"
    if re.search("undemocracy", referrer):
        fout = open(os.path.join(logincomingdir, "logpages_interlink.txt"), "a")
        fout.write(logtxt)
        fout.close()
        res = "internal"
    if re.search("wikipedia", referrer):
        fout = open(os.path.join(logincomingdir, "logpages_wikipedia.txt"), "a")
        fout.write(logtxt)
        fout.close()
        res = "wikipedia"
    return res


def ReadLogReferrers(logpagen):
    flog = os.path.join(logincomingdir, logpagen)
    if not os.path.isfile(flog):
        return [ ]
    fin = open(flog)
    loglines = fin.readlines()
    fin.close()

    #logtxt = "docpage = %s %s %s %s %s %s\n" % (docid, page, (referrer or "None"), ipaddress, nowdatetime, lua)
    res = [ ]
    for logline in loglines:
        lch = logline.split()
        if len(lch) == 8:
            res.append((lch[6], lch[4], lch[2], lch[3])) # time, referrer, docid, page
    return res



def DownPersonName(person):
    return DownAscii(person.split()[-1].lower())

def CanonicaliseNation(nationf):
    nationf = re.sub(" ", "_", nationf)
    nationf = re.sub("'", "", nationf)
    return nationf


def CompleteResYear(docid):
    mresno = re.match("S-RES-(\d+)(\.pdf)?$", docid)
    if mresno:
        resno = mresno.group(1)
        for ldocid in os.listdir(pdfdir):
            mlresno = re.match("S-RES-(\d+)([^.]*)", ldocid)
            if mlresno and mlresno.group(1) == resno:
                return "S-RES-%s%s%s" % (resno, mlresno.group(2), mresno.group(2) or "")
    return docid

def SortSPVdashdot(docid):
    mpvdd = re.match("S-PV(.)(\d+.*?)(\.pdf)?$", docid)
    if mpvdd:
        fname = os.path.join(pdfdir, "S-PV%s%s.pdf" % (mpvdd.group(1), mpvdd.group(2)))
        if not os.path.isfile(fname):
            ddalt = mpvdd.group(1) == "-" and "." or "-"
            fname2 = os.path.join(pdfdir, "S-PV%s%s.pdf" % (ddalt, mpvdd.group(2)))
            if os.path.isfile(fname2):
                return "S-PV%s%s%s" % (ddalt, mpvdd.group(2), mpvdd.group(3) or "")
    return docid 


# dereferencing for hackability
# this is a very brutal system for breaking it down
def DecodeHref(pathparts, form):
    if len(pathparts) == 0:
        searchvalue = form.has_key("search") and form["search"].value or ""  # returned by the search form
        if searchvalue:
            return { "pagefunc": "search", "searchvalue" : searchvalue }
        else:
            return { "pagefunc": "front" }

    if pathparts[0] == "imghrefrep":
        return { "pagefunc":"imghrefrep", "imghrefrep":"/".join(pathparts[1:]) }

    if pathparts[0] == "pdfpreviewjpg" and len(pathparts) == 2:
        return { "pagefunc":"pdfpreviewjpg", "docid":pathparts[1] }
    # case when someone has given a document reference with the slashes
    if re.match("[AS]$", pathparts[0]) and len(pathparts) >=2 and re.match("(PV|RES|\d+|HRC|C\.\d)", pathparts[1]):
        while len(pathparts) > 1 and re.match("[ASREPRTVCLHNGO\d\.()]+$|(?:Rev|Add|Corr|Resu)\.\d+$|S-\d+$", pathparts[1]):
            pathparts[0] = "%s-%s" % (pathparts[0], pathparts[1])
            del pathparts[1]

    if pathparts[0] == "search":
        if len(pathparts) == 2:
            return { "pagefunc": "search", "searchvalue" : pathparts[1] }
    if pathparts[0] in ["about", "incoming"]:
        return { "pagefunc":pathparts[0] }
    if pathparts[0] == "documents":
        if len(pathparts) == 1:
            return { "pagefunc":"documentlist", "body":"all" }
    if pathparts[0] == "nations":
        if len(pathparts) == 1:
            return { "pagefunc":"nationlist" }

    # Legacy URLs from the Drupal site
    if pathparts[0] == 'generalassembly' and len(pathparts) == 2 and re.match("^\d+$", pathparts[1]):
        return { "pagefunc":"gasession", "gasession":int(pathparts[1]) }
    if pathparts[0] == 'securitycouncil' and len(pathparts) == 2 and re.match("^\d+$", pathparts[1]):
        return { "pagefunc":"scyear", "scyear":int(pathparts[1]) }
    if pathparts[0] == 'members' and len(pathparts) == 2:
        return { "pagefunc":"nation", "nation":pathparts[1] }
    if pathparts[0] == 'special':
        return { "pagefunc":"special" }

    if len(pathparts) >= 2 and pathparts[1] == "webcastindex" and re.match("generalassembly$|securitycouncil$", pathparts[0]):
        wcdate = (len(pathparts) == 3 and pathparts[2] or "")
        return { "pagefunc":"webcastindex", "body":pathparts[0], "date":wcdate }        

    mga = re.match("(?:generalassembly|ga)_?(\d+)?$", pathparts[0])
    if mga and len(pathparts) >= 2 and re.match("topic[nx]_(.*)$", pathparts[1]):
        # agenda num should in theory match session number
        del pathparts[0]
        mga = None
    if mga:
        if mga.group(1):
            nsess = int(mga.group(1))
            if nsess > 1945:
                nsess = nsess - 1945
            #if nsess <= 48:
            #    return { "pagefunc":"fronterror" }  # in future will default to pdf files
            if nsess > currentgasession:
                return { "pagefunc":"fronterror" }
            if len(pathparts) == 1:
                return { "pagefunc":"gasession", "gasession":nsess }
        else:
            nsess = 0
            if len(pathparts) == 1:
                return { "pagefunc": "gatopics" }


        mmeeting = re.match("meeting_?(\d+)$", pathparts[1])
        if mmeeting:
            if not nsess:
                return { "pagefunc":"fronterror" }
            nmeeting = int(mmeeting.group(1))
            docid = "A-%d-PV.%d" % (nsess, nmeeting)
            pdfinfo = GetPdfInfo(docid)
            gadice = (len(pathparts) > 2 and re.match("pg\d+-bk\d+$", pathparts[2])) and pathparts[2] or ""
            
            mhighlightdoclink = re.match("highlight_(.+)$", pathparts[-1])
            highlightdoclink = mhighlightdoclink and mhighlightdoclink.group(1)
            if pdfinfo.htmlfile and os.path.isfile(pdfinfo.htmlfile):
                return { "pagefunc":"gameeting", "docid":docid, "gasession":nsess, "gameeting":nmeeting, "pdfinfo":pdfinfo, "htmlfile":pdfinfo.htmlfile, "gadice":gadice, "highlightdoclink":highlightdoclink }
            return { "pagefunc": "document", "docid":docid }

        if pathparts[1] == "documents":
            if nsess:
                docyearfile = os.path.join(indexstuffdir, "docyears", ("ga%d.txt" % nsess))
                if os.path.isfile(docyearfile):
                    return { "pagefunc": "gadocuments", "gasession":nsess, "docyearfile":docyearfile }
            return { "pagefunc":"documentlist", "body":"generalassembly" }

        return { "pagefunc": "fronterror" }

    mtopic = re.match("topic([nx])_(.+)$", pathparts[0])
    if mtopic:
        agnum = mtopic.group(2)
        if mtopic.group(1) == "n":
            return { "pagefunc":"agendanum", "agendanum":agnum }
        
        #aglist = LoadAgendaNames(agnum) # if this is length 1 we can demote this to single list html
        return { "pagefunc":"agendanumexpanded", "agendanum":agnum } #, "aglist":aglist }


    msc = re.match("(?:securitycouncil|sc)_?(\d+|early)?$", pathparts[0])
    if msc:
        if msc.group(1) == "early":
            return { "pagefunc":"scyearearly" }
        elif msc.group(1):
            nscyear = int(msc.group(1))
            if nscyear <= 1993:
                if nscyear < 1946 or len(pathparts) == 1 or pathparts[1] != "documents":
                    return { "pagefunc": "fronterror" }
            if nscyear > currentscyear:
                return { "pagefunc": "fronterror" }
            if len(pathparts) == 1:
                return { "pagefunc":"scyear", "scyear":nscyear }
        else:
            nscyear = 0
            if len(pathparts) == 1:
                return { "pagefunc":"sctopics" }
        mmeeting = re.match("meeting_?(\d+(?:-(?:Resu|Part)\.\d+)?)$", pathparts[1])
        if mmeeting:
            scmeeting = mmeeting.group(1)
            docid = "S-PV-%s" % scmeeting

            pdfinfo = GetPdfInfo(docid)
            mhighlightdoclink = re.match("highlight_(.+)$", pathparts[-1])
            highlightdoclink = mhighlightdoclink and mhighlightdoclink.group(1) or ""
            if pdfinfo.htmlfile and os.path.isfile(pdfinfo.htmlfile):
                return { "pagefunc":"scmeeting", "docid":docid, "scmeeting":scmeeting, "pdfinfo":pdfinfo, "htmlfile":pdfinfo.htmlfile, "highlightdoclink":highlightdoclink }
            return { "pagefunc":"document", "docid":docid, "pdfinfo":pdfinfo }

        if pathparts[1] == "documents":
            if nscyear:
                docyearfile = os.path.join(indexstuffdir, "docyears", ("sc%d.txt" % nscyear))
                if os.path.isfile(docyearfile):
                    return { "pagefunc":"scdocuments", "scyear":nscyear, "docyearfile":docyearfile }
            return { "pagefunc":"documentlist", "body":"securitycouncil" }
        return { "pagefunc":"fronterror" }

    if pathparts[0] == "meeting" and len(pathparts) >= 2:
        return { "pagefunc":"meeting", "docid":pathparts[1] }

    # avoid the superfluous "document" leader
    mdocid = re.match("([AS]T?-.*?)(\.pdf)?$", pathparts[0])
    if mdocid:
        docid = mdocid.group(1)
        if re.match("S-RES-\d+$", docid):
            docid = CompleteResYear(docid)
        docid = SortSPVdashdot(docid)

        pdfinfo = GetPdfInfo(docid)
        if len(pathparts) == 1:
            pdffile = os.path.join(pdfdir, docid + ".pdf")
            if mdocid.group(2):
                return { "pagefunc":"pdf", "docid":docid, "pdffile":pdffile }
            return { "pagefunc":"document", "docid":docid, "pdffile":pdffile, "pdfinfo":pdfinfo }
        mpage = re.match("(?:page|p)_?(\d+)$", pathparts[1])
        if mpage:
            npage = int(mpage.group(1))
            highlightrects = [ ]
            highlightedit = False
            for highlight in pathparts[2:]:
                mrect = re.match("rect_(\d+),(\d+)_(\d+),(\d+)$", highlight)
                if mrect:
                    highlightrects.append((int(mrect.group(1)), int(mrect.group(2)), int(mrect.group(3)), int(mrect.group(4))))
                elif highlight == "highlightedit":
                    highlightedit = True
            hmap = { "pagefunc":"pdfpage", "docid":docid, "page":npage, "pdfinfo":pdfinfo }
            hmap["highlightrects"] = highlightrects
            hmap["highlightedit"] = highlightedit
            return hmap

        if re.match("scrape$", pathparts[1]) and not os.path.isfile(pdfinfo.pdffile):
            return { "pagefunc":"document", "docid":docid, "pdfinfo":pdfinfo, "scrapedoc":True }
        return { "pagefunc":"document", "docid":docid, "pdfinfo":pdfinfo }

    mpngid = re.match("png(\d+)$", pathparts[0])
    if mpngid and len(pathparts) >= 3:
        mpage = re.match("page_(\d+)$", pathparts[2])
        docid = pathparts[1]
        hmap = { "pagefunc":"pagepng", "width":int(mpngid.group(1)), "docid":docid, "page":int(mpage.group(1))}
        hmap["pdffile"] = "%s/%s.pdf" % (pdfdir, docid)
        hmap["pngfile"] = os.path.join(undata, "%s/%s_page_%s.png" % (pathparts[0], docid, mpage.group(1)))
        highlightrects = [ ]
        for highlight in pathparts[3:]:
            mrect = re.match("rect_(\d+),(\d+)_(\d+),(\d+)$", highlight)
            if mrect:
                highlightrects.append((int(mrect.group(1)), int(mrect.group(2)), int(mrect.group(3)), int(mrect.group(4))))
        hmap["highlightrects"] = highlightrects
        return hmap

    # detect nations by the presence of Flag_of
    for flagfile in os.listdir("/home/goatchurch/undemocracy/unparse/web2/png100"):
        if flagfile.lower() == ("Flag_of_%s.png" % pathparts[0]).lower():
            nation = flagfile.replace("Flag_of_", "").replace(".png", "").replace("_", " ")
            if len(pathparts) == 1:
                return { "pagefunc":"nation", "nation":nation }
            return { "pagefunc":"nationperson", "nation":nation, "person":pathparts[1] }

    return { "pagefunc": "fronterror" }


def EncodeHref(hmap):
    if hmap["pagefunc"] == "meeting":
        mga = re.match("A-(\d\d)-PV\.(\d+)$", hmap["docid"])
        msc = re.match("S-PV.(\d+(?:-(?:Resu|Part)\.\d)?)$", hmap["docid"])
        if mga:
            hmap["pagefunc"] = "gameeting"
            hmap["gasession"] = int(mga.group(1))
            hmap["gameeting"] = int(mga.group(2))
        if msc:
            hmap["pagefunc"] = "scmeeting"
            hmap["scmeeting"] = msc.group(1)

    if hmap["pagefunc"] == "front":
        return "/"
    if hmap["pagefunc"] == "about":
        return "/about"
    if hmap["pagefunc"] == "special":
        return "/special"
    if hmap["pagefunc"] == "search":
        return "/search/%s" % (hmap["searchvalue"])
    if hmap["pagefunc"] == "nationlist":
        return "/nations" 
    if hmap["pagefunc"] == "document":
        scrsuff = hmap.get("scrapedoc") and "/scrape" or ""
        return "/%s%s" % (hmap["docid"], scrsuff)
    if hmap["pagefunc"] == "pdfpage":
        rl = [ "", hmap["docid"], ("page_%d" % hmap["page"]) ]
        if "highlightedit" in hmap and hmap["highlightedit"]:
            rl.append("highlightedit")
        if "highlightrects" in hmap:
            for highlightrect in hmap["highlightrects"]:
                rl.append("rect_%d,%d_%d,%d" % highlightrect)
        return "/".join(rl)
    if hmap["pagefunc"] == "nativepdf":
        return "/%s.pdf" % (hmap["docid"])
    if hmap["pagefunc"] == "gasession":
        return "/generalassembly_%d" % (hmap["gasession"])
    if hmap["pagefunc"] == "gadocuments":
        return "/generalassembly_%d/documents" % (hmap["gasession"])
    if hmap["pagefunc"] == "gatopics":
        return "/generalassembly"
    if hmap["pagefunc"] == "documentlist":
        if hmap["body"] == "both":
            return "/documents"
        return "/%s/documents" % (hmap["body"])
    if hmap["pagefunc"] == "sctopics":
        return "/securitycouncil" 
    if hmap["pagefunc"] == "scyear":
        return "/securitycouncil_%d" % (hmap["scyear"])
    if hmap["pagefunc"] == "scyearearly":
        return "/securitycouncil_early"
    if hmap["pagefunc"] == "scdocuments":
        return "/securitycouncil_%d/documents" % (hmap["scyear"])
    if hmap["pagefunc"] == "agendanum" or hmap["pagefunc"] == "agendanumexpanded":
        agtop = hmap["pagefunc"] == "agendanumexpanded" and "topicx" or "topicn"
        magnum = re.search("-(\d\d)$", hmap["agendanum"])
        if magnum:
            return "/generalassembly_%s/%s_%s" % (magnum.group(1), agtop, hmap["agendanum"])
        return "/%s_%s" % (agtop, hmap["agendanum"])   # such as condolences
    if hmap["pagefunc"] == "gameeting":
        hcode = hmap.get("gid", "") and ("#%s" % hmap["gid"]) or ""
        gadice = hmap.get("gadice", "") and ("/%s" % hmap["gadice"]) or ""
        hlight = hmap.get("highlightdoclink", "") and ("/highlight_%s" % hmap["highlightdoclink"]) or ""
        if gadice and hcode and hmap["gadice"] == hmap["gid"]:
            hcode = ""
        return "/generalassembly_%d/meeting_%d%s%s%s" % (hmap["gasession"], hmap["gameeting"], gadice, hlight, hcode)
    if hmap["pagefunc"] == "scmeeting":
        hcode = ("gid" in hmap) and ("#%s" % hmap["gid"]) or ""
        hlight = hmap.get("highlightdoclink", "") and ("/highlight_%s" % hmap["highlightdoclink"]) or ""
        # in future this could include the year
        return "/securitycouncil/meeting_%s%s%s" % (hmap["scmeeting"], hlight, hcode)
    if hmap["pagefunc"] == "nation":
        nationf = CanonicaliseNation(hmap["nation"])
        return "/%s" % (nationf)   # will do a fancy munge down of it
    if hmap["pagefunc"] == "nationperson":
        nationf = re.sub(" ", "_", hmap["nation"])
        nationf = re.sub("'", "", nationf)
        personf = DownPersonName(hmap["person"])  # just work with last name
        return "/%s/%s" % (nationf, personf)

    if hmap["pagefunc"] == "flagpng":
        fnation = re.sub(" ", "_", hmap["flagnation"])
        fnation = re.sub("'", "", fnation)
        flagfile = "png%d/Flag_of_%s.png" % (hmap["width"], fnation)
        if not os.path.isfile(flagfile):
            flagfile = "png%d/Flag_of_Unknown_Body.png" % hmap["width"]
        return "/%s" % (flagfile)

    if hmap["pagefunc"] == "pagepng":
        pagefile = "png%d/%s_page_%d.png" % (hmap["width"], hmap["docid"], hmap["page"])
        if os.path.isfile(pagefile) and not hmap["highlightrects"]:
            # should touch-modify this file so it doesn't get garbage collected
            return "/%s" % (pagefile)
        rl = [ "", ("png%d" % hmap["width"]), hmap["docid"], ("page_%d" % hmap["page"]) ]
        for highlightrect in hmap["highlightrects"]:
            rl.append("rect_%d,%d_%d,%d" % highlightrect)
        return "/".join(rl)

    if hmap["pagefunc"] == "webcastindex":
        if hmap["date"]:
            wcdate = "/%s" % hmap["date"][:4] 
            href = len(hmap["date"]) == 10 and ("#d%s" % hmap["date"]) or ""
            return "/%s/webcastindex/%s%s" % (hmap["body"], hmap["date"][:4], href)
        return "/%s/webcastindex" % (hmap["body"])

    return "/rubbish/%s" % (hmap["pagefunc"] + "__" + "|".join(hmap.keys()))


# Split words from a search into separate words
# Returns a pair of (link that might be highlighted, rexexp that gets highlighted)
def SplitHighlight(highlightth):
    # Split up search string into words
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
    return highlights


# more efficient to print out as we go through
rpdlk = '<a href="../(?:pdf|html)/[^"]*?\.(?:pdf|html)"[^>]*>'
rpdlkp = '<a href="../(pdf|html)/([^"]*?)\.(?:pdf|html)"([^>]*)>'
def MarkupLinks(ftext, highlightth):
    highlights = SplitHighlight(highlightth)

    # Apply highlighting
    res = [ ]
    if highlights[1]:
        rspl = '(%s|%s)' % (rpdlk, highlights[1])
    else:
        rspl = '(%s)' % rpdlk
    for ft in re.split(rspl, ftext):
        ma = re.match(rpdlkp, ft)
        if ma:
            if ma.group(1) == "html":
                res.append('<a href="%s"' % EncodeHref({"pagefunc":"meeting", "docid":ma.group(2)}))
            else:
                res.append('<a href="%s"' % (EncodeHref({"pagefunc":"document", "docid":ma.group(2)})))
            if highlights[0] and ma.group(2) == highlights[0]:
                res.append(' class="highlight"')
            res.append(ma.group(3))
            res.append('>')
        elif highlights[1] and re.match(highlights[1], ft):
            res.append('<span class="search-highlight">')
            res.append(ft)
            res.append('</span>')
        else:
            res.append(ft)
    return "".join(res)



def GenWDocLink(pdfinfo, npage, highlightrects):
    if highlightrects:
        lhighlightrects = [ ("rect_%d,%d_%d,%d" % highlightrect)  for highlightrect in highlightrects ]
        # ought to apply to the resurl

    lhref = EncodeHref({"pagefunc":"meeting", "docid":pdfinfo.pdfc})
    resurl = '<a href=&quot;%s%s&quot;>%s of %s</a>' % (basehref, lhref, pdfinfo.desc, pdfinfo.sdate)

    wklk = [ '<ref name=&quot;' ]
    wklk.append("UN_%s" % re.sub("[^0-9a-zA-Z]", "", pdfinfo.pdfc))
    if pdfinfo.sdate:
        wklk.append("_%s" % pdfinfo.sdate[:4])
    if npage:
        wklk.append("_page%d" % npage)
    wklk.append("&quot;>")
    wklk.append("{{UN document")
    wklk.append(" |docid=%s" % pdfinfo.pdfc)
    if pdfinfo.sdate:
        wklk.append(" |date=[[%d %s]] [[%s]]" % (int(pdfinfo.sdate[8:10]), monthnames[int(pdfinfo.sdate[5:7]) - 1], pdfinfo.sdate[:4]))
    wklk.append(' |type=%s' % pdfinfo.dtype)
    if pdfinfo.bSC:
        wklk.append(" |body=Security Council")
        if pdfinfo.nscyear:
            wklk.append(" |year=%d" % pdfinfo.nscyear)
        if pdfinfo.scmeeting:
            wklk.append(" |meeting=%s" % pdfinfo.scmeeting)
    if pdfinfo.bGA:
        wklk.append(" |body=General Assembly")
        if pdfinfo.nsess:
            wklk.append(" |session=%d" % pdfinfo.nsess)
        if pdfinfo.nmeeting:
            wklk.append(" |meeting=%d" % pdfinfo.nmeeting)
    if pdfinfo.dtype == "Resolution":
        wklk.append(" |resolution_number=%s" % pdfinfo.resolution_number)
    if pdfinfo.dtype == "Document" or pdfinfo.dtype == "Presidential Statement":
        wklk.append(" |document_number=%s" % pdfinfo.document_number)


    if highlightrects:
        wklk.append(' |highlight=%s' % "/".join(lhighlightrects))
    if npage:
        wklk.append(" |page=%d" % npage)
    wklk.append(" |accessdate=%s" % nowdatetime[:10])
    wklk.append("}}")
    wklk.append('</ref>')

    return resurl, "".join(wklk)

