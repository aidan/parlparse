#!/usr/bin/python2.4
import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs, IsNotQuiet, pdfinfodir
import datetime
from pdfinfo import PdfInfo
from db import GetDBcursor

import unpylons.model as model


rdoc = '\((?:<a href[^>]*>[^<]*</a>|and|Add|L|para|Parts?|to|\([^\)]*\)|[IV\-\d\s,.:])+\)'
rtraildoc = '\s*%s$' % rdoc


frontcommlist = [ '(?:Request for the reopening of the consideration of )?agenda items? (?:\([a-z]+\)|%s|[\d\s,;]|</?i>|\(|\)|continued|and|agenda|items?)+' % rdoc,
                  'Item \d+(?:\s|\([a-z]\))*of the provisional agenda(?:\(|\)|</?i>|continued|\s)*',
                  'Organization of work of the General Assembly:\s*',
                  'Operational activities for development:\s*',
                  'High-level Plenary Meeting of the General Assembly:\s*',
                  'Follow-up .. the outcome of the \S* special session:\s*',
                  'Programme of activities of ',
                  'Cooperation between the United Nations and ',
                  'Launching of ',
                  'Implementation of the guidelines and ',
                  'Consolidation of the regime established by ',
                ]
rfrontcomm = re.compile('%s(?i)' % "|".join(frontcommlist))  # this one is matched

trailcommlist = [ ': reports? of the .{0,80}? (?:committee|secretary[ \-]general|conference)(?: \([^\)]*\)|for the.*)?\s*$',
                  ': draft (?:resolution|decision)s?\s*',
                  ': chapters considered directly',
                  ': procedures for the establishment',
                  ': opening of the Decade',
                  ': letter from the Netherlands',
                  ': (?:request for the )?reopening of the consideration of agenda item',
                  ': High-level plenary meeting',
                  ': High-level Dialogue',
                  ': progress in fashioning a region of peace',
                  ' \(?Article 19 of the Charter\)?',
                  ', allocation of items and organization of work',
                  ', adoption of the agenda',
                  ' \(\S+ Committee\)$',
                  ' (?:\(|</?i>|\)|continued)+$',
                  ' \(rule \d+\)$',
                  ' of the United Nations$',
                  ' by the President of the General Assembly$',
                  ': outcome of the International Ministerial Conference',
                  ' and returning such assets, in particular to the countries of origin',
                  ', questions relating to refugees, returnees and displaced persons and humanitarian questions',
                  ', including East Jerusalem, and of the Arab population in the occupied Syrian Golan over their natural resources',
                  ' by the specialized agencies and the international institutions associated with the United Nations',
                  ' and Other Arabs of the Occupied Territories',
                  ': report of the Conference on Disarmament',
                  ' \(IAEA\)$',
                  ' under Article 12, paragraph 2, of the Charter',
                  ' and of the twenty-fourth special session of the General Assembly',
                  ': one day of plenary meetings to review',
                  ' transmitted under Article \d+',
                  ' and other elections$',
                  ', including alternative approaches for improving the effective enjoyment of human rights and fundamental freedoms',
                  ' and programme of action$',
                  ' and related matters$',
                  ' recognized by the Organization of African Unity and/or by the League of Arab States$',
                  ': report of the Special Political and Decolonization Committee',
                  ': (?:note by|reports? of) the Secretary-General',
                  ': aftermath of the war and natural disasters$',
                  ' in the General Assembly$',
                  ' and Other Such Violations Committed',
                  ' which impede the implementation',
                  ' and its grave consequences for the established international system',
                  ': special plenary meetings at a high level',
                  ' Established Pursuant to',
                  ' on the work of its \S+ session$'
                ]
rtrailcomm = re.compile('%s(?i)' % "|".join(trailcommlist))  # this one is searched

