import logging

from unpylons.lib.base import *

log = logging.getLogger(__name__)

class NationController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return 'List of nations ...'
    
    def info(self, id=None):
        return 'Nation is called: %s' % id
