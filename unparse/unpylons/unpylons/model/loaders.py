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


# can't be bothered to code them all properly
# (could replace this with a flat map of all)
romantodecmap = { "I":1, "II":2, "III":3, "IV":4, "V":5, "VI":6, "VII":7, "VIII":8, "IX":9, "X":10 }
romantodecmap = { "XXIX":29 }
def RomanToDecimal(rn):
    res = romantodecmap.get(rn)
    if res:
        return res
    
    lrn = list(rn)
    res = 0
    while lrn and lrn[-1] == "I":
        res += 1
        del lrn[-1]
    if not lrn:
        return res
    if lrn[-1] == "V":
        res += 5;
        del lrn[-1]
        if lrn and lrn[-1] == "I":
            res -= 1
            del lrn[-1]
    if not lrn:
        return res
    while lrn and lrn[-1] == "X":
        res += 10
        del lrn[-1]
    if lrn and lrn[-1] == "I":
        res -= 1
        del lrn[-1]
    assert not lrn, rn
    return res


def EnsureDocidExists(docid):
    res = [ ]
    m = Document.query.filter_by(docid=docid).first()
    if not m:
        m = Document(docid=docid)
        mda = re.match("A(-RES)?(-\d\d)?(-PV)?", docid)
        mds = re.match("S-RES-\d+\((\d+)\)|S(-PRST)?(-PV)?([\-.]\d+)(-\d+)?", docid)
        if mda:
            m.body = "GA"
            m.session = mda.group(2) and mda.group(2)[1:] or ""
            if mda.group(1):
                m.type = "RES"
                mgaresroman = re.match("A-RES-(\d+)\(([IVXL]+)\)", docid)
                if mgaresroman:
                    m.session = str(RomanToDecimal(mgaresroman.group(2)))
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
                if mds.group(2):
                    m.type = "PRST"
                else:
                    m.type = "DOC"
                    if mds.group(5):
                        lyear = int(mds.group(4)[1:])
                        if 1960 <= lyear <= currentyear:
                            m.year = lyear
                        else:
                            assert False, "what's the year: " + docid + "  [consider reparsing to capture a better docid]"
                        m.year = 0
                    else:
                        m.year = 0  # old-style docs eg S-45839
    
        else:
            print "  **** UNMATCHED", docid
        
        # (we could look up whether it is downloaded and record that)
        Session.flush()
        print "NewDocid added", docid
    return m
        
def EnsureDocidhrefExists(docid, href):
    docidhref = docid + "#" + href
    m = Meeting.query.filter_by(docidhref=docidhref).first()
    if not m:
        #print "making ", docidhref
        d = EnsureDocidExists(docid)
        assert d.type == "PV", d
        m = Meeting(docidhref=docidhref, docid=docid, href=href)
        m.body = d.body
        if d.body == "GA":
            m.session = d.session
            m.meetingnumber = re.match("A-\d+-PV.(\d+)$", docid).group(1)
        if d.body == "SC":
            m.meetingnumber = re.match("S-PV[\-.](\d.+)$", docid).group(1)
        Session.flush()
    return m

def EnsureMemberExists(membername, date):
    m = Member.query.filter_by(name=membername).first()
    #m = Member.query.filter_by(name=membername).filter(or_(member_table.c.started==None, and_(member_table.c.started<=date, member_table.c.finished))).first()
    if not m:
        print "Constructing member::", membername
        m = Member(name=unicode(membername))
        m.sname = membername.lower().replace(" ", "_").replace("'", "")
        m.isnation = False
        Session.flush()
    return m


def load_sc_topics(docid, heading, ldate, ldateend, topics, minutes, numspeeches, numparagraphs, numvotes, nextdocid):
    numvotes = 0 
    m = EnsureDocidhrefExists(docid, "")
    m.title = unicode(heading)[:499]   # shorten
    m.datetime = ldate
    m.year = int(ldate[:4])
    m.datetimeend = ldateend    
    m.minutes = minutes
    m.numspeeches, m.numparagraphs = numspeeches, numparagraphs
    m.numvotes = numvotes
    m.next_docid = nextdocid     # the list is scanned backwards
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
    for m in Meeting.query.filter_by(docid=docid):
        Session.delete(m)        
    session, meetingnumber = re.match("A-(\d+)-PV.(\d+)$", docid).groups()
    for (subheadingid, agendanumstr, agtitle) in gaagindoc:
        m = EnsureDocidhrefExists(docid, subheadingid)
        m.body = "GA"
        m.session = session
        m.meetingnumber = meetingnumber
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
        m = EnsureDocidhrefExists(docid, subheadingid)
        t.meetings.append(m)
    Session.flush()
    print 'Session', session, "Agenda", agendanum


def ProcessParsedVotePylon(document, href, subheadingmeeting, div_content):
    mvote = re.match('\s*<p class="motiontext"[^>]*>(.*?)</p>\s*<p class="votecount"[^>]*>(.*?)</p>\s*<p class="votelist"[^>]*>(.*?)</p>', div_content)
    assert mvote, div_content
    mvnum = re.match("favour=(\d+)\s+against=(\d+)\s+abstain=(\d+)\s+absent=(\d+)", mvote.group(2))
    vnum = [int(mvnum.group(1)), int(mvnum.group(2)), int(mvnum.group(3)), int(mvnum.group(4))]
    motiontext = mvote.group(1)
    
    resolution_docids = re.findall('<a href="../pdf/(.*?).pdf"', motiontext)
    resolution_docid = resolution_docids and resolution_docids[-1] or None
    for ldocid in resolution_docids:
        EnsureDocidExists(ldocid)

    motiontext = re.sub('<a [^>]*>([^<]*)</a>', "\\1", motiontext)
    motiontext = re.sub("<[^>]*>", " ", motiontext)
    motiontext = re.sub(" (?:was|were) (?:retained|adopted|rejected) by (?:.*? abstentions?|\d+ votes to \d+)", "", motiontext)
    
    if not motiontext:
        motiontext = unicode("blank space for: " + document.docid)
   
    docidhref = document.docid + "#" + href
    m = Division(docidhref=docidhref, docid=document.docid, href=href, meeting_docidhref=subheadingmeeting.docidhref, description=motiontext, resolution_docid=resolution_docid)
    m.favour = vnum[0]
    m.against = vnum[1]
    m.abstain = vnum[2]
    m.absent = vnum[3]
    m.body = document.body
    
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


