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
from analyser import ActParseBody
import legis


# may grow into a class which handles much of this

class ActFragment:
	def __init__(self,txt):
		self.txt=txt
		self.quotations=[]
		self.tables=[]
		self.isquotation=False
		self.id='fragment'

	def ParseAsQuotation(self):
		locus=legis.Locus(self)
		quotation=legis.Quotation(True,locus)
		if re.search('>"',self.txt):
			ActParseBody(self,quotation)
		else:
			print "***warning, tried to parse as quotation without quotation marks"
			#print "***warning, unparseable quotation text", self.txt
		return quotation

class QuotedActFragment(ActFragment):
	def __init__(self,txt):
		ActFragment.__init__(self,txt)
		self.isquotation=True

class Act(ActFragment):
	def __init__(self, cname, txt):
		m = re.search("(\d{4})c(\d+).html$", cname)
		self.year = m.group(1)
		self.chapter = m.group(2)
		self.txt = txt
		self.headvalues = { }
		self.quotations=[]
		self.tables=[]
		self.isquotation=False

	def ShortID(self):
		return "ukgpa%sc%s" % (self.year, self.chapter)

	# function for pulling off regexps from the front of the text
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
		elif hcode == 'isbn':
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

	def Parse(self):
		ActParseHead(act)
		
		legisact=legis.Act(self.year,0,self.chapter)
		self.ActLegisHeader(legisact)
		legisact.sourceinfo.source='opsi'
		ActParseBody(act,legisact)
		return legisact
	
	def QuotationAsFragment(self,n):
		qtext=self.quotations[n]
		fragment=QuotedActFragment(qtext)
		fragment.id="fragment of %s" % self.ShortID()
		return fragment

	def ActLegisHeader(self,legisact):
		legisact.preamble.longtitle=self.headvalues['longtitle'][0]
		#print self.headvalues
		enact=self.headvalues['enact'][0]
		if enact:
			legisact.preamble.enactment=re.sub('(<B>|</B>|<FONT[^>]*>|</FONT>)(?i)','',enact)

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
		print actdirhtml, ldir[i], os.path.join(actdirhtml, ldir[i])
		fin = open(os.path.join(actdirhtml, ldir[i]), "r")
		txt = fin.read()
		fin.close()

		act = Act(ldir[i], txt)
		patches.ActApplyPatches(act)

		# the parsing process
		#ActParseHead(act)
		lexact=act.Parse()

		out = open(os.path.join(actdirxml, lexact.id+".xml"), "w")
		out.write(lexact.xml()) 
