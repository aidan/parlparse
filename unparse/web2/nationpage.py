#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import indexstuffdir, currentgasession, currentscyear, scpermanentmembers, scelectedmembersyear, LongDate
from basicbits import EncodeHref, LookupAgendaTitle, DownPersonName
from xapsearch import XapLookup
from indexrecords import LoadSecRecords
from db import GetDBcursor


def WriteSpeechInstances(snation, person, nationdata):
    c = GetDBcursor()
    print '<h3>Speeches by the ambassador whose name matches "%s"</h3>' % person
    print '<ul>'
    prevdocid = ""
    for mp in nationdata:
        if mp["lntype"] == "ambassador" and DownPersonName(mp["name"]) == person and mp["docid"] != prevdocid:
            href = EncodeHref({"pagefunc":"meeting", "docid":mp["docid"], "gid":mp["gid"]})
            desc, sdate = LookupAgendaTitle(mp["docid"], mp["gid"], c)
            print '<li>%s %s <a href="%s">%s</a></li>' % (mp["sdate"], mp["name"], href, desc or mp["sdate"])
            prevdocid = mp["docid"]
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
        agtitle, sdate = LookupAgendaTitle(docid, gidspeech, c)
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
        mmv = re.match("((?:sc)?minorityvote) = (\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(.*)", nd)
        mamb = re.match("ambassador = (\S+)\s+(\S+)\s+(\S+)\s+(.*)", nd)
        # "Philippines","1945-10-24","9999-12-31","PH","PHL","Asia / Middle East"
        mcsv = re.match('nationdatacsv = "[^"]*","([^"]*)","([^"]*)","[^"]*","[^"]*","([^"]*)","([^"]*)', nd)
        if mmv:
            res.append({"lntype":mmv.group(1), "division":mmv.group(2), "docid":mmv.group(3), "gid":mmv.group(4), "date":mmv.group(5), "description":mmv.group(6)})
        elif mamb:
            res.append({"lntype":"ambassador", "docid":mamb.group(1), "gid":mamb.group(2), "sdate":mamb.group(3), "name":mamb.group(4)})
        elif mcsv:
            res.append({"lntype":"csvdata", "startdate":mcsv.group(1), "enddate":mcsv.group(2), "continent":mcsv.group(3),"missionurl":mcsv.group(4)})
    return res

def WriteNationHeading(nation, nationdata):
    c = GetDBcursor()
    fnation = re.sub(" ", "_", nation)
    c.execute("""SELECT nation, date_entered, date_left, continent, missionurl, wikilink, fname 
                 FROM un_nations WHERE fname='%s' or nation="%s" """ % (fnation, nation))
    ns = c.fetchone()
    if ns:
        nation = ns[0]
        print '<ul class="nationstats">'
        print '<li>%s has been a member of the United Nations since <em>%s</em></li>' % (nation, LongDate(ns[1].isoformat()))
        if ns[2].year != 9999:
            print '<li>%s left or was renamed in <em>%s</em></li>' % (nation, LongDate(ns[2].isoformat))
        if ns[4]:
            print '<li>Contact <a href="%s">the ambassador for %s</a></li>' % (ns[4], nation)
        else:
            print '<li>%s is not in <a href="http://www.un.int/index-en/index.html">the list of countries with webpages</a> at the UN.</li>' % nation
        print '<li>Read the <a href="%s">Wikipedia page for %s</a></li>' % (ns[5], nation)
        print '<li>%s is part of the <i>%s</i> block</li>' % (nation, ns[3])
        
        c.execute("""SELECT count(*), min(ldate), max(ldate) FROM un_votes 
                   LEFT JOIN un_divisions ON un_divisions.docid=un_votes.docid AND un_divisions.href=un_votes.href
                   WHERE nation=\"%s\" AND vote<>'absent'""" % nation)
        a = c.fetchone()
        if a and a[1]:
            print '<li>%s has participated in %d votes since <em>%s</em>,' % (nation, a[0], LongDate(a[1].isoformat()))
            print 'most recently on <em>%s</em></li>' % LongDate(a[2].isoformat())
        
        print '</ul>'

    csvdata = None
    for mp in nationdata:
        if mp["lntype"] == "csvdata":
            csvdata = mp

    if nation in scpermanentmembers:
        print '<p>%s is a <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council#Permanent_members">permanent member</a> of the Security Council.</p>' % nation
    if currentscyear not in scelectedmembersyear:
        print '<p>List of elected members not yet updated; please remind julian@goatchurch.org.uk to do it.</p>'
    elif nation in scelectedmembersyear[currentscyear]:
        print '<p>%s is an <a href="http://en.wikipedia.org/wiki/United_Nations_Security_Council#Elected_members">elected member</a> of the Security Council.</p>' % nation


def MinorityVoteWordsOutOf(nwith, ntotal):
    if nwith == 1:
        return "<b>alone</b> (out of %d nations)" % ntotal
    return "with <b>%s</b> other nation%s (out of %d)" % (nwith-1, nwith!=2 and "s" or "", ntotal)

