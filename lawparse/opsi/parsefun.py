# parsefun.py - utility functions for parser

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

import re
import sys

#def path2opt(p): 	# converts a path into options suitable for xml
#	a=''
#	for x in range(0,len(p)):
#		a=a + (' %s="%s%s%s"' % ('s' * (x+1),p[x][2],p[x][0],p[x][3]))
#	return a
#
#def pathsearch(p,item): # searches a path for a matching item type
#	#print "***pathsearch entry point****",p,len(p),item
#	for x in range(0,len(p)):
#		if p[x][1]==item[1] and p[x][2]==item[2] and p[x][3]==item[3]:
#			#print "***pathsearch exit point 1***",p,item,x
#			return x
#
#	#print "***pathsearch exit point 2***",p,item,x
#	return len(p)
#
#def makeitem(s):
#	m=re.match('([1-9][0-9]*)',s)
#	if m:
#		return (m.group(1),'numeric','','')
#
#	m=re.match('\(([a-z])\)',s)
#	if m:
#		return (m.group(1),'lalpha','(',')')
#
#	m=re.match('\(([1-9][0-9]*)\)',s)
#	if m:
#		return (m.group(1),'numeric','(',')')
#
#	m=re.match('\(([ivxdlcm]+)\)',s)
#	if m:
#		return (m.group(1),'lroman','(',')')
#
#	print "****Unknown enumeration item (%s)" % s
#
#def pathinsert(path,m):
#	item=makeitem(m.group(1))			
#	n=pathsearch(path,item)
#	if n==len(path):
#		path.append(item)
#	else:
#		path[n]=item
#		for i in range(n+1,len(path)):
#			path.pop(n+1)
#		#path=path[:n+1]			
#	#leafoptions=path2opt(path)+partoption
#	#print "****",n,path,item,m.group(1),right[:32]
#

def gettext(right):
	m=re.search('<(?!a|/a|format|/format)',right)
	if m:
		s=right[:m.start()]
		rest=right[m.start():]
		m2=re.match('<font size=-4>(\S*)</font>',rest)
		if m2:
			s=s+'<fraction>'+m2.group(1)+'</fraction>'
			(one,rest)=gettext(rest[m2.end():])
			s=s+one
		return(s,rest)
	else:
		return(right,'')	

