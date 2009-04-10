"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from pylons import config
from routes import Mapper

def make_map():
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('error/:action/:id', controller='error')

    # CUSTOM ROUTES HERE

# experimental loading of MPs and debates into the data-set


# highlight should disappear if there is a single click encompassing hardly any pixels
# list of meeting topics at the top

# check-in or rsync the document directories.

# get rid of web2 in meeting.py and in all other places.  move out
# move quickskins into the pylons stuff

# next/previous session in case of general assembly meetings
# nice dates in the helper function
# option to scrape documents we don't have
# make the search box work (with suggestions)
# database of all official general assembly members


#instructions
#  nationdata
#  scsummaries     to get the topics of meetings in place
#  agendanames     to get the agenda meetings in place
#  docmeasurements   list through the pdfs and call loader.ProcessParsedDocumentPylon on each document, setting its council-agenda, date, citations
#    could be expanded so we have xmls of all the other documents to look for dates, citations and titles there too, in a light form of parsing

# Rufus's machine at eu1.okfn.org with undemocracy partly deployed

# paster serve development.ini --reload

# look in loaders for the drop database

    map.connect('mps',      'mps', controller='publicwhip', action='mps')

    map.connect('nationscontinent',  'nations/bycontinent', controller='nation', action='nationscontinent')
    map.connect('nations',  'nations',          controller='nation', action='nations')
    map.connect('flagof',   'png100/Flag_of_:(entity).png', controller='nation', action='flagof')
    map.connect('nationambassador','nation/:snation/:sambassador',  controller='nation', action='nationambassador')
    map.connect('nation',   'nation/:snation',  controller='nation', action='nation')
    map.connect('votesnation','votes/:snation', controller='nation', action='nationvotes')

    map.connect('documentsall', 'document/all', controller='document', action='documentsall')

    # individual documents (missing highlight case)
    map.connect('documentpage',     'document/:docid/page_:page', controller='document', action='documentpage')
    map.connect('documentpagehighlight','document/:docid/page_:page/:highlightrects', controller='document', action='documentpage')
    map.connect('documentspec',     'document/:docid', controller='document', action='documentspec')
    map.connect('documentspecscrape','document/:docid/scrape', controller='document', action='documentspecscrape')
    map.connect('imagedocumentpage','docpages/*(pngname).png', controller='document', action='imagedocumentpage')  # needs to use * instead of : because sometimes pngname contains a .
    map.connect('meetingmonth',     'meeting/:year/:month', controller='indexes', action='meetingmonth')
    
    map.connect('gasessions',       'generalassembly', controller='indexes', action='gasessions')
    map.connect('gasessionagendas', 'generalassembly_:session/agendas', controller='indexes', action='gasessionagendas')
    map.connect('gaagenda',         'generalassembly/agenda/:(agendanum)', controller='indexes', action='gaagenda')
    map.connect('gacondolences',    'generalassembly/condolences', controller='indexes', action='gacondolences')
    
    map.connect('gameetinghref',    'generalassembly_:session/meeting_:meeting/:href', controller='meeting', action='gameetinghref')
    map.connect('gameeting',        'generalassembly_:session/meeting_:meeting', controller='meeting', action='gameeting')
    map.connect('documentsgasession','generalassembly_:session', controller='indexes', action='documentsgasession')

    map.connect('documentsscyear',  'securitycouncil_:year', controller='indexes', action='documentsscyear')
    map.connect('sctopics',         'securitycouncil/topics', controller='indexes', action='sctopics')
    map.connect('sctopic',          'securitycouncil/topic/:topic', controller='indexes', action='sctopic')
    map.connect('scmeeting',        'securitycouncil/meeting_:scmeetingnumber', controller='meeting', action='scmeeting')
    map.connect('documentsscyear',  'securitycouncil_:year', controller='indexes', action='documentsscyear')
    
    map.connect('incoming',         'incoming', controller='indexes', action='incoming')

# indexes not done.  we have a front page (sort of), but need lists of security council documents by year
    map.connect('security_council_topics_ordered', 'securitycouncil/:year', controller='indexes', action='scindexordered')
    #map.connect('security_council', 'sc_:year', controller='home', action='scyear', requirements={'year':'\d\d\d\d|early'})
    map.connect('security_council_topics', 'securitycouncil', controller='indexes', action='scindex')
    map.connect('search',  '/search', controller='indexes', action='search')
    map.connect('', controller='indexes', action='frontpage')

    # conditions to redirect
    #map.connect('meeting/:docid', controller='indexes', action='meeting')

    #map.connect('*url', controller='home', action='index')
    #map.connect('', controller='home', action='index')
    #map.connect('about', controller='home', action='about')
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map

