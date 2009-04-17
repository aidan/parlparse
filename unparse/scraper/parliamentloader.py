#!/usr/bin/python

import sys
import re
import os
import urllib2
from unmisc import IsNotQuiet
import datetime
from unscrape import ScrapePDF
from pdfinfo import PdfInfo

import unpylons.model as model
import xml.dom.minidom

parlparsedir = "/home/goatchurch/undemocracy/parlparse"
allmembersfile = os.path.join(parlparsedir, "members", "all-members.xml")
alllordsfile = os.path.join(parlparsedir, "members", "peers-ucl.xml")
peoplefile = os.path.join(parlparsedir, "members", "people.xml")

parldatadir = "/home/goatchurch/undemocracy/parldata"
parldebates = os.path.join(parldatadir, "scrapedxml", "debates")


# members
#<member
#    id="uk.org.publicwhip/member/4"
#    house="commons"
#    title="" firstname="Nick" lastname="Ainger"
#    constituency="Carmarthen West &amp; South Pembrokeshire" party="Lab"
#    fromdate="1997-05-01" todate="2001-05-14" fromwhy="general_election" towhy="general_election"
#/>
def LoadCommonsSeats():
    dom = xml.dom.minidom.parse(allmembersfile)
    for member in dom.getElementsByTagName("member"):
        constituency = member.getAttribute("constituency")
        mc = model.PWConstituency.query.filter_by(name=constituency).first()
        if not mc:
            mc = model.PWConstituency(name=constituency)
            model.Session.flush()
        
        m = model.Member(name=member.getAttribute("id"), house="PWcommons")
        m.pwtitle, m.pwfirstname, m.pwlastname = member.getAttribute("title"), member.getAttribute("firstname"), member.getAttribute("lastname")
        m.pwperson_fullname = "%s %s" % (m.pwfirstname, m.pwlastname)
        m.started, m.finished = member.getAttribute("fromdate"), member.getAttribute("todate")
        m.pwparty = member.getAttribute("party")
        if m.pwparty == "Lab/Co-op":  # don't care about this distinction
            m.pwparty = "Lab"
        m.pwrepresenting = constituency

        print m.name, constituency
        model.Session.flush()


#<lord
#    id="uk.org.publicwhip/lord/100439"
#    house="lords"
#    forenames="Philip"
#    forenames_full="Philip Brian Cecil"
#    title="Lord" lordname="Moore" lordofname="Wolvercote"
#    county="the City of Oxford"
#    peeragetype="L" affiliation="XB"
#    fromdate="1986" todate="9999-12-31"
#/>
def LoadLordsSeats():
    dom = xml.dom.minidom.parse(alllordsfile)
    for lord in dom.getElementsByTagName("lord"):
        m = model.Member(name=lord.getAttribute("id"), house="PWlords")
        m.pwtitle, m.pwfirstname, m.pwlastname = lord.getAttribute("title"), lord.getAttribute("lordname"), lord.getAttribute("lordofname")
        m.pwperson_fullname = "%s %s of %s" % (m.pwtitle, m.pwfirstname, m.pwlastname)
        m.started, m.finished = lord.getAttribute("fromdate"), lord.getAttribute("todate")
        m.pwparty = lord.getAttribute("affiliation")
    
        print m.name, m.pwperson_fullname
        model.Session.flush()


# people
#<person id="uk.org.publicwhip/person/10003" latestname="Baroness Adams of Craigielea">
#    <office id="uk.org.publicwhip/lord/100867" current="yes"/>
#    <office id="uk.org.publicwhip/member/3"/>
#    <office id="uk.org.publicwhip/member/689"/>
#    <office id="uk.org.publicwhip/moffice/2183"/>
#    <office id="uk.org.publicwhip/moffice/2374"/>
#    <office id="uk.org.publicwhip/moffice/2456"/>
#    <office id="uk.org.publicwhip/moffice/2606"/>
#</person>
def LoadPersons():
    dom = xml.dom.minidom.parse(peoplefile)
    for person in dom.getElementsByTagName("person"):
        latestname = name=person.getAttribute("latestname")
        m = model.PWPerson(id=person.getAttribute("id"), name=latestname)
        m.sname = latestname.lower().replace(" ", "_")
        model.Session.flush()
        print latestname
            
        for office in person.getElementsByTagName("office"):
            officeid = office.getAttribute("id")
            if re.search("member|lord", officeid):
                mp = model.Member.query.filter_by(name=officeid).first()
                if mp:
                    mp.pwperson = m
                else:
                    print "unmatched officid %s %s" % (latestname, officeid)  # these are ni-members
        model.Session.flush()
    

# main function
def LoadMPs():
    print "Deleting PWcommons"
    for m in model.Member.query.filter_by(house="PWcommons"):
        model.Session.delete(m)        
    print "Deleting PWlords"
    for m in model.Member.query.filter_by(house="PWlords"):
        model.Session.delete(m)        
    print "Deleting PWconstituencies"
    for m in model.PWConstituency.query.all():
        model.Session.delete(m)        
    print "Deleting PWpersons"
    for m in model.PWPerson.query.all():
        model.Session.delete(m)        
    
    LoadCommonsSeats()
    LoadLordsSeats()
    LoadPersons()

        
        
