#! /usr/bin/python2.3
# vim:sw=8:ts=8:et:nowrap

import sys
import urllib
import urllib2
import urlparse
import re
import os.path
import xml.sax
import time
import tempfile
import string
import miscfuncs
import shutil
import mx.DateTime

toppath = miscfuncs.toppath
pwcmdirs = miscfuncs.pwcmdirs
tempfilename = miscfuncs.tempfilename

from miscfuncs import NextAlphaString, AlphaStringToOrder
from patchtool import GenPatchFileNames


# Pulls in all the debates, written answers, etc, glues them together, removes comments,
# and stores them on the disk

# index file which is created
pwcmindex = os.path.join(toppath, "cmindex.xml")
TodayInTheCommonsIndexPageUrl = "http://www.publications.parliament.uk/pa/cm/cmtoday/home.htm"

class ScraperException:
	def __init__(self, message):
		self.message = message
	
	def __str__(self):
		return self.message

# this does the main loading and gluing of the initial day debate files from which everything else feeds forward
class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
        def http_error_default(self, req, fp, code, msg, headers):
                result = urllib2.HTTPError(
                                req.get_full_url(), code, msg, headers, fp)
                result.status = code
                return result

# gets the index file which we use to go through the pages
class CommonsIndex(xml.sax.handler.ContentHandler):
	def __init__(self):
		self.res = []
		self.check = {}
		
		if not os.path.isfile(pwcmindex):
			return
		parser = xml.sax.make_parser()
		parser.setContentHandler(self)
		parser.parse(pwcmindex)

	def startElement(self, name, attr):
		if name == "cmdaydeb":
			# check for repeats - error in input XML
			key = (attr["date"], attr["type"])
			if key in self.check:
				raise Exception, "Same date/type twice %s %s\nurl1: %s\nurl2: %s" % (ddr + (self.check[key],))
			self.check[key] = attr["url"]
			
			self.res.append(CommonsIndexElement(attr["date"], attr["type"], attr["url"]))

class CommonsIndexElement:
	def __init__(self, date, recordType, url):
		# sanity check the types
		if not re.search("answers|debates|westminster|ministerial|votes(?i)", recordType):
			raise Exception, "cmdaydeb of unrecognized type: %s" % recordType
		
		self.date = date
		self.recordType = recordType
		self.url = url
		
	def __repr__(self):
		return "<%s, %s, %s>" % (self.date, self.recordType, self.url)

def WriteCleanText(fout, text):
	abf = re.split('(<[^>]*>)', text)
	for ab in abf:
		# delete comments and links
		if re.match('<!-[^>]*?->', ab):
			pass

		elif re.match('<a[^>]*>(?i)', ab):
			anamem = re.match('<a name\s*?=\s*?"?(\S*?)"?\s*?>(?i)', ab)
                        if anamem:
                                aname = anamem.group(1)
                                if not re.search('column', aname): # these get in the way
                                        fout.write('<a name="%s">' % aname)
                        else:
                                # We should never find any other sort of <a> tag - such
                                # as a link (as there aren't any on parliament.uk)
                                print "Caught a link ", ab

		elif re.match('</a>(?i)', ab):
			pass

		# spaces only inside tags
		elif re.match('<[^>]*>', ab):
			fout.write(re.sub('\s', ' ', ab))

		# take out spurious > symbols and dos linefeeds
		else:
			fout.write(re.sub('>|\r', '', ab))

