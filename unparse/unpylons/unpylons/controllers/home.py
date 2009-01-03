import os
import logging
import sys

from unpylons.lib.base import *

import unpylons.model as model

log = logging.getLogger(__name__)

PYTHONPATH = "/home/goatchurch/undemocracy/unparse"
sys.path.append(PYTHONPATH)
sys.path.append(PYTHONPATH + "/djweb")
sys.path.append(PYTHONPATH + "/web2")
sys.path.append(PYTHONPATH + "/pylib")
os.environ['PYTHONPATH'] = PYTHONPATH

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.template import loader
import djweb.settings as settings
import web2.trunk
from web2.wikitables import ShortWikipediaTableM
from web2.db import LogIncomingDB, GetUnlogList
from web2.indexrecords import LoadAgendaNames, LoadSecRecords

class HomeController(BaseController):

    def index(self, url=None):
        ourpath = request.path_info
        extras = ourpath + '\n\n'
        extras += url + '\n\n'
        try:
            out = web2.trunk.maintrunkC(url)
            # out = ''
        except Exception, inst:
            out = 'There was an error: %s' % inst
        # print 'path is:', path
        # print 'out is:', out
        # out = extras + out
        return out


    # sc year business (the top bit)
    def scyear(self, year):
        if year != "early":
            y = int(year)
            c.year_before = y-1
            c.year_after = y+1
            if c.year_after > 2008:
                c.year_after = None
        else:
            c.year_before = None
            c.year_after = 1994
		
        # fetch the list of what we want to render for this year
        # should it be entered into a database or lifted from the file system?
        # return "Other years: " + yp + " | " + yn
        return render('sc')

    def scmeeting(self, scmeeting):
        WriteHTML(hmap["htmlfile"], hmap["pdfinfo"], "", hmap["highlightdoclink"])
    
    def about(self):
        recsc = LoadSecRecords("recent")[:12]
        recag = LoadAgendaNames("recent")[:8]
        wikirefs = ShortWikipediaTableM(12)
        searchlist = GetUnlogList("search", 100)
        x = loader.render_to_string('frontpage.html', {'searchlist':searchlist, 'trail':'locise', 'secrecords':recsc, 'garecords':recag, 'wikirefs':wikirefs, 'settings':settings})
        # x = loader.render_to_string('frontpage.html')
        return x

