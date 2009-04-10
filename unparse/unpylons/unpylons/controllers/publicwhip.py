import logging
import unicodedata

from unpylons.lib.base import *

log = logging.getLogger(__name__)

class PublicwhipController(BaseController):

    def mps(self):
        c.mps = model.Member.query.filter_by(countrycode3="MP").filter_by(finished="9999-12-31")
        return render('pwmps')
    

