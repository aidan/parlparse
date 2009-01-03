import logging
import unicodedata

from unpylons.lib.base import *

log = logging.getLogger(__name__)

class NationController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return 'List of nations ...'
    
    def info(self, id=None):
        return 'Nation is called: %s' % id

    def flagof(self, entity):
        response.headers['Content-type'] = 'image/png'
        fin = open("png100/Flag_of_Unknown.png", "rb")
        x = fin.read()
        fin.close()
        return x

    def nation(self, snation):
        c.nation = model.Member.query.filter_by(sname=snation).first()
        c.totalspeechcount = model.Speech.query.filter_by(member_name=c.nation.name).count()
        # can't work out how to query this in sqlalchemy -- filter(model.Vote.descrition.c.body=="SC") doesn't work
        
        c.totalvotecount = model.Vote.query.filter_by(member_name=c.nation.name).count()
        allvotes = model.Vote.query.filter_by(member_name=c.nation.name).order_by(model.Vote.c.minority_score)
        allvotes = [m  for m in allvotes  if m.division]  # where's the bad stuff getting in?
        c.scvotes = [m  for m in allvotes  if m.division.body=="SC"][:5]
        c.gavotes = [m  for m in allvotes  if m.division.body=="GA"][:10]
        c.lastvotedate = allvotes and allvotes[0].division.document.date
        for m in allvotes:
            c.lastvotedate = max(c.lastvotedate, m.division.document.date)
        sss = model.Division.query.first()
        #c.message = c.nation.name + "---- " + str(allvotes) # str([m.member_name  for m in sss.votes])
        #c.message += "  ******  "
        #c.message += str([m.division  for m in model.Vote.query.filter_by(member_name="El Salvador").limit(20).all()])
        return render('nation')
    


