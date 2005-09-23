
import re
import sys
from parsefun import *
import legis
#from actparse import Act

#actname='acts/1988/41p.html'
#actname='acts/1988/1.html'
actname='acts/1988/15.html'
actfile=open(actname,'r')
act=actfile.read()

url=re.search('<url>(.*?)</url>',act).group(1)
chapno=re.search('<chapter_number>([1-9][0-9]*?)</chapter_number>',act).group(1)
year=re.search('<year>([1-9][0-9]*?)</year>',act).group(1)

def output(s,t, u=''):
#	return ''
	t=t + ' act="%sc%s"' % (year,chapno)
	if len(u)==0:
		print "####<%s %s/>" % (s,t)
	else:
		print "####<%s %s>%s</%s>" % (s,t,u,s)

def threetable(t):
	tcontents=''
	while len(t) > 0:
		#print "****",t[:256],tcontents
		s=re.match('\s+',t)
		if s:
			t=t[s.end():]
			continue

		m=re.match('\s*<tr>([\s\S]*?)</tr>',t)
		if not m:
			#print "****threetable failed linescan",t[:256],"****tcontents=",tcontents,"------failed linescan"		
			nn=0
		else:
			#print "rowmatch row=(%s)" % m.group(1)
			nn=0
		row=m.group(1)
		tcontents=tcontents+"<row"
		dcount=0
		while len(row) > 0:
			#print "****rowloop",dcount,row,"------rowloop"
			rs=re.match('\s+',row)
			if rs:
				#print "****null line",len(row),rs.end(),type(row),row,"----null line"
				row=row[rs.end():]
				#print "****rowlength=",len(row)
				continue

			dcount=dcount+1
			d=re.match('\s*<td rowspan="1" colspan="1">([\s\S]*?)</td>',row)
			if not d:
			 	#print "****threetable failed rowscan",tcontents,"---",t[:256],dcount,"rowlength=",len(row),row,"----- failed rowscan"
				nn=0
			tcontents=tcontents+(' c%i="%s"' % (dcount,d.group(1)))
			row=row[d.end():]
		tcontents=tcontents+"/>\n"
		t=t[m.end():]

	return tcontents


# parseline is a misnomer since all it does is deal with some situations
# where there is a margin note. Should be simplified.

def parseline(line,locus):
	path=[]
	#leaf=legis.Leaf('provision',locus)
	# extract left and right parts of the line

	m=re.match('\s*<td width="20%">\s*<a name="mdiv(?:[1-9][0-9]*)"></a><br>\s*<font size="2">([\s\S]*?)</font>\s*<br>\s*</td>\s*<td>((\s|\S)*?)</td>\s*$',line)

	m2=re.match('\s*<td width="(?:5%|10%|20%)"(?: valign="top")?>(?:<br>|&nbsp;|\s)*</td>\s*<td>([\s\S]*)</td>',line)
	if m:
		marginalium=m.group(1)
		#print "****marginalium:",marginalium
		leftoption=' margin="%s"' % marginalium
		right=m.group(2)
		leaf.margin=marginalium
	elif m2:
		right=m2.group(1)
		leftoption=''
	else:
		print "unrecognised line element [[[\n%s\n]]]:" % line
		print line[:128]
		#print quotations[:-1]
		sys.exit()
	
	leafoptions=''
	#rpos=0

	aftersectionflag=False

	parseright(act,right,locus)

def parseright(act,right,locus,margin=legis.Margin()):
	rpos=0
	leafoptions=''
	first=True


	while rpos < len(right):
		if not first:
			margin=legis.Margin()

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
			
		m=re.match('(<BR>|&nbsp;|\s)*$(?i)',right)
		if m:
			leafoptions=''
			right=right[m.end():]
			continue

		# number matching
		# main section number

		m=re.match('\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;(?:<b>)?&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9][0-9]*)(\.)?(?:</b>)?(&nbsp;&nbsp;&nbsp;&nbsp;)?</b>',right)
		if m:
			#print "***matched section type I"
			section=m.group(1)
			locus.addenum(section)
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			path=[(section,'numeric','','')]
			leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True
			continue

		#alternative section, including whole locus

		m=re.match('\s*<B>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+)"></a>(\d+)\.</B> -\s(\(\d+\))',right)
		if m:
			print "***matched section type II"
			section=m.group(2)
			path=[(section,'numeric','','')]
			#leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True
			locus.addenum(m.group(2))
			locus.addenum(m.group(3))
			leaf=legis.Leaf('provision',locus)
			locus.lex.append(leaf)
			continue
		

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9][0-9]*)(\.)?</b>',right)
		if m:
			#print "***matched section III?"
			section=m.group(1)
			leaf.addenum(section)
			path=[(section,'numeric','','')]
			leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True

			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus)
			locus.lex.append(leaf)
			continue

