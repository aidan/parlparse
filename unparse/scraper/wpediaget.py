# -*- coding: latin1 -*-

import urllib2
import cookielib
import urlparse
import re
import sys
import os

def IsVeryNoisy():
    return True

# awful documentation can be found at: http://meta.wikimedia.org/wiki/API

transclusgetN = "http://en.wikipedia.org/w/api.php?action=query&generator=embeddedin&titles=Template:%s&prop=info&format=xml&geilimit=%d"
pageidget = "http://en.wikipedia.org/w/api.php?action=query&prop=revisions&pageids=%s&rvprop=content&format=xml"

def GetTransClusList(transtemplate, datefrom):
    transtemplate = re.sub("\s", "_", transtemplate)
    transclus = transclusgetN % (transtemplate, 200)

    if IsVeryNoisy():
        print "--Finding transclusions for:", transtemplate, "--before:", datefrom
    res = [ ]
    # this may have to iterate

    fin = urllib2.urlopen(transclus)
    tctext = fin.read()
    fin.close()

    # <page pageid="8789372" ns="10" title="Template:UN document" touched="2007-01-11T19:25:10Z" lastrevid="100046655" />
    tclist = re.findall('<page pageid="([^"]*)".*? title="([^"]*)" touched="([^"]*)".*?>', tctext)

    for pageid, pagetitle, pagedate in tclist:
        if (not re.match("Template:", pagetitle)) and pagedate >= datefrom:
            res.append((pagedate, pagetitle, pageid))
    res.sort()
    if IsVeryNoisy():
        print "--Found:", len(res)
    return res

rexmlwrappageid = '''(?xs)<\?xml[^>]*>\s*
                          <api>\s*<query>\s*<pages>\s*
                          <page\s+pageid="([^"]*)"\s+ns="\d"\s+title="([^"]*)">\s*
                          <revisions><rev[^>]*>
                          (.*?)
                          </rev></revisions></page></pages></query></api>
                          \s*$'''
def FetchTextFromId(pageid):
    pagetrans = pageidget % pageid
    fin = urllib2.urlopen(pagetrans)
    tccontent = fin.read()
    fin.close()

    mwrappedpage = re.match(rexmlwrappageid, tccontent)
    assert mwrappedpage, "Unrecognized xml wrapped content\n****************\n%s\n**************\n" % tccontent
    assert mwrappedpage.group(1) == pageid
    pagetitle = mwrappedpage.group(2)
    pagetext = mwrappedpage.group(3)
    pagetext = re.sub("&lt;", "<", pagetext)
    pagetext = re.sub("&gt;", ">", pagetext)
    pagetext = re.sub("&quot;", "\"", pagetext)
    pagetext = re.sub("&amp;", "&", pagetext)
    return pagetitle, pagetext

def GetEqSectionsFromText(text):
    hh = re.split("(?:\n|^) *(=.*?=) *\n", text)
    res = [ ("", []) ]
    for h in hh:
        meq = re.match("=(.*?)=$", h)
        if meq:
            while meq:
                h = meq.group(1)
                meq = re.match("=(.*?)=$", h)
            h = h.strip()
            if h:
                res.append((h, []))
                continue
        res[-1][1].append(h)
    return [ (r1, "\n".join(r2))  for r1, r2 in res ]


def ProcessTemplParams(templstackent):
    iel = 0
    templmap = { }
    for tt in templstackent:
        stt = "".join(tt).strip()
        mpeq = re.match("(?s)([\w\s]*)=(.*)$", stt)
        if mpeq:
            templmap[mpeq.group(1).strip()] = mpeq.group(2).strip()
        else:
            templmap[iel] = stt
        iel += 1
    return templmap


def GetCurlBracketTemplatesFromText(text):
    outertext = [ ]
    closedtemplates = [ ]
    templatestack = [ ]
    for a in re.split("(\{\{|\}\}|\|)", text):
        if re.match("\{\{", a):
            for t in templatestack:
                t[-1].append(a)
            templatestack.append([[]])
        elif templatestack:
            for t in templatestack[:-1]:
                t[-1].append(a)
            if re.match("\}\}", a):
                closedtemplates.append(ProcessTemplParams(templatestack[-1]))
                if len(templatestack) == 1:
                    tc = closedtemplates[-1][0].strip()
                    if False and not re.match("cite", tc):
                        outertext.append("<i>")
                        outertext.append(closedtemplates[-1][0].strip())
                        outertext.append("</i>")
                del templatestack[-1]
            elif re.match("\|", a):
                templatestack[-1].append([])
            else:
                templatestack[-1][-1].append(a)
        else:
            outertext.append(a)
    assert not templatestack  # not true if it's a bad page

    # convert down the outer-text so we can use it
    ot = "".join(outertext)
    ot = re.sub("\[\[(?:[^|\]]*\|)?([^|\]]*)\]\]", "\\1", ot)
    ot = re.sub("\[\s*http:(?:[^\s\]]*\|)([^\]]*)\]", "\\1", ot)
    ot = re.sub("\[\s*http:[^\]]*\]", "", ot)
    ot = re.sub("'''([^']*)'''", "<b>\\1</b>", ot)
    ot = re.sub("''([^']*)''", "<i>\\1</i>", ot)
    ot = re.sub("\s*\(\s*\)", "", ot)
    ot = re.sub("<[^>]*&>", "", ot)

    return ot, closedtemplates


