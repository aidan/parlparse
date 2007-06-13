import os
import sys
import re

from pdfinfo import PdfInfo
from downascii import DownAscii

currentgasession = 61
currentscyear = 2007
basehref = "http://staging.undemocracy.com"


htmldir = '/home/undemocracy/undata/html'
pdfdir = '/home/undemocracy/undata/pdf'
pdfinfodir = '/home/undemocracy/undata/pdfinfo'
pdfpreviewdir = '/home/undemocracy/undata/pdfpreview'
pdfpreviewpagedir = '/home/undemocracy/undata/pdfpreviewpage'
indexstuffdir = '/home/undemocracy/undata/indexstuff'

monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def WriteGenHTMLhead(title):
    print "Content-Type: text/html\n"
    print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'
    print '<html>'
    print '<head>'
    print '<title>UNdemocracy - %s</title>' % title
    print '<link href="%s/unview.css" type="text/css" rel="stylesheet" media="all">' % basehref
    print '<script language="JavaScript" type="text/javascript" src="%s/unjava.js"></script>' % basehref
    print '</head>'
    print '<body>'
    print '<a href="%s"><h1 class="tophead">UNdemocracy.com</h1></a>' % basehref
    print '<h1 class="topheadspec">%s</h1>' % title


def GetPdfInfo(docid):
    res = PdfInfo(docid)
    res.UpdateInfo(pdfinfodir)
    if re.match("A-\d+-PV|S-PV", docid):
        res.htmlfile = os.path.join(htmldir, docid + ".html")
    else:
        res.htmlfile = ""
    return res


