#!/usr/bin/python2.4
import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs
import datetime


def LoadAllVotes(rels):
    res = { }  # { nation : { voterecid: vote } }
    for nation in nationdates:
        res[nation] = { }

    for rel in rels:
        fin = open(rel)
        doccontent = fin.read()
        fin.close()

        document_id = re.search('<span class="code">([^<]*)</span>', doccontent).group(1)
        for recvotet in re.findall('<p class="votelist" id="(pg\d+-bk\d+)-pa\d+">(.*?)</p>', doccontent):
            #print document_id, recvotet[0]
            for voten in re.findall('<span class="([^"]*)">([^<]*)</span>', recvotet[1]):
                res[voten[1]][(document_id, recvotet[0])] = re.match(".*?([^\-]*)", voten[0]).group(1)

    #print res["Sudan"]
    return res

vweights = { "fafa":(2, 2), "abab":(1, 1), "agag":(5, 5), "abfa":(1, 2), "abag":(1, 2), "agfa":(0, 5) }
def CompareVDistance(voterec1, voterec2):
    voverlap = set(voterec1.keys())
    voverlap = voverlap.intersection(voterec2.keys())
    favfav, abab, agag = 0, 0, 0
    favab, favag, abag = 0, 0, 0
    #vsums = { "fafa":0, "abab":0, "agag":0, "abfa":0, "abag":0, "agfa":0 }
    wnum, wden = 0, 0
    for vl in voverlap:
        vll1 = voterec1[vl][:2]   # abstain and absent -> ab
        vll2 = voterec2[vl][:2]
        vsi = vll1 < vll2 and ("%s%s" % (vll1, vll2)) or ("%s%s" % (vll2, vll1))
        vwnum, vwden = vweights[vsi]
        wnum += vwnum
        wden += vwden
        #vsums[vsi] += 1
    assert wden >= wnum
    if wden == 0.0:
        return 0.5
    return (wden - wnum) * 1.0 / wden


nationlist = nationdates.keys()
nationlist.sort()
#print flatnationlist

def WriteVoteDistances(stem, htmldir, fout):
    rels = GetAllHtmlDocs(stem, False, False, htmldir)
    votetable = LoadAllVotes(rels)  # creates gigantic table of votes for these countries by loading all the files
    i = 1
    D = [ ]
    ns = [ ]
    ps = [ ]
    for nation1 in nationlist:
        ns.append("na%04d" % i)
        fout.write('na%04d = "%s";\n' % (i, nation1))
        ps.append("pa%04d" % i)
        continent = nationdates[nation1]["continent"] or "Antarctica"
        fout.write('pa%04d = "%s";\n' % (i, continent))
        res = [ ]
        for nation2 in nationlist:
            res.append("%.3f" % CompareVDistance(votetable[nation1], votetable[nation2]))
        D.append("r%04d" % i)
        fout.write('r%04d = [%s];\n' % (i, ", ".join(res)))
        i += 1
    fout.write("D=[%s;];\n" % "; ".join(D))
    fout.write("ns=[%s;];\n" % "; ".join(ns))
    fout.write("ps=[%s;];\n" % "; ".join(ps))


############################
currentyear = datetime.date.today().year
currentsession = currentyear - 1946
if datetime.date.today().month >= 9:
    currentsession += 1

meetseq = [ ]  # used to sort the SC and GAs
for gas in range(currentsession, 47, -1):
    meetseq.append(("%4d-09-01" % (gas + 1945), "GA", "%2d" % gas))
for scs in range(currentyear, 1992, -1):
    meetseq.append(("%4d-01-01" % scs, "SC", "%4d" % scs))
meetseq.sort()
meetseq.reverse()


def MakeNationMeetSeq(nation):
    nationparams = nationdates[nation]
    res = { }
    for meeto in meetseq:
        if meeto[1] == "GA":
            prevsdate = "%4d%s" % (int(nationparams["startdate"][:4]) - 1, nationparams["startdate"][4:])
            if prevsdate <= meeto[0] <= nationparams["enddate"]:
                res["GA%s" % meeto[2]] = [ 0, 0 ]
        if meeto[1] == "SC":
            if nationparams["startdate"][:4] <= meeto[0][:4] <= nationparams["enddate"][:4]:
                res["SC%s" % meeto[2]] = [ 0, 0 ]
    return res

def SetValuesOnGA(nationcounts, gacode, ftext):
    for nation in re.findall('<span class="nation">([^<]+)</span>', ftext):
        if nation == "Brunei Darussalam":
            continue
        if nation != "None":
            if gacode not in nationcounts[nation]:
                print nation, gacode
            nationcounts[nation][gacode][0] += 1

