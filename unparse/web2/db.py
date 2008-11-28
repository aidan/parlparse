#!/usr/bin/python

import MySQLdb
import re
import urlparse
import datetime
import sys
import config
from dbpasswords import *

db=MySQLdb.connect(user=db_user, passwd=db_password, db=db_name)


def GetDBcursor():
    return db.cursor()


# this is going to be run once when it eventually works
def MakeTableIncomingLog(c):
    tablename = "unlog_incoming"
    tablecols = [ "docid VARCHAR(30)", "page VARCHAR(30)", "referrer TEXT", "refdomain VARCHAR(30)", "reftitle TEXT", 
                  "ltime DATETIME", "ipnumber VARCHAR(20)", "useragent TEXT", "url TEXT" ]
    
    print "Creating table", tablename
    c.execute("DROP TABLE IF EXISTS %s" % tablename)
    c.execute("CREATE TABLE %s (%s);" % (tablename, ", ".join(tablecols)))

def MakeTableWikiredirects(c):
    print "Creating table wikiredirects"
    c.execute("DROP TABLE IF EXISTS wikiredirects;")
    c.execute("CREATE TABLE wikiredirects (reftitle_wrong TEXT, reftitle_right TEXT);")

    # load from the original file
    fin = open("wikiredirects.txt")
    mainname = ""
    for sline in fin.readlines():

        lsline = sline.strip()
        if lsline:
            if not(sline[0] == " " or sline[0] == "\t"):
                mainname = lsline
            elif mainname:
                lvalues = "'%s', '%s'" % (lsline, mainname)
                #print lvalues
                c.execute("INSERT INTO wikiredirects (reftitle_wrong, reftitle_right) VALUES (%s);" % lvalues)
                
    fin.close()


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


def ParseReferrer(referrer, c):
    referrer_parsed = urlparse.urlparse(referrer)
    refdomain = referrer_parsed[1]
    reftitle = referrer_parsed[2]
    
    if refdomain == "en.wikipedia.org":
        reftitle = re.sub("/wiki/", "", reftitle)
    
        reftitle = re.sub("^UN_(?i)", "United_Nations_", reftitle)
        reftitle = re.sub("^United_Nations_Resolution_(?i)", "United_Nations_Security_Council_Resolution_", reftitle)
        c.execute("SELECT reftitle_right FROM wikiredirects WHERE reftitle_wrong = '%s';" % reftitle)
        res = c.fetchone()
        if res:
            wreftitle = res[0]
    return refdomain, reftitle


def RefreshReferrerParsings(c, c1):
    print "Refreshing all the referrers into reftitles"
    c.execute("SELECT referrer, refdomain, reftitle FROM unlog_incoming WHERE refdomain = 'en.wikipedia.org' GROUP BY referrer;")
    while True:
        ref = c.fetchone()
        if not ref:
            break
        refdomain, reftitle = ParseReferrer(ref[0], c1)
        if ref[2] != reftitle:
            print "updating: ", reftitle, ref[0]
            c1.execute("UPDATE unlog_incoming SET refdomain='%s', reftitle='%s' WHERE referrer='%s';" % (refdomain, reftitle, ref[0]))



def LogIncomingDB(docid, page, referrer, ipnumber, useragent, url):
    
    # not interested in bots
    if re.search("google|picsearch|search.msnbot|search.msn.com/msnbot|cuill.*?robot|ysearch/slurp|door/crawler|crawler.archive.org", useragent):
        return "searchengine"
    
    c = GetDBcursor()
    nowdatetime = datetime.datetime.now().__str__()
    refdomain, reftitle = ParseReferrer(referrer, c)
        

    paramlist = "docid, page, referrer, refdomain, reftitle, ltime, ipnumber, useragent, url"
    paramvalues = "'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s'" % (docid, page, referrer, refdomain, reftitle, nowdatetime, ipnumber, useragent, url)
    c.execute("INSERT INTO unlog_incoming (%s) VALUES (%s);" % (paramlist, paramvalues))

    res = 'unknown'
    if re.search("wikipedia", refdomain):
        res = "wikipedia"
    if re.search("undemocracy", refdomain):
        res = "internal"
    return res

def GetUnlogList(pagefunc, limit):
    paramlist = [ "docid", "page", "referrer", "refdomain", "reftitle", "ltime", "ipnumber", "useragent", "url"]
    c = db.cursor()
    c.execute("SELECT page, referrer, ltime, ipnumber FROM unlog_incoming WHERE docid='%s' ORDER BY ltime DESC LIMIT %d" % (pagefunc, limit))
    res = [ ]
    for row in c.fetchall():
        res.append({"page":row[0], "referrer":row[1], "ltime":row[2], "ipnumber":row[3]})
    return res

    


# handling the different command line improvements
if __name__ == "__main__":

    c = db.cursor()
    c1 = db.cursor()
    #MakeTablesIncomingLog(c)  # rebuild the incoming table
#MakeTableWikiredirects(c) # rebuild the redirects from the wikiredirects.txt
    #RefreshReferrerParsings(c, c1)  # re-apply all the wikiredirects
    MakeTableHeadings(c)

    sys.exit(0)
    
    c.execute("select * from wikiredirects;")
    for a in c.fetchall():
        print a


