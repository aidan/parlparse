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

parlparsedir = "/home/goatchurch/undemocracy/parlparse"
allmembersfile = os.path.join(parlparsedir, "members", "all-members.xml")
peoplefile = os.path.join(parlparsedir, "members", "people.xml")

def LoadMPs():
    fin = open(allmembersfile)
    allmemberstext = fin.read().decode('latin-1')
    fin.close()
    
    for m in model.Member.query.filter_by(countrycode3="MP"):
        model.Session.delete(m)        
    
    for membertext in re.findall('(?s)<member(.*?)/>', allmemberstext):
        memberm = { }
        for param, val in re.findall('(\w+)="([^"]*)"', membertext):
            memberm[param] = unicode(val)
           
        print memberm["id"]
    
        mc = model.PWConstituency.query.filter_by(name=memberm["constituency"]).first()
        if not mc:
            mc = model.PWConstituency(name=memberm["constituency"])
            model.Session.flush()
        
        m = model.Member(name=memberm["id"], countrycode3="MP")
        m.pwperson_fullname = "%s %s" % (memberm["firstname"], memberm["lastname"])
        m.isnation = False
        m.started = memberm["fromdate"]
        m.finished = memberm["todate"]
        m.pwparty = memberm["party"]
        m.pwrepresenting = memberm["constituency"]
        #    Column('pwperson_id', String(100), ForeignKey('pwperson.id')), 

        model.Session.flush()

    fin = open(peoplefile)
    peopletext = fin.read()
    fin.close()

# members
#<member
#    id="uk.org.publicwhip/member/4"
#    house="commons"
#    title="" firstname="Nick" lastname="Ainger"
#    constituency="Carmarthen West &amp; South Pembrokeshire" party="Lab"
#    fromdate="1997-05-01" todate="2001-05-14" fromwhy="general_election" towhy="general_election"
#/>

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