def WriteDocMeasurements(htmldir, pdfdir, fout):
    rels = GetAllHtmlDocs("", False, False, htmldir)
    gadcount = { }
    scdcount = { }
    scpcount = { }
    gavcount = { }
    scvcount = { }
    scrcount = { }
    garcount = { }

    nationyearactivity = { }

    for pdf in os.listdir(pdfdir):
        mgadoc = re.match("A-(\d\d)-[L\d]", pdf)
        mscdoc = re.match("S-(\d\d\d\d)-\d", pdf)
        mgares = re.match("A-RES-(\d\d)", pdf)
        mscprst = re.match("S-PRST-(\d\d\d\d)", pdf)
        mscres = re.match("S-RES-\d+\((\d\d\d\d)\)", pdf)

        if mgadoc:
            gadcount[mgadoc.group(1)] = gadcount.setdefault(mgadoc.group(1), 0) + 1
        elif mscdoc:
            scdcount[mscdoc.group(1)] = scdcount.setdefault(mscdoc.group(1), 0) + 1
        elif mgares:
            garcount[mgares.group(1)] = garcount.setdefault(mgares.group(1), 0) + 1
        elif mscprst:
            scpcount[mscprst.group(1)] = scpcount.setdefault(mscprst.group(1), 0) + 1
        elif mscres:
            scrcount[mscres.group(1)] = scrcount.setdefault(mscres.group(1), 0) + 1
        elif not re.search("A-\d\d-PV|S-PV-\d\d\d\d", pdf):
            print "What is this?", pdf

    nationcounts = { }
    for nation in nationdates:
        nationcounts[nation] = MakeNationMeetSeq(nation)

    for htdoc in rels:
        maga = re.search("A-(\d\d)-PV", htdoc)
        masc = re.search("S-PV-(\d\d\d\d)", htdoc)

        #if maga:    continue
        #if masc and masc.group(1)[:2] != "46":  continue

        fin = open(htdoc)
        ftext = fin.read()
        fin.close()
        #print htdoc

        if maga:
            gavcount[maga.group(1)] = gavcount.setdefault(maga.group(1), 0) + 1
            SetValuesOnGA(nationcounts, "GA%s" % maga.group(1), ftext)

        elif masc:
            mdate = re.search('<span class="date">(\d\d\d\d)-\d\d-\d\d</span>', ftext)
            scvcount[mdate.group(1)] = scvcount.setdefault(mdate.group(1), 0) + 1
            SetValuesOnGA(nationcounts, "SC%s" % mdate.group(1), ftext)

        else:
            print "what is this?", htdoc

    scyears = set()
    scyears.update(scdcount)
    scyears.update(scpcount)
    scyears.update(scrcount)
    scyears.update(scvcount)

    gasess = set()
    gasess.update(gadcount)
    gasess.update(garcount)
    gasess.update(gavcount)

    fout.write('\n<table class="docmeasuresshort">\n')
    fout.write('<tr class="heading"><th class="docmeasyear">Year</th><th class="docmeasdocs">Docs</th></tr>\n')
    for meeto in meetseq:
        if meeto[1] == "SC":
            sscy = meeto[2]
            scbase = "securitycouncil/%s" % sscy
            fout.write('<tr class="scrow"> <td class="scyear"><a href="%s" title="Security Council">%s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, scvcount.get(sscy, 0) + scrcount.get(sscy, 0) + scdcount.get(sscy, 0)))
        if meeto[1] == "GA":
            sgas = meeto[2]
            gabase = "generalassembly/%s" % sgas
            fout.write('<tr class="garow"> <td class="gasess"><a href="%s" title="General Assembly">Session %s</a></td> <td class="num"><a href="%s/documents">%d</a></td>\n' % (gabase, sgas, gabase, gavcount.get(sgas, 0) + garcount.get(sgas, 0) + gadcount.get(sgas, 0)))
    fout.write("</table>\n")

    fout.write('\n<table class="docmeasures">\n')
    fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Meetings</th> <th class="docmeasres">Number of Resolutions</th> <th class="docmeasdocs">Number of Documents</th></tr>\n');
    for meeto in meetseq:
        if meeto[1] == "SC":
            sscy = meeto[2]
            scbase = "securitycouncil/%s" % sscy
            fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td>%d</td> <td>%d</td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scvcount.get(sscy, 0), scrcount.get(sscy, 0), scbase, scdcount.get(sscy, 0) + scpcount.get(sscy, 0)))
        if meeto[1] == "GA":
            sgas = meeto[2]
            gabase = "generalassembly/%s" % sgas
            fout.write('<tr class="garow"> <td class="gasess"><a href="%s">Session %s</a></td> <td>%d</td> <td>%d</td> <td><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, gavcount.get(sgas, 0), garcount.get(sgas, 0), gabase, gadcount.get(sgas, 0)))
    fout.write("</table>\n")

    for nation in nationcounts:
        nmeetseq = nationcounts[nation]
        fout.write('\n<table class="nationmeas" id="%s">\n' % nation)
        fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Speeches</th></tr>\n');
        for meeto in meetseq:
            nmeeto = "%s%s" % (meeto[1], meeto[2])
            if nmeeto not in nmeetseq:
                continue
            if meeto[1] == "SC":
                sscy = meeto[2]
                scbase = "securitycouncil/%s" % sscy
                fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, nationcounts[nation][nmeeto][0]))
            if meeto[1] == "GA":
                sgas = meeto[2]
                gabase = "generalassembly/%s" % sgas
                fout.write('<tr class="scrow"> <td class="gayear"><a href="%s">Session %s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, gabase, nationcounts[nation][nmeeto][0]))
        fout.write("</table>\n")