# Matching various patterns used for numbering

		# subsection numbers

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;(\(\d+\))\s*',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue


		m=re.match('&\#151;(\([1-9][0-9]*\))&nbsp;',right)
		if m:
			#print "****match",right[:16]
			pathinsert(path,m)
			leafoptions=path2opt(path)+partoption+divoptions
			#leaf.addenum(m.group(1))
			#
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		
		# numbers like this (1), usually subsections		

		m=re.match('\s*(?:<br>)*&nbsp;&nbsp;&nbsp;&nbsp;(\([1-9][0-9]*\))&nbsp;',right)
		if m:
			pathinsert(path,m)
			leafoptions=path2opt(path)+partoption+divoptions
			right=right[m.end():]
			continue

		# usually lower level numbering like (a)

		m=re.match('\s*<ul>&nbsp;(\S*)&nbsp;',right)
		if m:
			pathinsert(path,m)
			leafoptions=path2opt(path)+partoption+divoptions
			right=right[m.end():]
			continue

		# not sure what this is or where it occurs

		m=re.match('\s*<td width="10%" valign="top">&nbsp;</td>\s*<td>(\(\d+\))&nbsp;',right)
		if m:
			pathinsert(path,m)
			leafoptions=path2opt(path)+partoption+divoptions
			right=right[m.end():]
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus)
			locus.lex.append(leaf)
			continue
		

# I found this in s.8 ICTA 1988, a bit yucky, but not exactly wrong. It seems 
# to occur elsewhere in the act.

		m=re.match('\s*<ul>([\s\S]*?)</ul>',right)
		if m:
			#output('leaf','type="text" format="hanging"',
			#	m.group(1))
			right=right[m.end():]
			leaf=legis.Leaf('text',locus)
			leaf.content=m.group(1)
			locus.lex.append(leaf)
			continue
	
# This should never match (since I hope all such occurances have alaredy been
# removed.

		m=re.match('\s*<center>\s*(<table>[\S\s]*?<table>\s*<tr>)',
			right)

		if m:
			print "****Warning matched a table special"
			output('tablespecial','',m.group(1))
			right=right[m.end():]
			continue

# Parsing XML entities that have been inserted earlier by me

		m=re.match('<excision n="(\d*)"\s*/>',right)
		if m:
			right=right[m.end():]
			continue			


		m=re.match('<quotation n="(\d)*"\s+pattype="(\w*)"\s*/>',right)
		if m:
			#print "****found quotation"
			right=right[m.end():]
			output('leaf','type="quotation"',act.quotations[int(m.group(1))])			
			leaf=legis.Leaf('quotation',locus)
			leaf.content=act.quotations[int(m.group(1))]
			locus.lex.append(leaf)
			continue

# Remove "whitespace"

		m=re.match('(<br>)+\s*',right)
		if m:
			right=right[m.end():]
			continue

		m=re.match('<',right)
		if m:
			print "unrecognised right line element [[[\n%s\n]]]:" % right
			print right[:128]
			sys.exit()
		else:
			(t,right)=gettext(right)
			#output('leaf','type="text"',t)
			leaf=legis.Leaf('text',locus)
			leaf.content=t
			locus.lex.append(leaf)			

#print '<?xml version="1.0" encoding="UTF-8">'
#print '<act'
#print '        url="%s"' % url
#print '        chapno="%s"' % chapno
#print '        >\n'
#print '<body>'

# start parsing here

