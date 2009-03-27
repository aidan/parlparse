# -*- coding: utf8 -*-

import os
import re
import datetime
from models import *
import unicodedata

def IsNotQuiet():
    return False

#metadata.drop_all()  # clears the tables 
#print "\n\nDDDDropped\n\n\n"
metadata.create_all()

def EnsureDocidsExist(docids):
    res = [ ]
    for docid in docids:
        m = Document.query.filter_by(docid=docid).first()
        if not m:
            m = Document(docid=docid)
            # (we could look up whether it is downloaded and record that)
            print "NewDocid added", docid
        res.append(m)
    return res
        
def EnsureDocidhrefExists(docidhref):
    m = Meeting.query.filter_by(docidhref=docidhref).first()
    if not m:
        docid = re.sub("#.*", "", docidhref)
        m = Meeting(docidhref=docidhref)
        print "making ", docidhref
    return m




def load_sc_topics(docid, heading, ldate, ldateend, topics, minutes, numspeeches, numparagraphs, numvotes, nextdocid):
    numvotes = 0 
    EnsureDocidsExist([docid])
    m = Meeting.query.filter_by(docid=docid).first()
    if not m:
        m = Meeting(docid=docid, docidhref=docid, body="SC")
    m.title = unicode(heading)[:499]   # shorten
    m.datetime = ldate
    m.year = int(ldate[:4])
    m.datetimeend = ldateend    
    m.minutes = minutes
    m.numspeeches, m.numparagraphs = numspeeches, numparagraphs
    m.numvotes = numvotes
    m.next_docid = nextdocid     # the list is scanned backwards
    m.meetingnumber = re.match("S-PV-(\d.+)$", docid).group(1)
    del m.topics[:]  # clear the list
    for tn in topics:
        t = Topic.query.filter_by(name=unicode(tn)).first()
        if not t:
            t = Topic(name=unicode(tn))
        m.topics.append(t)
    Session.flush()
    print 'Saved:', m.docid, [t.id  for t in m.topics]


# would like docid and href to be not rammed together, but docid is a primary key, unfortunately
def load_ga_debate(docid, ldate, gaagindoc):
    EnsureDocidsExist([docid])
    for m in Meeting.query.filter_by(docid=docid):
        Session.delete(m)        
    session, meetingnumber = re.match("A-(\d+)-PV.(\d+)$", docid).groups()
    for (subheadingid, agendanumstr, agtitle) in gaagindoc:
        docidhref = docid + "#" + subheadingid

        m = Meeting.query.filter_by(docidhref=docidhref).first()
        if not m:
            m = Meeting(docidhref=docidhref, docid=docid, href=subheadingid, body="GA", session=session, meetingnumber=meetingnumber)
        m.title = agtitle.decode("latin1")
        m.datetime = ldate
        m.agendanumstr = agendanumstr
        
        #print m.title
    Session.flush()
    
def load_ga_agendanum(session, agendanum, mctitle, mccategory, dochrefs):
    t = Topic.query.filter_by(agendanum=agendanum).first()
    if not t:
        t = Topic(agendanum=agendanum)

    t.name = unicode(mctitle.decode("latin1"))
    t.session = session
    t.meetings = [ ]        
    for docid, subheadingid in dochrefs:
        docidhref = docid + "#" + subheadingid
        m = Meeting.query.filter_by(docidhref=docidhref).first()
        if m:
            t.meetings.append(m)
    Session.flush()
    print 'Session', session, "Agenda", agendanum


