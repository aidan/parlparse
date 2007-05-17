#!/usr/bin/python2.4
import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs
import datetime


class AgendaHeading:
    def __init__(self, sdate, docid, subheadingid, agendanum, titletext):
        self.sdate = sdate
        self.docid = docid
        self.session = re.match("A-(\d\d)", docid).group(1)
        self.subheadingid = subheadingid
        self.agendas = agendanum.split(",")

        for a in self.agendas:
            sa = a.split("-")
            assert len(sa) == 2
            assert sa[1] == self.session

        self.titlelines = re.findall("<(p|blockquote)[^>]*>(.*)</(?:p|blockquote)>", titletext)
        print
        print self.titlelines


def WriteAgendaSummaries(htmldir, fout):
    rels = GetAllHtmlDocs("", False, False, htmldir)

    for htdoc in rels:
        maga = re.search("(A-\d\d-PV\.\d+)\.html", htdoc)
        masc = re.search("(S-PV-\d+)\.html", htdoc)

        if not maga:
            if not masc:
                print "Whatis", htdoc
            continue

        docid = maga.group(1)

        fin = open(htdoc)
        ftext = fin.read()
        fin.close()

        mdate = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', ftext)
        sdate = mdate.group(1)

#<div class="subheading" id="pg001-bk02" agendanum="9-49">
#	<p id="pg001-bk02-pa01">Agenda item 9 <i>(continued)</i></p>
#	<p class="boldline-p" id="pg001-bk02-pa02">General debate</p>
#</div>
        allagendas = [ ]
        agheadings = re.findall('(?s)<div class="subheading" id="([^"]*)" agendanum="([^"]*)">(.*?)</div>', ftext)
        for agheading in agheadings:
            allagendas.append(AgendaHeading(sdate, docid, agheading[0], agheading[1], agheading[2]))


        #break
