#!/usr/bin/python2.4 
import sys
import re
import os
import xapian

query = sys.argv[1]

xapian_file = "/home/francis/toobig/undata/xapdex.db"
xapian_db = xapian.Database(xapian_file)
xapian_enquire = xapian.Enquire(xapian_db)

xapian_query = xapian.QueryParser()
xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
xapian_query.set_default_op(xapian.Query.OP_AND)
xapian_query.add_prefix("id", "I")
xapian_query.add_prefix("subid", "J")
xapian_query.add_prefix("class", "C")
xapian_query.add_prefix("name", "S")
xapian_query.add_prefix("nation", "N")
xapian_query.add_prefix("language", "L")
xapian_query.add_prefix("document", "D")
xapian_query.add_prefix("reference", "R")
parsed_query = xapian_query.parse_query(query)

xapian_enquire.set_query(parsed_query)

# do sorting etc. here

matches = xapian_enquire.get_mset(0, 500)
print matches.size()
for match in matches:
    print match[3], match[4].get_data()


