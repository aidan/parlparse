#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import os
import patches

import miscfun
actdirhtml = miscfun.actdirhtml
actdirxml = miscfun.actdirxml

from parsehead import ActParseHead
from analyser import ParseBody, ParseError
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
		fragment=QuotedActFragment(qtext)
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
			self.headvalues[hcode] = mline.groups()

		# move on
		self.txt = self.txt[mline.end(0):]


# Probably don't need a separate class for this, but I am not sure.

class ActFragment(LegislationFragment):
	def __init__(self,txt):
		LegislationFragment.__init__(self,txt)

class QuotedActFragment(ActFragment):
	def __init__(self,txt):
		ActFragment.__init__(self,txt)
		self.isquotation=True


	def ParseAsQuotation(self):
		locus=legis.Locus(self)
		quotation=legis.Quotation(True,locus)
		if re.search('>"',self.txt):
			ParseBody(self,quotation)
		else:
			print "***warning, tried to parse as quotation without quotation marks"
			#print "***warning, unparseable quotation text", self.txt
		return quotation


class SI(LegislationFragment):
	def __init__(self, year, number, txt):
		LegislationFragment.__init__(self,txt)
		self.year=year
		self.number=number

	def ShortID(self):
		return "uksi%sno%s" % (year,number)

	
	
class Act(ActFragment):
	def __init__(self, cname, txt):
		LegislationFragment.__init__(self,txt)
		m = re.search("(\d{4})c(\d+).html$", cname)
		self.year = m.group(1)
		self.chapter = m.group(2)
		urlmatch=re.match('<pageurl page="0" url="([^"]*?)"/>',txt)
		if urlmatch:
			self.url=urlmatch.group(1)
		else:
			print "****Warning, cannot see pageurl at beginning of act"
			self.url=''

	def ShortID(self):
		return "ukgpa%sc%s" % (self.year, self.chapter)

	def Parse(self):
		ActParseHead(self)
		
		legisact=legis.Act(self.year,0,self.chapter)
		legisact.sourceinfo=OpsiSourceInfo(self.url)
		self.LegisHeader(legisact)

		ParseBody(self,legisact)
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
		
		

# main running part
if __name__ == '__main__':
	if len(sys.argv) > 1:
		ldir = ["ukgpa%s.html" % x for x in sys.argv[1:]]
	else:
		ldir = os.listdir(actdirhtml)
		del ldir[0]	# removes file ".svn"
	
	# just run through and apply to all the files
	for i in range(0,len(ldir)):
		print "reading ", i, ldir[i]
		if ldir[i] in ['ukgpa1997c31.html','ukgpa1988c1.html']:
			print "***skipping***", ldir[i]
			continue
		print actdirhtml, ldir[i], os.path.join(actdirhtml, ldir[i])
		fin = open(os.path.join(actdirhtml, ldir[i]), "r")
		txt = fin.read()
		fin.close()

		act = Act(ldir[i], txt)
		patches.ActApplyPatches(act)

		# the parsing process
		#ActParseHead(act)
		try:
			lexact=act.Parse()
		except ParseError:
			print "+++Error occurred in file number %s" % i
			raise
		out = open(os.path.join(actdirxml, lexact.id+".xml"), "w")
		out.write(lexact.xml()) 
