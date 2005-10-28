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

toppath = miscfuncs.toppath
pwcmdirs = miscfuncs.pwcmdirs
tempfilename = miscfuncs.tempfilename

from miscfuncs import NextAlphaString, AlphaStringToOrder
from patchtool import GenPatchFileNames


# Pulls in all the debates, written answers, etc, glues them together, removes comments,
# and stores them on the disk

# index file which is created
pwcmindex = os.path.join(toppath, "cmindex.xml")


# this does the main loading and gluing of the initial day debate files from which everything else feeds forward
class DefaultErrorHandler(urllib2.HTTPDefaultErrorHandler):
        def http_error_default(self, req, fp, code, msg, headers):
                result = urllib2.HTTPError(
                                req.get_full_url(), code, msg, headers, fp)
                result.status = code
                return result

# gets the index file which we use to go through the pages
class LoadCmIndex(xml.sax.handler.ContentHandler):
	def __init__(self, lpwcmindex):
		self.res = []
		self.check = {}
		if not os.path.isfile(lpwcmindex):
			return
		parser = xml.sax.make_parser()
		parser.setContentHandler(self)
		parser.parse(lpwcmindex)

	def startElement(self, name, attr):
		if name == "cmdaydeb":
			ddr = (attr["date"], attr["type"], attr["url"])
			self.res.append(ddr)

			# check for repeats - error in input XML
			key = (attr["date"], attr["type"])
			if key in self.check:
				raise Exception, "Same date/type twice %s %s\nurl1: %s\nurl2: %s" % (ddr + (self.check[key],))
			if not re.search("answers|debates|westminster|ministerial|votes(?i)", attr["type"]):
				raise Exception, "cmdaydeb of unrecognized type: %s" % attr["type"]
			self.check[key] = attr["url"]



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


def GlueByNext(fout, url, urlx):
	# put out the indexlink for comparison with the hansardindex file
	lt = time.gmtime()
	fout.write('<pagex url="%s" scrapedate="%s" scrapetime="%s"/>\n' % \
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




###############
# main function
###############
def PullGluePages(datefrom, dateto, forcescrape, folder, typ):
	# make the output firectory
	if not os.path.isdir(pwcmdirs):
		os.mkdir(pwcmdirs)
	pwcmfolder = os.path.join(pwcmdirs, folder)
	if not os.path.isdir(pwcmfolder):
		os.mkdir(pwcmfolder)

	# load the index file previously made by createhansardindex
	ccmindex = LoadCmIndex(pwcmindex)

	# the following is code copied from the lordspullgluepages

	# scan through the directory and make a mapping of all the copies for each
	lddaymap = { }
	for ldfile in os.listdir(pwcmfolder):
		mnums = re.match("%s(\d{4}-\d\d-\d\d)([a-z]*)\.html$" % typ, ldfile)
		if mnums:
			lddaymap.setdefault(mnums.group(1), []).append((AlphaStringToOrder(mnums.group(2)), mnums.group(2), ldfile))
		elif os.path.isfile(os.path.join(pwcmfolder, ldfile)):
			print "not recognized file:", ldfile, " in ", pwcmfolder

	# loop through the index of day line.
	for dnu in ccmindex.res:
		# implement date range
		if not re.search(typ, dnu[1], re.I):
			continue
		if dnu[0] < datefrom or dnu[0] > dateto:
			continue

		# make the filename
		dgflatestalpha, dgflatest, dgflatestdayalpha = "", None, None
		if dnu[0] in lddaymap:
			ldgf = max(lddaymap[dnu[0]]) # uses alphastringtoorder
			dgflatestalpha = ldgf[1]
			dgflatest = os.path.join(pwcmfolder, ldgf[2])
			dgflatestdayalpha = "%s%s" % (dnu[0], dgflatestalpha)
		dgfnextalpha = NextAlphaString(dgflatestalpha)
		ldgfnext = '%s%s%s.html' % (typ, dnu[0], dgfnextalpha)
		dgfnext = os.path.join(pwcmfolder, ldgfnext)
		dgfnextdayalpha = "%s%s" % (dnu[0], dgfnextalpha)
		assert not dgflatest or os.path.isfile(dgflatest)
		assert not os.path.isfile(dgfnext)

		# hansard index page
		urlx = dnu[2]
		if dnu[1] == 'Votes and Proceedings':
			url0 = urlx
		else:
			url0 = ExtractFirstLink(urlx, dgflatest, forcescrape)  # this checks the url at start of file
		if not url0:
			continue

		# make the message
		print dnu[0], (dgflatest and 'RE-scraping' or 'scraping'), re.sub(".*?cmhansrd/", "", urlx)

		# now we take out the local pointer and start the gluing
		dtemp = open(tempfilename, "w")
		GlueByNext(dtemp, url0, urlx)
		dtemp.close()

		# now we have to decide whether it's actually new and should be copied onto dgfnext.
		# "getsize" is unreliable because the readlines strips all the '\r's from the file
		# and can make two different sized files the same size
		if dgflatest:    # and os.path.getsize(tempfilename) == os.path.getsize(dgflatest):
			# load in as strings and check matching
			fdgflatest = open(dgflatest)
			sdgflatest = fdgflatest.readlines()
			fdgflatest.close()

			fdgfnext = open(tempfilename)
			sdgfnext = fdgfnext.readlines()
			fdgfnext.close()

			# first line contains the scrape date, so we ignore it
			if sdgflatest[1:] == sdgfnext[1:]:
				print "  matched with:", dgflatest
				continue


		# before we copy over the file from tempfilename to dgfnext, copy over the patch if there is one.

		# now find the patch file and copy it in, verifying we know what we're doing
		lpatchfilenext, lorgfilenext = GenPatchFileNames(folder, dgfnextdayalpha)[:2]
		assert lorgfilenext == dgfnext  # patchtool should give same name we are using
		if os.path.isfile(lpatchfilenext):
			print "    *****Warning: patchfile already present for newly scraped file:", lpatchfilenext
			assert False  # patchfile already present for newly scraped file
		if dgflatest:
			lpatchfile, lorgfile, tmpfile = GenPatchFileNames(folder, dgflatestdayalpha)[:3]
			assert lorgfile == dgflatest

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

		# now commit the file
		# print "  writing:", dgfnext
		os.rename(tempfilename, dgfnext)