def GlueByNext(outputFileName, url, urlx):
	fout = open(outputFileName, "w")
	# put out the indexlink for comparison with the hansardindex file
	lt = time.gmtime()
	fout.write('<pagex url="%s" scrapedate="%s" scrapetime="%s" type="printed" />\n' % \
			(urlx, time.strftime('%Y-%m-%d', lt), time.strftime('%X', lt)))

	# loop which scrapes through all the pages following the nextlinks
	while 1:
		# print " reading " + url
		ur = urllib.urlopen(url)
		sr = ur.read()
		ur.close();

		# write the marker telling us which page this comes from
                if (url != urlx):
                        fout.write('<page url="' + url + '"/>\n')

                sr = re.sub('<!-- end of variable data -->.*<hr>(?si)', '<hr>', sr)

		# split by sections
                hrsections = re.split('<hr(?: size=3)?>(?i)', sr)

		# this is the case for debates on 2003-03-13 page 30
		# http://www.publications.parliament.uk/pa/cm200203/cmhansrd/vo030313/debtext/30313-32.htm
		if len(hrsections) == 1:
			print len(hrsections)
			print ' page missing '
			print url
			fout.write('<UL><UL><UL></UL></UL></UL>\n')
			break

		# write the body of the text
		for i in range(1,len(hrsections) - 1):
			WriteCleanText(fout, hrsections[i])

		# find the lead on with the footer
		footer = hrsections[-1]

		# the files are sectioned by the <hr> tag into header, body and footer.
		nextsectionlink = re.findall('<\s*a\s+href\s*=\s*"?(.*?)"?\s*>next section</a>(?i)', footer)
		if not nextsectionlink:
			break
		if len(nextsectionlink) > 1:
			raise Exception, "More than one Next Section!!!"
		url = urlparse.urljoin(url, nextsectionlink[0])
		
	fout.close()


# now we have the difficulty of pulling in the first link out of this silly index page
def ExtractFirstLink(url, dgf, forcescrape):
	request = urllib2.Request(url)
	if not forcescrape and dgf and os.path.exists(dgf):
		mtime = os.path.getmtime(dgf)
		mtime = time.gmtime(mtime)
		mtime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", mtime)
		request.add_header('If-Modified-Since', mtime)
	opener = urllib2.build_opener( DefaultErrorHandler() )
	urx = opener.open(request)
	if hasattr(urx, 'status'):
		if urx.status == 304:
			return ''

	while 1:
		xline = urx.readline()
		if not xline:
			break
		if re.search('<hr>(?i)', xline):
			break

	lk = []
	while xline:
		# <a HREF =" ../debtext/31106-01.htm#31106-01_writ0">Oral Answers to Questions </a>
		lk = re.findall('<a\s+href\s*=\s*"(.*?)">.*?\s*</a>(?i)', xline)
		if lk:
			break
		xline = urx.readline()
	urx.close()

	if not lk:
		print urx
		print url
		raise Exception, "No link found!!!"
	return urlparse.urljoin(url, re.sub('#.*$' , '', lk[0]))



def MakeDayMap(folder, typ):
	# make the output firectory
	if not os.path.isdir(pwcmdirs):
		os.mkdir(pwcmdirs)
	pwcmfolder = os.path.join(pwcmdirs, folder)
	if not os.path.isdir(pwcmfolder):
		os.mkdir(pwcmfolder)


	# the following is code copied from the lordspullgluepages

	# scan through the directory and make a mapping of all the copies for each
	lddaymap = { }
	for ldfile in os.listdir(pwcmfolder):
		mnums = re.match("%s(\d{4}-\d\d-\d\d)([a-z]*)\.html$" % typ, ldfile)
		if mnums:
			lddaymap.setdefault(mnums.group(1), []).append((AlphaStringToOrder(mnums.group(2)), mnums.group(2), ldfile))
		elif os.path.isfile(os.path.join(pwcmfolder, ldfile)):
			print "not recognized file:", ldfile, " in ", pwcmfolder
	
	return lddaymap, pwcmfolder
	
	
def GetFileDayVersions(day, lddaymap, pwcmfolder, typ):
	# make the filename
	dgflatestalpha, dgflatest, dgflatestdayalpha = "", None, None
	if day in lddaymap:
		ldgf = max(lddaymap[day]) # uses alphastringtoorder
		dgflatestalpha = ldgf[1]
		dgflatest = os.path.join(pwcmfolder, ldgf[2])
		dgflatestdayalpha = "%s%s" % (day, dgflatestalpha)
	dgfnextalpha = NextAlphaString(dgflatestalpha)
	ldgfnext = '%s%s%s.html' % (typ, day, dgfnextalpha)
	dgfnext = os.path.join(pwcmfolder, ldgfnext)
	dgfnextdayalpha = "%s%s" % (day, dgfnextalpha)
	assert not dgflatest or os.path.isfile(dgflatest)
	assert not os.path.isfile(dgfnext)
	return dgflatest, dgflatestdayalpha, dgfnext, dgfnextdayalpha


