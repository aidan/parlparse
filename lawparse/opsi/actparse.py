#!/usr/bin/python

# actparse.py - parses acts from HTML into XML files

# Copyright (C) 2005 Francis Davey and Julian Todd, part of lawparse

# lawparse is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# 
# lawparse is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with lawparse; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA  02110-1301  USA


import urllib
import urlparse
import re
import sys
import os
import patches
import logging
import getopt
import traceback
import optparse 
import options


import parsefun

import miscfun
#actdirhtml = miscfun.actdirhtml
#actdirxml = miscfun.actdirxml

from parsehead import ActParseHead
from analyser import ParseBody
import legis


# basic class -- some legislative text

class OpsiSourceInfo(legis.SourceInfo):
	def __init__(self,url):
		legis.SourceInfo.__init__(self,'opsi')
		self.url=url
		self.values={}

	def xml(self):
		s=''
		for k in self.values.keys():
			s=s+'\n\t%s="%s"' % (k, self.values[k])
		return '<sourceinfo source="opsi"\n\turl="%s"%s\n/>' % (self.url,s)
		

class LegislationFragment:
	def __init__(self,txt):
		self.txt=txt
		self.quotations=[]
		self.tables=[]
		self.isquotation=False
		self.headvalues={}

	def ShortID(self):
		return 'unidentified fragment'

	# function for pulling off regexps from the front of the text

	def QuotationAsFragment(self,n,locus):
		qtext=self.quotations[n]
		fragment=QuotedActFragment(qtext,locus)
		#fragment.id="quoted in(%s)" % locus.text()
		fragment.id=locus.text()
		return fragment

	def NibbleHead(self, hcode, hmatch):
		mline = re.match(hmatch, self.txt)
		if not mline:
			print 'failed at:', hcode, ":\n", hmatch, "\non:"
			print self.txt[:1000]
			raise Exception

		# extract any strings
		# (perhaps make a class that has all these fields in it)
		elif hcode == "middle":
			pass
		elif hcode == "checkfront":
			return  # just for the checking
		elif hcode == 'preisbn':
			if mline.group(1):
				isbn = "%s %s %s" % (mline.group(2), mline.group(3), mline.group(4))
			else:
				isbn="XXXXXXXXXXX"
			self.headvalues[hcode] = [isbn]

		# remaining parameter found
		else:
			if self.headvalues.has_key(hcode):
				logger.warning('second use of key %s with value %s' % (hcode, mline.groups()))
			self.headvalues[hcode] = mline.groups()

		# move on
		self.txt = self.txt[mline.end(0):]


# Probably don't need a separate class for this, but I am not sure.

class ActFragment(LegislationFragment):
	def __init__(self,txt):
		LegislationFragment.__init__(self,txt)

class QuotedActFragment(ActFragment):
	def __init__(self,txt,locus):
		ActFragment.__init__(self,txt)
		self.isquotation=True
		self.locus=locus

	def ParseAsQuotation(self):
		logger=logging.getLogger('opsi.actparse')
		#locus=legis.Locus(self)
		quotation=legis.Quotation(True,self.locus)
		if re.search('>"',self.txt):
			ParseBody(self,quotation,'entire')
		else:
			logger.warning("***warning, tried to parse as quotation without quotation marks")
			#print "***warning, unparseable quotation text", self.txt
		return quotation


class SI(LegislationFragment):
	def __init__(self, cname, txt):
		LegislationFragment.__init__(self,txt)
		m = re.search("(\d{4})no(\d+).html$", cname)
		self.year=m.group(1)
		self.number=m.group(2)

	def ShortID(self):
		return "uksi%sno%s" % (self.year,self.number)

	def dir(options, name):
		dir=options.__dict__['sidir' + name]
		#print name,dir
		return dir

	dir=staticmethod(dir)
	

	def Parse(self):
		ActParseHead(self)
		
		legisobj=legis.SI(self.year,self.number)
		legisobj.sourceinfo=OpsiSourceInfo(self.url)
		self.LegisHeader(legisobj)

		ParseBody(self,legisobj,'none')
		return legisobj

	