def ActParseBody(act,pp):
	#start=act.NibbleHead('first','<table width="95%" cellpadding="2">\s*(<p>)?(?i)')
	#if not start:
	#	print "Cannot find start of table"
	#	sys.exit()
	
	locus=legis.Locus(pp)


	remain=act.txt#[start.end():]
	pos=0
	startpart=False
	startschedule=False
	justhad3table=False
	schedoptions=''
	
	part=''		# part subdivisions of acts, etc
	chapter=''	# chapter subdivisions of acts, etc
	division='main'	# division of the act (i.e. main part or schedule number)
	
	partoption=''
	divoptions=' division="main"'
	
	# Remove troublesome tables
	#
	
	tables=[]
	n=0
	tablepat='<center>\s*<table>[\s\S]*?</table>\s*?</center>'
	while re.search(tablepat,remain):
		m=re.search(tablepat,remain)
		tables.append(m.group())
		#tablebody='<excision n="%s" />' % n
		tablebody=''
		n=n+1
		remain=re.sub(tablepat,tablebody,remain)
	
	
	# displayed quotation processing
	
	quotations=[]
	n=0
	
	#print "****removing quotations"
	
	quotepatterns=[
		('<table cellpadding="8">\s*<tr>\s*<td width="10%"(?: valign="top")?>&nbsp;</td>\s*<td>&quot;([\s\S]*?)&quot;\s*</td>\s*(?:</tr>\s*|(?=<tr))</table>','simple'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="15%">\s*<br>([\s\S]*?)&quot;</td>\s*</tr>\s*</table>','withmargin'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="5%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&nbsp;&nbsp;&nbsp;&nbsp;<b>([\s\S]*?)&quot;\s*</td>\s*</tr>\s*</table>','section'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="20%">&nbsp;</td>\s*<td>\s*<br><i>\s*<center>([\s\S]*?)</tr>\s*</table>','full'),
		('<table cellpadding="8">\s*<tr>\s*<td width="10%" valign="top">&nbsp;</td>\s*<td align="center">\s*<a name="sdiv1A">([\s\S]*?)</tr>\s*</table>','heading'),
		('(?=there shall be inserted&\#151;)([\s\S]*?)&quot;</td>\s*</tr>\s*</table>','error'),
		('(?<=<TR><TD valign=top>&nbsp;</TD><TD valign=top>)<TABLE>([\s\S]*)</TABLE>(?=</TD></TR>)(?i)','rightquote')]
	
	#rquotepat='<table cellpadding="8">\s*<tr>\s*<td width="10%"(?: valign="top")?>&nbsp;</td>\s*<td>&quot;([\s\S]*?)&quot;\s*</td>\s*(?:</tr>\s*|(?=<tr))</table>'
	
	#mquotepat='<table cellpadding="8">\s*<tr valign="top">\s*<td width="15%">\s*<br>([\s\S]*?)&quot;</td>\s*</tr>\s*</table>'
	
	print re.search('(?<=<TR><TD valign=top>&nbsp;</TD><TD valign=top>)<TABLE>[\s\S]*</TABLE>(?=</TD></TR>)(?i)',remain)
	
	for (quotepat,pattype) in quotepatterns:
		while re.search(quotepat,remain):
			m=re.search(quotepat,remain)
			act.quotations.append(m.group(1))
			quote='<quotation n="%i" pattype="%s"/>' % (n,pattype)
			n=n+1
			#print pattype, type(pattype)
			#
			#print n,quotepat,quote,m.start(),m.end(),len(remain),remain[:128]
			#	sys.exit()
			remain=re.sub(quotepat,quote,remain)
	print "****Found %i quotation patterns" % n
	#print quotations
	
	# Main loop
	
	while pos < len(remain):
		m=re.match('\s*<TR><TD valign=top><FONT size="?2"?>([^<]*)</FONT></TD>\s*<td[^>]*>(.*?)</td></tr>(?i)',remain)
		if m:
			parseright(act,m.group(2),locus,legis.Margin(m.group(1)))
			#print "****New match of [[%s###%s]]" % (m.group(1),m.group(2))
			remain=remain[m.end():]
			continue
			#sys.exit()

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD valign=top>([\s\S]*?)</TD>\s*</TR>(?i)',remain)
		if m:
			parseright(act,m.group(1),locus,legis.Margin())
			remain=remain[m.end():]
			continue



		m=re.match('\s*(?:<p>)?\s*<tr(?: valign="top">|>(?=\s*<td width="(?:20%|10%)" valign="top">))([\s\S]*?)</tr>\s*(?:</p>)?',remain)
		if m:
			lineend=m.end()
			line=m.group(1)
			lpos=0
	
			if startschedule:
		 		m=re.match('\s*<td width="20%" valign="top">([\s\S]*?)</td>\s*<td>&nbsp;</td>\s*',line)
				startschedule=False
				if m:
					marginalium=m.group(1)
					marginopts=' margin="%s"' % marginalium
					output('heading',schedoptions+marginopts)
					remain=remain[lineend:]
					schedoptions=''
					continue
				else:
					print "++++Warning: no margin note with schedule"
					output('heading',schedoptions)
					schedoptions=''
	
			#check for centered heading
			m=re.match('\s*<td width="20%">&nbsp;</td>\s*<td>\s*(<br>)?\s*(<i>)?\s*<center>((?:<a>|</a>|&#160;|[\s0-9a-zA-Z,\(\)\'\-\.: ])*)</center>\s*(</i>)?\s*</td>',line)
			if m:
				heading=m.group(3)
				m1=re.match('P(?:ART|art) \s*([IVXLDCM]+)',heading)
				if m1:
					startpart=True
					part=m1.group(1)
					partno=part
					partoption=' part="%s"' % partno
					
					locus.addpart('part',partno)
					leaf=legis.Division(locus,'part',partno)
					pp.append(leaf)	
				else:
					if startpart:
						output('heading',
						  'type="part" n="%s"' % partno,
						  heading)
						startpart=False
					else:
						output('heading', 'type="heading" n="%s"' % heading)
					lastleaf=pp.last()
					if leastleaf.t=='division':
						leastleaf.content=heading
					else:
						leaf=legis.Heading(locus)
						pp.append(leaf)

				remain=remain[lineend:]
				continue
	
	
			m=re.match('\s*<td width="20%" valign="top">&nbsp;</td>\s*<td align="center">\s*<br><br>\s*<font size="4">SCHEDULES</font>\s*<br>\s*</td>\s*',line)		
			if m:
				output('heading', 'type="schedules"')
				remain=remain[lineend:]
				continue
	
			m=re.match('\s*<td width="20%" valign="top">\s*<br>&nbsp;</td>\s*<td align="center">\s*<br><a name="sdiv(\d+)"></a>SCHEDULE (\d+)</td>\s*',line)	
			if m:
				startschedule=True
				if not m.group(1)==m.group(2):
					print "++++insignificant error, schedule and sdiv number do not match at schedule %s" % m.group(2)
			
				division=m.group(2)
				#marginalium=m.group(3)
				divoptions=' division="%s"' % division
				schedoptions='type="schedule" n="%s"' % (m.group(2))
				#output('heading', )
				remain=remain[lineend:]
				continue
		
			m=re.match('\s*<td width="20%" valign="top">&nbsp;</td>\s*<td align="center">([\s\S]*?)</td>',line)
			if m:
				heading=m.group(1)
				output('heading', 'type="heading" n="%s"' % heading)
				remain=remain[lineend:]
				continue
	
			else:
				if startpart:
					output('heading', 'type="part" n="%s"' % partno)
				parseline(line,locus)
	
	
			remain=remain[lineend:]
			continue
	
		m=re.match('\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td>([\s\S]*?)</td>\s*</tr>',remain)
		if m and justhad3table:
			output('leaf', 'type="tablecomment"', m.group(1))
			remain=remain[m.end()]
			justhad3table=False
			continue

		m=re.match('\s*<TR><TD colspan=2>\s*</TD></TR>(?i)',remain)
		if m:
			remain=remain[m.end():]
			continue
	
		m=re.match('\s*<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>',remain)
		if m:
			remain=remain[m.end():]
			continue
	
		m=re.match('<tr>\s*<td width="20%">&nbsp;</td>\s*<td>\s*<br><br>\s*<table cols="c3" border="1"><tfoot><tr>\s*<td rowspan="1" colspan="1">\s*</td>\s*</tr>\s*</tfoot>\s*<tbody>([\s\S]*?)</tbody>\s*</table>\s*<br><br>\s*</td>\s*</tr>',remain)
		if m:
			#print "***** 3table found"
			tcontents=threetable(m.group(1))
			output("3table",partoption+divoptions,tcontents) #need path options too
			remain=remain[m.end():]
			justhad3table=True
			continue
	
		elif 	re.match('\s*</p>\s*<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>',remain):
			lineend=re.match('\s*</p>\s*<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>',remain)
			pos=lineend.end()
			remain=remain[pos:]
			#remain=remain[lineend:]
			continue
		elif	re.match('\s*<tr>\s*<td valign="top">&nbsp;</td>\s*(?=<tr)',remain):
			lineend=re.match('\s*<tr>\s*<td valign="top">&nbsp;</td>\s*(?=<tr)',remain)
			pos=lineend.end()
			remain=remain[pos:]
			#remain=remain[lineend:]
			continue
		else:
			print "unrecognised line:"
			print remain[:128]
			sys.exit()

	