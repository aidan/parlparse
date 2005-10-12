# miscfun.py - where files are kept
 
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

import os
import sys

# change current directory to lawparse folder
current_dir = os.path.dirname(sys.argv[0]) or '.'
lawdata_dir = os.path.join(current_dir, '../../lawdata')
if not os.path.exists(lawdata_dir):
    print "lawdata path %s doesn't exist" % lawdata_dir
    sys.exit(1)
os.chdir(lawdata_dir)

# starting point for directories
actdir = "acts"
actdirhtml = os.path.join(actdir, "html")
actdirxml = os.path.join(actdir, "xml")
sidir = "si"
sidirhtml = os.path.join(sidir, "html")
sidirxml = os.path.join(sidir, "xml") 

if not os.path.isdir(actdir):
	os.mkdir(actdir)

if not os.path.isdir(sidir):
	os.mkdir(sidir)

if not os.path.isdir(actdirhtml):
	os.mkdir(actdirhtml)

if not os.path.isdir(actdirxml):
	os.mkdir(actdirxml)

if not os.path.isdir(sidirhtml):
	os.mkdir(sidirhtml)

if not os.path.isdir(sidirxml):
	os.mkdir(sidirxml)



