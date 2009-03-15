from sqlalchemy import *
from sqlalchemy.orm import *
import sys

import unpylons.dbpasswords as dbpasswords
# sys.path.append("/home/goatchurch/undemocracy/unparse/web2")
undatadir = dbpasswords.undata_path

metadata = MetaData(dbpasswords.dburi)
Session = scoped_session(sessionmaker(
    autoflush=True,
    transactional=False,
    bind=metadata.bind
))

meeting_table = Table('meeting', metadata,
    Column('docidhref', String(100), primary_key=True), 
    # need unique to make next_docid fk to this table from itself work
    Column('docid', String(100), ForeignKey('document.docid'), unique=True), 
    Column('href', String(100)), # used in GA
    Column('body', String(10)), # SC or GA
    Column('title', UnicodeText), 
    Column('datetime', DateTime),
    Column('datetimeend', DateTime), # SC
    Column('year', Integer), # SC
    Column('session', String(10)), # GA (can be S-27 special session)
    Column('agendanumstr', String(100)), # GA (will need another table of agendanums instead of topics)
    Column('notes', UnicodeText),
    Column('numspeeches', Integer),
    Column('numparagraphs', Integer), 
    Column('numvotes', Integer),
    Column('minutes', Integer),
    Column('next_docid', String(100), ForeignKey('meeting.docid')),
    )

topic_table = Table('topic', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', UnicodeText),
    Column('agendanum', String(50)),  # for GA case
    Column('session', String(10)), # for GA case
    )

topic2meeting = Table('topic2meeting', metadata,
    Column('meeting_docidhref', String(100), ForeignKey('meeting.docidhref'), primary_key=True),
    Column('topic_id', Integer, ForeignKey('topic.id'), primary_key=True)
    )

document_table = Table('document', metadata, 
    Column('docid', String(100), primary_key=True),
    Column('numpages', Integer), 
    Column('body', String(10)), # SC,GA,C-1
    Column('type', String(10)), # PV,RES,PRST,REPORT
    Column('author', String(50)), # Secretary General, Blix, nation, etc
    Column('year', Integer), 
    Column('session', Integer), 
    Column('date', Date), 
    Column('date_made', Date), # GA resolutions have a date of the vote as well
    Column('title', String(500)),
    # needs some column to help with when we are to update everything?
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

member_table = Table('member', metadata, 
    Column('name', Unicode(100), primary_key=True),
    Column('sname', String(100)), # simplified name
    Column('isnation', Boolean),
    Column('started', Date),
    Column('finished', Date),
	Column('group', String(100)), # eg continent
	#Column('representing', String(100), ForeignKey to constituencies)
	Column('url', String(200)), # to the permanent mission 
	Column('wpname', String(100)) # this will also be a primary_key
	
	# this would be done with groupings
	#Column('successor_member', String(100), ForeignKey('member.name'),  # Foreign key to self
    )
    
speech_table = Table('speech', metadata, 
    Column('docidhref', String(100), primary_key=True),  
    Column('docid', String(100), ForeignKey('document.docid')),  
    Column('href', String(100)), 
    Column('name', Unicode(100)),
    Column('lastname', String(100)), # last name lower case
    Column('member_name', Unicode(100), ForeignKey('member.name')),  # the nation
    Column('meeting_docidhref', String(100), ForeignKey('meeting.docidhref')),  # to the heading part of the meeting
    Column('numparagraphs', Integer),
    )
    
division_table = Table('division', metadata, 
    Column('docidhref', String(100), primary_key=True), 
    Column('docid', String(100), ForeignKey('document.docid')), 
    Column('href', String(100)), 
    Column('description', UnicodeText), 
    Column('resolution_docid', String(100), ForeignKey('document.docid')), 
    Column('body', String(10)), # it should be possible to drill through the document to get this, but I can't filter it.  help 
    Column('favour', Integer), 
    Column('against', Integer), 
    Column('abstain', Integer), 
    Column('absent', Integer), 
    )
    
vote_table = Table('vote', metadata, 
    Column('id', Integer, primary_key=True),
    Column('docidhref', String(100), ForeignKey('division.docidhref')), 
    Column('member_name', Unicode(100), ForeignKey('member.name')), 
    Column('vote', String(10)),     # favour, against, abstain, absent
    Column('orgvote', String(10)),  # when the vote was initially wrong
    Column('isteller', Boolean),    # not used in UN
    Column('minority_score', Numeric), 
    )
    
# this is user-generated use data
incoming_links_table = Table('incoming_links', metadata, 
    Column('id', Integer, primary_key=True),
    Column('page', String(30)),
    Column('referrer', Text),
    Column('refdomain', String(30)),
    Column('reftitle', Text),
    Column('ltime', DateTime),
    Column('ipnumber', String(20)),
    Column('useragent', Text),
    Column('url', Text),
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

class Topic(object):
    @classmethod
    def by_name(klass, name):
        t = klass.query.filter_by(name=name).first()
        if not t:
            t = klass(name=name)
        return t

    @classmethod
    def by_agendanum(klass, agendanum):        
        t = klass.query.filter_by(agendanum=agendanum).first()
        if not t:
            t = klass(agendanum=agendanum)
        return t

class Member(object):
    pass

class IncomingLinks(object):
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
    })

mapper(Member, member_table, properties={
    'speeches':relation(Speech, primaryjoin=member_table.c.name==speech_table.c.member_name,
        viewonly=True),
    'votes':relation(Vote, primaryjoin=member_table.c.name==vote_table.c.member_name),
    })

mapper(Speech, speech_table, properties={
    'document':relation(Document, primaryjoin=speech_table.c.docid==document_table.c.docid), 
    'meeting':relation(Meeting, primaryjoin=speech_table.c.meeting_docidhref==meeting_table.c.docidhref), 
    })

mapper(Division, division_table, properties={
    'document':relation(Document, primaryjoin=division_table.c.docid==document_table.c.docid), 
    'votes':relation(Vote, primaryjoin=vote_table.c.docidhref==division_table.c.docidhref), 
    })

mapper(Vote, vote_table, properties={
    'division':relation(Division, primaryjoin=vote_table.c.docidhref==division_table.c.docidhref), 
    'member':relation(Member, primaryjoin=vote_table.c.member_name==member_table.c.name), 
    })

mapper(DocumentRefDocument, documentRefdocument)

mapper(IncomingLinks, incoming_links_table)

# probably some fancy mapper could do this
def GetSessionsYears():
    sga = select([Document.c.session, func.count(Document.c.docid)], Document.c.body=="GA").group_by(Document.c.session).order_by(Document.c.session)
    gasessions = Session.execute(sga).fetchall()
    ssc = select([Document.c.year, func.count(Document.c.docid)], Document.c.body=="SC").group_by(Document.c.year).order_by(Document.c.year)
    scyears = Session.execute(ssc).fetchall()
    return gasessions, scyears