# dereferencing for hackability
# this is a very brutal system for breaking it down
def DecodeHref(pathparts):
    if len(pathparts) == 0:
        return { "pagefunc": "front" }

    # case when someone has given a document reference with the slashes
    if re.match("[AS]$", pathparts[0]) and len(pathparts) >=2 and re.match("(PV|RES|\d+)", pathparts[1]):
        pathparts[0] = "-".join(pathparts)
        del pathparts[1:]

    if pathparts[0] == "documents":
        if len(pathparts) == 1:
            return { "pagefunc":"documentlist", "body":"all" }

    mga = re.match("(?:generalassembly|ga)_?(\d+)?$", pathparts[0])
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
                return { "pagefunc": "fronterror" }


        mmeeting = re.match("meeting_?(\d+)$", pathparts[1])
        if mmeeting:
            if not nsess:
                return { "pagefunc":"fronterror" }
            nmeeting = int(mmeeting.group(1))
            docid = "A-%d-PV.%d" % (nsess, nmeeting)
            pdfinfo = GetPdfInfo(docid)
            mhighlightdoclink = (len(pathparts) > 2) and re.match("highlight_([SA]-.*?)$", pathparts[2])
            highlightdoclink = mhighlightdoclink and mhighlightdoclink.group(1)
            if pdfinfo.htmlfile and os.path.isfile(pdfinfo.htmlfile):
                return { "pagefunc":"gameeting", "docid":docid, "gasession":nsess, "gameeting":nmeeting, "pdfinfo":pdfinfo, "htmlfile":pdfinfo.htmlfile, "highlightdoclink":highlightdoclink }
            return { "pagefunc": "document", "docid":docid }

        mtopic = re.match("topicn_(.+)$", pathparts[1])
        if mtopic:
            return { "pagefunc": "agendanum", "agendanum":mtopic.group(1) }
            # agenda num should in theory match session number
        if pathparts[1] == "documents":
            if nsess:
                docyearfile = os.path.join(indexstuffdir, "docyears", ("ga%d.txt" % nsess))
                if os.path.isfile(docyearfile):
                    return { "pagefunc": "gadocuments", "gasession":nsess, "docyearfile":docyearfile }
            return { "pagefunc":"documentlist", "body":"generalassembly" }

        return { "pagefunc": "fronterror" }

    mtopic = re.match("topicn_(.+)$", pathparts[0])
    if mtopic:
        return { "pagefunc":"agendanum", "agendanum":mtopic.group(1) }

    msc = re.match("(?:securitycouncil|sc)_?(\d+)?$", pathparts[0])
    if msc:
        if msc.group(1):
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
        mmeeting = re.match("meeting_?(\d+)(?:_?(Resu(?:mtion)?|Part)_(\d))?$", pathparts[1])
        if mmeeting:
            docid = "S-PV-%s" % mmeeting.group(1)
            if mmeeting.group(2):
                docid = "%s-%s.%s" % (docid, mmeeting.group(1), mmeeting.group(2))
            pdfinfo = GetPdfInfo(docid)
            mhighlightdoclink = (len(pathparts) > 2) and re.match("highlight_([SA]-.*?)$", pathparts[2])
            highlightdoclink = mhighlightdoclink and mhighlightdoclink.group(1)
            if pdfinfo.htmlfile and os.path.isfile(pdfinfo.htmlfile):
                return { "pagefunc":"scmeeting", "docid":docid, "pdfinfo":pdfinfo, "htmlfile":pdfinfo.htmlfile, "highlightdoclink":highlightdoclink }
            return { "pagefunc":"document", "docid":docid, "pdfinfo":pdfinfo }

        if pathparts[1] == "documents":
            if nscyear:
                docyearfile = os.path.join(indexstuffdir, "docyears", ("sc%d.txt" % nscyear))
                if os.path.isfile(docyearfile):
                    return { "pagefunc":"scdocuments", "scyear":nscyear, "docyearfile":docyearfile }
            return { "pagefunc":"documentlist", "body":"securitycouncil" }
        return { "pagefunc":"fronterror" }


    # avoid the superfluous "document" leader
    mdocid = re.match("([AS]-.*?)(\.pdf)?$", pathparts[0])
    if mdocid:
        docid = mdocid.group(1)
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

        return { "pagefunc":"document", "docid":docid, "pdfinfo":pdfinfo }

    mpngid = re.match("png(\d+)$", pathparts[0])
    if mpngid and len(pathparts) >= 3:
        mpage = re.match("page_(\d+)$", pathparts[2])
        docid = pathparts[1]
        hmap = { "pagefunc":"pagepng", "width":int(mpngid.group(1)), "docid":docid, "page":int(mpage.group(1))}
        hmap["pdffile"] = "%s/%s.pdf" % (pdfdir, docid)
        hmap["pngfile"] = "%s/%s_page_%s.png" % (pathparts[0], docid, mpage.group(1))
        highlightrects = [ ]
        for highlight in pathparts[3:]:
            mrect = re.match("rect_(\d+),(\d+)_(\d+),(\d+)$", highlight)
            if mrect:
                highlightrects.append((int(mrect.group(1)), int(mrect.group(2)), int(mrect.group(3)), int(mrect.group(4))))
        hmap["highlightrects"] = highlightrects
        return hmap

    # detect nations by the presence of Flag_of
    if os.path.isfile(os.path.join("png100", ("Flag_of_%s.png" % pathparts[0]))):
        nation = re.sub("_", " ", pathparts[0])
        if len(pathparts) == 1:
            return { "pagefunc":"nation", "nation":nation }
        return { "pagefunc":"nationperson", "nation":nation, "person":pathparts[1] }

    return { "pagefunc": "fronterror" }



