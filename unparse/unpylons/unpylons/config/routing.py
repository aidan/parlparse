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


# add non-existent documents that are referenced into the database (noting their non-loaded state)
# parse all document codes (incl roman numeral ones)
# fix the add comment here killing off (again)
# fix the wiki-ref
# get the wikipedia coding to work
# make the search box work (with suggestions)
# reload file data partially (not all files in database)
# get rect areas working again


#instructions
#  dbfill doesn't do anything (except when there's force)
#  scmeetings to get the topics of meetings in place
#  agendanums to get the agenda meetings in place
#  docmeasurements list through the pdfs and call loader.ProcessParsedDocumentPylon on each document, setting its council-agenda, date, citations
#    could be expanded so we have xmls of all the other documents to look for dates, citations and titles there too, in a light form of parsing

    map.connect('nations', 'nations', controller='indexes', action='nations')
    map.connect('nation', 'nation/:snation', controller='nation', action='nation')
    map.connect('flagof', 'png100/Flag_of_:(entity).png', controller='nation', action='flagof')

    map.connect('documentsall', 'document/all', controller='document', action='documentsall')

    # individual documents (missing highlight case)
    map.connect('documentpage', 'document/:docid/page_:page', controller='document', action='documentpage')
    map.connect('documentspec', 'document/:docid', controller='document', action='documentspec')
    map.connect('imagedocumentpage', 'docpages/:(docid)_page_:(page).png', controller='document', action='imagedocumentpage')
    
    map.connect('gasessionagendas', 'generalassembly_:session/agendas', controller='indexes', action='gasessionagendas')
    map.connect('gaagenda', 'generalassembly/agenda/:(agendanum)', controller='indexes', action='gaagenda')
    map.connect('gacondolences', 'generalassembly/condolences', controller='indexes', action='gacondolences')
    map.connect('gameetinghref', 'generalassembly_:session/meeting_:meeting/:href', controller='meeting', action='gameetinghref')
    map.connect('gameeting', 'generalassembly_:session/meeting_:meeting', controller='meeting', action='gameeting')
    map.connect('documentsgasession', 'generalassembly_:session', controller='indexes', action='documentsgasession')

    map.connect('documentsscyear', 'securitycouncil_:year', controller='indexes', action='documentsscyear')
    map.connect('sctopics', 'securitycouncil/topics', controller='indexes', action='sctopics')
    map.connect('sctopic', 'securitycouncil/topic/:topic', controller='indexes', action='sctopic')
    map.connect('scmeeting', 'securitycouncil/meeting_:scmeetingnumber', controller='meeting', action='scmeeting')

# indexes not done.  we have a front page (sort of), but need lists of security council documents by year
    map.connect('security_council_topics_ordered', 'securitycouncil/:year', controller='indexes', action='scindexordered')
    map.connect('security_council', 'sc_:year', controller='home', action='scyear', requirements={'year':'\d\d\d\d|early'})
    map.connect('security_council_topics', 'securitycouncil', controller='indexes', action='scindex')
    map.connect('', controller='indexes', action='frontpage')


    map.connect('*url', controller='home', action='index')
    map.connect('', controller='home', action='index')
    map.connect('about', controller='home', action='about')
    map.connect(':controller/:action/:id')
    map.connect('*url', controller='template', action='view')

    return map

