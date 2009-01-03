#!/usr/bin/python

import MySQLdb
import re
import sys
from dbpasswords import *

db = MySQLdb.connect(user=db_user, passwd=db_password, db=db_name)


def GetDBcursor():
    return db.cursor()





def MakeTableHeadings(c):
    print "Creating table for all the headings in SC and GA"
    tablecols = [ "docid VARCHAR(30)", "href VARCHAR(30)", "heading TEXT", 
                  "agendanum VARCHAR(15)", "session VARCHAR(10)",
                  "ldatetime_from DATETIME", "ldatetime_to DATETIME", 
                  "num_speeches INT", "num_votes INT", 
                  "INDEX(docid)", "INDEX(href)",
                  "UNIQUE(docid, href)" ]
    c.execute("DROP TABLE IF EXISTS un_headings;")
    c.execute("CREATE TABLE un_headings (%s);" % ", ".join(tablecols))


def MakeTableVotes(c):
    print "Creating table for divisions and votes"
    tablecolsdivision = [ "docid VARCHAR(30)", "href VARCHAR(30)", "body enum('GA', 'SC')", 
                          "motiontext TEXT", "ldate DATE", 
                          "favour INT", "against INT", "abstain INT", "absent INT",
                          "INDEX(docid)", "INDEX(href)",
                          "UNIQUE(docid, href)" ]
    c.execute("DROP TABLE IF EXISTS un_divisions;")
    c.execute("CREATE TABLE un_divisions (%s);" % ", ".join(tablecolsdivision))

    tablecolsvote = [ "docid VARCHAR(30)", "href VARCHAR(30)", 
                      "nation VARCHAR(40)", "vote enum('favour', 'against', 'abstain', 'absent')",
                      "intended_vote enum('favour', 'against', 'abstain', 'absent')",
                      "minority_score FLOAT", 
                      "INDEX(docid)", "INDEX(href)", "INDEX(nation)", 
                      "UNIQUE(docid, href, nation)" ]
    c.execute("DROP TABLE IF EXISTS un_votes;")
    c.execute("CREATE TABLE un_votes (%s);" % ", ".join(tablecolsvote))


def AddWholeDivision(c):
    pass

def escape_string(str):
    return MySQLdb.escape_string(str)

# handling the different command line improvements
if __name__ == "__main__":

    c = db.cursor()
    c1 = db.cursor()
    MakeTableHeadings(c)
    MakeTableVotes(c)


    sys.exit(0)
    
    c.execute("select * from wikiredirects;")
    for a in c.fetchall():
        print a


