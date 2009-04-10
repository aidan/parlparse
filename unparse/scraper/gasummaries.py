#!/usr/bin/python

import sys
import re
import os
import urllib2
from nations import nationdates
from unmisc import IsNotQuiet
import datetime
from unscrape import ScrapePDF
from pdfinfo import PdfInfo

from unpylons.model import currentyear, currentmonth, currentsession

monthnames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

def GASummariesURL(sess):
    if sess >= 52:
        return "http://www.un.org/Depts/dhl/resguide/r%d.htm" % sess
    elif sess >= 36:
        return "http://www.un.org/Depts/dhl/res/resa%d.htm" % sess
    return "http://www.un.org/documents/ga/res/%d/ares%d.htm" % (sess, sess)

def ScrapeGASummaries(gasummariesdir):
    for sess in range(1, currentsession + 1):
        f = os.path.join(gasummariesdir, "gaact%d.html" % sess)
        url = GASummariesURL(sess)

        if sess == currentsession or (sess == currentsession - 1 and currentmonth == 9) or not os.path.isfile(f):
            if IsNotQuiet():
                print "Scraping", url
            fin = urllib2.urlopen(url)
            gaindext = fin.read()
            fin.close()

            fout = open(f, "w")
            fout.write(gaindext)
            fout.close()

def ConvDate(ldate):
    mdate = re.match("(\d+)\s+(\w+)\s+(\d+)", ldate)
    assert mdate, ldate
    assert mdate.group(2) in monthnames, ldate
    nmonth = monthnames.index(mdate.group(2)) + 1
    ndate = int(mdate.group(1))
    nyear = int(mdate.group(3))
    assert 1945 <= nyear <= 3000
    return "%04d-%02d-%02d" % (nyear, nmonth, ndate)


def ParseScrapeGASummaries(gasummariesdir, pdfinfodir, sess):
    f = os.path.join(gasummariesdir, "gaact%d.html" % sess)
    fin = open(f)
    fstext = fin.read()
    fin.close()

    for mrow in re.finditer('<tr[^>]*>(.*?)</tr>(?is)', fstext):
        if re.search("UN\s+home\s+page(?i)", mrow.group(1)):
            continue
        tds = re.findall('<td[^>]*>\s*(?:<font[^>]*>\s*)?(.*?)\s*(?:</font>\s*)?</td>(?is)', mrow.group(1))
        mlink = re.match('<a\s*href="([^"]*)"[^>]*>\s*(.*?)\s*</a>(?is)', tds[0])
        sdate = ConvDate(tds[1])

        ltitle = re.sub("\s\s+|\n", " ", tds[2])
        print ltitle
        print mlink.group(2)

        undocname = None
        mearlyres = re.match("(\d+)\s\(([IVX\-S\d]+)\)", mlink.group(2))
        if mearlyres:
            undocname = "A-RES-%s(%s)" % (mearlyres.group(1), mearlyres.group(2))
        assert undocname, tds[0]
        lplenaryurl = GASummariesURL(sess)
        ScrapePDF(undocname, plenaryurl=lplenaryurl)

        pdfinfo = PdfInfo(undocname)
        pdfinfo.UpdateInfo(pdfinfodir)
        pdfinfo.title = ltitle
        pdfinfo.sdate = sdate
        print "writing", sdate
        pdfinfo.WriteInfo(pdfinfodir)