def readPageX(filename):
	if not filename or not os.path.isfile(filename):
		return {}
	hFile = open(filename)
	line= hFile.readline()
	hFile.close()
	
	map={}
	attributes= re.search('<pagex(( +[^ =]+="[^"]+")+) */>', line).group(0)
	for match in re.finditer('([^ =]+)="([^"]+)"', attributes):
		map[match.group(1)] = match.group(2)
	return map

def CompareScrapedFiles(prevfile, nextfile):
	if not prevfile:
		return "DIFFERENT"
	
	hprevfile = open(prevfile)
	dprevfile = hprevfile.readlines()
	hprevfile.close()
		
	hnextfile = open(nextfile)
	dnextfile = hnextfile.readlines()
	hnextfile.close()
	
	if len(dprevfile) == len(dnextfile) and dprevfile[1:] == dnextfile[1:]:
		return "SAME"
	if len(dprevfile) < len(dnextfile) and dprevfile[1:] == dnextfile[1:len(dprevfile)]:
		return "EXTENSION"
	return "DIFFERENT"


##############################
# For gluing together debates
##############################
def PullGluePages(datefrom, dateto, forcescrape, folder, typ):
	daymap, scrapedDataOutputPath = MakeDayMap(folder, typ)

	# loop through the index file previously made by createhansardindex
	for commonsIndexRecord in CommonsIndex().res:
		# implement date range
		if not re.search(typ, commonsIndexRecord.recordType, re.I):
			continue
		if commonsIndexRecord.date < datefrom or commonsIndexRecord.date > dateto:
			continue

		latestFilePath, latestFileStem, nextFilePath, nextFileStem = \
			GetFileDayVersions(commonsIndexRecord.date, daymap, scrapedDataOutputPath, typ)

		# hansard index page
		urlx = commonsIndexRecord.url
		if commonsIndexRecord.recordType == 'Votes and Proceedings':
			url0 = urlx
		else:
			url0 = ExtractFirstLink(urlx, latestFilePath, forcescrape)  # this checks the url at start of file
		if not url0:
			continue

		# make the message
		print commonsIndexRecord.date, (latestFilePath and 'RE-scraping' or 'scraping'), re.sub(".*?cmhansrd/", "", urlx)

		# now we take out the local pointer and start the gluing
		GlueByNext(tempfilename, url0, urlx)

		if CompareScrapedFiles(latestFilePath, tempfilename) == "SAME":
			print "  matched with:", latestFilePath
			continue

		# before we copy over the file from tempfilename to nextFilePath, copy over the patch if there is one.
		ReplicatePatchToNewScrapedVersion(folder, latestFileStem, latestFilePath, nextFilePath, nextFileStem)
		
		# now commit the file
		os.rename(tempfilename, nextFilePath)

def ReplicatePatchToNewScrapedVersion(folderName, latestFileStem, latestFilePath, nextFilePath, nextFileStem):
	if not latestFilePath:
		return
		
	# check that the patch file for the 'next' version has not yet been created
	lpatchfilenext, lorgfilenext = GenPatchFileNames(folderName, nextFileStem)[:2]
	assert lorgfilenext == nextFilePath  # patchtool should give same name we are using
	if os.path.isfile(lpatchfilenext):
		print "    *****Warning: patchfile already present for newly scraped file:", lpatchfilenext
		assert False  # patchfile already present for newly scraped file
	
	# now find the patch file and copy it in, verifying we know what we're doing
	lpatchfile, lorgfile, tmpfile = GenPatchFileNames(folderName, latestFileStem)[:3]
	assert lorgfile == latestFilePath

	# if there's an old patch, apply the patch to the old file
	if os.path.isfile(lpatchfile):
		shutil.copyfile(tempfilename, tmpfile)
		status = os.system("patch --quiet %s < %s" % (tmpfile, lpatchfile))
		if status == 0:
			print "Patchfile still applies, copying over ", lpatchfile, "=>", lpatchfilenext
			print "   There you go..."
			shutil.copyfile(lpatchfile, lpatchfilenext)
		else:
			print "    Could not apply old patch file to this, status=", status

