#!/usr/bin/python

# actparse.py - parses acts from HTML into XML files

# Copyright (C) 2005 Francis Davey, part of lawparse

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

import logging
import re
import sys
import getopt
import os
import miscfun
import optparse

class OpsiOptionParser(optparse.OptionParser):
	def __init__(self, *args):
		optparse.OptionParser.__init__(self, option_list=[
			optparse.make_option('-d', '--lawdatadir', dest='lawdata_dir'),
			optparse.make_option('--actdir', dest="actdir"),
			optparse.make_option('--actdirhtml', dest="actdirhtml"),
			optparse.make_option('--actdirxml', dest="actdirxml"),
			optparse.make_option('--sidir', dest="sidir"),
			optparse.make_option('--sidirhtml', dest="sidirhtml"),
			optparse.make_option('--sidirxml', dest="sidirxml"),
			], *args)
		current_dir = os.path.dirname(sys.argv[0]) or '.'
		lawdata_dir = os.path.join(current_dir, '../../lawdata')
		actdir= 'acts'
		sidir='si'
		self.set_defaults(actdir=actdir)
		self.set_defaults(sidir=sidir)
		self.set_defaults(actdirhtml=os.path.join(actdir, 'html'))
		self.set_defaults(actdirxml=os.path.join(actdir, 'xml'))
		self.set_defaults(sidirhtml=os.path.join(sidir, 'html'))
		self.set_defaults(sidirxml=os.path.join(sidir, 'xml'))

		

def parselist(l):
	return re.split(',',l)
	

class ShortFormatter(logging.Formatter):
	def formatException(self,(exctype,value,traceback)):
		#e=traceback.format_exception_only(exctype,value)[0]
		#print "**** called ShortFormatter"
		return "Exception %s" % str(exctype)


levelNames={}

for i in range(10,60,10):
	levelNames[logging.getLevelName(i)]=i

class Log:
	def __init__(self,level=logging.INFO,length='long'):
		self.level=level
		self.length=length

	def __str__(self):
		return "Log(%s,%s)" % (self.level, self.length)

	def getarg(string):
		l=re.split(',',string)
		if len(l)==1:
			level=levelNames[l[0]]
		else:
			level=levelNames[l[0]]
			length=l[1]


		#print string, level, length
		#sys.exit()

		return Log(level,length)

	getarg=staticmethod(getarg)

	def ConfigHandler(self,handler):
		handler.setLevel(self.level)
		formatter=logging.Formatter('%(name)-6s: %(levelname)-8s %(message)s')
		if self.length=='short':
			#print "setting ShortFormatter"
			handler.setFormatter(ShortFormatter())
			#handler.setFormatter(formatter)
		else:
			pass
			#print "setting Long Formatter"
			handler.setFormatter(formatter)

class Option:
	def __init__(self,name,description):
		self.name=name
		self.description=description
		self.type='null'

	def __str__(self):
		return "Option(%s,%s,%s)\n" % (self.type, self.name, self.description)

	def key(self):
		return self.name

class SimpleOption(Option):
	def __init__(self,name,description):
		Option.__init__(self,name,description)
		self.type='simple'
		
class ComplexOption(Option):
	def __init__(self,name,description,default,map):
		Option.__init__(self,name,description)
		self.type='complex'
		self.default=default
		self.map=map

	def __str__(self):
		return "Option(%s,%s,%s,%s)\n" % (self.type, self.name, self.description,self.default)


	def key(self):
		return self.name + '='


OptionDescriptionList=[ComplexOption('skip','Names of files to be skipped',['ukgpa1997c31.html','ukgpa1988c1.html','ukgpa1988c17.html'],lambda x:parselist(x)),
	ComplexOption('debug','',Log(logging.WARNING,'short'),lambda x:Log.getarg(x)),
	ComplexOption('consoledebug','',Log(logging.WARNING,'short'),lambda x:Log.getarg(x)),
	ComplexOption('filedebug','',Log(logging.INFO,'long'),lambda x:Log.getarg(x)),
	ComplexOption('start','Number of file in list of files at which to start',0,lambda x:int(x)),
	SimpleOption('stoponerror','Whether to continue processing if there is a parsing error, or whether to throw an exception'),
	SimpleOption('help','Displays this help message')]


class Options:
	def __init__(self):
		self.keylist=[]
		self.description={}
		self.options={}
		for opt in OptionDescriptionList:
			self.description[opt.name]=opt
			if opt.type=='complex':
				self.options[opt.name]=opt.default
			self.keylist.append(opt.key())

	def __str__(self):
		return "Options(%s;\n%s)" % (["%s: %s" % (x,self.description[x]) for x in self.description.keys()], ["%s: %s" % (x,self.options[x]) for x in self.options.keys()])

	def isset(self,name):
		return self.options.has_key(name)

	def value(self,name):
		return self.options[name]
 
	def usage(self):
		for (name,opt) in self.description:
			print "%s\t\t%s" % (name,opt.description)

	def ParseArguments(self):

		if len(sys.argv) > 1:
			opts, args = getopt.getopt(sys.argv[1:],"",self.keylist)
			#print opts, args
			for o, a in opts:
				o=re.sub('--','',o)
				if self.description[o].type=='complex':
					self.options[o]=self.description[o].map(a)
					#print o, self.options[o]
				elif o == "help":
					self.usage()
					sys.exit()
				else:
					self.usage()
					sys.exit()
		else:
			args=[]
	
		if len(args) > 0:
			ldir = ["ukgpa%s.html" % x for x in args]
		else:
			ldir = os.listdir(miscfun.actdirhtml)
			del ldir[0]	# removes file ".svn"
	
	
		return ldir	