generlinelist = [ '(?:Reports? of|Notes? by)? the (?:.{0,80}? committee|\S* working group|secretary[ \-]general|economic and social council|secretariat)',
                  'draft (?:resolution|decision)s?:?\s*',
                  'amendments?\s*$',
                  'amendments:',
                  'Article 19 of the Charter$',
                  'Administrative and budgetary aspects of the financing of the United Nations peace-?keeping operations:?$',
                  'Human resources management$',
                  'Curricul(?:a|um) vitae$',
                  'List of candidates$',
                  'Strengthening of the United Nations system$',
                  'First meeting of the Summit$',
                  '(?:Appointments|Elections) to fill vacancies in (?:subsidiary|principal) organs(?: and other elections| and other appointments)?$',
                  'Report of the Committee on the Exercise of the Inalienable Rights of the Palestinian People$',
                  'Request for the inclusion of an additional item$',
                  'Operational activities for development$',
                  'Maintenance of international security$',
                  'Election of the Executive Director',
                  'Letter dated',
                  'Letter from',
                  'Conference room paper$',
                  'Proposed programme budget',
                  'Joint Inspection Unit$',
                  'Adoption of the agenda and organization of work$',
                  'Strengthening of the coordination of humanitarian and disaster relief assistance of the United Nations, including special economic assistance$',
                  'Cooperation between the United Nations and regional and other organizations$',
                  'Integrated and coordinated implementation of and follow-up to the outcomes of the major United Nations conferences and summits in the economic, social and related fields$',
                  'Report on the work of the United Nations Open-ended Informal Consultative Process on Oceans and the Law of the Sea at its fifth meeting',
                  'Two plenary meetings devoted to the evaluation of the progress made in the implementation of the World Programme of Action for Youth to the year 2000 and Beyond',
                  'Sub-item \([a-z]\)$',
                  'International Civil Service Commission$',
                  'General Debate$',
                  'Report of the High-level Open-ended Working Group on the Financial Situation',
                  'Implementation of the international development strategy for the fourth united nations development decade',
                  'Note$',
                ]
rgenerline =re.compile('%s(?i)' % "|".join(generlinelist))  # this one is matched

substs = [ ("durable peace", "peace"),
           ("economic, commercial and financial embargo", "embargo"),
           ("the development and manufacture of new", "new"),
           ("to the world social situation and", "to"),
           ("and other activities which affect the interests", "activities"),
           ("of and follow-up to", "of"),
           ("of the administrative and financial", "of"),
           ("of the United Nations with", "with"),
           (" of the United Nations$", ""),  # these can slip through, because all truncations are not recursive
           ("Implementation of the Declaration on the Granting of Independence to", "Independence of"),
           ("Financing and liquidation", "Financing"),
           ("States set out in paragraph 3 \(c\).*$", "States"),
           (" effective ", " "),
           ("the use or threat of use", "threat"),
           ("Which May Be Deemed to Be Excessively Injurious or to Have", "which have"),
           ("for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991", "for the Prosecution of Persons in the Former Yugoslavia"),
           ("the Socialist People's Libyan Arab Jamahiriya", "Libya"),
           ("of the Assembly of Heads of State and Government of the Organization of African Unity on", "on"),
           #("for the Prosecution of Persons Responsible for Genocide and Other Serious Violations of International Humanitarian Law Committed in the Territory of Rwanda and Rwandan Citizens Responsible for Genocide and Other Such Violations Committed in the Territory of Neighbouring States between 1 January and 31 December 1994", "for the Prosecution of Persons Responsible for Genocide and Other Serious Violations of International Humanitarian Law Committed in the Territory of Rwanda and Rwandan Citizens Responsible for Genocide  in the Territory of Neighbouring States between 1 January and 31 December 1994"),
         ]