def WriteMinorityVotes(nation, nationdata):
    c = GetDBcursor()
    qsel = "SELECT un_divisions.docid, un_divisions.href, ldate, motiontext, vote, favour, against, abstain, absent FROM un_divisions "
    qlj = "LEFT JOIN un_votes ON un_votes.docid=un_divisions.docid AND un_votes.href=un_divisions.href AND un_votes.nation=\"%s\"" % nation
    c.execute("%s %s WHERE body='GA' AND vote is not null ORDER BY minority_score LIMIT 20" % (qsel, qlj))

    minority = c.fetchall()

    minorityvotes = [ ]
    scminorityvotes = [ ]
    for mp in nationdata:
        if mp["lntype"] == "minorityvote":
            minorityvotes.append(mp)
        elif mp["lntype"] == "scminorityvote":
            scminorityvotes.append(mp)
    if not minorityvotes and not scminorityvotes:
        return

    print '<h3 style="clear:both">Minority votes in the General Assembly</h3>'
    print '<p>Sometimes these votes highlight an issue where there is a difference from the majority of the international community.</p>'
    print '<p style="margin-top: 1em"><b>%s...</b></p>' % nation
    
    print '<table class="minorityvote">'
    for mp in minority:
        print '<tr><td class="col1">'
        (docid, href, ldate, motiontext, vote, favour, against, abstain, absent) = mp
        mvotes = favour + against + abstain
        if vote == "against":
            print 'voted %s <b>against</b>' % MinorityVoteWordsOutOf(against, mvotes)
        elif vote == "favour":
            print 'voted %s <b>in favour</b> of ' % MinorityVoteWordsOutOf(favour, mvotes)
        elif vote == "abstain":
            print 'voted %s to <b>abstain</b> on' % MinorityVoteWordsOutOf(abstain, mvotes)
        elif vote == "absent":
            print 'was <b>absent</b> with <b>%d</b> other nation%s when %d voted' % (absent - 1 or "zero", absent!=2 and "s" or "", mvotes)
        else:
            print ' error vote ', vote, ':::'
        print '</td>'
        print '<td class="col3"><a href="%s">%s</a></td>' % (EncodeHref({"pagefunc":"meeting", "docid":docid, "gid":href}), motiontext)
        print '<td class="col2"><i>%s</i></td>' % LongDate(ldate.strftime("%Y-%m-%d"))
        print '</tr>'
    print '</table>'

    #print '<ul>'
    #for mp in minorityvotes:
    #    print '<li>%s - <a href="%s">%s</a></li>' % (LongDate(mp["date"]), EncodeHref({"pagefunc":"meeting", "docid":mp["docid"], "gid":mp["gid"]}), mp["description"])
    #print '</ul>'

    if not scminorityvotes:
        return

    
    print '<h3 style="clear:both">Minority votes in the Security Council</h3>'
    print '<p>For a permanent member a vote against constitutes a veto.</p>'
    print '<ul class="scminorityvote">'
    for mp in scminorityvotes:
        sdesc = "Description"
        c.execute("SELECT heading, ldate FROM un_scheadings WHERE docid='%s'" % mp["docid"])
        a = c.fetchone()
        if a:
            sdesc = re.sub("<[^>]*>", "", a[0]).strip()
            if not sdesc:
                sdesc = "Ediscription"
        print '<li>%s - <a href="%s">%s</a></li>' % (LongDate(mp["date"]), EncodeHref({"pagefunc":"meeting", "docid":mp["docid"], "gid":mp["gid"]}), sdesc)
    print '</ul>'


def WriteAmbassadorList(nation, nationdata):
    # group by ambassadors
    ambmap = { }
    for mp in nationdata:
        if mp["lntype"] == "ambassador":
            ambmap.setdefault(mp["name"], set()).add((mp["sdate"], mp["docid"]))

    
    amblist = [ ]
    for name, sdatedocs in ambmap.iteritems():
        sk = re.search("(\S+)$", name).group(1) # last name
        amblist.append((sk, name, sdatedocs))
    
    amblist.sort()

    print '<h3>Ambassadors</h3>'
    print '<p>People who have spoken in the General Assembly or Security Council in the name of %s.  Sometimes ministers or heads of state take the place of the official ambassador of the day.</p>' % nation

    print '<table class="nationambassadortable" style="background-color:lightgray;">'
    print '<tr><th>Name</th><th>Speeches</th><th>First</th><th>Last</th></tr>'
    for ambl in amblist:
        href = EncodeHref({"pagefunc":"nationperson", "nation":nation, "person":ambl[1]})
        sdatedocs = ambl[2]
        ndocs = len(sdatedocs)
        firstdate = min(sdatedocs)[0]
        lastdate = max(sdatedocs)[0]
        print '<tr><td><a href="%s">%s</a></td>  <td>%d</td> <td>%s</td> <td>%s</td></tr>' % (href, ambl[1], ndocs, LongDate(firstdate), LongDate(lastdate))
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
    
    res = [ ]
    for nat in os.listdir(nationactivitydir):
        if nat[0] != ".":
            nation = re.sub("_", " ", nat[:-4])  # remove .txt
            flaghref = EncodeHref({"pagefunc":"flagpng", "width":100, "flagnation":nation})
            href = EncodeHref({"pagefunc":"nation", "nation":nation})
            res.append((nation, href, flaghref))
    
    res.sort()
    ncols = 4 
    colleng = (len(res) + ncols - 1) / ncols
    print '<table><tr>'
    for j in range(ncols):
        print '<td style="vertical-align:top;"><table>'
        for k in range(j * colleng, min(len(res), (j + 1) * colleng)):
            print '<tr>'
            nation, href, flaghref = res[k]
            print '<td class="smallflag_lis"><a href="%s"><img class="smallflag_lis" src="%s"></a></td>' % (href, flaghref)
            print '<td><a href="%s">%s</a></td>' % (href, nation)
            print '</tr>'
        print '</table></td>'
    print '</tr></table>'