class Act(ActFragment):
	def __init__(self, cname, txt):
		logger=logging.getLogger('')
		LegislationFragment.__init__(self,txt)
		m = re.search("(\d{4})c(\d+).html$", cname)
		self.year = m.group(1)
		self.chapter = m.group(2)
		urlmatch=re.match('<pageurl page="0" url="([^"]*?)"/>',txt)
		if urlmatch:
			self.url=urlmatch.group(1)
		else:
			logger.warning("Cannot see pageurl at beginning of act")
			self.url=''

	def dir(options, name):
		return options.__dict__['actdir' + name]

	dir=staticmethod(dir)

	def ShortID(self):
		return "ukgpa%sc%s" % (self.year, self.chapter)

	def Parse(self):
		ActParseHead(self)
		
		legisact=legis.Act(self.year,0,self.chapter)
		legisact.sourceinfo=OpsiSourceInfo(self.url)
		self.LegisHeader(legisact)

		ParseBody(self,legisact,'none')
		return legisact

	

	def LegisHeader(self,legisact):

		if self.headvalues.has_key('longtitle'):
			legisact.preamble=legis.ActPreamble()
			legisact.preamble.longtitle=self.headvalues['longtitle'][0]
			enact=self.headvalues['enact'][0]
			if enact:
				legisact.preamble.enactment=re.sub('(<B>|</B>|<FONT[^>]*>|</FONT>)(?i)','',enact)
		else:
			legisact.preamble=legis.SupplyActPreamble()
			legisact.preamble.apply=self.headvalues['apply']
			legisact.preamble.date=self.headvalues['consoldate']
			if self.headvalues.has_key('petition1'):
				legisact.preamble.petition=self.headvalues['petition1']
			else:
				legisact.preamble.petition=self.headvalues['petition2']+self.headvalues['enact']
		
		keylist=['name','year','chapter','prodid','name2','name3','chapt2']
		for k in keylist:
			if self.headvalues.has_key(k):
				legisact.sourceinfo.values[k]=self.headvalues[k][0]


		#print self.headvalues
		


# Note: skipped acts
# Some of the acts are too hard. Others turn out to have serious erros with 
# them. We should develop a list of "acts needing attention". Provisionally:

# 1988c17 -- Schedule 2 is missing a heading in the quoted material, and
# does not properly close a table.


def SetupLogging(options,name):

	logger=logging.getLogger('')

	mainlog = logging.FileHandler('actparse.log')
	options.value('debug').ConfigHandler(mainlog)
	logger.addHandler(mainlog)

	console = logging.StreamHandler()
	#print "console log options: %s" % options.value('consoledebug')
	options.value('consoledebug').ConfigHandler(console)
	logger.addHandler(console)	

	#print logging.getLogger('').getEffectiveLevel()

def ParseLoop(statlist,options, Stat):
	# just run through and apply to all the files
	logger=logging.getLogger('')

	start=options.value('start')
	skipfiles=options.value('skip')
	filedebuglevel=options.value('filedebug')

	for i in range(start,len(statlist)):
		s="reading %s %s" % (i, statlist[i])
		logger.warning(s)
		if statlist[i] in skipfiles:
			logger.warning("skipping %s %s" % (i, statlist[i]))
			#logger.warning(s)
			continue

		dirhtml=Stat.dir(options2, 'html')
		logger.debug(dirhtml, statlist[i], os.path.join(dirhtml, statlist[i]))
		fin = open(os.path.join(dirhtml, statlist[i]), "r")
		txt = fin.read()
		fin.close()

		stat = Stat(statlist[i], txt)
		patches.ActApplyPatches(stat)

		# the parsing process

		# need to do configuration better -- put in config for log

		opsilogger=logging.getLogger('')
		filelogname=os.path.join('log',stat.ShortID()+'.log')
		if os.path.exists(filelogname):
			os.remove(filelogname)
	
		filehandler=logging.FileHandler(filelogname)
		options.value('filedebug').ConfigHandler(filehandler)
		opsilogger.addHandler(filehandler)


		try:
			lexed=stat.Parse()
		except parsefun.ParseError, inst:
			opsilogger.warning(inst)
			opsilogger.exception("+++Error occurred in file number %s (%s)" % (i,stat.ShortID()))
			opsilogger.exception(traceback.format_exc())
#			if options.isset('stoponerror'):
#				raise parsefun.ParseError
			
			success=False
		else:
			success=True
		
		filehandler.flush()
		opsilogger.removeHandler(filehandler)
#		filehandler.close()

		if success:

			out = open(os.path.join(Stat.dir(options2, 'xml'), lexed.id+".xml"), "w")
			out.write(lexed.xml()) 

		

# main running part
if __name__ == '__main__':
		
	#print os.path.basename(sys.argv[0])

	if os.path.basename(sys.argv[0])=='actparse.py':
		Stat=Act
	else:
		Stat=SI

	logging.getLogger('').setLevel(0)

	parser = options.OpsiOptionParser()
	(options2, args) = parser.parse_args()

	options=options.Options()
	args=options.ParseArguments()

	
	if len(args) > 0:
		statlist = ["ukgpa%s.html" % x for x in args]
	else:
		statlist = os.listdir(Stat.dir(options2, 'html'))
		del statlist[0]	# removes file ".svn"

	SetupLogging(options,'opsi')

	ParseLoop(statlist,options, Stat)