def ProcessParsedVotePylon(docid, href, div_content):
    mvote = re.match('\s*<p class="motiontext"[^>]*>(.*?)</p>\s*<p class="votecount"[^>]*>(.*?)</p>\s*<p class="votelist"[^>]*>(.*?)</p>', div_content)
    assert mvote, div_content
    mvnum = re.match("favour=(\d+)\s+against=(\d+)\s+abstain=(\d+)\s+absent=(\d+)", mvote.group(2))
    vnum = [int(mvnum.group(1)), int(mvnum.group(2)), int(mvnum.group(3)), int(mvnum.group(4))]
    motiontext = mvote.group(1)
    
    resolution_docids = re.findall('<a href="../pdf/(.*?).pdf"', motiontext)
    resolution_docid = resolution_docids and resolution_docids[-1] or None
    docidhref = docid + "#" + href
    EnsureDocidsExist(resolution_docids)

    motiontext = re.sub('<a [^>]*>([^<]*)</a>', "\\1", motiontext)
    motiontext = re.sub("<[^>]*>", " ", motiontext)
    motiontext = re.sub(" (?:was|were) (?:retained|adopted|rejected) by (?:.*? abstentions?|\d+ votes to \d+)", "", motiontext)
    
    if not motiontext:
        motiontext = unicode("blank space for: " + docid)
   

    m = Division(docidhref=docidhref, docid=docid, href=href, description=motiontext, resolution_docid=resolution_docid)
    m.favour = vnum[0]
    m.against = vnum[1]
    m.abstain = vnum[2]
    m.absent = vnum[3]
    m.body = re.match("A", docid) and "GA" or "SC"
    
    totalv = float(vnum[0] + vnum[1] + vnum[2] + vnum[3])
    minorityscores = { 'favour':vnum[0]/totalv, 'against':vnum[1]/float(vnum[0]+vnum[1]),
                       'abstain':vnum[2]/totalv, 'absent':vnum[3]/totalv }
        
    print "mmminorityscores", minorityscores
    mvlist = [ ]
    for mvoten in re.finditer('<span class="([^"\-]*)-?([^"]*)">([^<]*)</span>', mvote.group(3)):
        nation = mvoten.group(3)
        vote = mvoten.group(1)
        intendedvote = mvoten.group(2) or vote
        mv = Vote(docidhref=docidhref, member_name=nation, vote=intendedvote, orgvote=vote, minority_score=minorityscores[intendedvote])
        mvlist.append(mv) 
        
    Session.flush()


def ProcessParsedDocumentPylon(m, docid, ftext):
    assert m.docid == docid
    
    # how to delete in a batch???
    for lm in DocumentRefDocument.query.filter_by(document1_docid=docid):
        #print "deleting", lm.meeting1_docidhref
        Session.delete(lm)
    for lm in Speech.query.filter_by(docid=docid):
        Session.delete(lm)
    for lm in Division.query.filter_by(docid=docid):
        Session.delete(lm)
    Session.flush()

    doccitations = [ ]
    mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)")?[^>]*>\s*(.*?)^</div>', ftext, re.S + re.M)
    subheadinghref = ""
    
    for mdiv in mdivs:
        # used to dereference the string as it is in the file
        div_class = mdiv.group(1)
        div_href = mdiv.group(2)
        div_data = (docid, mdiv.start(), mdiv.end() - mdiv.start(), mdiv.group(2))
        div_content = unicode(mdiv.group(4))
        docidhref = docid + "#" + div_href
        
        if div_class == "recvote":
            ProcessParsedVotePylon(docid, div_href, div_content)
        elif div_class == "subheading":
            subheadinghref = div_href  # these are going to be collated into meetings in the agendas
            #print "\n\n\n", div_content
        elif div_class == "heading":
            m.date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', div_content).group(1)
            #print "sssssdate", m.date
        elif div_class == "council-agenda":
            ca = re.sub("<p[^>]*>", "", div_content)
            ca = re.sub("\s*</p>\s*", "\n", ca)
            ca = re.sub("<[^>]*>", "", ca).strip()
            m.title = unicode(ca)[:500]  # make short 
            #print "\n\n\n", m.title
        
        elif div_class == "spoken":
            mm = re.match('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(non-)?nation">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>\s*', div_content)
            assert mm, div_content[:160]
            pcontent = div_content[mm.end(0):]
            #print mm.groups()
            name = mm.group(1)
            member = mm.group(3) or None 
            if member and not Member.query.filter_by(name=member).first():
                print "Constructing member::", member
                m = Member(name=unicode(member))
                m.sname = member.lower().replace(" ", "_").replace("'", "")
                m.isnation = False
            meeting = docid + "#" + subheadinghref
            EnsureDocidhrefExists(meeting)
            isnation = not mm.group(2)
            sname = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').lower().strip()
            lastname = re.search("(\S+)$", sname).group(1)
            m = Speech(docidhref=docidhref, name=name, lastname=lastname, member_name=member, 
                       docid=docid, href=div_href, meeting_docidhref=meeting, numparagraphs=9, isnation=isnation)
            
        elif div_class == "italicline":
            pass
        elif div_class == "italicline-tookchair":
            pass
        elif div_class == "italicline-spokein":
            pass
        
        elif div_class == "end-document":
            pass
        elif div_class == "council-attendees":
            pass
        elif div_class == "assembly-chairs":
            pass
             
        else:
            print "UNKNOWNDIVCLASS", div_class
    
        
        # make all the citations in the speech
        pgid = div_href
        for mdoc in re.finditer('id="([^"]*)"|<a href="../(?:pdf|html)/([\w\-\.()]*?)\.(?:pdf|html)"[^>]*>', div_content):
            if mdoc.group(1):
                pgid = mdoc.group(1)
            if mdoc.group(2):
                docid2 = mdoc.group(2)
                meeting1_docidhref = docid + "#" + subheadinghref
                EnsureDocidhrefExists(meeting1_docidhref)
                EnsureDocidsExist([docid2])
                Session.flush()
                doccite = DocumentRefDocument(document1_docid=docid, document2_docid=docid2, href1=pgid)
                doccite.meeting1_docidhref = meeting1_docidhref
                doccitations.append(doccite)
    
    #print " Added citations", len(doccitations)
    Session.flush()