class TemplationStruct:
    def __init__(self, pagetitle, sectionheading, cleantext, templmap):
        self.pagetitle = pagetitle
        self.sectionheading = sectionheading
        self.cleantext = cleantext
        wpagetitle = re.sub(" ", "_", pagetitle)
        wsectionheading = re.sub(" ", "_", sectionheading)
        self.wpurl = "http://en.wikipedia.org/wiki/%s%s%s" % (wpagetitle, wsectionheading and "#", wsectionheading)
        self.templname = re.sub("_", " ", templmap.get(0, "no-name")).strip()
        self.templmap = templmap


def FetchProcessedTextFromId(pageid):
    res = [ ]
    pagetitle, pagetext = FetchTextFromId(pageid)
    if IsVeryNoisy():
        print "--Fetched:", pagetitle
    eqsections = GetEqSectionsFromText(pagetext)
    for sectionheading, sectiontext in eqsections:
        cleantext, templmaps = GetCurlBracketTemplatesFromText(sectiontext)
        for templmap in templmaps:
            res.append(TemplationStruct(pagetitle, sectionheading, cleantext, templmap))
            if IsVeryNoisy():
                print "    template:", res[-1].templname, "--section:", res[-1].sectionheading
    return res


# the incoming function
# {{ UN document |code=S/PV/4251 |body=S |type=PV |meeting=4251 |date=[[19 December]] [[2000]] |time=16:00 |accessdate=2007-01-08 |anchor=pg002-bk08 |page=2|speakername=Mr. Farhâdi |speakernation=Afghanistan }}

def FetchWikiBacklinks(commentsdir):
    currfile = os.path.join(commentsdir, "wptransloc-undoc.html")
    destfile = os.path.join(commentsdir, "wptransloc-undoc.unindexed.html")
    templname = "UN document"

    prevrecords = [ ]
    datefrom = "2000-01-01"
    if os.path.isfile(currfile):
        print "copy out previous records from file and set the datefrom"
    tclist = GetTransClusList(templname, datefrom)

    fout = open(destfile, "w")
    fout.write("<html><head></head><body>\n")
    for pagedate, pagetitle, pageid in tclist:
        if IsVeryNoisy():
            print "\n--Fetching:", pagetitle, "--pageid:", pageid
        templations = FetchProcessedTextFromId(pageid)
        for templation in templations:
            if templation.templname != templname:
                continue
            code = templation.templmap.get("code", "")
            anchor = templation.templmap.get("anchor", "")
            wpurl = templation.templmap.get("wpurl", "")

            fout.write('\n<div>\n')
            fout.write('    <p><span class="date">%s</span>\n' % pagedate)
            fout.write('    <a href="http://staging.undemocracy.com/code/%s/%s">%s %s</a>\n' % (re.sub("/", "-", code), anchor, code, anchor))
            fout.write('    <a href="%s">%s # %s</a>\n' % (wpurl, pagetitle, templation.sectionheading))
            fout.write('    </p>\n')
            fout.write('  <blockquote>')
            fout.write(templation.cleantext)
            fout.write('  </blockquote>\n')
            fout.write('</div>\n')

    fout.write("</body></html>\n")
    fout.close()


# run directly; the code outside FetchWikiBacklinks is useable for making, say,
# deepest cave page, or located maps, to be run on a cron-job
if __name__ == "__main__":
    transtemplate = "UN document"
    #transtemplate = "UK Parliament"
    #transtemplate = "Infobox_Cave"

    tclist = GetTransClusList(transtemplate, "2007-01-01")
    for pagedate, pagetitle, pageid in tclist:
        if IsVeryNoisy():
            print "\n--Fetching:", pagetitle, "--pageid:", pageid
        FetchProcessedTextFromId(pageid)




