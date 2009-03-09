import os
import logging
import sys
import re

from unpylons.lib.base import *

import unpylons.model as model

log = logging.getLogger(__name__)


class IndexesController(BaseController):

    def frontpage(self, url=None):
        c.scmeetings = list(model.Meeting.query.filter_by(body="SC").order_by(model.meeting_table.c.datetime.desc()).limit(12))
        c.garecords = list(model.Meeting.query.filter_by(body="GA").order_by(model.meeting_table.c.datetime.desc()).limit(12))
        c.wikirefs = []#ShortWikipediaTableM(12)
        return render('frontpage')

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

    def gasessions(self):
        c.gasessions, c.scyears = model.GetSessionsYears()
        return render('gasessions')
    
    
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

    def gacondolences(self):
        c.topic = model.Topic.query.filter_by(agendanum="condolence").first()
        return render('gatopic')
    
    def scindexordered(self, year):
        if year == "all":
            c.scmeetings = model.Meeting.query.filter_by(body="SC").order_by(model.meeting_table.c.datetime)
        else:
            c.scmeetings = model.Meeting.query.filter_by(body="SC", year=year).order_by(model.meeting_table.c.datetime)
        return render('scindexordered')


    # redirects from wikipedia constructs to either the parsed or the document type, whichever is better
    def meeting(self, docid):
        # check if meeting actually parsed
        response.status_int = 302
        response.headers['location'] = h.url_for_doc(docid)
        return "Moved temporarily"
        #return redirect_to('gameeting', session=mga.group(1), meeting=mga.group(2))
        # http://127.0.0.1:5000/meeting/A-51-PV.88#pg024-bk02
