#!/usr/bin/python

# parsetest.py - parses every act that has already been parsed

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

import re
import sys
import os

import miscfun
actdirhtml = miscfun.actdirhtml
actdirxml = miscfun.actdirxml

import actparse


ldir = os.listdir(actdirxml)
del ldir[0]	# removes file ".svn"

ldir = [re.sub('ukpga(\d{4}c\d+).xml','ukgpa\g<1>.html',x) for x in ldir]

print ldir

actparse.ParseLoop(ldir)