class AgendaHeading:
    def __init__(self, sdate, docid, subheadingid, agendanumstr, titletext):
        self.sdate = sdate
        self.docid = docid
        mdocid = re.match("A-(\d\d)-PV\.(\d+)$", docid)
        assert mdocid, docid
        self.nsession = int(mdocid.group(1))
        self.nmeeting = int(mdocid.group(2)) # so we can sort by it
        self.sortval = (self.nsession, self.nmeeting)

        self.subheadingid = subheadingid
        self.agendanumstr = agendanumstr
        self.agendanums = agendanumstr.split(",")


        for agendanum in self.agendanums:
            sa = agendanum.split("-")
            assert len(sa) == 2
            assert int(sa[1]) == self.nsession

        # break the agenda text up by paragraph
        self.titletext = titletext
        self.titlelines = re.findall("<(?:p|blockquote)[^>]*>(.*?)\.?</(?:p|blockquote)>", titletext)

        # loop forwards to remove agenda items as highest priority
        i = 0
        while i < len(self.titlelines):
            # remove the agenda items title parts
            magmatch = rfrontcomm.match(self.titlelines[i])
            if magmatch:
                if magmatch.end(0) == len(self.titlelines[i]):
                    if len(self.titlelines) > 1:
                        del self.titlelines[i]
                        continue
                else:
                    self.titlelines[i] = self.titlelines[i][magmatch.end(0):].capitalize()
            i += 1

        # loop backwards and trim as much as possible from each row of text
        for i in range(len(self.titlelines) - 1, -1, -1):
            # remove trailing references to documents in parentheses
            mtraildoc = re.search(rtraildoc, self.titlelines[i])
            if mtraildoc:
                if mtraildoc.start(0) == 0:
                    if len(self.titlelines) > 1:
                        del self.titlelines[i]
                        continue
                else:
                    self.titlelines[i] = self.titlelines[i][:mtraildoc.start(0)]

            # remove trailing references to reports   ": report of the Fifth Committee (Part III)"
            while True:  # recurse
                mtrailcommrep = rtrailcomm.search(self.titlelines[i])
                if not mtrailcommrep:
                    break
                if mtrailcommrep.start(0) == 0:
                    if len(self.titlelines) > 1:
                        del self.titlelines[i]
                        continue
                else:
                    self.titlelines[i] = self.titlelines[i][:mtrailcommrep.start(0)]

            # remove entire lines that are generic
            mgenerline = rgenerline.search(self.titlelines[i])
            if mgenerline and len(self.titlelines) > 1:
                del self.titlelines[i]
                continue

            # substitutions
            for substm, substr in substs:
                self.titlelines[i] = re.sub(substm, substr, self.titlelines[i])


        if re.search("agenda item(?i)", self.titlelines[0]) and IsNotQuiet():
            print "Poss bad agenda item", self.titlelines
        assert self.titlelines
        assert not re.match("\s*$", self.titlelines[0]), self.titletext
        #self.agtitle = " || ".join(self.titlelines)

    def SeeTextForHeading(self, stext):
        self.numspeeches, self.numparagraphs = 0, 0
        for mspoke in re.finditer('(?s)<div class="spoken"[^>]*>(.*?)</div>', stext):
            self.numspeeches += 1
            self.numparagraphs =+ len(re.findall('<(?:p|blockquote)', mspoke.group(1)))
        self.numdocuments = len(set(re.findall('<a href="([^"]*)"', stext)))  # unique documents
        self.numvotes = len(set(re.findall('<div class="recvote"', stext)))

def CleanupTitles(aggroup):
    for ag0, ag in reversed(aggroup):
        letteredtitles = [ ]
        for i in range(len(ag.titlelines)):
            ag.titlelines[i] = re.sub("<[^>]*>", "", ag.titlelines[i])
            mlett = re.match("\([a-z]\)\s*", ag.titlelines[i])
            if mlett:
                ag.titlelines[i] = ag.titlelines[i][mlett.end(0):]
                letteredtitles.append(i)
        if letteredtitles:
            ag.titlelines = [ag.titlelines[i]  for i in letteredtitles]


