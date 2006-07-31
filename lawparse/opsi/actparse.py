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
		

class RemoveTablesError(parsefun.ParseError):
	pass


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

	def RemoveQuotationMarks(self):
			logger=logging.getLogger('')
			quotes=re.findall('&quot;',self.txt)
			if len(quotes) % 2 > 0:
				logger.warning("an odd number (%i) of quotation marks found" % len(quotes))
			if len(quotes)<2:
				logger.warning("fewer than two quotation marks in quotation")
			else:
				first=self.txt.find('&quot;')
				last=self.txt.rfind('&quot;')
				self.txt=self.txt[:first]+self.txt[first+6:last]+self.txt[last+6:]
	
			logging.debug("After removal:\n%s\n---------------" % self.txt)
	

	def RemoveJunk(self):
		'''Removes various superfluous tags and comments.

		Removes horizontal rules (which shouldn't be there); XML 
		comments which reveal only the inner workings of opsi, 
		and <dt1 and <p4 which must be mistakes (surely).
		'''

		self.txt=re.sub('\s*<hr[^>]*>(?i)','',self.txt)
		self.txt=re.sub('<dt1[^>]*>([\s\S]*?)</dt1>(?i)','\\1',self.txt)
		self.txt=re.sub('<p4[^>]*>([\s\S]*?)</p4>(?i)','\\1',self.txt)
		self.txt=re.sub('<!--[^-]*-->','',self.txt)


	def RemoveTables(self, tablelist, patternlist, tabtype):
		logger=logging.getLogger('')
		n=0	
		logger.info('Removing tables')
		for (firstpattern, secondpattern, label) in patternlist:
			logger.info('Searching for tabtype=%s label=%s' % (tabtype, label))
			logger.debug('pattern to be matched %s' % firstpattern)
			logger.debug('%s' % re.search(firstpattern,self.txt))
	
			logger.debug("**** %s" %  re.search('<table cellpadding="8"',self.txt))
	
			while re.search(firstpattern,self.txt):
	
				leftmatch=re.search(firstpattern,self.txt)
				logger.info('Table pattern(%s,%s,%s)' % (tabtype, label, leftmatch.start()))
				logger.debug('spattern=%s' % firstpattern)
				# obtain the pre match pattern.
				if leftmatch.groupdict().has_key('pre'):
					pre=leftmatch.group('pre')
				else:
					pre=''
	
				tableoffset=parsefun.TableBalance(self.txt[leftmatch.end():])
				tablestart=leftmatch.end()
				tableend=tablestart+tableoffset
	
				tablematch=re.match('<table[^>]*?>([\s\S]*?)</table>$',self.txt[tablestart:tableend])
				if not tablematch:
					raise RemoveTablesError, 'table pattern fails to match:\n%s' % self.txt[tablestart:tableend]
				store=tablematch.group(1)
				logging.debug("Storing at number n=%s\n%s" % (n, store))
	
				if False: #n==8:
					print "*****storing:"
					print store
					print "*****"
	
				rightmatch=re.match(secondpattern,self.txt[tableend:])
				if not rightmatch:
					raise RemoveTablesError
				if rightmatch.groupdict().has_key('post'):
					post=rightmatch.group('post')
				else:
					post=''
	
				tablelist.append(store)
	
				quote='<%s n="%i" pattype="%s"/>' % (tabtype, 
					n,label)
				n=n+1
				#self.txt=self.txt[:tablestart] + pre + quote + post + self.txt[tableend:]
				lstart=leftmatch.start()
				lend=leftmatch.end()
				rstart=rightmatch.start()+tableend
				rend=rightmatch.end()+tableend
				#print lstart,lend, tablestart, tableend, firstpattern, secondpattern, n, label, rstart, rend
				#print self.txt[lstart:lend]
				#print self.txt[rstart:rend]
				#self.txt=self.txt[:leftmatch.start()] + pre + quote + post + self.txt[rightmatch.end():]
				self.txt=self.txt[:lstart] + pre + quote + post + self.txt[rend:]
								

				#sys.exit()

	def RemoveTabular(self):
		self.RemoveTables(self.tables, parsefun.tablepatterns, 'tabular')

	def RemoveQuotations(self):
		self.RemoveTables(self.quotations, parsefun.quotepatterns, 'quotation')



	def Tidy(self, isquote=False):
		self.RemoveJunk()
		self.RemoveQuotations()
		self.RemoveTabular()
	
		if isquote:
			logging.info("Removing quotation marks")
			self.RemoveQuotationMarks()
	

	def QuotationAsFragment(self,n,locus):
		qtext=self.quotations[n]
		fragment=QuotedActFragment(qtext,locus)
		#fragment.id="quoted in(%s)" % locus.text()
		fragment.id=locus.text()
		return fragment

	def NibbleHead(self, hcode, hmatch):
		logger=logging.getLogger('')
		mline = re.match(hmatch, self.txt)
		if not mline:
			#print 'failed at:', hcode, ":\n", hmatch, "\non:"
			#print self.txt[:1000]
			raise parsefun.ParseError, 'failed at:%s:\n%s:\non:\n%s' % (hcode, hmatch, self.txt[:1000])
			

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
		
		ParseBody(self,quotation,'entire')
		
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
		logger=logging.getLogger('opsi.actparse')
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
		return "ukpga%sc%s" % (self.year, self.chapter)

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