#<division id="uk.org.publicwhip/debate/2009-03-10a.215.2" nospeaker="true" divdate="2009-03-10" divnumber="56" colnum="215"  time="018:48:00" url="http://www.publications.parliament.uk/pa/cm200809/cmhansrd/cm090310/debtext/90310-0013.htm#090310128000626">
#    <divisioncount ayes="161" noes="349" tellerayes="2" tellernoes="2"/>
#    <mplist vote="aye">
#        <mpname id="uk.org.publicwhip/member/1929" vote="aye">Afriyie, Adam</mpname>
#        <mpname id="uk.org.publicwhip/member/1857" vote="aye">Ainsworth, Mr. Peter</mpname>
#        <mpname id="uk.org.publicwhip/member/1785" vote="aye" teller="yes">James Duddridge</mpname>
#    </mplist>
#    <mplist vote="no">
#        <mpname id="uk.org.publicwhip/member/1604" vote="no">Abbott, Ms Diane</mpname>
#        <mpname id="uk.org.publicwhip/member/1911" vote="no" teller="yes">Claire Ward</mpname>
#    </mplist>
#</division>

def LoadDivision(subheadingmeeting, href, ldatetime, divisionnode):
    # load in all MPs who could vote here and then over-ride things with the settings
    print "  division:", divisionnode.getAttribute("divdate"), divisionnode.getAttribute("divnumber")
    docidhref = subheadingmeeting.docid + "#" + href
    divisioncode = "uk.org.publicwhip/debatedivision/%s/%s" % (divisionnode.getAttribute("divdate"), divisionnode.getAttribute("divnumber"))
    
    m = model.Division(docidhref=docidhref, docid=subheadingmeeting.docid, href=href, meeting_docidhref=None, description=divisioncode)
    m.body = subheadingmeeting.body
    divdate = divisionnode.getAttribute("divdate")
    assert divdate == subheadingmeeting.document.date
    m.datetime = ldatetime
    m.meeting = subheadingmeeting
    model.Session.flush()
            
            
    # lift (redundant) numbers from there
    divisioncount = divisionnode.getElementsByTagName("divisioncount")[0]
    m.favour = int(divisioncount.getAttribute("ayes"))
    m.against = int(divisioncount.getAttribute("noes"))
    
    
    # fill in the absent votes at this point here (wish had done so in the parser)
    possiblevoters = model.Member.query.filter_by(house=m.body).filter(model.and_(model.member_table.c.started<=divdate, model.member_table.c.finished>divdate))
    allvotes = { }
    for possiblevoter in possiblevoters:
        allvotes[possiblevoter.name] = "absent"
    m.absent = len(allvotes) - (m.favour + m.against)
    tellers = [ ]
    for mpname in divisionnode.getElementsByTagName("mpname"):
        voterid = mpname.getAttribute("id")
        if allvotes[voterid] == "favour" and mpname.getAttribute("vote") == "no":
            allvotes[voterid] = "abstain"
        else:
            assert allvotes[voterid] == "absent", "%s: %s" % (voterid, allvotes[voterid])
            if mpname.getAttribute("vote") == "aye":
                allvotes[voterid] = "favour"
            else:
                assert mpname.getAttribute("vote") == "no"
                allvotes[voterid] = "against"
        if mpname.getAttribute("teller"):
            tellers.append(voterid)
        
        
    # produce minority scores per party per vote scaled
    partyminorityscores = { }
    for voterid, vote in allvotes.iteritems():
        party = model.Member.query.filter_by(name=voterid).one().pwparty
        partyminorityscore = partyminorityscores.setdefault(party, {"favour":0, "against":0, "absent":0, "abstain":0})
        partyminorityscore[vote] += 1

    for partyminorityscore in partyminorityscores.values():
        partyminorityscoresum = float(sum(partyminorityscore.values()))
        for vote in partyminorityscore:
            partyminorityscore[vote] /= partyminorityscoresum

        
    for voterid, vote in allvotes.iteritems():
        member = model.Member.query.filter_by(name=voterid).one()
        mv = model.Vote(docidhref=docidhref, member=member, vote=vote)
        mv.minority_score = partyminorityscores[member.pwparty][vote]
        mv.isteller = (voterid in tellers)

    model.Session.flush()



