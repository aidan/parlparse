#!/usr/bin/python2.4

import sys
import os
import random
import datetime
import time
import urllib
import glob

from BeautifulSoup import MinimalSoup
from BeautifulSoup import NavigableString
from BeautifulSoup import Tag
from BeautifulSoup import Comment

from common import month_name_to_int
from common import non_tag_data_in
from common import tidy_string

agent = "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"

class MyURLopener(urllib.FancyURLopener):
    version = agent

urllib._urlopener = MyURLopener()

import re

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

# Make sure we have an up-to-date list of the written answers that are
# known about (note this means that this script must be run after
# parse-written-answers.py)...

os.system("./get-written-answer-id-list")

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

currentdate = datetime.date.today()
currentyear = datetime.date.today().year

output_directory = "../../../parldata/cmpages/sp/bulletins/"
bulletin_template = output_directory + "wa%s_%d.html"
bulletin_urls_template = output_directory + "wa%s.urls"

# Fetch the year indices that we either don't have
# or is the current year's...

bulletin_prefix = "http://www.scottish.parliament.uk/business/businessBulletin/"
bulletin_year_template = bulletin_prefix + "%d.htm"

# Find the existing contents pages in the excluding those in the 90s...

existing_contents_pages = glob.glob( output_directory + "contents-bb-[0-8]*" )
existing_contents_pages.sort()

for year in range(1999,currentyear+1):
    index_page_url = bulletin_year_template % year
    output_filename = output_directory + str(year) + ".html"
    if (not os.path.exists(output_filename)) or (year == currentyear):
        ur = urllib.urlopen(index_page_url)
        fp = open(output_filename, 'w')
        fp.write(ur.read())
        fp.close()
        ur.close()

for year in range(1999,currentyear+1):

    year_index_filename = output_directory  + str(year) + ".html"
    if not os.path.exists(year_index_filename):
        raise Exception, "Missing the year index: '%s'" % year_index_filename
    fp = open(year_index_filename)
    html = fp.read()
    fp.close()

    soup = MinimalSoup( html )
    link_tags = soup.findAll( 'a' )

    contents_pages = set()
    daily_pages = set()

    contents_hash = {}

    for t in link_tags:

        if t.has_key('href') and re.match('^bb-',t['href']):

            page = t['href']

            subdir, leaf = page.split("/")

            contents_pages.add( (subdir,leaf) )
            contents_hash[subdir+"_"+leaf] = True

    # Fetch all the contents pages:

    for (subdir,leaf) in contents_pages:

        contents_filename = output_directory + "contents-"+subdir+"_"+leaf
        contents_url = bulletin_prefix + subdir + "/" + leaf

        # Make sure we refetch the latest one, since it might have been updated.
        if not os.path.exists(contents_filename) or (len(existing_contents_pages) > 0 and existing_contents_pages[-1] == contents_filename):
            ur = urllib.urlopen(contents_url)
            fp = open(contents_filename, 'w')
            fp.write(ur.read())
            fp.close()
            ur.close()
                
    # Now find all the daily pages from the contents pages...

    for (subdir,leaf) in contents_pages:

        contents_filename = output_directory + "contents-"+subdir+"_"+leaf

        fp = open(contents_filename)
        contents_html = fp.read()
        fp.close()

        contents_html = re.sub('&nbsp;',' ',contents_html)
        contents_soup = MinimalSoup(contents_html)
        link_tags = contents_soup.findAll( lambda x: x.name == 'a' and x.has_key('href') and re.search('(?i)[ab]b-\d\d-\d\d',x['href']) )
        link_urls = [ ]
        if len(link_tags) == 0:
            # Annoyingly, some of these file are so broken that
            # BeautifulSoup can't parse them, and just returns a
            # single NavigableString.  So, if we don't find any
            # appropriate links, guess that this is the case and look
            # for links manually :(
            # 
            matches = re.findall( '(?ims)<a[^>]href\s*=\s*"?([^"> ]+)["> ]', contents_html )
            for m in matches:
                link_urls.append(m)
        else:
            for t in link_tags:
                link_urls.append(t['href'])
        link_leaves = [ ]
        for u in link_urls:
            parts = u.split('/')
            if len(parts) == 1:
                link_leaves.append(parts[0])
            if len(parts) > 1:
                if parts[-2] == subdir:
                    link_leaves.append(parts[-1])
                else:
                    if re.match('(?i)[ab]b-',parts[-2]):
                        print "Warning: subdirs differed between "+subdir+" and "+parts[-2]+"/"+parts[-1]+" when parsing file: "+contents_filename

        for l in link_leaves:

            m = re.match('(?i)^\s*([ab]b-\d\d-\d\d-?(\w*)\.htm)',l)

            if not m:
                print "Couldn't parse '%s' in file %s" % ( l, contents_filename )
                continue

            page = m.group(1)
            section = m.group(2)

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

            day_filename = output_directory + "day-" + subdir + "_" + page
            day_url = bulletin_prefix + subdir + "/" + page

            if not os.path.exists(day_filename):
                ur = urllib.urlopen(day_url)
                fp = open(day_filename, 'w')
                fp.write(ur.read())
                fp.close()
                ur.close()
                amount_to_sleep = int( 4 * random.random() )
                time.sleep( amount_to_sleep )

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
