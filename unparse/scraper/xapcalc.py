#!/usr/bin/python2.4
import sys
import re
import os
import xapian
from nations import nationdates
from unmisc import CharToFlat

xapian_file = "../../undata/xapdex.db/"  #sys.argv[1]
xapian_db = xapian.Database(xapian_file)

flatnationlist = [ CharToFlat(nation)  for nation in nationdates ]
flatnationlist.sort()
print flatnationlist

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
        for nation2 in flatnationlist[i + 1:]:
            query = "nation:%s nation:%s Zvda1000" % (nation1, nation2)
            parsed_query = xapian_query.parse_query(query)
            #value0/1000, NcountryA NcountryB Zvda1000 date|countryA|countryB

            # clean out previous values
            xapian_enquire.set_query(parsed_query)
            mset = xapian_enquire.get_mset(0, 5)
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
            parsed_query = xapian_query.parse_query(query)
            xapian_enquire.set_query(parsed_query)
            mset = xapian_enquire.get_mset(0, 5000, 5000)
            print mset.size(), querysame


UpdateVoteDistances("2000-00-00", False)

