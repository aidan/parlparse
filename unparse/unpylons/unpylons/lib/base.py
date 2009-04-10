"""The base Controller API

Provides the BaseController class for subclassing, and other objects
utilized by Controllers.
"""
from pylons import c, cache, config, g, request, response, session
from pylons.controllers import WSGIController
from pylons.controllers.util import abort, etag_cache, redirect_to
from pylons.decorators import jsonify, validate
from pylons.i18n import _, ungettext, N_
from pylons.templating import render

import unpylons.lib.helpers as h
import unpylons.model as model
from unpylons.lib.referrerlogging import logreferrer

# this is going to fill in the third column for wikipedia references
def DLogPrintReferrer():
    logreferrer(referrer = request.environ.get("HTTP_REFERER") or "", ipaddress = request.environ["REMOTE_ADDR"], useragent = request.environ["HTTP_USER_AGENT"], pathinfo = request.environ["PATH_INFO"]) 

class BaseController(WSGIController):

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # WSGIController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']
        return WSGIController.__call__(self, environ, start_response)

# Include the '_' function in the public names
__all__ = [__name for __name in locals().keys() if not __name.startswith('_') \
           or __name == '_']