def SetupLogging(values,name):

	logger=logging.getLogger('')

	mainlogfh = logging.FileHandler('actparse.log')
	mainlog=options.Log.getarg(values.debug)
	mainlog.ConfigHandler(mainlogfh)	

	logger.addHandler(mainlogfh)

	consolefh = logging.StreamHandler()
	console=options.Log.getarg(values.consoledebug)
	console.ConfigHandler(consolefh)

	logger.addHandler(consolefh)	

	#print logging.getLogger('').getEffectiveLevel()

def ParseLoop(statlist,values, Stat):
	# just run through and apply to all the files
	logger=logging.getLogger('')

	start=values.start #options.value('start')
	skipfiles=[ 'ukpga%s.html' % id for id in values.skip]  #options.value('skip')

	filedebuglevel=options.Log.getarg(values.filedebug).level

	#options.value('filedebug')

	for i in range(start,len(statlist)):
		s="reading %s %s" % (i, statlist[i])
		logger.warning(s)

		if statlist[i] in skipfiles:
			logger.warning("skipping %s %s" % (i, statlist[i]))
			#logger.warning(s)
			continue

		dirhtml=Stat.dir(values, 'html')
		logger.debug(dirhtml, statlist[i], os.path.join(dirhtml, statlist[i]))
		fin = open(os.path.join(dirhtml, statlist[i]), "r")
		txt = fin.read()
		fin.close()

		stat = Stat(statlist[i], txt)
		
		patches.ActApplyPatches(stat)
		
		if values.patchonly:
			sys.exit()

		# the parsing process

		# need to do configuration better -- put in config for log

		opsilogger=logging.getLogger('')
		filelogname=os.path.join('log',stat.ShortID()+'.log')
		if os.path.exists(filelogname):
			os.remove(filelogname)
	
		filehandler=logging.FileHandler(filelogname)
		options.Log.getarg(values.filedebug).ConfigHandler(filehandler)
		opsilogger.addHandler(filehandler)
	
		try:
			if values.preprocess:
				print "preprocessing"
				
				ActParseHead(stat)
				
				stat.Tidy()
				print "tidied statute"

				outfile=os.path.join(Stat.dir(values, 'xml'),"%s.pp" % stat.ShortID())
				outstring=stat.txt
			else:
				lexed=stat.Parse()
				outfile=os.path.join(Stat.dir(values, 'xml'), lexed.id+'.xml')
				outstring=lexed.xml()				
		except (parsefun.ParseError,legis.LegisError), inst:
			opsilogger.warning(inst)
			opsilogger.error("+++Error occurred in file number %s (%s)" % (i,stat.ShortID()))
			#opsilogger.exception(traceback.format_exc())
			if False: #values.stoponerror:
				#raise parsefun.ParseError
				#raise Exception
				print "values.stoponerror=%s\nstopped on error" % values.stoponerror
				sys.exit()
			
			success=False
		else:
			success=True
		
		filehandler.flush()
		opsilogger.removeHandler(filehandler)
#		filehandler.close()

		if success:
			
			print outfile, len(outstring), success
			
			out = open(outfile, "w")
			out.write(outstring) 

		

# main running part
if __name__ == '__main__':
		
	#print os.path.basename(sys.argv[0])

	if os.path.basename(sys.argv[0])=='actparse.py':
		Stat=Act
	else:
		Stat=SI

	logging.getLogger('').setLevel(0)

	# setting up options for actparse.py

	parser = options.OpsiOptionParser

	parser.add_option('-s','--start',dest='start', type="int", help="Number of file to start at")
	parser.add_option('-p','--preprocess',dest='preprocess', action="store_true", help="Only run the file through the preprocessor.")
	parser.add_option('-x','--stoponerror', dest='stoponerror', action="store_true", help="Stop if a file gives an error, rather than continuing regardless", default="False")
	parser.add_option('--patchonly',dest='patchonly',action="store_true",help="only apply patches to the file")

	parser.set_defaults(preprocess=False, start=0, patchonly=False)

	(values, args) = parser.parse_args()

	print "values.stoponerror=%s" % values.stoponerror
	#sys.exit()

	if len(args) > 0:
		statlist = ["ukpga%s.html" % x for x in args]
	else:
		statlist = os.listdir(Stat.dir(values, 'html'))
		del statlist[0]	# removes file ".svn"

	SetupLogging(values,'opsi')

	ParseLoop(statlist,values, Stat)
