#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import os

import miscfun
actdirhtml = miscfun.actdirhtml

from parsehead import ActParseHead


# may grow into a class which handles much of this
class Act:
	def __init__(self, cname, txt):
		m = re.search("(\d{4})c(\d+).html$", cname)
		self.year = m.group(1)
		self.chapter = m.group(2)
		self.txt = txt
		self.headvalues = { }

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


# main running part
if __name__ == '__main__':
	# just run through and apply to all the files
	ldir = os.listdir(actdirhtml)
	for i in range(len(ldir)):
		print "reading ", i, ldir[i]
		fin = open(os.path.join(actdirhtml, ldir[i]), "r")
		txt = fin.read()
		fin.close()

		act = Act(ldir[i], txt)

		# the parsing process
		ActParseHead(act)