def ProcessParsedDocumentPylon(document, ftext):
    
    # how to delete in a batch???
    for lm in DocumentRefDocument.query.filter_by(document1_docid=document.docid):
        #print "deleting", lm.meeting1_docidhref
        Session.delete(lm)
    for lm in Speech.query.filter_by(docid=document.docid):
        Session.delete(lm)
    for lm in Division.query.filter_by(docid=document.docid):
        for lv in lm.votes:
            Session.delete(lv)
        Session.delete(lm)
    Session.flush()

    mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)")?[^>]*>\s*(.*?)^</div>', ftext, re.S + re.M)
    subheadinghref = ""
    subheadingmeeting = EnsureDocidhrefExists(document.docid, "")
    
    for mdiv in mdivs:
        # used to dereference the string as it is in the file
        div_class = mdiv.group(1)
        div_href = mdiv.group(2)
        div_data = (document.docid, mdiv.start(), mdiv.end() - mdiv.start(), mdiv.group(2))
        div_content = unicode(mdiv.group(4))
        
        if div_class == "recvote":
            ProcessParsedVotePylon(document, div_href, subheadingmeeting, div_content)
        
        elif div_class == "subheading":
            if document.body != "SC":  # otherwise leave as default meeting (blank href) since only one meeting per sc
                subheadinghref = div_href  # these are going to be collated into meetings in the agendas
                subheadingmeeting = EnsureDocidhrefExists(document.docid, div_href)
            #print "\n\n\n", div_content
        
        elif div_class == "heading":
            document.date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', div_content).group(1)
            #print "sssssdate", m.date
        
        # gets title of document (diff from title of meeting?)
        elif div_class == "council-agenda":
            ca = re.sub("<p[^>]*>", "", div_content)
            ca = re.sub("\s*</p>\s*", "\n", ca)
            ca = re.sub("<[^>]*>", "", ca).strip()
            document.title = unicode(ca)[:500]  # make short 
            #print "\n\n\n", m.title
        
        elif div_class == "spoken":
            mm = re.match('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(non-)?nation">([^<]*)</span>)?(?: <span class="language">([^<]*)</span>)? </h3>\s*', div_content)
            assert mm, div_content[:160]
            pcontent = div_content[mm.end(0):]
            
            name = mm.group(1)
            sname = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').lower().strip()
            lastname = re.search("(\S+)$", sname).group(1)
            
            membername = mm.group(3) or None 
            if membername:
                member = EnsureMemberExists(membername, document.date)
                if member.isnation != (not mm.group(2)):
                    # we'll allow Switzerland to exist outside of its membership status (when it couldn't vote, but was an observer)
                    assert membername == "Switzerland", "\n\n\n\n ***  Disagreed member " + membername + "\n\n" + mm.group(0)
                
                ambassador = Ambassador.query.filter_by(lastname=lastname).filter_by(member=member).first()
                if not ambassador:
                    ambassador = Ambassador(lastname=lastname, member=member)
            
                numparagraphs = len(re.findall("<p|<blockquote", div_content))
                docidhref = document.docid + "#" + div_href
                m = Speech(docidhref=docidhref, name=name, member_name=membername, ambassador=ambassador, 
                           docid=document.docid, href=div_href, meeting_docidhref=subheadingmeeting.docidhref, numparagraphs=numparagraphs)
                Session.flush()
                                
                                
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
                EnsureDocidExists(docid2)
                doccite = DocumentRefDocument(document1_docid=document.docid, document2_docid=docid2, href1=pgid)
                doccite.meeting1_docidhref = subheadingmeeting.docidhref
                Session.flush()
    
    #print " Added citations", len(doccitations)
    Session.flush()


def ProcessDocumentPylon(docid, pdfdir, htmldir, bforcedocmeasurements):
    document = EnsureDocidExists(docid)

    fpdf = os.path.join(pdfdir, docid + ".pdf")
    if os.path.exists(fpdf):
        cmd = 'pdfinfo "%s"' % fpdf
        pdfinfo = os.popen(cmd).read()
        mpages = re.search("Pages:\s*(\d+)", pdfinfo)
        if mpages:
            document.numpages = int(mpages.group(1))
            Session.flush()

    fhtml = os.path.join(htmldir, docid + ".html")
    if os.path.exists(fhtml):
        parseddoctimestamp = datetime.datetime.fromtimestamp(os.stat(fhtml).st_mtime)
        if not bforcedocmeasurements and parseddoctimestamp == document.docmodifiedtime:
            print "Skipping already loaded doc by timestamp", docid
            return
        print "Parsing doc", docid
        
        # load and parse the html (could also do the xapian)
        fin = open(fhtml)
        ftext = fin.read().decode('latin1')
        fin.close()
        ProcessParsedDocumentPylon(document, ftext)
        document.docmodifiedtime = parseddoctimestamp
        Session.flush()
        