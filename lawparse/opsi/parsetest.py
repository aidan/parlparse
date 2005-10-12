#!/usr/bin/python

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