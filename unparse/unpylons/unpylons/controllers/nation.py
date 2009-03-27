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
        # can't work out how to query this in sqlalchemy -- filter(model.Vote.description.c.body=="SC") doesn't work
        
        c.totalvotecount = model.Vote.query.filter_by(member_name=c.nation.name).count()
    
        #allvotes = model.Vote.query.filter_by(member_name=c.nation.name).order_by(model.Vote.c.minority_score)
        #allvotes = [m  for m in allvotes  if m.division]  # where's the bad stuff getting in?
        
        c.scvotes = model.Vote.query.filter_by(member_name=c.nation.name).join('division').filter(model.Division.body=="SC").order_by(model.Vote.c.minority_score).limit(5)
        c.scvotes = [m  for m in c.scvotes  if m.division]
        #return str([m.division.body  for m in c.scvotes])
    
        #c.gavotes = [m  for m in allvotes  if m.division.body=="GA"][:10]
        c.gavotes = model.Vote.query.filter_by(member_name=c.nation.name).join('division').filter(model.Division.body=="GA").order_by(model.Vote.c.minority_score).limit(10)
        c.gavotes = [m  for m in c.gavotes  if m.division]
        
        securitycouncildates = list(model.MemberCommittee.query.filter_by(member_name=c.nation.name).filter(model.MemberCommittee.body=="SC").order_by(model.MemberCommittee.started))
        if securitycouncildates and str(securitycouncildates[0].finished) == "9999-12-31":
            c.securitycouncimembership = "Permanent"
        elif securitycouncildates:
            c.securitycouncimembership = ", ".join(["%s-%s" % (scd.started.year, int(scd.started.year) + 1)  for scd in securitycouncildates])
        else:
            c.securitycouncimembership = "Never"
        
        #c.lastvotedate = allvotes and allvotes[0].division.document.date
        #for m in allvotes:
        #    c.lastvotedate = max(c.lastvotedate, m.division.document.date)
        # a = model.select("SELECT max(document.date) FROM document")
        # a = model.select(model.func.max(model.document_table.c.date))
        #from sqlalchemy.sql import text
        #a = text('Select max(date) from document')
        #a = model.Session.connection().execute(a).fetchall()[0]
#        a = model.Vote.query.from_statement("SELECT max(document.date) FROM vote LEFT JOIN division ON vote.docidhref = division.docidhref LEFT JOIN document ON division.docid = document.docid WHERE vote.member_name='United Kingdom'").params(name=c.nation).all()
        
        #print a
        #return "hi there"
    
        #c.lastvotedate = model.Vote.query.filter_by(member_name=c.nation.name).join('division', 'document').group_by("*").max(model.Document.date)
        
        sss = model.Division.query.first()
        #c.message = c.nation.name + "---- " + str(allvotes) # str([m.member_name  for m in sss.votes])
        #c.message += "  ******  "
        #c.message += str([m.division  for m in model.Vote.query.filter_by(member_name="El Salvador").limit(20).all()])
        return render('nation')
    


