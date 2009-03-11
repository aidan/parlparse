#!/usr/bin/python
# -*- coding: latin-1 -*-

import sys
import re
import os
import urllib2
from nations import nationdates
from unmisc import IsNotQuiet
import datetime
#from db import GetDBcursor, escape_string

import unpylons.model as model


def ScrapeSCSummaries(scsummariesdir):
    #print "Skipping ScrapeSCSummaries"
    #return

    currentdate = datetime.date.today()
    currentyear = currentdate.year
    currentmonth = currentdate.month
    for y in range(1994, currentyear + 1):
        f = os.path.join(scsummariesdir, "scact%d.html" % y)
        url = "http://www.un.org/Depts/dhl/resguide/scact%d.htm" % y
        if y == currentyear or (y == currentyear - 1 and currentmonth == 1) or not os.path.isfile(f):
            if IsNotQuiet():
                print "Scraping", url
            fin = urllib2.urlopen(url)
            scindext = fin.read()
            fin.close()

            fout = open(f, "w")
            fout.write(scindext)
            fout.close()

#<th><font size="2">Meeting<br>
#                  Record</font></th>
#                <th><font size="2">Date</font></th>
#                <th><font size="2">Press<br>
#                  Release</font></th>
#                <th><font size="2">Topic</font></th>
#                <th><font size="2">Security Council<br>
#                  Action / Vote</font></th>

#    <tr valign="top">
#               <td> <font size="2"><a target="_blank" href="http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/PV.3485&Lang=E">S/PV.3485</a></font></td>
#                <td><font size="2"> 22 Dec. </font></td>
#                <td><font size="2"> SC/5971 </font></td>
#                <td><font size="2"> Burundi </font></td>
#                <td> <font size="2"><a target="_blank" href="http://daccess-ods.un.org/access.nsf/Get?Open&DS=S/PRST/1994/82&Lang=E">S/PRST/1994/82</a> </font>
#                  </td>
#              </tr>


def ExtractPVlinks(meetingrecs):
    mpvcode = re.match("S/PV\.(\d+)\s*(?:\(Resumption\s*([I\d]*\))\s*)?(?:\(Part\s*(I*)\)\s*)?(\(closed\))?$", meetingrecs[0])
    assert mpvcode, meetingrecs
    #print meetingrecs
    pvcode = "S-PV-%s" % mpvcode.group(1)
    meetingnumber = int(mpvcode.group(1))
    secondarymeetingnumber = 0
    if mpvcode.group(2):  # needs to have the bracket so there is always something
        rv = mpvcode.group(2)[:-1]
        if not rv or rv == "I":
            rv = "1"
        pvcode = "%s-Resu.%d" % (pvcode, int(rv))
        secondarymeetingnumber = int(rv)

    if mpvcode.group(3):
        assert not secondarymeetingnumber  # parts and resu. don't mix
        if mpvcode.group(3) == "I":
            rp = 1
        elif mpvcode.group(3) == "II":
            rp = 2
        pvcode = "%s-Part.%d" % (pvcode, rp)
        secondarymeetingnumber = rp

    corrs = [ ]
    for corr in meetingrecs[1:]:
        if corr:
            mcorr = re.match("Corr\.(\d)\s*$", corr)
            assert mcorr, meetingrecs
            assert int(mcorr.group(1)) >= len(corrs) + 1, meetingrecs  # sometimes misses a corr
            corrs.append("%s-Corr.%d" % (pvcode, int(mcorr.group(1))))

    #print pvcode, meetingrecs[0]
    if mpvcode.group(4) and IsNotQuiet():
        print "the closed one:", pvcode
    return pvcode, (meetingnumber, secondarymeetingnumber), corrs


