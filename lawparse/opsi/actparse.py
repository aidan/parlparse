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
		self.isquotation=False

	def ParseAsQuotation(self):
		pp=legis.Legis()
		if re.search('>"',self.txt):
			ActParseBody(self,pp)
		else:
			print "***warning, tried to parse as quotation without quotation marks"
			#print "***warning, unparseable quotation text", self.txt
		return pp

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
			self.headvalues[hcode] = isbn

		# remaining parameter found
		else:
			self.headvalues[hcode] = mline.group(1)

		# move on
		self.txt = self.txt[mline.end(0):]

	def Parse(self):
		ActParseHead(act)
		
		parsedact=legis.Act(self.year,0,self.chapter)
		ActParseBody(act,parsedact)
		return parsedact
	
	def QuotationAsFragment(self,n):
		qtext=self.quotations[n]
		fragment=QuotedActFragment(qtext)
		return fragment

# main running part
if __name__ == '__main__':
	# just run through and apply to all the files
	ldir = os.listdir(actdirhtml)
	del ldir[0]	# removes file ".svn"
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