# find common title
def FindDelCommonTitle(agendanum, aggroup):
    CleanupTitles(aggroup)

    titlelinescount = { }
    mostcommon = (None, 0)

    ncountgendebate = 0
    ncountaddressby = 0
    ncountother = 0

    for ag0, ag in reversed(aggroup):
        for titleline in reversed(ag.titlelines):

            if re.match("general debate(?i)", titleline):
                ncountgendebate += 1
            elif re.match("address by(?i)", titleline):
                ncountaddressby += 1
            else:
                ncountother += 1

            if titleline in titlelinescount:
                titlelinescount[titleline] += 1
            else:
                titlelinescount[titleline] = 1
            if titlelinescount[titleline] >= mostcommon[1]:
                mostcommon = (titleline, titlelinescount[titleline])

    # now delete this title from the lists where possible
    for ag0, ag in aggroup:
        for i in range(len(ag.titlelines) - 1, -1, -1):
            if len(ag.titlelines) > 1 and ag.titlelines[i] == mostcommon[0]:
                del ag.titlelines[i]

    mctitle = mostcommon[0]
    if re.match("(?:natdis|condolence)", agendanum):
        return "Condolences", "Procedure"
    if ncountother == 0 and ncountaddressby != 0:
        return "Addresses by ministers", "Procedure"
    if re.search("financing|financial|budget|economic|expenses|pension(?i)", mctitle):
        return mctitle, "Finance"
    if re.search("meditation|address by|addresses by|programme of work|organization of work|admission of|election|appointment(?i)", mctitle):
        return mctitle, "Procedure"
    if re.search("report(?i)", mctitle):
        return mctitle, "Reports"
    if re.search("question of|situation in(?i)", mctitle):
        return mctitle, "Situations"
    if re.search("terrorism|arms|war|forces|military|weapon|nuclear|conflict|mine|test-ban|aggression|disarmament(?i)", mctitle):
        return mctitle, "Violence"
    if re.search("human rights|rights of|right of|discrimination|women(?i)", mctitle):
        return mctitle, "Humanitarian"
    return mctitle, "Other"


# this takes a group of
def WriteAgendaGroup(mccategory, mctitle, agendanum, aggroup, fout, agendasperdoc):

    fout.write('\n<div class="agendagroup" agendanum="%s">\n' % agendanum)
    fout.write('\t<h3>%s</h3>\n' % mctitle)
    for ag0, ag in aggroup:
        agtitle = " || ".join(ag.titlelines)
        fout.write('\t<p>')
        fout.write('<a href="../html/%s.html#%s">%s</a>' % (ag.docid, ag.subheadingid, ag.sdate))
        fout.write(' <span class="documentid">%s</span>' % ag.docid)
        fout.write(' <span class="subheadingid">%s</span>' % ag.subheadingid)
        fout.write(' <span class="date">%s</span>' % ag.sdate)
        fout.write(' <span class="numspeeches">%d</span>' % ag.numspeeches)
        fout.write(' <span class="numparagraphs">%d</span>' % ag.numparagraphs)
        fout.write(' <span class="numdocuments">%d</span>' % ag.numdocuments)
        fout.write(' <span class="numvotes">%d</span>' % ag.numvotes)
        fout.write(' <span class="agendanum">%s</span>' % agendanum)
        fout.write(' <span class="agtitle">%s</span>' % agtitle)
        fout.write(' <span class="aggrouptitle">%s</span>' % mctitle)
        fout.write(' <span class="agcategory">%s</span>' % mccategory)
        fout.write('</p>\n')

        if agendasperdoc:
            agendasperdoc.setdefault(ag.docid, [ ]).append((ag.subheadingid, ag.agendanumstr, agtitle))
    fout.write('</div>\n')



#<div class="subheading" id="pg001-bk02" agendanum="9-49">
#	<p id="pg001-bk02-pa01">Agenda item 9 <i>(continued)</i></p>
#	<p class="boldline-p" id="pg001-bk02-pa02">General debate</p>
#</div>
def AddAgendaGroups(agendagroups, sdate, docid, ftext):
    res = [ ] # the other result is the agendagroups map
    agheadings = re.finditer('(?s)<div class="subheading" id="([^"]*)" agendanum="([^"]*)">(.*?)</div>', ftext)
    agendaheading = None
    for magheading in agheadings:
        if agendaheading:
            agendaheading.SeeTextForHeading(ftext[agendaheadingE:magheading.start(0)])
        agendaheading = AgendaHeading(sdate, docid, magheading.group(1), magheading.group(2), magheading.group(3))
        res.append(agendaheading)        
        for agendanum in agendaheading.agendanums:
            if agendanum not in agendagroups:
                agendagroups[agendanum] = [ ]
            agendagroups[agendanum].append((agendaheading.sortval, agendaheading))
        agendaheadingE = magheading.end(0)

    if agendaheading:  # end of final heading
        agendaheading.SeeTextForHeading(ftext[agendaheadingE:])
    return res

#def AddAgendasToDB(docid, htdoc):
#    fin = open(htdoc)
#    ftext = fin.read()
#    fin.close()
#    mdate = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', ftext)
#    sdate = mdate.group(1)
    # not complete


