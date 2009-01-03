#!/usr/bin/python2.4

# this module to be superceded by gennatdata.py

import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs, IsNotQuiet
import datetime

# writes out the votetable.txt
def LoadAllVotes(rels):
    res = { }  # { nation : { voterecid: vote } }
    for nation in nationdates:
        res[nation] = { }
    res["Brunei Darussalam"] = {}# quick fix

    for rel in rels:
        if IsNotQuiet():
            print "loading:", rel
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



