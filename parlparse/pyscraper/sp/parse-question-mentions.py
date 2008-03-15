#!/usr/bin/python2.4

import sys
import os
import random
import datetime
import time
import urllib
import glob
import re

sys.path.append('../')
from BeautifulSoup import MinimalSoup
from BeautifulSoup import NavigableString
from BeautifulSoup import Tag
from BeautifulSoup import Comment

from common import month_name_to_int
from common import non_tag_data_in
from common import tidy_string
from common import fix_spid

from findquotation import ScrapedXMLParser
from findquotation import find_quotation_from_text
from findquotation import find_speech_with_trailing_spid

from mentions import Mention
from mentions import add_mention_to_dictionary
from mentions import load_question_mentions
from mentions import save_question_mentions

from wransspidlist import load_wrans_spid_list

from optparse import OptionParser

spid_re =                   '(S[0-9][A-LN-Z0-9]+\-[0-9]+)'
spid_re_bracketed =         '\(\s*'+spid_re+'\s*\)'
spid_re_at_start =          '^\s*'+spid_re
spid_re_bracketed_at_end =  spid_re_bracketed+'\s*$'

sxp = ScrapedXMLParser("../../../parldata/scrapedxml/sp/sp%s.xml")

parser = OptionParser()
parser.add_option('-f', "--force", dest="force", action="store_true",
                  default=False, help="don't load the old file first, regenerate everything")
parser.add_option('-v', "--verbose", dest="verbose", action="store_true",
                  default=False, help="output verbose progress information")
(options, args) = parser.parse_args()
force = options.force
verbose = options.verbose

# The first Business Bulletin:
last_bulletin_info_date = "1999-05-12"

if force:
    id_to_mentions = { }
else:
    id_to_mentions = load_question_mentions()
    for k in id_to_mentions.keys():
        mentions = id_to_mentions[k]
        for m in mentions:
            if m.mention_type == 'business-written' or m.mention_type == 'business-oral' or m.mention_type == 'business-today':
                # Since they're all ISO 8601 dates we can just compare
                # the strings...
                if m.iso_date > last_bulletin_info_date:
                    last_bulletin_info_date = m.iso_date
    
last_bulletin_info_date = datetime.date(*time.strptime(last_bulletin_info_date,"%Y-%m-%d")[:3])
bulletins_after = last_bulletin_info_date - datetime.timedelta(days=14)

wrans_hash = load_wrans_spid_list()

for k in wrans_hash.keys():
    for t in h[k]:
        date, k, holding_date = t
        value = Mention(k,date,None,"answer",None)
        add_mention_to_dictionary(k,value,id_to_mentions)
        if len(holding_date) > 0:
            holding_value = Mention(k,holding_date,None,"holding",None)
            add_mention_to_dictionary(k,holding_value,id_to_mentions)

bulletin_prefix = "http://www.scottish.parliament.uk/business/businessBulletin/"
bulletins_directory = "../../../parldata/cmpages/sp/bulletins/"

bulletin_filenames = glob.glob( bulletins_directory + "day-*" )
bulletin_filenames.sort()

