from sqlalchemy import *
from sqlalchemy.orm import *
import sys
import datetime

import unpylons.dbpasswords as dbpasswords
# sys.path.append("/home/goatchurch/undemocracy/unparse/web2")
undatadir = dbpasswords.undata_path

# useful to have these parameters
currentdate = datetime.date.today()
currentyear = currentdate.year
currentmonth = currentdate.month
currentsession = currentyear - 1946
if currentmonth >= 9:
    currentsession += 1


metadata = MetaData(dbpasswords.dburi)
Session = scoped_session(sessionmaker(
    autoflush=True,
    transactional=False,
    bind=metadata.bind
))

meeting_table = Table('meeting', metadata,
    Column('docidhref',     String(100), primary_key=True), 
    
    # need unique to make next_docid fk to this table from itself work
        # but this can't be unique as there are several meetings for one document.  The above (concattenated) key is unique
    Column('docid',         String(100), ForeignKey('document.docid')), 
    Column('href',          String(100)), # used in GA
    Column('body',          String(10)), # SC or GA
    Column('title',         UnicodeText), 
    Column('datetime',      DateTime),
    Column('datetimeend',   DateTime), # SC
    Column('year',          Integer), # SC
    Column('session',       String(10)), # GA (can be S-27 special session)
    Column('agendanumstr',  String(200)), # GA (will need another table of agendanums instead of topics)
    Column('notes',         UnicodeText),
    Column('numspeeches',   Integer),
    Column('numparagraphs', Integer), 
    Column('numvotes',      Integer),
    Column('minutes',       Integer),
    Column('next_docid',    String(100)), # , ForeignKey('meeting.docid')), used for Security Council links where the meetings and docids are the same
    Column('meetingnumber', String(100)), # can contain Resu.1
    )

topic_table = Table('topic', metadata,
    Column('id',        Integer, primary_key=True),
    Column('name',      UnicodeText),
    Column('agendanum', String(50)),  # for GA case
    Column('session',   String(10)), # for GA case
    )

