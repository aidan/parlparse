import os
import sys
import re
import cgi

from basicbits import indexstuffdir, ReadLogReferrers, LongDate

def Wikiredirect(wrefpage):
    
    # some standard mistakes
    wrefpage = re.sub("^UN_(?i)", "United_Nations_", wrefpage)
    wrefpage = re.sub("^United_Nations_Resolution_(?i)", "United_Nations_Security_Council_Resolution_", wrefpage)

    fin = open("wikiredirects.txt")
    mainname = ""
    for sline in fin.readlines():
        if re.match("\s*$", sline):
            pass
        elif re.match("\S", sline):
            mainname = sline.strip()
        elif wrefpage == sline.strip() and mainname:
            wrefpage = mainname
    return wrefpage


def ReadWikipediaReferrers():
    wprefs = ReadLogReferrers("logpages_wikipedia.txt")
    wprefs.sort()
    wprefs.reverse()
    mres = { }  # wikipediapage : [ recentdate, wikipediafullurl, number ]
    for wpref in wprefs:
        mref = re.match("(http://.*?wikipedia.org/wiki/([^#/]*))(?:#.*)?$", wpref[1])
        if not mref:
            continue
        wsdate = wpref[0]
        #if wsdate < fromdate:  # use to measure for the last 30 days
        #    break
        wrefpage = Wikiredirect(mref.group(2))
        if wrefpage in mres:
            mres[wrefpage][2] += 1
        else:
            mres[wrefpage] = [wsdate, mref.group(1), 1]

    lres = [ ]
    for mr, mrl in mres.iteritems():
        lres.append((mrl[0], mrl[2], mrl[1], mr))
    lres.sort()  # date, number, fullurl, name
    lres.reverse()
    return lres

def ConvertName(wname):
    wname = re.sub("_", " ", wname)
    if re.search("%", wname):
        wname = re.sub("%28", "(", wname)
        wname = re.sub("%29", ")", wname)
        wname = re.sub("%C3%B6", "ö", wname)
    return wname

def ShortWikipediaTable(nentries):
    lres = ReadWikipediaReferrers()
    res = [ ]
    for wpref in lres[:nentries]:
        res.append((LongDate(wpref[0][:10]), wpref[0][11:], wpref[1], wpref[2], ConvertName(wpref[3])))
    return res

def BigWikipediaTable():
    wprefs = ReadLogReferrers("logpages_wikipedia.txt")
    res = [ ] # wikiname, docid, page, date, wikifullurl
    for wpref in wprefs:
        mref = re.match("(http://.*?wikipedia.org/wiki/)([^#/]*)(#.*)?$", wpref[1])
        if not mref:
            continue
        wrefpage = Wikiredirect(mref.group(2))
        wikifullurl = "%s%s%s" % (mref.group(1), wrefpage, mref.group(3) or "")
        res.append((ConvertName(wrefpage), wpref[2], wpref[3], wpref[0], wikifullurl))
    res.sort()
    return res
