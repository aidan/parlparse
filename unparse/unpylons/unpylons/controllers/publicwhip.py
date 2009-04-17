import logging
import unicodedata
import os
import re
import xml.dom.minidom

from unpylons.lib.base import *

log = logging.getLogger(__name__)

import unpylons.model as model

# table of parliamentary terms
termdates = {"1997":("1997-05-01", "2001-05-01"), 
             "2001":("2001-05-01", "2005-05-01"), 
             "2005":("2005-05-01", "9999-12-31")}

def VoteMajority(vote):
    if vote.division.favour >= vote.division.against:
        if vote.vote == "favour":
            return "majority"
        if vote.vote == "against":
            return "minority"
    else:
        if vote.vote == "favour":
            return "minority"
        if vote.vote == "against":
            return "majority"
    return vote.vote
        


# should save scrape version in the document
def GetFile(docid):
    parldataxmldir = "/home/goatchurch/undemocracy/parldata/scrapedxml"
    mdocid = re.match("uk.org.publicwhip/(.*?)/(\d\d\d\d-\d\d-\d\d)", docid)
    if mdocid.group(1) == "debate":
        parldir, stem = os.path.join(parldataxmldir, "debates"), "debates" + mdocid.group(2) + "[a-z]"
    fdebs = [ f  for f in os.listdir(parldir)  if re.match(stem, f) ]
    return os.path.join(parldir, max(fdebs))

def GetText(pnode):
    res = [ ]
    for node in pnode.childNodes:
        if node.nodeType == xml.dom.Node.TEXT_NODE:
            res.append(node.data)
    return " ".join(res)
    

# load debates/votes
class PublicwhipController(BaseController):

    def members(self, term):
        c.termfrom, c.termto = termdates[term]
        c.mps = model.Member.query.filter(model.or_(model.member_table.c.house=="PWcommons", model.member_table.c.house=="PWlords"))\
                        .filter(model.and_(model.member_table.c.started<c.termto, model.member_table.c.finished>c.termfrom))\
                        .group_by(model.member_table.c.pwperson_id)\
                        .order_by([model.member_table.c.pwlastname, model.member_table.c.pwfirstname])
        c.persons = [mp.pwperson  for mp in c.mps  if mp.pwperson]
        return render('pwmps')
    
    def member(self, sname):
        c.person = model.PWPerson.query.filter_by(sname=sname).first()
        c.votes = [ ]
        c.speeches = [ ]
        for seat in c.person.seats:
            c.votes.extend(seat.votes)
            c.speeches.extend(seat.speeches)
        c.VoteMajority = VoteMajority
        
        meetingsspokenmap = { }
        for speech in c.speeches:
            meetingsspokenmap.setdefault(speech.meeting_docidhref, []).append(speech.numparagraphs)
        c.meetingsspoken = [model.Meeting.query.filter_by(docidhref=meetingdocidhref).one()  for meetingdocidhref in meetingsspokenmap]
        c.meetingsspoken.sort(key=lambda meeting: (meeting.datetime))
        return render('pwperson')

    def divisions(self, term):
        c.termfrom, c.termto = termdates[term]
        c.divisions = model.Division.query.filter(model.or_(model.division_table.c.body=="PWlords", model.member_table.c.house=="PWcommons"))\
                        .filter(model.and_(model.division_table.c.datetime>=c.termfrom, model.division_table.c.datetime<c.termto))
        return render('pwdivisions')

    def division(self, date, house, number):
        divhouse = (house == "commons" and "debatedivision" or "lordsdivision")
        divisioncode = "uk.org.publicwhip/%s/%s/%s" % (divhouse, date, number)
        c.division = model.Division.query.filter(model.division_table.c.description==divisioncode).first()
        c.votes = list(c.division.votes)
        c.votes.sort(key=lambda vote: (vote.member.pwparty, vote.member.pwlastname, vote.member.pwfirstname))
        return render('pwdivision')

    def meeting(self, date, house, meetinghref):
        debhouse = (house == "commons" and "debate" or "lords")
        docid = "uk.org.publicwhip/%s/%s" % (debhouse, date)
        c.document = model.Document.query.filter_by(docid=docid).one()
        fdeb = GetFile(docid)
        
        dom = xml.dom.minidom.parse(fdeb)
        topelement = dom.getElementsByTagName("publicwhip")[0]

        c.blocks = [ ]
        subheadinghref = ""
        for node in topelement.childNodes:
            if node.nodeType != xml.dom.Node.ELEMENT_NODE:
                continue
            mid = re.match("(uk.org.publicwhip/debate/(\d\d\d\d-\d\d-\d\d))[a-z]\.(\d+\.\d+)", node.getAttribute("id"))
            href = mid.group(3)
            docidhref = docid + "#" + href
            
            if re.match("\w*?-heading", node.tagName):
                subheadinghref = href  
            
            if meetinghref and subheadinghref != meetinghref:
                continue
            
            # build up the block
            block = { }
            if re.match("\w*?-heading", node.tagName):
                block["divclass"] = "heading"
                block["meeting"] = model.Meeting.query.filter_by(docidhref=docidhref).one()
            
            # this one looks for the member rather than the speech (in case it doesn't exist -- eg Hon Members) - should consider the speeches
            elif node.tagName == "speech":
                block["divclass"] = "speech"
                speakerid = node.getAttribute("speakerid")
                block["speakerid"] = speakerid 
                if speakerid and speakerid != "unknown":
                    block["member"] = model.Member.query.filter_by(name=speakerid).first()
                else:
                    block["member"] = None
                block["paragraphs"] = [GetText(pnode)  for pnode in node.getElementsByTagName("p")]

            elif node.tagName == "division":
                block["divclass"] = "division"
                block["division"] = model.Division.query.filter_by(docidhref=docidhref)

            c.blocks.append(block)

        return render('pwmeeting')
