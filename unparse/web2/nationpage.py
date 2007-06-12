#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import indexstuffdir, currentgasession, currentscyear
from basicbits import EncodeHref
from xapsearch import XapLookup
from indexrecords import LoadSecRecords, LoadAgendaNames

def WriteSpeechInstances(snation, person):
    print '<h3>Subselection of speeches by %s</h3>' % person

    recs = XapLookup("nation:%s name:%s" % (snation, person))
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


def WriteMinorityVotes(snation):
    print '<h3>Minority votes</h3>'

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


