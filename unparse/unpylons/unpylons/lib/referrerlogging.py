import re
import unpylons.model as model
import datetime
import urlparse

def ConvertName(wname):
    wname = re.sub("/wiki/", "", wname)
    wname = re.sub("_", " ", wname)
    if re.search("%", wname):
        wname = re.sub("%28", "(", wname)
        wname = re.sub("%29", ")", wname)
        wname = re.sub("%C3%A9", "&#233;", wname)
        wname = re.sub("%C3%B6", "&#246;", wname)
        wname = re.sub("%C3%B4", "&#244;", wname)
        wname = re.sub("%27", "'", wname)
        wname = re.sub("%2C", ",", wname)
    return wname
    
    #wrefpage = re.sub("^UN_(?i)", "United_Nations_", wrefpage)
    #wrefpage = re.sub("^United_Nations_Resolution_(?i)", "United_Nations_Security_Council_Resolution_", wrefpage)

# somehow make do the count of incoming links
def logreferrer(referrer, ipaddress, useragent, pathinfo):
    if re.search("google|picsearch|search.msnbot|search.msn.com/msnbot|cuill.*?robot|ysearch/slurp|door/crawler|crawler.archive.org", useragent):
        return
    print (referrer, ipaddress, useragent, pathinfo)
    netloc, path = urlparse.urlsplit(referrer)[1:3] 
    if netloc == "en.wikipedia.org":
        path = ConvertName(path)
    if netloc == "127.0.0.1:5000":
        return
    m = model.IncomingLinks(referrer=referrer, url=pathinfo, ipnumber=ipaddress, useragent=useragent, ltime=datetime.datetime.now())
    m.refdomain = netloc
    m.reftitle = path
    m.url = pathinfo
    #Column('page',      String(30)), # tells us where the deeplink goes
    model.Session.flush()


