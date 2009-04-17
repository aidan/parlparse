"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
# lots of stuff changed from webhelpers 0.3 to webhelpers 0.6.4
# for < 0.6
from webhelpers import *
# for 0.6.4
try:
    from webhelpers.rails.wrapped import *
    from routes import url_for, redirect_to
except:
    pass

import re  # also imported already in textile
import os
import datetime
import unpylons.model as model
import itertools

undatadir = "/home/goatchurch/undemocracy/undata"  # should come from config
root_url = "http://www.undemocracy.com" # should come from config

def todaydate():
    return str(datetime.date.today())

def strip_tags_in_subheading(text):
    if not text:
        return "NONE"
    lt = [re.sub("<[^>]*>", "", t).strip()  for t in re.split("</p>", text)]
    lt = [t  for t in lt  if t]
    return lt

def truncateN(text, n):
    if not text:
        return "BLANK"
    return truncate(text, n)

def split_links(text):
    lt = re.split('(<a[^>]*>.*?</a>|<i>[^<]*</i>)', text)
    res = [ ]
    for t in lt:
        mlk = re.match('<a href="[^"]*?/([AS][^/]*?)\.(?:pdf|html)"[^>]*>([^<]*)</a>$', t)
        mit = re.match('<i>([^<]*)</i>', t)
        if mlk:
            res.append((mlk.group(1), mlk.group(2)))
        elif mit:
            res.append(("italics", mit.group(1)))
        else:
            res.append((None, t))
    return res

# this could look up whether the doc exists and take to html versions
def url_for_doc(docid):
    if not docid:
        return ""
    mgameeting = re.match("A.(\d+).PV.(\d+)$", docid)
    mscmeeting = re.match("S.PV.(\d.*)$", docid)
    if mgameeting and list(model.Meeting.query.filter_by(docid=docid)):
    #int(mgameeting.group(1)) >= 49 and os.path.isfile(os.path.join(undatadir, "html", docid + ".html")):
        return url_for('gameeting', session=mgameeting.group(1), meeting=mgameeting.group(2))
    if mscmeeting:
        return url_for('scmeeting', scmeetingnumber=mscmeeting.group(1))
    return url_for('documentspec', docid=docid)


