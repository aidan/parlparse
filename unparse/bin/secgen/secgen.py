#
# secgen.py:
# Twitter the daily schedule of the UN Secretary-General
#
# Copyright (c) 2007 Matthew Somerville. All rights reserved.
# http://www.dracos.co.uk/

import optparse
import os
import re
import sys
import textwrap
import urllib
import urllib2
from datetime import datetime, timedelta
from time import strptime, sleep
from BeautifulSoup import BeautifulSoup

localfile = 'schedule.shtml'

def main():
    p = optparse.OptionParser(version="UN Secretary-General > Twitter v1.0")
    choices = [ 'fetch', 'twitter', 'test' ]
    p.add_option('--action', type='choice', choices=choices,
            help='Action to perform; one of %s' % ', '.join(choices) )
    options, args = p.parse_args()

    if options.action == 'fetch':
        if fetch():
            test()
    elif options.action == 'twitter':
        now = datetime.today()
        for time, event in parse():
            if now>=time and now<time+timedelta(minutes=5):
                print twitter(event)
    elif options.action == 'test':
        test()
    else:
        p.print_help()

def test():
    for time, event in parse():
            print time, event


def fetch():
    new = get_contents('http://www.un.org/sg/schedule.shtml')
    current = ''
    try:
        current = get_contents(localfile)
    except:
        pass
    if current != new:
        f = open(localfile, 'w')
        f.write(new)
        f.close()
        try:
            os.remove('%s-override' % localfile)
        except:
            pass
        print "New schedule downloaded"
        return True
    return False

def parse():
    try:
        d = get_contents("%s-override" % localfile)
    except:
        d = get_contents(localfile)
    soup = BeautifulSoup(d)
    table = soup('body')[1].find('table')
    events = []
    pastnoon = False
    for row in table('tr'):
        cells = row('td')
        time = parsecell(cells[0])
        if time == '':
            continue
        if len(cells)==1: # Heading
            time = re.sub('\(Subject to change\)', '', time)
            time = re.sub('&nbsp;', '', time)
            time = re.sub('&nbsp', '', time)
            time = re.sub(',', '', time)
            time = time.strip()
            try:
                date = strptime(time, '%A %d %B %Y')
            except:
                print time
                sys.exit() # Bomb out if we can't get a date
            continue
        time, pastnoon = parsetime(time, date, pastnoon)
        event = parsecell(cells[2], True)
        event = prettify(event)
        events.append((time, event))
    return events

def twitter(s):
#    x = urllib2.HTTPPasswordMgrWithDefaultRealm()
#    x.add_password(None, 'http://twitter.com/statuses/', email, password)
#   auth = urllib2.HTTPBasicAuthHandler(x)
#   opener = urllib2.build_opener(auth)
   if len(s)>140:
       wrapped = textwrap.wrap(s, 137)
   else:
       wrapped = [ s ]
   resp = ''
   first = True
   for line in wrapped:
       if resp:
           sleep(5)
       if first and len(wrapped)>1:
           line = "%s..." % line
       if not first:
           line = "...%s" % line
       fileHandle = open ( 'test.txt', 'a' )
       fileHandle.write ( '\n\n\nBottom line.' )
       fileHandle.close() 
#       resp += opener.open('http://twitter.com/statuses/update.xml',
#           'status=%s' % urllib.quote(line)).read()
#       first = False
 #  return resp

def parsetime(time, date, pastnoon):
    m = re.search('(\d+)(?::|\.)(\d+)(?: (a|p|noon))?', time)
    (hour, min, pm) = m.groups()
    hour = int(hour)
    min = int(min)
    if not pm and pastnoon:
        hour += 12
    if pm == 'p' and hour != 12:
        hour += 12
    if pm == 'a' and hour == 12:
        hour -= 12
    if pm == 'p' or pm == 'noon':
        pastnoon = True
    d = datetime(date.tm_year, date.tm_mon, date.tm_mday, hour, min)
    d += timedelta(hours=5) # Assume we're in New York, and BST is same (which it isn't)
    return d, pastnoon

def prettify(s):
    if re.match('Meeting (with|on)', s):
        return s
    if re.match('Secretary-General to address ', s):
        return re.sub('Secretary-General to address ', 'Addressing ', s)
    if (re.match('Permanent Representative', s) or re.search('Team$', s) or re.search('Permanent Representatives', s)) and not re.search('luncheon', s):
        s = 'Meeting the %s' % s
    elif 'Presentation of credential' in s or re.match('Remarks at', s) or re.match('Election of', s):
        pass
    elif re.match('His Majesty|Ambassador|H\.E\.|Mr\.|Prof\.|Dr\.|Ms\.|Amb\.|Mayor|Messrs\.|Senator|Rt\. Hon\.', s):
        s = re.sub('Amb\.', 'Ambassador', s)
        s = 'Meeting %s' % s
    elif re.search('Special Representative|President of', s):
        s = 'Meeting %s' % s
    else:
        s = 'Attending the %s' % s
    return s


def parsecell(s, d=False):
    s = s.renderContents()
    if d:
        s = re.sub("<br />", ", ", s)
        s = re.sub("</p>", "; ", s)
    s = re.sub("<[^>]*>", "", s)
    s = re.sub("&amp;nbsp;", "", s)
    s = re.sub("\s+", " ", s)
    s = s.strip(" ;")
    return s

def get_contents(s):
    if 'http://' in s:
        f = urllib.urlopen(s)
    else:
        f = open(s)
    o = f.read()
    f.close()
    return o
main()
