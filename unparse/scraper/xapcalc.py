#!/usr/bin/python2.4
import sys
import re
import os
if sys.platform == "win32":
    import fakexapian as xapian
else:
    import xapian

from nations import nationdates
from xapdex import GetAllHtmlDocs

from optparse import OptionParser


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


parser = OptionParser()

parser.set_usage("""
./xapcalc.py

Example command lines:
./xapdex.py --vote-distances""")
parser.add_option("--xapdb", dest="xapdb", default="",
                  help="Xapian database as path relative to UN data directory; defaults to xapdex.db")
parser.add_option("--vote-distances", action="store_true", dest="votedistances", default=False,
                  help="Erases existing database, and indexes all .html files")
parser.add_option("--date", dest="date", default="",
                  help="Sets the date stamp for this pre-calculated information")
parser.add_option("--force", action="store_true", dest="force", default=False,
                  help="Overwrites all entries")
parser.add_option("--undata", dest="undata", default=None,
                  help="UN data directory; if not specified searches for it in current directory, up to 3 parent directories, and home directory")
parser.add_option("--stem", dest="stem", default="",
      help="Restricts the files scanned within the directory similar to the parser feature")

options, args = parser.parse_args()
rels, xapian_file = GetAllHtmlDocs(options.stem, False, options.force, options.undata, options.xapdb)

nationlist = nationdates.keys()
nationlist.sort()
flatnationlist = set([ re.sub("['\s\-]", "", nation).lower()  for nation in nationdates ])
#print flatnationlist

def WriteAllVoteDistances():
    votetable = LoadAllVotes(rels)  # creates gigantic table of votes for these countries by loading all the files
    i = 1
    for nation1 in nationlist:
        print 'na%04d = "%s";' % (i, nation1)
        print 'pa%04d = "%s";' % (i, "Oceania")  # this to be continent
        res = [ ]
        for nation2 in nationlist:
            res.append("%.3f" % CompareVDistance(votetable[nation1], votetable[nation2]))
        print 'pa%04d = [%s];' % (i, ", ".join(res))
        i += 1


os.environ['XAPIAN_PREFER_FLINT'] = '1' # use newer/faster Flint backend
xapian_db = xapian.WritableDatabase(xapian_file, xapian.DB_CREATE_OR_OPEN)

# the distance between two countries is recorded within the values
#value0/1000, NcountryA NcountryB Zvda1000 date|countryA|countryB

def UpdateVoteDistances(sdate, bforce):
    xapian_enquire = xapian.Enquire(xapian_db)
    xapian_query = xapian.QueryParser()
    xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
    xapian_query.set_default_op(xapian.Query.OP_AND)
    xapian_enquire.set_weighting_scheme(xapian.BoolWeight())

    xapian_query.add_boolean_prefix("session", "Z")
    xapian_query.add_boolean_prefix("vote", "V")
    xapian_query.add_boolean_prefix("nation", "N")

    for i in range(len(flatnationlist) - 1):
        nation1 = flatnationlist[i]
        for nation2 in flatnationlist[i + 1:]:
            query = "nation:%s nation:%s session:vda1000" % (nation1, nation2)
            parsed_query = xapian_query.parse_query(query)
            #value0/1000, NcountryA NcountryB Zvda1000 date|countryA|countryB

            # clean out previous values
            xapian_enquire.set_query(parsed_query)
            mset = xapian_enquire.get_mset(0, 5, 5)
            if mset.size():
                assert mset.size() == 1, "Should be only one for any matching pair of countries: %d" % mset.size()
                nrmset = 0
                for mdoc in mset:
                    dstring = mdoc[4].get_data()
                    if bforce or dstring.split("|")[0] < sdate:
                        xapian_db.delete_document(mdoc[0])
                        print "Deleting: ", dstring
                    else:
                        nrmset += 1
                if nrmset == 1:
                    continue
                assert nrmset == 0

            # now find out how many matching
            querysame = "(vote:%s-favour vote:%s-favour)" % (nation1, nation2)
            parsed_query = xapian_query.parse_query(querysame)
            xapian_enquire.set_query(parsed_query)
            mset = xapian_enquire.get_mset(0, 5000, 5000)
            print mset.size(), querysame


if options.votedistances:
    WriteAllVoteDistances()
    #UpdateVoteDistances(options.date, False)


