#!/usr/bin/python2.4

import sys
import os
import random
import datetime
import time
import urllib
import glob
import re

from BeautifulSoup import MinimalSoup
from BeautifulSoup import NavigableString
from BeautifulSoup import Tag
from BeautifulSoup import Comment

from common import month_name_to_int
from common import non_tag_data_in
from common import tidy_string

# This is just for easy sorting in the order that seems sensible to me:

mention_type_order = { "business-today" : "1",
                       "business-oral" : "2",
                       "business-written" : "3",
                       "answer" : "4",
                       "holding" : "5" }

class Mention:
    def __init__(self,spid,iso_date,url,mention_type):
        self.spid = spid
        self.iso_date = iso_date
        self.url = url
        self.mention_type = mention_type
        if mention_type not in [ "business-oral", "business-written", "business-today", "answer", "holding" ]:
            raise Exception, "Unknown mention_type: "+mention_type
        self.mention_index = mention_type_order[mention_type]
        if not self.mention_index:
            raise Exception, "Something was missing from mention_type_order ("+mention_type+")"
    def __eq__(self,other):
        return (self.spid == other.spid) and (self.iso_date == other.iso_date) and (self.mention_type == other.mention_type)

id_to_mentions = { }

fp = open("../../../parldata/cmpages/sp/written-answer-question-spids","r")
for line in fp.readlines():
    m = re.match("^(.*):(.*):(.*)$",line)
    if m:
        k = m.group(2)
        holding_date = m.group(3)
        date = m.group(1)
        value = Mention(k,date,None,"answer")
        holding_value = None
        if len(holding_date) > 0:
            holding_value = Mention(k,holding_date,None,"holding")
        id_to_mentions.setdefault(k,[])
        if value not in id_to_mentions[k]:
            id_to_mentions[k].append(value)
        if holding_value and (holding_value not in id_to_mentions[k]):
            id_to_mentions[k].append(holding_value)

bulletin_prefix = "http://www.scottish.parliament.uk/business/businessBulletin/"
bulletins_directory = "../../../parldata/cmpages/sp/bulletins/"

bulletin_filenames = glob.glob( bulletins_directory + "day-*" )

for day_filename in bulletin_filenames:

    m = re.search('(?i)day-(.*)_([ab]b-\d\d-\d\d-?(\w*)\.html?)$',day_filename)

    if not m:
        print "Couldn't parse file %s" % ( day_filename )
        continue

    subdir = m.group(1)
    page = m.group(2)
    section = m.group(3)

    day_url = bulletin_prefix + subdir + '/' + page

    oral_question = False
    todays_business = False

    if section == 'a':
        oral_question = True
        todays_business = True
    elif section == 'd':
        oral_question = True
        todays_business = False
    elif section == 'e':
        oral_question = False
        todays_business = False
    else:
        continue

    # Now we have the file, soup it:

    fp = open(day_filename)
    day_html = fp.read()
    fp.close()
            
    day_html = re.sub('&nbsp;',' ',day_html)
    day_soup = MinimalSoup(day_html)

    day_body = day_soup.find('body')
    if day_body:
        page_as_text = non_tag_data_in(day_body)
    else:
        print "File couldn't be parsed by MinimalSoup: "+day_filename
        page_as_text = re.sub('(?ims)<[^>]+>','',day_html)

    filename_leaf = day_filename.split('/')[-1]
    date = None

    m = re.search('(?ims)((Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+)(\d+)\w*\s+(\w+)(\s+(\d+))?',page_as_text)
    if not m:
        m = re.search('(?ims)((Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+)?(\d+)\w*\s+(\w+)(\s+(\d+))?',page_as_text)
    if m:
        day_of_week = m.group(2)
        day = m.group(3)
        month = month_name_to_int(m.group(4))
        if month == 0:
            print "Whole match was '" + str(m.group(1)) + "'"
            raise Exception, "Month name '"+m.group(4)+"' not known in file: "+day_filename
        else:
            year = m.group(6)
            # Sometimes the date string doesn't have the year:
            if not year:
                m = re.search('(?i)day-[ab]b-(\d\d)',day_filename)
                if m.group(1) == '99':
                    year = '1999'
                else:
                    year = '20' + m.group(1)
            date = datetime.date( int(year,10), month, int(day,10) )
    else:
        raise Exception, "No date found in file: "+day_filename
            
    matches = re.findall('S[0-9][A-Z0-9]+\-[0-9]+',page_as_text)

    for spid in matches:
        id_to_mentions.setdefault(spid,[])
        mention_type = None
        if oral_question:
            if todays_business:
                mention_type = "business-today"
            else:
                mention_type = "business-oral"
        else:
            mention_type = "business-written"
        value = Mention(spid,str(date),day_url,mention_type)
        if value not in id_to_mentions[spid]:
            id_to_mentions[spid].append(value)

keys = id_to_mentions.keys()
keys.sort()
keys = set(keys)

fp = open( "../../../parldata/scrapedxml/sp-question-mentions.xml", "w" )

fp.write( '<?xml version="1.0" encoding="utf-8"?>\n' )
fp.write( '<publicwhip>\n' )
for k in keys:
    mentions = id_to_mentions[k]
    fp.write( '  <question gid="uk.org.publicwhip/spq/%s">\n' % k )
    mentions.sort( key = lambda m: m.iso_date + m.mention_index )
    for mention in mentions:
        url_string = None
        answer_gid = None
        if mention.url:
            url_string = ' url="%s"' % mention.url
        else:
            url_string = ''
        if mention.mention_type == 'answer':
            answer_gid = ' spwrans="uk.org.publicwhip/spwa/%s.%s.q0"' % ( mention.iso_date, k )
        else:
            answer_gid = ''
        fp.write( '    <mention date="%s" type="%s"%s%s/>\n' % ( mention.iso_date, mention.mention_type, url_string, answer_gid ) )
    fp.write( '  </question>\n\n' )
fp.write( '</publicwhip>' )
