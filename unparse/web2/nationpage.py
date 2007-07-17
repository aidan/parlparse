#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import indexstuffdir, currentgasession, currentscyear, scpermanentmembers, scelectedmembers, LongDate
from basicbits import EncodeHref, LookupAgendaTitle, DownPersonName
from xapsearch import XapLookup
from indexrecords import LoadSecRecords


def WriteSpeechInstances(snation, person, nationdata):
    print '<h3>Speeches by the ambassador whose name matches "%s"</h3>' % person
    print '<ul>'
    for mp in nationdata:
        if mp["lntype"] == "ambassador" and DownPersonName(mp["name"]) == person:
            href = EncodeHref({"pagefunc":"meeting", "docid":mp["docid"], "gid":mp["gid"]})
            desc, sdate = LookupAgendaTitle(mp["docid"], mp["gid"])
            print '<li>%s %s <a href="%s">%s</a></li>' % (mp["sdate"], mp["name"], href, desc or mp["sdate"])
    print '</ul>'
    return


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


def GatherNationData(snation):
    fname = os.path.join(indexstuffdir, "nationactivity", snation + ".txt")
    res = [ ]
    if not os.path.isfile(fname):
        return res
    fin = open(fname)
    for nd in fin.readlines():
        mmv = re.match("minorityvote = (\S+)\s+(\S+)\s+(\S+)\s+(.*)", nd)
        mamb = re.match("ambassador = (\S+)\s+(\S+)\s+(\S+)\s+(.*)", nd)
        # "Philippines","1945-10-24","9999-12-31","PH","PHL","Asia / Middle East"
        mcsv = re.match('nationdatacsv = "[^"]*","([^"]*)","([^"]*)","[^"]*","[^"]*","([^"]*)","([^"]*)', nd)
        if mmv:
            res.append({"lntype":"minorityvote", "division":mmv.group(1), "docid":mmv.group(2), "gid":mmv.group(3), "description":mmv.group(4)})
        elif mamb:
            res.append({"lntype":"ambassador", "docid":mamb.group(1), "gid":mamb.group(2), "sdate":mamb.group(3), "name":mamb.group(4)})
        elif mcsv:
            res.append({"lntype":"csvdata", "startdate":mcsv.group(1), "enddate":mcsv.group(2), "continent":mcsv.group(3),"missionurl":mcsv.group(4)})
    return res

def WriteNationHeading(nation, nationdata):
    csvdata = None
    for mp in nationdata:
        if mp["lntype"] == "csvdata":
            csvdata = mp
    if csvdata:
        print '<p>%s (<i>%s</i>) joined the United Nations on %s' % (nation, csvdata["continent"], LongDate(csvdata["startdate"]))
        if not re.match("9999", csvdata["enddate"]):
            print 'and left the UN in %s' % LongDate(csvdata["enddate"])
        print '</p>'
        if csvdata["missionurl"]:
            print '<p>See the <a href="%s">webpage of %s at the United Nations</a> for contact details and further information</p>' % (csvdata["missionurl"], nation)
        else:
            print '<p>There is no webpage for %s at the United Nations, according to <a href="http://www.un.int/index-en/index.html">the records</a>.</p>' % nation
    else:
        print "<p>No csv data</p>"

    if nation in scpermanentmembers:
        print '<p>%s is a <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council#Permanent_members">permanent member</a> of the Security Council.</p>' % nation
    if nation in scelectedmembers:
        print '<p>%s is an <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council#Elected_members">elected member</a> of the Security Council.</p>' % nation

def WriteMinorityVotes(nation, nationdata):
    print '<h3 style="clear:both">Minority votes</h3>'
    print '<p>Votes where %s was most in the minority.</p>' % nation
    print '<table class="minorityvotetable">'
    print '<tr> <th>Favour</th> <th>Against</th> <th>Abstain</th> <th>Absent</th> <th>Topic</th> </tr>'
    for mp in nationdata:
        if mp["lntype"] == "minorityvote":
            vts = [ int(v)  for v in mp["division"].split("/") ]
            print '<tr>'
            print '<td>%d</td>' % vts[0]
            print '<td>%d</td>' % vts[1]
            print '<td>%d</td>' % vts[2]
            print '<td>%d</td>' % vts[3]
            print '<td><a href="%s">%s</a></tr>' % (EncodeHref({"pagefunc":"meeting", "docid":mp["docid"], "gid":mp["gid"]}), mp["description"])
            print '</tr>'
    print '</table>'
    return


def WriteAmbassadorList(nation, nationdata):
    # group by ambassadors
    ambmap = { }
    for mp in nationdata:
        if mp["lntype"] == "ambassador":
            ambmap.setdefault(mp["name"], [ ]).append(mp["sdate"])

    amblist = [ (max(sdates), name, len(sdates), min(sdates))  for name, sdates in ambmap.iteritems() ]
    amblist.sort()
    amblist.reverse()

    print '<h3>Ambassadors</h3>'
    print '<table class="nationambassadortable" style="background-color:lightgray;">'
    print '<tr><th>Name</th><th>Speeches</th><th>First</th><th>Last</th></tr>'
    for ambl in amblist:
        href = EncodeHref({"pagefunc":"nationperson", "nation":nation, "person":ambl[1]})
        print '<tr><td><a href="%s">%s</a></td>  <td>%d</td> <td>%s</td> <td>%s</td></tr>' % (href, ambl[1], ambl[2], LongDate(ambl[3]), LongDate(ambl[0]))
    print '</table>'


def WriteIndexStuffNation(nation, person):
    WriteGenHTMLhead('Nation page for %s' % nation)
    flaghref = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":nation})
    print '<h1>%s</h1>' % nation
    print '<img class="nationpageflag" src="%s">' % flaghref
    snation = re.sub(" ", "_", nation)
    nationdata = GatherNationData(snation)

    if person:
        WriteSpeechInstances(snation, person, nationdata)
    else:
        WriteNationHeading(nation, nationdata)
        WriteMinorityVotes(nation, nationdata)
        WriteAmbassadorList(nation, nationdata)


def WriteAllNations():
    WriteGenHTMLhead('List of all nations')
    nationactivitydir = os.path.join(indexstuffdir, "nationactivity")
    print '<table><tr>'
    ns = 0
    for nat in sorted(os.listdir(nationactivitydir)):
        nation = re.sub("_", " ", nat[:-4])  # remove .txt
        flaghref = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":nation})
        href = EncodeHref({"pagefunc":"nation", "nation":nation})
        print '<td><a href="%s"><img class="smallflag" src="%s"></a>' % (href, flaghref)
        print '<a href="%s">%s</a></td>' % (href, nation)
        if ns == 5:
            print '</tr><tr>'
            ns = 0
        else:
            ns += 1
    print '</tr></table>'

