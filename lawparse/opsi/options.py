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
import copy

def check_list(option, opt, value):
	return value.split(',')

class ExtendedOption (optparse.Option):
	TYPES = optparse.Option.TYPES + ("list",)
	TYPE_CHECKER = copy.copy(optparse.Option.TYPE_CHECKER)
	TYPE_CHECKER["list"] = check_list

OpsiOptionParser=optparse.OptionParser(option_class=ExtendedOption)
OpsiOptionParser.add_option('-d', '--lawdatadir', dest='lawdata_dir', help='directory where data file directories are to be found'),
OpsiOptionParser.add_option('--actdir', dest="actdir"),
OpsiOptionParser.add_option('--actdirhtml', dest="actdirhtml"),
OpsiOptionParser.add_option('--actdirxml', dest="actdirxml"),
OpsiOptionParser.add_option('--sidir', dest="sidir"),
OpsiOptionParser.add_option('--sidirhtml', dest="sidirhtml"),
OpsiOptionParser.add_option('--sidirxml', dest="sidirxml"),
#
OpsiOptionParser.add_option('--consoledebug', dest="consoledebug"),
OpsiOptionParser.add_option('--filedebug', dest="filedebug"),
#
OpsiOptionParser.add_option('--skip', dest="skip", type="list", help='list of statutes to skip')

current_dir = os.path.dirname(sys.argv[0]) or '.'
lawdata_dir = os.path.join(current_dir, '../../lawdata')
actdir= 'acts'
sidir='si'

OpsiOptionParser.set_defaults(actdir=actdir, 
	sidir=sidir,
	actdirhtml=os.path.join(actdir, 'html'),
	actdirxml=os.path.join(actdir, 'xml'),
	sidirhtml=os.path.join(sidir, 'html'),
	sidirxml=os.path.join(sidir, 'xml'),
	consoledebug="WARNING", 
	filedebug="INFO", 
	debug="WARNING", 
	skip=[])

class ShortFormatter(logging.Formatter):
	def formatException(self,(exctype,value,traceback)):
		#e=traceback.format_exception_only(exctype,value)[0]
		#print "**** called ShortFormatter"
		s= "Exception type=%s value=%s" % (str(exctype),str(value))
		return s[:255]

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
			length='long'
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
		#sformatter=ShortFormatter()
		if self.length=='short':
			#print "setting ShortFormatter"
			handler.setFormatter(ShortFormatter())
			#handler.setFormatter(formatter)
		else:
			pass
			#print "setting Long Formatter"
			handler.setFormatter(formatter)
			#handler.setFormatter(sformatter)
