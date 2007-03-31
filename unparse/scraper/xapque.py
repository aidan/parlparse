#!/usr/bin/python2.4 
import sys
import re
import os
import xapian

# Query Xapian database made using xapdex.py

# Usage:
# ./xapque.py QUERY_STRING
# The QUERY_STRING must be just one parameter, so quote it if it has multiple
# terms, or escape quotes if you want to do a phrase search.

# e.g. 
# ./xapque.py "last july"
# ./xapque.py "\"last july\""
# ./xapque.py "nation:solomonislands"

# The names of prefixes (like nation:) are given in the code below, see
# xapdex.py for what they mean.

#if len(sys.argv) < 3:
#    print "Please specify xapian database and query as two parameters"
#    sys.exit()
#if len(sys.argv) > 3:
#    print "Please specify xapian database and query as two parameters (use quotes if multiple words)"
#    sys.exit()
query = sys.argv[1]

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
print "desc:", parsed_query.get_description()

xapian_enquire.set_query(parsed_query)
xapian_enquire.set_sort_by_value(0, xapian.Enquire.ASCENDING)
xapian_enquire.set_weighting_scheme(xapian.BoolWeight())

# do sorting etc. here

matches = xapian_enquire.get_mset(0, 500)
print matches.size()
for match in matches:
    #print match
    print match[4].get_value(0), match[4].get_data()