def PullGlueToday(forcescrape):
	# Fetch 'Today in the Commons' index page
	frontpagedata = fetchTextFromUrl(TodayInTheCommonsIndexPageUrl)
	pageurl = urlparse.urljoin(
			TodayInTheCommonsIndexPageUrl,
			re.search("<a href=\"(01\.htm)\">Go to Full Report</a>", frontpagedata).group(1)
		)

	preparedDateMatch = re.search("<p class=\"prepared\">Prepared: <strong>(\d+:\d+) on (\d+ [a-zA-Z]+ \d+)</strong></p>", frontpagedata)
	preparedDateTime = mx.DateTime.DateTimeFrom(preparedDateMatch.group(1) + " " + preparedDateMatch.group(2))


	# make files which we will copy into
	lddaymap, pwcmfolder = MakeDayMap("debates", "debates")
	dgflatest, dgflatestdayalpha, dgfnext, dgfnextdayalpha = GetFileDayVersions(preparedDateTime.date, lddaymap, pwcmfolder, "debates")

	# See if we actually want to proceed with scraping, or if there already exists a 'printed' version
	# in which case we avoid replacing it with the 'today' version
	latestScrapedFileMetaData = readPageX(dgflatest)
	if ('type' in latestScrapedFileMetaData and latestScrapedFileMetaData['type']=='printed'):
		print "'Printed' version of hansard for today has already been scraped. Skipping scrape of 'Today' version"
		return None

	tempFileHandle = open(tempfilename, "w")
	tempFileHandle.write('<pagex url="%s" scrapedate="%s" scrapetime="%s" prepareddatetime="%s" type="today" />\n' % (TodayInTheCommonsIndexPageUrl, time.strftime('%Y-%m-%d', time.gmtime()), time.strftime('%X', time.gmtime()), preparedDateTime))

	GlueByToday(tempFileHandle, pageurl)
	tempFileHandle.close()

	comp = CompareScrapedFiles(dgflatest, tempfilename)

	if comp == 'DIFFERENT' or comp == 'EXTENSION':
		# now commit the file
		os.rename(tempfilename, dgfnext)
	elif comp != 'SAME':
		raise ScraperException("Unknown comparison type '%s'" % comp)

def GlueByToday(outputFileHandle, pageurl):
	pagenumber=1
	while pageurl:
		assert pagenumber==int(re.search('(\d+)\.htm$', pageurl).group(1))
		preparedDateTime, nextLink, body = ScrapeTodayPage(pageurl)

		print "Processed [%s] which was prepared [%s]" % (pageurl, preparedDateTime)
		now = time.gmtime()
		outputFileHandle.write('<page url="%s" prepareddatetime="%s" />\n' % (pageurl, preparedDateTime) )
		outputFileHandle.write(body)
		outputFileHandle.write('\n')

		if nextLink:
			pageurl = urlparse.urljoin(pageurl, nextLink)
		else:
			pageurl = None
		pagenumber += 1

def ScrapeTodayPage(pageurl):
	raw_html = fetchTextFromUrl(pageurl)
	matches = re.search('''(?sx)
	<body\sclass="commons".*
	<p\sclass="preparedFullText">
	Prepared:\s
	<strong>
		(\d+:\d+)\son\s(\d+\s[a-zA-Z]+\s\d+)
	</strong>
	.*
	(?:
		<a\shref="(\d+\.htm)">Next</a>           # link to next page
		|
		<!--\sSPACE\sFOR\sNEXT\sLABEL\s-->
	)
	.*
	<a\sname="toptop"></a>
	(.*)  # main body text of page
	<hr>\s*<ul\sclass="prevNext">
	''', raw_html
	)

	preparedDateTime = mx.DateTime.DateTimeFrom(matches.group(1) + " " + matches.group(2))
	nextLink = matches.group(3)
	sbody = matches.group(4)

	# remove junk links inserted for left hand panel
	body = re.sub('<span><a href="#toptop">Back to top</a></span>', '', sbody)

	return preparedDateTime, nextLink, body


def fetchTextFromUrl(url):
	ur = urllib.urlopen(url)
	frontpagedata = ur.read()
	ur.close();
	return frontpagedata



