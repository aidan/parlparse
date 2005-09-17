
import re
import sys

actname='acts/1988/41.html'
actfile=open(actname,'r')
act=actfile.read()

url=re.search('<url>(.*?)</url>',act).group(1)
chapno=re.search('<chapter_number>([1-9][0-9]*?)</chapter_number>',act).group(1)
year=re.search('<year>([1-9][0-9]*?)</year>',act).group(1)


def output(s,t, u=''):
	t=t + ' act="%sc%s"' % (year,chapno)
	if len(u)==0:
		print "<%s %s/>" % (s,t)
	else:
		print "<%s %s>%s</%s>" % (s,t,u,s)

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

	print "****Unknown enumeration item (%s)" % s

def pathinsert(path,m):
	item=makeitem(m.group(1))			
	n=pathsearch(path,item)
	if n==len(path):
		path.append(item)
	else:
		path[n]=item
		path=path[:n+1]			
	#leafoptions=path2opt(path)+partoption
	#print "****",n,path,item,m.group(1),right[:32]
	



def parseline(line):
	path=[]
	m=re.match('\s*<td width="20%">\s*<a name="mdiv(?:[1-9][0-9]*)"></a><br>\s*<font size="2">([ \w:.]*?)</font>\s*<br>\s*</td>\s*<td>((\s|\S)*?)</td>\s*</tr>',line)
	if m:
		leftitem=m.group(1)
		leftoption=' leftitem="%s"' % leftitem
	else:
		print "unrecognised line element [[[\n%s\n]]]:" % line
		print remain[:128]
		sys.exit()
	
	leafoptions=''
	rpos=0
	right=m.group(2)
	aftersectionflag=False

	while rpos < len(right):
		if len(leafoptions)>0:
			if re.match('(\s*<(?!a|/a)|&#151;)',right):
				output('leaf',leafoptions)
			else:
				m=re.search('<(?!a|/a)',right)
				if m:
					output('leaf',leafoptions,right[:m.start()])
					right=right[m.start():]
				else:
					output('leaf',leafoptions,right)
					right=''
					continue

		m=re.match('</ul>',right)
		if m:
			leafoptions=''
			right=right[m.end():]
			continue
			
		m=re.match('\s*$',right)
		if m:
			leafoptions=''
			right=right[m.end():]
			continue

# number matching

		m=re.match('\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9][0-9]*)\.</b>(&nbsp;&nbsp;&nbsp;&nbsp;)?</b>',right)
		if m:
			section=m.group(1)
			path=[(section,'numeric','','')]
			leafoptions=path2opt(path)+partoption
			right=right[m.end():]
			aftersectionflag=True
			continue

		#print "****",right[:16]
		m=re.match('&\#151;(\([1-9][0-9]*\))&nbsp;',right)
		if m:
			#item=makeitem(m.group(1))
			
			#n=pathsearch(path,item)
			#if n==len(path):
			#	path.append(item)
			#else:
			#	path[n]=item
			#	path=path[:n+1]
			
			leafoptions=path2opt(path)+partoption
			#print "****",n,path,item,m.group(1),right[:32]
			right=right[m.end():]
			continue
		

		m=re.match('\s*(?:<br>)*&nbsp;&nbsp;&nbsp;&nbsp;(\([1-9][0-9]*\))&nbsp;',right)
		if m:
			#print "***found:", m.group(1), path
			pathinsert(path,m)
			#item=makeitem(m.group(1))			
			#n=pathsearch(path,item)
			#if n==len(path):
			#	path.append(item)
			#else:
			#	path[n]=item
			#	path=path[:n+1]			
			leafoptions=path2opt(path)+partoption
			#print "****",n,path,item,m.group(1),right[:32]
			right=right[m.end():]
			continue


		m=re.match('\s*<ul>&nbsp;(\S*)&nbsp;',right)
		if m:
			#print "***found:", m.group(1), path
			pathinsert(path,m)
			#item=makeitem(m.group(1))
			#n=pathsearch(path,item)
			#if n==len(path):
			#	path.append(item)
			#else:
			#	path[n]=item
			#	path=path[:n+1]
			leafoptions=path2opt(path)+partoption
			#print "****",path,item,m.group(1),right[:32]
			right=right[m.end():]
			continue

		m=re.match('\s*<center>\s*(<table>[\S\s]*?<table>\s*<tr>)',right)
#\s*</center>',right)
		if m:
			output('tablespecial','',m.group(1))
			right=right[m.end():]
			continue

		m=re.match('<excision\s*/>',right)
		if m:
			right=right[m.end():]
			continue			
		else:
			print "unrecognised right line element [[[\n%s\n]]]:" % right
			print remain[:128]
			sys.exit()




print '<?xml version="1.0" encoding="UTF-8">'
print '<act'
print '        url="%s"' % url
print '        chapno="%s"' % chapno
print '        >\n'
print '<body>'

# start parsing here

start=re.search('<table width="95%" cellpadding="2">\s*(<p>)?(?i)',act)
if not start:
	print "Cannot find start of table"
	sys.exit()

remain=act[start.end():]
pos=0
startpart=False
part=''

while re.search('<center>\s*<table>[\s\S]*</table>\s*?</center>',remain):
	remain=re.sub('<center>\s*<table>[\s\S]*?</table>\s*</center>','<excision />',remain)


while pos < len(remain):
	m=re.match('\s*<tr valign="top">',remain)
	if m:
		lineend=re.search('</tr>',remain)
		line=remain[m.end():lineend.end()]
		lpos=0

		#check for centered heading
		m=re.match('\s*<td width="20%">&nbsp;</td>\s*<td>\s*(<br>)?\s*(<i>)?\s*<center>([a-zA-Z: ]*)</center>\s*(</i>)?\s*</td>',line)
		if m:
			#print m.group(2)
			heading=m.group(3)
			m1=re.match('P(?:ART|art) \s*([IVXLDCM]+)',heading)
			if m1:
				startpart=True
				part=m1.group(1)
				partno=part
				partoption=' part="%s"' % partno		
			else:
				if startpart:
					output('heading',
					  'type="part" n="%s"' % partno,
					  heading)
					startpart=False
				else:
					output('heading', 'type="heading" n="%s"' % heading)
		else:
			if startpart:
				output('heading', 'type="part" n="%s"' % partno)
			parseline(line)
		pos=lineend.end()
		remain=remain[pos:]
		continue
	else:
		print "unrecognised line:"
		print remain[:128]
		sys.exit()
	