def EncodeHref(hmap):
    if hmap["pagefunc"] == "meeting":
        mga = re.match("A-(\d\d)-PV\.(\d+)$", hmap["docid"])
        msc = re.match("S-PV-(\d+)(?:-(Resu|Part)\.(\d))?$", hmap["docid"])
        if mga:
            hmap["pagefunc"] = "gameeting"
            hmap["gasession"] = int(mga.group(1))
            hmap["gameeting"] = int(mga.group(2))
        if msc:
            hmap["pagefunc"] = "scmeeting"
            hmap["scmeeting"] = int(msc.group(1))
            if msc.group(2):
                hmap["scmeetingsuffix"] = "_%s_%s" % (msc.group(2), msc.group(3))
            else:
                hmap["scmeetingsuffix"] = ""

    if hmap["pagefunc"] == "front":
        return "%s" % basehref
    if hmap["pagefunc"] == "document":
        return "%s/%s" % (basehref, hmap["docid"])
    if hmap["pagefunc"] == "pdfpage":
        rl = [ basehref, hmap["docid"], ("page_%d" % hmap["page"]) ]
        if "highlightedit" in hmap and hmap["highlightedit"]:
            rl.append("highlightedit")
        if "highlightrects" in hmap:
            for highlightrect in hmap["highlightrects"]:
                rl.append("rect_%d,%d_%d,%d" % highlightrect)
        return "/".join(rl)
    if hmap["pagefunc"] == "nativepdf":
        return "%s/%s.pdf" % (basehref, hmap["docid"])
    if hmap["pagefunc"] == "gasession":
        return "%s/generalassembly_%d" % (basehref, hmap["gasession"])
    if hmap["pagefunc"] == "gadocuments":
        return "%s/generalassembly_%d/documents" % (basehref, hmap["gasession"])
    if hmap["pagefunc"] == "documentlist":
        if hmap["body"] == "both":
            return "%s/documents" % (basehref)
        return "%s/%s/documents" % (basehref, hmap["body"])
    if hmap["pagefunc"] == "sctopics":
        return "%s/securitycouncil" % (basehref)
    if hmap["pagefunc"] == "scyear":
        return "%s/securitycouncil_%d" % (basehref, hmap["scyear"])
    if hmap["pagefunc"] == "scdocuments":
        return "%s/securitycouncil_%d/documents" % (basehref, hmap["scyear"])
    if hmap["pagefunc"] == "agendanum":
        magnum = re.search("-(\d\d)$", hmap["agendanum"])
        if magnum:
            return "%s/generalassembly_%s/topicn_%s" % (basehref, magnum.group(1), hmap["agendanum"])
        return "%s/topicn_%s" % (basehref, hmap["agendanum"])   # such as condolences
    if hmap["pagefunc"] == "gameeting":
        hcode = ("gid" in hmap) and ("#%s" % hmap["gid"]) or ""
        hlight = ("highlightdoclink" in hmap) and ("/highlight_%s" % hmap["highlightdoclink"]) or ""
        return "%s/generalassembly_%d/meeting_%d%s%s" % (basehref, hmap["gasession"], hmap["gameeting"], hlight, hcode)
    if hmap["pagefunc"] == "scmeeting":
        hcode = ("gid" in hmap) and ("#%s" % hmap["gid"]) or ""
        hlight = ("highlightdoclink" in hmap) and ("/highlight_%s" % hmap["highlightdoclink"]) or ""
        # in future this could include the year
        return "%s/securitycouncil/meeting_%d%s%s%s" % (basehref, hmap["scmeeting"], hmap["scmeetingsuffix"], hlight, hcode)
    if hmap["pagefunc"] == "nation":
        nationf = re.sub(" ", "_", hmap["nation"])
        nationf = re.sub("'", "", nationf)
        return "%s/%s" % (basehref, nationf)   # will do a fancy munge down of it
    if hmap["pagefunc"] == "nationperson":
        nationf = re.sub(" ", "_", hmap["nation"])
        nationf = re.sub("'", "", nationf)
        personf = DownAscii(hmap["person"].split()[-1].lower())  # just work with last name
        return "%s/%s/%s" % (basehref, nationf, personf)

    if hmap["pagefunc"] == "flagpng":
        fnation = re.sub(" ", "_", hmap["flagnation"])
        fnation = re.sub("'", "", fnation)
        flagfile = "png%d/Flag_of_%s.png" % (hmap["width"], fnation)
        if not os.path.isfile(flagfile):
            return ""
        return "%s/%s" % (basehref, flagfile)

    if hmap["pagefunc"] == "pagepng":
        pagefile = "png%d/%s_page_%d.png" % (hmap["width"], hmap["docid"], hmap["page"])
        if os.path.isfile(pagefile) and not hmap["highlightrects"]:
            # should touch-modify this file so it doesn't get garbage collected
            return "%s/%s" % (basehref, pagefile)
        rl = [ basehref, ("png%d" % hmap["width"]), hmap["docid"], ("page_%d" % hmap["page"]) ]
        for highlightrect in hmap["highlightrects"]:
            rl.append("rect_%d,%d_%d,%d" % highlightrect)
        return "/".join(rl)

    return "%s/rubbish/%s" % (basehref, hmap["pagefunc"] + "__" + "|".join(hmap.keys()))

