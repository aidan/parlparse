# Functions to assist the analyser in parsing acts

import re
import sys

def path2opt(p): 	# converts a path into options suitable for xml
	a=''
	for x in range(0,len(p)):
		a=a + (' %s="%s%s%s"' % ('s' * (x+1),p[x][2],p[x][0],p[x][3]))
	return a

def pathsearch(p,item): # searches a path for a matching item type
	#print "***pathsearch entry point****",p,len(p),item
	for x in range(0,len(p)):
		if p[x][1]==item[1] and p[x][2]==item[2] and p[x][3]==item[3]:
			#print "***pathsearch exit point 1***",p,item,x
			return x

	#print "***pathsearch exit point 2***",p,item,x
	return len(p)

def makeitem(s):
	m=re.match('([1-9][0-9]*)',s)
	if m:
		return (m.group(1),'numeric','','')

	m=re.match('\(([a-z])\)',s)
	if m:
		return (m.group(1),'lalpha','(',')')

	m=re.match('\(([1-9][0-9]*)\)',s)
	if m:
		return (m.group(1),'numeric','(',')')

	m=re.match('\(([ivxdlcm]+)\)',s)
	if m:
		return (m.group(1),'lroman','(',')')

	print "****Unknown enumeration item (%s)" % s

def pathinsert(path,m):
	item=makeitem(m.group(1))			
	n=pathsearch(path,item)
	if n==len(path):
		path.append(item)
	else:
		path[n]=item
		for i in range(n+1,len(path)):
			path.pop(n+1)
		#path=path[:n+1]			
	#leafoptions=path2opt(path)+partoption
	#print "****",n,path,item,m.group(1),right[:32]

def gettext(right):
	m=re.search('<(?!a|/a)',right)
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