def LoadParlDebate(debdoc, fdeb):
    dom = xml.dom.minidom.parse(fdeb)
    topelement = dom.getElementsByTagName("publicwhip")[0]
    
    # topelement.getAttribute("scrapeversion")  a,b,c
    if topelement.getAttribute("latest") == "no":  # otherwise has <gidredirect>s and some extra speeches
        print "  skipping not latest parsing"
        return
    
    # tells when the document (pdf or html) was last modified so we can rescan (eg for search) just the new ones
    
    subheadinghref = ""
    subheadingmeeting = model.Meeting(docidhref=debdoc.docid + "#", docid=debdoc.docid, href=subheadinghref)
    
    for node in topelement.childNodes:
        if node.nodeType != xml.dom.Node.ELEMENT_NODE:
            continue
        
        mid = re.match("(uk.org.publicwhip/debate/(\d\d\d\d-\d\d-\d\d))[a-z]\.(\d+\.\d+)", node.getAttribute("id"))
        assert mid, "Failed on: " + str([node.attributes.item(i).name  for i in range(node.attributes.length)])
        assert mid.group(2) == debdoc.date
        docid, href = mid.group(1), mid.group(3)
        #print docid, debdoc.docid
        assert docid == debdoc.docid
        docidhref = debdoc.docid + "#" + href
        ldatetime = debdoc.date + " " + node.getAttribute("time")  # this will have problems with the over-running case beyond midnight
        
        if re.match("\w*?-heading", node.tagName):
            subheadinghref = href  
            subheadingmeeting = model.Meeting(docidhref=docidhref, docid=debdoc.docid, href=href)
            subheadingmeeting.body = debdoc.body
            subheadingmeeting.title = re.sub("\s+", " ", node.firstChild.data).strip()
            #print node.tagName, subheadingmeeting.title
            subheadingmeeting.datetime = ldatetime
            model.Session.flush()
            
        #<speech id="uk.org.publicwhip/debate/2008-05-15b.1540.1" speakerid="uk.org.publicwhip/member/1929" speakername="Adam Afriyie" colnum="1540"  time="10:30:00" url="http://www.publications.parliament.uk/pa/cm200708/cmhansrd/cm080515/debtext/80515-0003.htm#08051586000918">
        #<p pid="b.1540.1/1">The Sainsbury review is a stinging indictment of Government failure when it comes to innovation. It...</p>
        #<p pid="b.1540.1/2">After talking for 10 years about public procurement innovation, the Minister said last week that...</p>
        #<p pid="b.1540.1/3" class="indent">&quot;Demand-side factors, such as procurement and regulation, ...</p>
        #<p pid="b.1540.1/4">Does the Minister agree with his well-respected predecessor?</p>
        #</speech>
        elif node.tagName == "speech":
            numparagraphs = len(node.getElementsByTagName("p"))
            member_name = node.getAttribute("speakerid")
            m = model.Speech(docidhref=docidhref, docid=debdoc.docid, href=href, meeting_docidhref=subheadingmeeting.docidhref, numparagraphs=numparagraphs)
            if node.getAttribute("nospeaker") != "true" and member_name != "unknown":
                assert member_name, node.getAttribute("id")
                m.member_name = member_name 
            model.Session.flush()

            # we could load the text into here and have done with referring back to the file!  
        
        if node.tagName == "division":
            LoadDivision(subheadingmeeting, href, ldatetime, node)


# construct the document
# then the meetings from the headings
# then link the divisions to it
# then make the votes link to those

# could we make the lords and commons simply committees of the Parliament?

# go through all the debates
def LoadParliamentaryDebates(stem, bforceparse):
    debmap = { }
    for parlfile in os.listdir(parldebates):
        mparlfile = re.match("(.*?\d\d\d\d-\d\d-\d\d)([a-z]).xml", parlfile)
        if mparlfile:
            debd = mparlfile.group(1)
            if not stem or re.match(stem, debd):  # match the stem
                debmap.setdefault(debd, [ ]).append(parlfile)
    
    # now the loop through the documents
    # (we will handle the upgrades between the docids sometime later)
    debs = sorted(debmap.keys())
    for debd in debs:
        debfile = max(debmap[debd])   # choose to parse the latest version
        fdeb = os.path.join(parldebates, debfile)
        parseddoctimestamp = datetime.datetime.fromtimestamp(os.stat(fdeb).st_mtime)
        
        # make the new debate docid that matches inside the document
        debstem, debdate = re.match("([^\d]+)(\d\d\d\d-\d\d-\d\d)", debd).groups()
        if debstem == "debates":
            docid = "uk.org.publicwhip/debate/" + debdate
            body = "PWcommons"
        else:
            assert False, "unknown: " + debd
        
        # clear out and reboot everything connected to this document
        debdoc = model.Document.query.filter_by(docid=docid).first()
        if debdoc:
            if not bforceparse and parseddoctimestamp == debdoc.docmodifiedtime:
                print "Skipping already loaded doc by timestamp", docid, debd
                continue
            
            for lm in debdoc.meetings:
                model.Session.delete(lm)
            for lm in debdoc.speeches:
                model.Session.delete(lm)
            for lm in debdoc.divisions:
                for lmv in lm.votes:
                    model.Session.delete(lmv)
                model.Session.delete(lm)
            model.Session.delete(debdoc)
            model.Session.flush()
            
        # debstem is the body and type somehow
        debdoc = model.Document(docid=docid, body=body, type=debstem, date=debdate)
        model.Session.flush()
        
        print "Parsing doc", fdeb
        LoadParlDebate(debdoc, fdeb)
        debdoc.docmodifiedtime = parseddoctimestamp
        
    
    