monthdict = { "Jan.":1, "Feb.":2, "Mar.":3, "Apr.":4, "May":5, "June":6, "July":7, "Aug.":8, "Sept.":9, "Sep.":9, "Oct.":10, "Nov.":11, "Dec.":12 }
def ExtractPVdate(daterecstr, year):
    mdate = re.match("(\d+)(?:\s*\+\s*(\d+))?\s+([\w\.]+)$", daterecstr)
    assert mdate, daterecstr
    if mdate.group(2):
        assert int(mdate.group(2)) == int(mdate.group(1)) + 1
    month = mdate.group(3)
    assert month in monthdict, daterecstr
    return "%s-%02d-%02d" % (year, monthdict[month], int(mdate.group(1)))




# list just to force through the changes in names
flattopicmapstr = """
Children and armed conflicts
Children and armed conflict

Letter dated 22 November 2006 from the Secretary-General addressed to the President of the Security Council
Nepal

Letter dated 4 July 2006 from the Permanent Representative of Japan to the United Nations addressed to the President of the Security Council
Nuclear testing--Democratic People's Republic of Korea

Peace and security--nuclear tests by India
Nuclear testing--India

Peace and security--nuclear tests by India and Pakistan
Nuclear testing--India--Pakistan

Peace and security--nuclear tests by Pakistan
Nuclear testing--Pakistan

Peace and security--terrorist acts Peace and security--Africa
Peace and security--terrorist acts

Meeting of the Security Council with the potential troop and civilian police-contributing countries to the proposed United Nations peace-keeping operation in Liberia
Troop contributions--Liberia

Maintenance of peace and security
Peace and security

Exit strategy for peace-keeping
Peace-keeping

Peacekeeping operations
Peace-keeping

Post-conflict peace-building
Peace-building

Peacekeeping--troop-contributing countries
Troop contributions--Peace-keeping

Solomon Islands--peace agreement
Solomon Islands

South Africa--Elections
South Africa

Security Council working methods and procedure
Security Council procedure

Security Council meetings in Nairobi
Security Council procedure

Peace and security--regional organizations
Peace and security

Peace and security--terrorist acts committed in Kenya and the United Republic of Tanzania
Peace and security--terrorist acts--Kenya--Tanzania

Peace and security--terrorist acts committed in the United States
Peace and security--terrorist acts--United States

High-level meeting on the anniversary of 11 September 2001--acts of international terrorism
Peace and security--terrorist acts--United States

International Tribunal--Rwanda & Yugoslavia
International Tribunal--Rwanda--Former Yugoslavia

Interim accord between Greece and the former Yugoslav Republic of Macedonia
Former Yugoslav Republic of Macedonia--Greece

The former Yugoslav Republic of Macedonia
Former Yugoslav Republic of Macedonia

Timor-Leste
East Timor

Federal Republic of Yugoslavia (Serbia and Montenegro)--Sanctions
Federal Republic of Yugoslavia--Sanctions

Federal Republic of Yugoslavia--termination of sanctions
Federal Republic of Yugoslavia--Sanctions

Israel-Syrian Arab Republic
Israel--Syria

Situation along the borders of Guinea, Liberia, Sierra Leone
Guinea--Liberia--Sierra Leone

Stand-by arrangements for peace-keeping
Peace-keeping

Civilian police in peace-keeping
Peace-keeping

Civilian aspects of conflict management and peace-building
Peace-building

Strengthening cooperation with troop-contributing countries
Troop contributions

Troop contributions--Ethiopia and Eritrea
Troop contributions--Ethiopia--Eritrea

The situation in the occupied Arab territories
Palestinian question

Food aid in context of conflict settlement
Food

Trusteeship System--Palau
Palau

The siuation in the former Yugoslavia
Former Yugoslavia

The situation in the former Yugoslavia
Former Yugoslavia

The situation in the Middle East--UN Disengagement Observer Force
Middle East--UN Disengagement Observer Force

United Nations Protection Force
UN Protection Force

Yugoslavia
Federal Republic of Yugoslavia

Peace and security--Africa's food crisis
Food crisis and aid--Africa

Conflicts in Africa
Africa

Pacific settlement of disputes
Role of United Nations

Justice and the rule of law--the United Nations role
Role of United Nations

Complex crises and UN response
Role of United Nations

Prevention of armed conflicts
Role of United Nations

The role of the Security Council in humanitarian crises
Role of United Nations

Security of UN personnel
Protection of UN personnel

Protection of civilians in armed conflict
Civilians in armed conflict

Security Council Summit--maintaining peace and security
Role of United Nations

Rwandan and Burundian refugees in Zaire
Rwandan--Burundi--Zaire

Security Council mission--Sudan and Chad
Security Council mission--Sudan--Chad

Security Council mission--Sudan, Chad and the African Union headquarters in Addis Ababa
Security Council mission--Sudan--Chad

Strengthening international law
Role of United Nations

Commemoration of the end of World War II in Europe
Commemoration of the end of World War II

Commemoration of the end of World War II in the Asia-Pacific region
Commemoration of the end of World War II

Aggression against non-nuclear weapon states
Nuclear Weapons

African Nuclear-Weapon-Free Zone Treaty
Nuclear Weapons--Africa

African Union
Africa

AIDS and peace-keeping
Peace-keeping--AIDS

AIDS in Africa
Africa--AIDS

Agenda for Peace
The fiftieth anniversary of the UN

Reports of the Secretary-General on the Sudan
Sudan

Consideration of the draft report of the Security Council to the General Assembly
Annual report to the General Assembly

Federal Republic of Yugoslavia--Chinese Embassy
Federal Republic of Yugoslavia--China

High-level meeting--combating terrorism
Terrorism

International Tribunals--appointment of Prosecutor
International Tribunal

International Tribunal--Yugoslavia
International Tribunal--Former Yugoslavia

Meeting with countries contributing troops to the UN Disengagement Observer Force
Troop contributions--UN Disengagement Observer Force

Meeting with countries contributing troops to the United Nations Disengagement Observer Force
Troop contributions--UN Disengagement Observer Force

Meeting with countries contributing troops to the UN Interim Force in Lebanon
Troop contributions--UN Interim Force in Lebanon

Meeting with countries contributing troops to the UN Iraq--Kuwait Observation Mission
Troop contributions--UN Iraq-Kurait Observation Mission

Non-proliferation of weapons of mass destruction
Non-proliferation

Role of business in conflict prevention, peace-keeping and post-conflict peace-building
Peace-building

Role of civil society in conflict prevention and the pacific settlement of disputes
Peace-building

Role of civil society in post-conflict peace-building
Peace-building

UN West Africa Office
West Africa

UN peace-keeping--Dag Hammarskjold Medal
Peace-keeping--Dag Hammarskjold Medal

United Nations peace-keeping
Peace-keeping

Women and peace and security
Women
"""

