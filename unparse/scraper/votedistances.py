#!/usr/bin/python2.4
import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs

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


def WriteDocMeasurements(htmldir, pdfdir, fout, foutshort):
    rels = GetAllHtmlDocs("", False, False, htmldir)
    gadcount = { }
    scdcount = { }
    scpcount = { }
    gavcount = { }
    scvcount = { }
    scrcount = { }
    garcount = { }

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

    for htdoc in rels:
        maga = re.search("A-(\d\d)-PV", htdoc)
        masc = re.search("S-PV-(\d\d\d\d)", htdoc)
        if maga:
            gavcount[maga.group(1)] = gavcount.setdefault(maga.group(1), 0) + 1
        elif masc:
            fin = open(htdoc)
            while True:
                flin = fin.readline()
                mdate = re.search('<span class="date">(\d\d\d\d)-\d\d-\d\d</span>', flin)
                if mdate:
                    break
            scvcount[mdate.group(1)] = scvcount.setdefault(mdate.group(1), 0) + 1
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

    foutshort.write('<table class="docmeasuresshort">\n')
    foutshort.write('<tr class="heading"><th class="docmeasyear">Year</th><th class="docmeasbody">Body</a><th class="docmeasdocs">Docs</th></tr>\n')
    
    fout.write('<table class="docmeasures">\n')
    fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Meetings</th> <th class="docmeasres">Number of Resolutions</th> <th class="docmeasdocs">Number of Documents</th></tr>\n');
    for gas in range(int(max(gasess)), 47, -1):
        sgas = "%2d" % gas
        sscy = "%4d" % (gas + 1946)
        scbase = "securitycouncil/%s" % sscy
        gabase = "generalassembly/%s" % sgas
        
        foutshort.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td class="bbody">SC</td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, scvcount.get(sscy, 0) + scrcount.get(sscy, 0) + scdcount.get(sscy, 0)))
        
        fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td>%d</td> <td>%d</td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scvcount.get(sscy, 0), scrcount.get(sscy, 0), scbase, scdcount.get(sscy, 0) + scpcount.get(sgas, 0)))
        if gas == 48:
            break
        
        foutshort.write('<tr class="garow"> <td class="gasess"><a href="%s">Session %s</a></td> <td class="bbody">GA</td> <td class="num"><a href="%s/documents">%d</a></td>\n' % (gabase, sgas, gabase, gavcount.get(sgas, 0) + garcount.get(sgas, 0) + gadcount.get(sgas, 0)))

        fout.write('<tr class="garow"> <td class="gasess"><a href="%s">Session %s</a></td> <td>%d</td> <td>%d</td> <td><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, gavcount.get(sgas, 0), garcount.get(sgas, 0), gabase, gadcount.get(sgas, 0)))
    fout.write("</table>\n")
    foutshort.write("</table>\n")