topic2meeting = Table('topic2meeting', metadata,
    Column('meeting_docidhref', String(100), ForeignKey('meeting.docidhref'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topic.id'), primary_key=True)
    )


# to add document on disc boolean (obvious if numpages not null)
# bool pdffileexists
document_table = Table('document', metadata, 
    Column('docid',     String(100), primary_key=True),
    Column('numpages',  Integer), 
    Column('body',      String(10)), # SC,GA,C-1
    Column('type',      String(10)), # PV,RES,PRST,REPORT
    Column('author',    String(50)), # Secretary General, Blix, nation, etc
    Column('year',      Integer), 
    Column('session',   String(10)), # GA (can be S-27 special session)
    Column('date',      Date), 
    Column('date_made', Date), # GA resolutions have a date of the vote as well
    Column('title',     UnicodeText),
    
    # tells when the document (pdf or html) was last modified so we can rescan (eg for search) just the new ones
    Column('docmodifiedtime', DateTime),
    )

documentRefdocument = Table('documentRefdocument', metadata, 
    Column('id', Integer, primary_key=True),
    Column('document1_docid', String(100), ForeignKey('document.docid')),
    Column('page1', Integer),
    Column('href1', String(50)), 
    Column('meeting1_docidhref', String(100), ForeignKey('meeting.docidhref')),
    
    Column('document2_docid', String(100), ForeignKey('document.docid')),
        # the pair of keys are unique, but the individuals are not
    Column('count', Integer),
    )


pwconstituency_table = Table('pwconstituency', metadata, 
    Column('name', Unicode(100), primary_key=True), 
    )
    
pwperson_table = Table('pwperson', metadata, 
    Column('id', String(100), primary_key=True), 
    Column('name', Unicode(100)), 
    Column('sname', Unicode(100)), 
    )

# these are the vested entities (nations for UN, or MPs for Parliament)
member_table = Table('member', metadata, 
    #Column('id', Integer, primary_key=True), # get rid of name as non-duplicating so we can match by date (eg for Switzerland)
    Column('name',      Unicode(300), primary_key=True), 
    Column('sname',     String(100)), # simplified name (used in the URL -- should we use wpname instead?)
    Column('flagof',    String(200)), # links to the flag we use here
    Column('house',     String(20)),  # UNunknown, UNmember, UNobserver, PWcommons, PWlords -- should this be body?
    
# get rid of these
    Column('countrycode2',  String(10)), # two letter country code
    Column('countrycode3',  String(10)), # three letter country code
    
# party    
    Column('countrycontinent',  String(10)), # 2 letter continent code AF, AS, EU, NA, OC, SA
    
    Column('started',   Date),  # date entered
    Column('finished',  Date),  # date left
    Column('url',       Text), # to the permanent mission 
    Column('wpname',    String(100)), # this could instead be a primary_key

    Column('successor_member', Unicode(100), ForeignKey('member.name')),  # Foreign key to self
    
# publicwhip things
    Column('pwtitle',       Unicode(100)), 
    Column('pwfirstname',   Unicode(100)), 
    Column('pwlastname',    Unicode(100)), 
    Column('pwrepresenting',Unicode(100), ForeignKey('pwconstituency.name')), 
    Column('pwparty',       Unicode(100)), 
    Column('pwperson_fullname', Unicode(100)), 
    Column('pwperson_id',   Unicode(100), ForeignKey('pwperson.id')), 
    )


ambassador_table = Table('ambassador', metadata, 
    Column('id', Integer, primary_key=True), 
    Column('lastname', String(100)), 
    Column('member_name', Unicode(100), ForeignKey('member.name')), 
    )

# using this to mark the SC Security Council committee
membercommittee_table = Table('membercommittee', metadata, 
    Column('id',    Integer, primary_key=True),
    Column('body',  String(10)),  # SC or GA (or standing committee) (should be a Foreign Key)
    Column('member_name', Unicode(100), ForeignKey('member.name')), # needs conv
    Column('started',   Date),  # date entered
    Column('finished',  Date),  # date left (one past the date)
    )

speech_table = Table('speech', metadata, 
    Column('docidhref',     String(100), primary_key=True),  
    Column('docid',         String(100), ForeignKey('document.docid')),  
    Column('href',          String(100)), 
    Column('name',          Unicode(100)),
    Column('ambassador_id', Integer, ForeignKey('ambassador.id')), 
    Column('member_name',   Unicode(100), ForeignKey('member.name')),  # the nation
    Column('meeting_docidhref', String(100), ForeignKey('meeting.docidhref')),  # to the heading part of the meeting
    Column('numparagraphs', Integer),
    )
    
division_table = Table('division', metadata, 
    Column('docidhref',     String(100), primary_key=True), 
    Column('docid',         String(100), ForeignKey('document.docid')), 
    Column('href',          String(100)), 
    Column('description',   UnicodeText), 
    Column('resolution_docid', String(100), ForeignKey('document.docid')), 
    Column('body',          String(10)), # it should be possible to drill through the document to get this, but I can't filter it.  help 
    Column('meeting_docidhref', String(100), ForeignKey('meeting.docidhref')),  # to the heading part of the meeting
    
    # these values could be summed up at runtime, but are better cached so they can be sorted accordingly
    Column('favour',        Integer), 
    Column('against',       Integer), 
    Column('abstain',       Integer), 
    Column('absent',        Integer), 
    
    Column('datetime',      DateTime),  # added for publicwhip
    )
    
vote_table = Table('vote', metadata, 
    Column('id', Integer, primary_key=True),
    Column('docidhref', String(100), ForeignKey('division.docidhref')), 
    Column('member_name', Unicode(100), ForeignKey('member.name')), 
    Column('vote', String(10)),     # favour, against, abstain, absent
    Column('orgvote', String(10)),  # when the vote was initially wrong
    
    Column('isteller', Boolean),    # not used in UN
    Column('minority_score', Float), 
    )
    
# this is user-generated use data (might want to back it up in a logfile which gets reparsed)
incoming_links_table = Table('incoming_links', metadata, 
    Column('id',        Integer, primary_key=True),
    Column('page',      String(30)),
    Column('referrer',  Text),
    Column('refdomain', String(30)),
    Column('reftitle',  Text),
    Column('ltime',     DateTime),
    Column('ipnumber',  String(20)),
    Column('useragent', Text),
    Column('url',       Text),
    )

            
class Division(object):
    pass

class Vote(object):
    pass

class Speech(object):
    pass

class Meeting(object):
    pass

class Document(object):
    def __str__(self):
        return "<" + self.docid + ">"

class DocumentRefDocument(object):
    pass

class MemberCommittee(object):
    pass

class Topic(object):
    pass

class Member(object):
    pass

class Ambassador(object):
    pass

class IncomingLinks(object):
    pass

class PWConstituency(object):
    pass

class PWPerson(object):
    pass


mapper = Session.mapper

mapper(Meeting, meeting_table, properties={
    'document':relation(Document, primaryjoin=document_table.c.docid==meeting_table.c.docid), 
    'topics':relation(Topic, secondary=topic2meeting),#, backref='meetings'),
    'references':relation(Document, secondary=documentRefdocument, 
        primaryjoin=meeting_table.c.docid==documentRefdocument.c.document1_docid, 
        secondaryjoin=documentRefdocument.c.document2_docid==document_table.c.docid,
        foreign_keys=[documentRefdocument.c.document1_docid,
            documentRefdocument.c.document2_docid], 
        viewonly=True),
    'citations':relation(Document, secondary=documentRefdocument, 
        primaryjoin=meeting_table.c.docid==documentRefdocument.c.document2_docid, 
        secondaryjoin=documentRefdocument.c.document1_docid==document_table.c.docid,
        foreign_keys=[documentRefdocument.c.document1_docid], 
        _local_remote_pairs=[(meeting_table.c.docid,documentRefdocument.c.document2_docid),
            (documentRefdocument.c.document1_docid,document_table.c.docid)
            ],
        viewonly=True),
    
    'divisions':relation(Division, primaryjoin=meeting_table.c.docidhref==division_table.c.meeting_docidhref,
        viewonly=True),
    'speeches':relation(Speech, primaryjoin=meeting_table.c.docidhref==speech_table.c.meeting_docidhref,
        viewonly=True),
    }, order_by=meeting_table.c.datetime)

mapper(Topic, topic_table, properties={
    'meetings':relation(Meeting, secondary=topic2meeting, order_by=[meeting_table.c.datetime])
    })

mapper(Document, document_table, properties={
    'references':relation(Document, secondary=documentRefdocument, 
        primaryjoin=document_table.c.docid==documentRefdocument.c.document1_docid, 
        secondaryjoin=documentRefdocument.c.document2_docid==document_table.c.docid,
        foreign_keys=[documentRefdocument.c.document2_docid,
            documentRefdocument.c.document1_docid], 
        viewonly=True),
    'citations':relation(Document, secondary=documentRefdocument, 
        primaryjoin=document_table.c.docid==documentRefdocument.c.document2_docid, 
        secondaryjoin=documentRefdocument.c.document1_docid==document_table.c.docid,
        foreign_keys=[documentRefdocument.c.document2_docid,
            documentRefdocument.c.document1_docid], 
        viewonly=True),
    'meetings':relation(Meeting, primaryjoin=document_table.c.docid==meeting_table.c.docid,
        viewonly=True),
    'meeting_citations':relation(Meeting, secondary=documentRefdocument, 
        primaryjoin=document_table.c.docid==documentRefdocument.c.document2_docid, 
        secondaryjoin=documentRefdocument.c.meeting1_docidhref==meeting_table.c.docidhref,
        foreign_keys=[documentRefdocument.c.document2_docid,
            documentRefdocument.c.meeting1_docidhref], 
        viewonly=True),
    
    'divisions':relation(Division, primaryjoin=document_table.c.docid==division_table.c.docid,
        viewonly=True),
    'speeches':relation(Speech, primaryjoin=document_table.c.docid==speech_table.c.docid,
        viewonly=True),
    })

mapper(Member, member_table, properties={
    'speeches':relation(Speech, primaryjoin=member_table.c.name==speech_table.c.member_name, viewonly=True),
    'votes':relation(Vote, primaryjoin=member_table.c.name==vote_table.c.member_name),
    'committees':relation(MemberCommittee, primaryjoin=member_table.c.name==membercommittee_table.c.member_name),
    'ambassadors':relation(Ambassador, primaryjoin=member_table.c.name==ambassador_table.c.member_name, viewonly=True, order_by=[ambassador_table.c.lastname]),
    
    'constituency':relation(PWConstituency, primaryjoin=member_table.c.pwrepresenting==pwconstituency_table.c.name), 
    'pwperson':relation(PWPerson, primaryjoin=member_table.c.pwperson_id==pwperson_table.c.id), 
    })

mapper(Speech, speech_table, properties={
    'document':relation(Document, primaryjoin=speech_table.c.docid==document_table.c.docid), 
    'meeting':relation(Meeting, primaryjoin=speech_table.c.meeting_docidhref==meeting_table.c.docidhref), 
    'member':relation(Member, primaryjoin=speech_table.c.member_name==member_table.c.name), 
    'ambassador':relation(Ambassador, primaryjoin=speech_table.c.ambassador_id==ambassador_table.c.id), 
    })

mapper(Ambassador, ambassador_table, properties={
    'member':relation(Member, primaryjoin=ambassador_table.c.member_name==member_table.c.name), 
    'speeches':relation(Speech, primaryjoin=ambassador_table.c.id==speech_table.c.ambassador_id, viewonly=True),
    })

mapper(Division, division_table, properties={
    'document':relation(Document, primaryjoin=division_table.c.docid==document_table.c.docid), 
    'meeting':relation(Meeting, primaryjoin=division_table.c.meeting_docidhref==meeting_table.c.docidhref), 
    'votes':relation(Vote, primaryjoin=vote_table.c.docidhref==division_table.c.docidhref), 
    })

mapper(Vote, vote_table, properties={
    'division':relation(Division, primaryjoin=vote_table.c.docidhref==division_table.c.docidhref), 
    'member':relation(Member, primaryjoin=vote_table.c.member_name==member_table.c.name), 
    })

mapper(MemberCommittee, membercommittee_table)

mapper(DocumentRefDocument, documentRefdocument)

mapper(IncomingLinks, incoming_links_table)

mapper(PWConstituency, pwconstituency_table, properties={
    'mps':relation(Member, primaryjoin=pwconstituency_table.c.name==member_table.c.pwrepresenting), 
    })

mapper(PWPerson, pwperson_table, properties={
    'seats':relation(Member, primaryjoin=pwperson_table.c.id==member_table.c.pwperson_id, order_by=[member_table.c.finished]) , 
    })


# probably some fancy mapper could do this
def GetSessionsYears():
    sga = select([Document.c.session, func.count(Document.c.docid)], Document.c.body=="GA").group_by(Document.c.session).order_by(Document.c.session)
    gasessions = Session.execute(sga).fetchall()
    ssc = select([Document.c.year, func.count(Document.c.docid)], Document.c.body=="SC").group_by(Document.c.year).order_by(Document.c.year)
    scyears = Session.execute(ssc).fetchall()
    return gasessions, scyears



