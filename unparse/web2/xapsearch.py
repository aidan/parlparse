#!/usr/bin/python
import sys
import re
import os

def XapLookup(query):
    import xapian

    xapian_file = "../../undata/xapdex.db/"  #sys.argv[1]
    xapian_db = xapian.Database(xapian_file)
    xapian_enquire = xapian.Enquire(xapian_db)

    xapian_query = xapian.QueryParser()
    xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
    xapian_query.set_default_op(xapian.Query.OP_AND)
    xapian_query.add_boolean_prefix("id", "I")
    xapian_query.add_boolean_prefix("subid", "J")
    xapian_query.add_boolean_prefix("class", "C")
    xapian_query.add_boolean_prefix("name", "S")
    xapian_query.add_boolean_prefix("nation", "N")
    xapian_query.add_boolean_prefix("language", "L")
    xapian_query.add_boolean_prefix("document", "D")
    xapian_query.add_boolean_prefix("reference", "R")
    xapian_query.add_boolean_prefix("date", "E")
    xapian_query.add_boolean_prefix("agenda", "A")
    xapian_query.add_boolean_prefix("vote", "V")
    xapian_query.add_boolean_prefix("session", "Z")

    parsed_query = xapian_query.parse_query(query, 16+4+2+1) # allows wildcards
    #print "desc:", parsed_query.get_description()

    xapian_enquire.set_query(parsed_query)
    xapian_enquire.set_sort_by_value(0, xapian.Enquire.ASCENDING)
    xapian_enquire.set_weighting_scheme(xapian.BoolWeight())

    # do sorting etc. here

    matches = xapian_enquire.get_mset(0, 500)
    res = [ ]
    #print matches.size()
    for match in matches:
        #print match[4].get_value(0), match[4].get_data()
        res.append(match[4].get_data())
    return res