def WriteAgendaSummaries(stem, htmldir, fout, agendaindexdir):
    rels = GetAllHtmlDocs("", False, False, htmldir)

    agendagroups = { }
    for htdoc in rels:
        maga = re.search("(A-\d\d-PV\.\d+)\.(?:unindexed\.)?html", htdoc)
        masc = re.search("(S-PV.\d+(?:-(?:Resu|Part)\.\d)?)\.(?:unindexed\.)?html", htdoc)

        if not maga:
            if not masc:
                print "Whatis", htdoc
            continue

        docid = maga.group(1)
        
        if stem and not re.match(stem, docid):
            continue

        fin = open(htdoc)
        ftext = fin.read()
        fin.close()

        mdate = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', ftext)
        sdate = mdate.group(1)

        if IsNotQuiet():
            print docid,
        agendasdoc = AddAgendaGroups(agendagroups, sdate, docid, ftext)
        #if len(agendagroups) > 100:
        #    print "preeeematureabort"        
        #    break

        # copy agenda data into database        
        gaagindoc = [ ]
        for ag in agendasdoc:
            gaagindoc.append((ag.subheadingid, ag.agendanumstr, "||".join(ag.titlelines)))
        model.load_ga_debate(docid, sdate, gaagindoc)

    #return

    # the agendagroups are lists of agenda items; call them topics
    allagendas = [ ]
    recentagendas = [ ]
    for agendanum, aggroup in agendagroups.iteritems():
        agsession = aggroup[0][1].nsession
        mctitle, mccategory = FindDelCommonTitle(agendanum, aggroup)

        model.load_ga_agendanum(agsession, agendanum, mctitle, mccategory, [ (ag.docid, ag.subheadingid)  for ag0, ag in aggroup ])

        allagendas.append((agsession, mccategory, mctitle, agendanum, aggroup))
        recentagendas.extend(aggroup)


    allagendas.sort()
    agendasperdoc = { }

    #for r in allagendas:
    #    print r[0], r[1], r[3], len(r[4])
    #sys.exit(0)

    fout.write('<html><head>\n<style type="text/css">\n')
    fout.write('p { color: #7f007f; padding-left:20; margin-top:0; margin-bottom:0; }\n')
    fout.write('.documentid, .date, .subheadingid, .aggrouptitle, .agcategory, .agendanum  { display: none; }\n')
    fout.write('.numspeeches, .numparagraphs, .numdocuments, .numvotes { border: thin black solid; }\n')
    fout.write('h2 { text-decoration: underline; text-align: center; }\n')
    fout.write('</style>\n</head>')
    fout.write('<body>\n')

    prevagsession, prevmccategory = None, None
    for (agsession, mccategory, mctitle, agendanum, aggroup) in allagendas:
        if agsession != prevagsession:
            fout.write('\n<h1>Session %s</h1>\n' % agsession)
            prevagsession = agsession
        if mccategory != prevmccategory:
            fout.write('\n<h2>%s</h2>\n' % mccategory)
            prevmccategory = mccategory
        WriteAgendaGroup(mccategory, mctitle, agendanum, aggroup, fout, agendasperdoc)

        if agendaindexdir:
            fagname = os.path.join(agendaindexdir, agendanum + ".html")
            fagout = open(fagname, "w")
            WriteAgendaGroup(mccategory, mctitle, agendanum, aggroup, fagout, None)
            fagout.close()

    recentagendas.sort()
    recentagendas.reverse()
    agnumrecent = "recent"
    fagname = os.path.join(agendaindexdir, agnumrecent + ".html")
    fagout = open(fagname, "w")
    WriteAgendaGroup("Recent", "Recent", agnumrecent, recentagendas[:100], fagout, None)
    fagout.close()

    fout.write('</body>\n</html>\n')


    # now make up the pdfinfo stuff so that every file has knowledge of what the agendas should be called
    # has to be done after the agendas are put together and their names have been sorted out
    for docid, agendascontained in agendasperdoc.iteritems():
        pdfinfo = PdfInfo(docid)
        pdfinfo.UpdateInfo(pdfinfodir)
        agendascontained.sort()
        pdfinfo.agendascontained = agendascontained # replace it
        pdfinfo.WriteInfo(pdfinfodir)