flattopicmap = { }
mfrom = None
for mval in flattopicmapstr.split("\n"):
    mval = mval.strip()
    if mval:
        if mfrom:
            flattopicmap[mfrom] = mval
            mfrom = None
        else:
            mfrom = mval


def InitialCleanupTopic(st, year):
    st = re.sub("</?font[^>]*>|<br>|<p>", " ", st).strip()
    st = re.sub("\s\s+", " ", st)
    st = re.sub("ICJ(?:\-+[Ee]lection)?", "International Court of Justice", st)
    st = re.sub("(?:international )?peace[ \-]?keeping(?: operations)?", "peace-keeping", st)
    st = re.sub("peace[ \-]?building", "peace-building", st)
    st = re.sub(" \[ministerial level\]| \[report on 1994 genocide\]| \(summary paper:[^)]*\)| \(18-19 November 2004\)", "", st)
    st = re.sub("(?:Recommendation for the )?(?:re)?appointment of (?:the )?Secretary-General(?: of the United Nations)?$(?i)", "Appointment of the Secretary-General", st)
    st = re.sub("Herzegovina-Croatia", "Herzegovina--Croatia", st)
    st = re.sub("(Chad|Ethiopia)-Sudan", "\\1--Sudan", st)
    st = re.sub("Eritrea-Ethiopia", "Eritrea--Ethiopia", st)
    st = re.sub("(Democratic People's Republic of Korea|Cuba)-USA", "\\1--United States", st)
    st = re.sub("\s*[/+:]\s*", "--", st)
    st = re.sub(", including the Palestinian question", "--Palestinian question", st)
    st = re.sub("(?:HIV--)?AIDS", "AIDS", st)
    st = re.sub("(Kosovo) \([^)]*\)", "\\1", st)
    if year == "1996":  st = re.sub("Korea$", "Democratic People's Republic of Korea", st)
    st = re.sub("Iraq-Kuwait(?: \[termination of trade and financial sanctions\])?", "Iraq--Kuwait", st)
    st = re.sub("Annual [Rr]eport of the Security Council", "Annual report", st)
    st = re.sub("-IAEA", "--International Atomic Energy Authority", st)
    st = re.sub('<a href="[^"]*">[^<]*<\-*a>', "", st)

    st = re.sub("OSCE", "Organization for Security and Cooperation in Europe", st)
    st = re.sub("Briefings by[^\-]*--\s*", "Briefings--", st)
    #st = re.sub("Briefing by(?: Special Envoy)?", "Briefings--", st)
    st = re.sub("Meeting with countries contributing troops to the UN (?:Mission of Observers|Mission|Stabilization Mission|Operation|Mission of Support|Observer Mission|Organization Mission|Transitional Administration|Peacekeeping Force|Mission for the Referendum) in (?:the )?", "Troop contributions--", st)
    st = re.sub("Mine (?:action for |[Cc]learance--)", "Mine clearance--", st)

    st = re.sub("UNDOF", "UN Disengagement Observer Force", st)
    st = re.sub("UNIFIL", "UN Interim Force in Lebanon", st)
    st = re.sub("Middle East situation", "Middle East", st)
    st = re.sub("gggg", "gggg", st)
    st = re.sub("gggg", "gggg", st)
    st = re.sub("gggg", "gggg", st)

    if re.match("Admission of new Members$", st):
        assert year == "2006"
        st = "%s--Montenegro" % st
    mwrappup = re.match("Wrap-up discussion on the work of the Security Council for the month of \w+\s*", st)
    if mwrappup:
        if mwrappup.end(0) == len(st):
            st = "%s %s" % (st, year)
        else:
            st = st[mwrappup.end(0):]

    st = flattopicmap.get(st, st)
    return st


