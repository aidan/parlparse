import os
import logging
import sys

from unpylons.lib.base import *

log = logging.getLogger(__name__)

sys.path.append("/home/undemocracy/unparse-live")
sys.path.append("/home/undemocracy/unparse-live/djweb")
sys.path.append("/home/undemocracy/unparse-live/web2")
sys.path.append("/home/undemocracy/unparse-live/pylib")
os.environ['PYTHONPATH'] = "/home/undemocracy/unparse-live"

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
    
    def about(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        from django.template import loader
        import djweb.settings as settings
        from web2.wikitables import ShortWikipediaTableM
        from web2.db import LogIncomingDB, GetUnlogList
        from web2.indexrecords import LoadAgendaNames, LoadSecRecords

        recsc = LoadSecRecords("recent")[:12]
        recag = LoadAgendaNames("recent")[:8]
        wikirefs = ShortWikipediaTableM(12)
        searchlist = GetUnlogList("search", 100)
        x = loader.render_to_string('frontpage.html', {'searchlist':searchlist, 'trail':'locise', 'secrecords':recsc, 'garecords':recag, 'wikirefs':wikirefs, 'settings':settings})
        # x = loader.render_to_string('frontpage.html')
        return x
