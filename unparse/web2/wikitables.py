import os
import sys
import re
import cgi

from basicbits import indexstuffdir, ReadLogReferrers, LongDate
from db import GetDBcursor
import datetime

def Wikiredirect(wrefpage):
    
    # some standard mistakes
    wrefpage = re.sub("^UN_(?i)", "United_Nations_", wrefpage)
    wrefpage = re.sub("^United_Nations_Resolution_(?i)", "United_Nations_Security_Council_Resolution_", wrefpage)
    return wrefpage  # disable below for now

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
        mref = re.match("(http://en.wikipedia.org/wiki/([^#/]*))(?:#.*)?$", wpref[1])
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
        wname = re.sub("%C3%A9", "&#233;", wname)
        wname = re.sub("%C3%B6", "&#246;", wname)
        wname = re.sub("%C3%B4", "&#244;", wname)
        wname = re.sub("%27", "'", wname)
        wname = re.sub("%2C", ",", wname)

    return wname


def TimeAgo(ltime):
    timeago = datetime.datetime.now() - ltime
    hours = timeago.seconds / 3600
    minutes = (timeago.seconds / 60) % 60
    seconds = timeago.seconds % 60
    if hours >= 5:
        return "%d hours ago" % hours
    if hours != 0:
        return "%d hours, %d minutes ago" % (hours, minutes)
    if minutes >= 5:
        return "%d minutes ago" % minutes
    if minutes == 1:
        return "1 minute, %d seconds ago" % seconds
    if minutes != 0:
        return "%d minutes, %d seconds ago" % (minutes, seconds)
    return "%d seconds ago" % seconds


def ShortWikipediaTable(nentries):
    c = GetDBcursor()
    c.execute("SELECT max(ltime) AS mtime, count(*), referrer, reftitle FROM unlog_incoming WHERE refdomain = 'en.wikipedia.org' GROUP BY reftitle ORDER BY mtime DESC LIMIT %d;" % nentries)
    lres = c.fetchall()
    res = [ ]
    for wpref in lres:
        dt = wpref[0].strftime("%Y-%m-%d;%H:%M")
        #res.append((LongDate(dt[:10]), dt[11:], wpref[1], wpref[2], ConvertName(wpref[3])))
        res.append((TimeAgo(wpref[0]), "", wpref[1], wpref[2], ConvertName(wpref[3])))
    return res

def BigWikipediaTable():
    wprefs = ReadLogReferrers("logpages_wikipedia.txt")
    wprefs.extend(ReadLogReferrers("logpages_wikipedia_1.txt"))
    wprefs.extend(ReadLogReferrers("logpages_wikipedia_2.txt"))
    res = [ ] # wikiname, docid, page, date, wikifullurl
    for wpref in wprefs:
        mref = re.match("(http://en.wikipedia.org/wiki/)([^#/]*)(#.*)?$", wpref[1])
        if not mref:
            continue
        wrefpage = Wikiredirect(mref.group(2))
        wikifullurl = "%s%s%s" % (mref.group(1), wrefpage, mref.group(3) or "")
        res.append((ConvertName(wrefpage), wpref[2], wpref[3], wpref[0], wikifullurl))
    res.sort()
    return res