rrow = re.compile('(?s)<td[^>]*>(.*?)\s*(?:</td>)?\s*<td[^>]*>(.*?)\s*</td>\s*<td[^>]*>(.*?)\s*</td>\s*<td[^>]*>(.*?)\s*</td>')
class SCrecord:
    def __init__(self, year, row, htmldir):

        mrow = rrow.match(row)
        assert mrow, row
        meetingrecstr = mrow.group(1)
        meetingrecstr = re.sub("</?font[^>]*>|<br>", " ", meetingrecstr).strip()
        meetingrecs = re.findall("<a[^>]*>\s*([^<]*)</a>", meetingrecstr)
        assert meetingrecs, row
        self.pvcode, self.meetingorder, self.corrs = ExtractPVlinks(meetingrecs)

        daterecstr = mrow.group(2)
        daterecstr = re.sub("</?font[^>]*>", " ", daterecstr).strip()
        self.sdate = ExtractPVdate(daterecstr, year)
        #print sdate
        hfile = os.path.join(htmldir, self.pvcode + ".html")
        hfileunindexed = os.path.join(htmldir, self.pvcode + ".unindexed.html")
        self.bparsed = os.path.isfile(hfile) or os.path.isfile(hfileunindexed)

        # not too worried about these for now
        pressrecstr = mrow.group(3)
        pressrecstr = re.sub("</?font[^>]*>", " ", pressrecstr).strip()
        self.pressrecstr = pressrecstr

        self.otopicrecstr = InitialCleanupTopic(mrow.group(4), year)
        self.minutes = -1
        self.datetime = self.sdate
        self.datetimeend = self.sdate

    # maybe this could pull out a longer summary from the agenda where possible
    def ScanHtmlMeet(self, htmlfile):
        fin = open(htmlfile)
        ftext = fin.read()
        fin.close()
        self.numspeeches, self.numparagraphs = 0, 0
        for mspoke in re.finditer('(?s)<div class="spoken"[^>]*>(.*?)</div>', ftext):
            self.numspeeches += 1
            self.numparagraphs =+ len(re.findall('<(?:p|blockquote)', mspoke.group(1)))
        self.numdocuments = len(set(re.findall('<a href="([^"]*)"', ftext)))  # only count unique entries, not multiple mentions
        self.numvotes = len(set(re.findall('<div class="recvote"', ftext)))

        mdocument_date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', ftext)
        assert mdocument_date, "not found date in file %s" % htmlfile
        document_date = mdocument_date.group(1)
        mdocument_times = re.search('<span class="time">(\d\d:\d\d)</span><span class="rosetime">(\d\d:\d\d)</span>', ftext)
        assert mdocument_times, "not found date in file %s" % htmlfile
        document_time = mdocument_times.group(1)
        self.datetime = "%s %s:00" % (document_date, document_time)
        document_timeend = mdocument_times.group(2)
        self.datetimeend = "%s %s:00" % (document_date, document_timeend)  # doesn't account for past midnight
                
        hourminutestart = map(int, document_time.split(":"))
        hourminuteend = map(int, document_timeend.split(":"))
        self.minutes = (hourminuteend[0] - hourminutestart[0]) * 60 + (hourminuteend[1] - hourminutestart[1])


    def FindTopicCats(self, htmldir, pdfdir):
        self.numspeeches, self.numparagraphs, self.numdocuments, self.numvotes = -1, -1, -1, -1
        htmlfile = os.path.join(htmldir, self.pvcode + ".html")
        print htmlfile, "hhhh"
        pdffile = os.path.join(pdfdir, self.pvcode + ".pdf")
        if os.path.isfile(htmlfile):
            self.doclink = '"../html/%s.html" class="lkhtml"' % self.pvcode
            self.ScanHtmlMeet(htmlfile)
        elif os.path.isfile(pdffile):
            self.doclink = '"../pdf/%s.pdf" class="lkpdf"' % self.pvcode
        else:
            self.doclink = '"../pdf/%s.pdf" class="lkmissing"' % self.pvcode

        if re.match("Wrap-up discussion on the work of the Security Council for the month", self.otopicrecstr):
            self.topics = [ "Wrap-up discussion for the month" ]
            return

        self.topics = [ ]
        for a in self.otopicrecstr.split("--"):
            if re.match("[A-Z]", a):
                self.topics.append(a)
            else:
                self.topics.append(a[:1].upper() + a[1:])

        # do this to over-ride the splitting and see the original files
        #self.topics = [ self.otopicrecstr ]



def WriteSCSummaries(stem, scsummariesdir, htmldir, pdfdir):
    screcords = [ ]
    
    # this is iterating through the pages of indexes, so will be in order    
    for lf in reversed(sorted(os.listdir(scsummariesdir))):
        if re.match("\.svn", lf):
            continue
        myear = re.search("\d\d\d\d", lf)
        assert myear, lf
        year = myear.group(0)
        if stem and not re.match(stem, year):
            continue
        if IsNotQuiet():
            print "year", year
        
        f = os.path.join(scsummariesdir, lf)
        fin = open(f)
        ftext = fin.read()
        fin.close()

        for mrow in re.finditer('(?s)<tr valign="top">(.*?)</tr>', ftext):
            row = mrow.group(1).strip()
            screcord = SCrecord(year, row, htmldir)
            screcord.FindTopicCats(htmldir, pdfdir)
            screcord.nextpvcode = screcords and screcords[-1].pvcode or None
            screcords.append(screcord)
            model.load_sc_topics(screcord.pvcode, screcord.otopicrecstr, screcord.datetime, screcord.datetimeend, 
                                 screcord.topics, screcord.minutes, screcord.numspeeches, screcord.numparagraphs, screcord.numvotes, screcord.nextpvcode)
    




