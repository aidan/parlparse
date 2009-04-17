import logging
import unicodedata

from unpylons.lib.base import *

log = logging.getLogger(__name__)

class NationController(BaseController):

    def nations(self):
        c.nations = list(model.Member.query.filter_by(house="UNmember").filter_by(finished="9999-12-31"))
        c.ncols = 4
        c.colleng = int((len(c.nations) + c.ncols - 1) / c.ncols)
        
        c.defunctnations = list(model.Member.query.filter_by(house="UNmember").filter(model.Member.finished!="9999-12-31"))
        
        c.nonnations = list(model.Member.query.filter_by(house="UNunknown"))

        return render('nations')
    
    def nationscontinent(self):
        c.nations = list(model.Member.query.filter_by(house="UNmember").filter_by(finished="9999-12-31"))
        c.ncols = 3
        c.nationscontinent = [ ]
        for continentcode, continent in [("AF", "Africa"), ("AS", "Asia"), ("EU", "European Union"), ("NA", "North America"), ("OC", "Oceania"), ("SA", "South America")]:
            lnationscontinent = [ nation  for nation in c.nations  if nation.countrycontinent == continentcode ]
            c.nationscontinent.append({"continent":continent, "nations":lnationscontinent, "colleng":int((len(lnationscontinent) + c.ncols - 1) / c.ncols) })
        return render('nationscontinent')
        
    
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
        
        # could be efficient sql things to get these things
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
        
        return render('nation')
    

    def nationambassador(self, snation, sambassador):
        c.nation = model.Member.query.filter_by(sname=snation).first()
        if sambassador == "all":
            return render('nationambassadorall')
        c.ambassador = model.Ambassador.query.filter_by(member=c.nation).filter_by(lastname=sambassador).first()
        return render('nationambassador')
        
    def nationvotes(self, snation):
        c.nation = model.Member.query.filter_by(sname=snation).first()
        return render('votesnation')

