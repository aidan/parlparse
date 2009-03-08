import os
import logging
import sys
import re

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

class IndexesController(BaseController):

    def frontpage(self, url=None):
        c.scmeetings = list(model.Meeting.query.filter_by(body="SC").order_by(model.meeting_table.c.datetime.desc()).limit(12))
        c.garecords = LoadAgendaNames("recent")[:8]
        c.wikirefs = ShortWikipediaTableM(12)

# produce this rendering of the scmeetings in the front page column

        x = render('frontpage') #, {'trail':'locise', 'secrecords':recsc, 'garecords':recag, 'wikirefs':wikirefs, 'settings':settings})
        # x = loader.render_to_string('frontpage.html')
        return x

    def nations(self):
        c.nations = list(model.Member.query.filter_by(finished="9999-12-31"))
        c.ncols = 4
        c.colleng = int((len(c.nations) + c.ncols - 1) / c.ncols)
        return render('nations')

    def documentsgasession(self, session):
        c.session = session
        c.documents = model.Document.query.filter_by(body="GA", session=session).filter('type!="PV"')
        c.pvdocuments = model.Document.query.filter_by(body="GA", session=session).filter('type="PV"')
        return render('documentsgasession')

    def documentsscyear(self, year):
        c.year = year
        c.documents = model.Document.query.filter_by(body="SC", year=year).filter('type!="PV"') # should order (copy over the dates)
        c.pvdocuments = model.Document.query.filter_by(body="SC", year=year).filter('type="PV"')
        return render('documentsscyear')

    def sctopics(self):
        c.topics = model.Topic.query.filter_by(agendanum=None).order_by(model.topic_table.c.name)
        #c.topics = [m  for m in topics  if not m.agendanum]
        return render('sctopics')

    def sctopic(self, topic):
        c.topic = model.Topic.query.filter_by(name=topic.replace("_", " ")).first()
        return render('sctopic')

    def gasessionagendas(self, session):
        c.session = session
        c.topics = model.Topic.query.filter_by(session=session).order_by(model.topic_table.c.name)
        return render('gatopics')

    def gaagenda(self, agendanum):
        c.topic = model.Topic.query.filter_by(agendanum=agendanum).first()
        return render('gatopic')

    def scindexordered(self, year):
        if year == "all":
            c.scmeetings = model.Meeting.query.filter_by(body="SC").order_by(model.meeting_table.c.datetime)
        else:
            c.scmeetings = model.Meeting.query.filter_by(body="SC", year=year).order_by(model.meeting_table.c.datetime)
        return render('scindexordered')


    # redirects
    def meeting(self, docid):
        mga = re.match("A.(\d+).PV.(\d+)$", docid)
        if mga:
            # check if meeting actually parsed
            return redirect_to('gameeting', session=mga.group(1), meeting=mga.group(2))
        return document.documentspec(docid)
        # http://127.0.0.1:5000/meeting/A-51-PV.88#pg024-bk02