def ProcessDocumentPylon(docid, pdfdir, htmldir):
    m = Document.query.filter_by(docid=docid).first()
    if not m:
        m = Document(docid=docid)

    mda = re.match("A(-RES)?(-\d\d)?(-PV)?", docid)
    mds = re.match("S-RES-\d+\((\d+)\)|S(-PRST)?(-PV)?(-\d+)", docid)
    if mda:
        m.body = "GA"
        m.session = mda.group(2) and int(mda.group(2)[1:]) or 0
        if mda.group(1):
            m.type = "RES"
        elif mda.group(3):
            m.type = "PV"
        else:
            m.type = "DOC"

    elif mds:
        m.body = "SC"
        if mds.group(1):
            m.type = "RES"
            m.year = int(mds.group(1))
        elif mds.group(3):
            m.type = "PV"
            m.year = m.meetings and m.meetings[0].year or 0
        else:
            m.type = mds.group(2) and "PRST" or "DOC"
            m.year = int(mds.group(4)[1:])

    else:
        print "  **** UNMATCHED", docid
    print docid

    doctimestamp = 0
    
    fpdf = os.path.join(pdfdir, docid + ".pdf")
    if os.path.exists(fpdf):
        doctimestamp = os.stat(fpdf).st_mtime
        cmd = 'pdfinfo "%s"' % fpdf
        pdfinfo = os.popen(cmd).read()
        mpages = re.search("Pages:\s*(\d+)", pdfinfo)
        if mpages:
            m.numpages = int(mpages.group(1))

    # could set the date from m.meetings[0].datetime, but will do it in ProcessParsedDocument
    Session.flush()

    fhtml = os.path.join(htmldir, docid + ".html")
    if os.path.exists(fhtml):
        doctimestamp = max(os.stat(fhtml).st_mtime, doctimestamp)
        fin = open(fhtml)
        ftext = fin.read().decode('latin1')
        fin.close()
        ProcessParsedDocumentPylon(m, docid, ftext)

    if doctimestamp:
        m.docmodifiedtime = datetime.datetime.fromtimestamp(doctimestamp)
        Session.flush()
        