for day_filename in bulletin_filenames:

    m = re.search('(?i)day-(bb-(\d\d))_([ab]b-(\d\d)-(\d\d)-?(\w*)\.html?)$',day_filename)

    if not m:
        if verbose: print "Couldn't parse file %s" % ( day_filename )
        continue

    subdir = m.group(1)
    two_digit_year = m.group(2)
    page = m.group(3)
    two_digit_month = m.group(4)
    two_digit_day = m.group(5)
    section = m.group(6)

    # if not (two_digit_year == '08' or two_digit_year == '07'):
    # if not (two_digit_year == '08'):
    #     continue

    day_url = bulletin_prefix + subdir + '/' + page

    oral_question = False
    todays_business = False

    if section == 'a':
        oral_question = False
        todays_business = True
    elif section == 'd':
        oral_question = True
        todays_business = False
    elif section == 'e':
        oral_question = False
        todays_business = False
    else:
        continue

    if verbose: print "------------------------------"
    if verbose: print "Parsing file: "+day_filename

    # Now we have the file, soup it:

    fp = open(day_filename)
    day_html = fp.read()
    fp.close()

    day_html = re.sub('&nbsp;',' ',day_html)
    day_html = fix_spid(day_html)
    
    filename_leaf = day_filename.split('/')[-1]

    date = None

    date_from_filename = None
    date_from_filecontents = None

    # First, guess the date from the filename:
    filename_year = None
    filename_month = int(two_digit_month,10)
    filename_day = int(two_digit_day,10)
    if two_digit_year == '99':
        filename_year = 1999
    else:
        filename_year = int('20'+two_digit_year,10)
    try:
        date_from_filename = datetime.date(filename_year,filename_month,filename_day)
    except ValueError:
        date_from_filename = None
        if verbose: print "Date in filename %s-%s-%s" % ( filename_year, filename_month, filename_day )

    # Don't soup it if we don't have to:
    if date_from_filename and date_from_filename < bulletins_after:
        continue

    day_soup = MinimalSoup(day_html)

    day_body = day_soup.find('body')
    if day_body:
        page_as_text = non_tag_data_in(day_body)
    else:
        error = "File couldn't be parsed by MinimalSoup: "+day_filename
        raise Exception, error

    # Now guess the date from the file contents as well:
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
            date_from_filecontents = datetime.date( int(year,10), month, int(day,10) )

    if date_from_filename == date_from_filecontents:
        date = date_from_filename
    else:
        # Sometimes one method works, sometime the other:
        if date_from_filename and not date_from_filecontents:
            date = date_from_filename
        elif date_from_filecontents and not date_from_filename:
            date = date_from_filecontents
        else:
            # So toss a coin here, more or less.  Let's go with the
            # filename, since there many be many dates in the file
            # itself.
            date = date_from_filename
        
    if verbose: print "Date: "+str(date)

    if date < bulletins_after:
        continue

    matches = []

    ps = day_body.findAll( lambda t: t.name == 'p' or t.name == 'li' )
    for p in ps:
        plain = non_tag_data_in(p)
        m_end_bracketed = re.search(spid_re_bracketed_at_end,plain)
        m_start = re.search(spid_re_at_start,plain)
        spid = None
        if oral_question:
            spid = m_end_bracketed and m_end_bracketed.group(1)
        elif todays_business:
            spid = (m_start and m_start.group(1)) or (m_end_bracketed and m_end_bracketed.group(1))
        else:
            spid = m_start and m_start.group(1)
        plain = re.sub(spid_re_bracketed_at_end,'',plain)
        plain = re.sub(spid_re_at_start,'',plain)
        if m_start or m_end_bracketed:
            if not spid:
                print "SPID seemed to be at the wrong end of the paragraph:"
                print "   oral_question was: "+str(oral_question)
                print "   todays_business was: "+str(todays_business)
                print "   m_start was: "+str(m_start)
                print "   m_end_bracketed was: "+str(m_end_bracketed)
                raise Exception("Problem.")
            spid = fix_spid(spid)
            matches.append(spid)
            allusions = re.findall(spid_re,plain)
            for a in allusions:
                a = fix_spid(a)
                mention = Mention(a,None,None,'referenced-in-question-text',spid)
                add_mention_to_dictionary(a,mention,id_to_mentions)
            if oral_question:
                mention = Mention(spid,str(date),day_url,'business-oral',None)
                add_mention_to_dictionary(spid,mention,id_to_mentions)
            elif todays_business:
                mention = Mention(spid,str(date),day_url,'business-today',None)
                add_mention_to_dictionary(spid,mention,id_to_mentions)
            else: 
                mention = Mention(spid,str(date),day_url,'business-written',None)
                add_mention_to_dictionary(spid,mention,id_to_mentions)

    # If this is the oral question section, it'd be nice to find out
    # if they were actually asked in the official report, and if so
    # include that as a different type of mention.  We look in the
    # next 10 days of official reports.  Fortunately, there always
    # seems to be the spid in brackets at the end of the question
    # being asked in the official reports.
    
    # (Note that this is pretty slow.)

    if oral_question and day_body:
        total_found = 0
        for spid in matches:
            found = False
            for i in range(0,15):
                later_date = date+datetime.timedelta(days=i)
                gid = find_speech_with_trailing_spid(sxp,str(later_date),spid)
                if gid:
                    if verbose: print "Got %9s in %s, %d days later" % (spid,gid,i)
                    found = True
                    value = Mention(spid,str(later_date),None,"oral-asked-in-official-report",gid)
                    add_mention_to_dictionary(spid,value,id_to_mentions)
                    break
            if found:
                total_found += 1
            else:
                if verbose: print "Couldn't find: "+spid
                pass
        if total_found == 0 and (len(matches) > 0):
            if verbose: print "None found from "+str(day_filename)

save_question_mentions(id_to_mentions)
