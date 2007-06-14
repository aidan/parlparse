#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import indexstuffdir, currentgasession, currentscyear
from basicbits import EncodeHref, LookupAgendaTitle
from xapsearch import XapLookup
from indexrecords import LoadSecRecords, LoadAgendaNames


def WriteSpeechInstances(snation, person):
    print '<h3>Speeches by the ambassador whose name matches "%s"</h3>' % person

    recs = XapLookup("nation:%s name:%s class:spoken" % (snation, person))
    if not recs:
        print '<p>No results found</p>'
        return

    print '<ul>'
    for rec in recs:
        srec = rec.split("|")
        gidspeech = srec[0]
        docid = srec[1]
        gidsubhead = srec[4]
        agtitle, sdate = LookupAgendaTitle(docid, gidspeech)
        href = EncodeHref({"pagefunc":"meeting", "docid":docid, "gid":gidspeech})
        print '<li>%s <a href="%s">%s</a></li>' % (sdate or "", href, agtitle or docid)
    print '</ul>'


def WriteMinorityVotes(snation):
    print '<h3>Minority votes</h3>'

    fname = os.path.join(indexstuffdir, "nationactivity", snation + ".txt")
    if not os.path.isfile(fname):
        return
    fin = open(fname)
    print '<ul>'
    for nd in fin.readlines():
        mmv = re.match("minorityvote = (\S+)\s+(\S+)\s+(\S+)\s+(.*)", nd)
        if mmv:
            vts = [ int(v)  for v in mmv.group(1).split("/") ]
            print '<li>'
            rw = [ ]
            rw.append('<input style="width:%dpx; background-color:green;"></input>' % vts[0])
            rw.append('<input style="width:%dpx; background-color:red;"></input>' % vts[1])
            rw.append('<input style="width:%dpx; background-color:purple;"></input>' % vts[2])
            rw.append('<input style="width:%dpx; background-color:gray;"></input>' % vts[3])
            print '<span style="border:thin black solid">%s</span>' % "".join(rw)
            print '<a href="%s">%s</a></li>' % (EncodeHref({"pagefunc":"meeting", "docid":mmv.group(2), "gid":mmv.group(3)}), mmv.group(4))
    print '</ul>'
    return

    # defunct
    recs = XapLookup("vote:%s-minority" % snation)
    if not recs:
        print '<p>No results found</p>'
        return

    print '<ul>'
    for rec in recs:
        srec = rec.split("|")
        gidspeech = srec[0]
        docid = srec[1]
        gidsubhead = srec[4]
        print '<li><a href="%s">%s</a></li>' % (EncodeHref({"pagefunc":"meeting", "docid":docid, "gid":gidspeech}), docid)
    print '</ul>'


# not written
def WriteIndexStuffNation(nation, person):
    WriteGenHTMLhead('Nation page for %s' % nation)
    flaghref = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":nation})
    print '<h1>%s</h1>' % nation
    print '<img class="nationpageflag" src="%s">' % flaghref
    snation = re.sub("\s", "", nation.lower())

    if person:
        WriteSpeechInstances(snation, person)
    else:
        WriteMinorityVotes(snation)


