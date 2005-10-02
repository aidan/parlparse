
import re
import sys
from parsefun import *
import legis

formats=[('i','italic'),('b','bold')]

	
quotepatterns=[
		('<table cellpadding="8">\s*<tr>\s*<td width="10%"(?: valign="top")?>&nbsp;</td>\s*<td>&quot;([\s\S]*?)&quot;\s*</td>\s*(?:</tr>\s*|(?=<tr))</table>(?i)','simple'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="15%">\s*<br>([\s\S]*?)&quot;</td>\s*</tr>\s*</table>(?i)','withmargin'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="5%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;&quot;&nbsp;&nbsp;&nbsp;&nbsp;<b>([\s\S]*?)&quot;\s*</td>\s*</tr>\s*</table>(?i)','section'),
		('<table cellpadding="8">\s*<tr valign="top">\s*<td width="20%">&nbsp;</td>\s*<td>\s*<br><i>\s*<center>([\s\S]*?)</tr>\s*</table>(?i)','full'),
		('<table cellpadding="8">\s*<tr>\s*<td width="10%" valign="top">&nbsp;</td>\s*<td align="center">\s*<a name="sdiv1A">([\s\S]*?)</tr>\s*</table>(?i)','heading'),
		('(?=there shall be inserted&\#151;)([\s\S]*?)&quot;</td>\s*</tr>\s*</table>(?i)','error'),
		('(?<=<TR><TD valign=top>&nbsp;</TD><TD valign=top>)<TABLE>([\s\S]*?)</TABLE>\s*(?=</TD>\s*</TR>)(?i)','rightquote')]

tablepatterns1=[('<center>\s*<table>([\s\S]*?)</table>\s*?</center>','tableCentered')]

tablepatterns2=[
		('(?<=<TR><TD valign=top>&nbsp;</TD><TD valign=top>)\s*<table>\s*<TR><TD valign=top align=center colspan=2>&nbsp;<BR>TABLE([\s\S]*?)</TABLE>\s*(?=</TD>\s*</TR>)(?i)','simpletable'),
		('(?<=<TR><TD valign=top>&nbsp;</TD><TD valign=top align=center>)&nbsp;<BR>T<FONT size=-1>ABLE OF </FONT>R<FONT size=-1>ATES OF </FONT>T<FONT size=-1>AX</TD></TR>\s*<TR><TD></TD><TD valign=top>\s*<table border width=100%>([\s\S]*?)</table>\s*(?=</td>\s*</tr>)(?i)','taxtable1997c16'),
		('<TABLE cellpadding=10 border>([\s\S]*?)</table>(?i)','repealtable1'),
		('<table border>([\s\S]*?)</table>(?i)','repealtable2'),
		('<table[^>]*>([\s\S]*?)</table>(?i)','misctable')]
	

class ParseError(Exception):
	"""Exception class for parse errors"""
	pass

def deformat(s,count=0):
	for (a,b) in formats:
		s=re.sub('<%s>(?i)' % a,'<format charstyle="%s">' % b,s,count)
		s=re.sub('</%s>(?i)' % a,'</format>',s,count)
	s=re.sub('<img[^>]*>(?i)','',s)
	return s

def defont(s):
	s=re.sub('<font[^>]*>|</font>(?i)','',s)
	return s

def deamp(s):
	s=re.sub('&','&amp;',s)
	return s

# assumes no nested tables.

def RemoveTables(act, tablelist, patternlist, tabtype):
	n=0
	for (pat,pattype) in patternlist:
		while re.search(pat,act.txt):
			m=re.search(pat,act.txt)
			tablelist.append(m.group(1))
			quote='<%s n="%i" pattype="%s"/>' % (tabtype, 
				n,pattype)
			n=n+1
			act.txt=re.sub(pat,quote,act.txt)
			
			# Diagnostic
#			if pattype=='repealtable2':
#				print "***** diagnostic for repealtable2"
#				print act.txt[m.start()-32:m.end()+32]
#				print m.group(2)
#				print n
#

	print "****Found %i %s patterns" % (n, tabtype)
	#print act.txt
	i=0
	for t in tablelist:
		print "***** number:", i
		print t
		i=i+1
#	sys.exit()

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


# call this when we run across the start of a quote, pass it the leaf that
# we would have output, if it wasn't the start of a quotation.

def quotestart(locus,leaf):
	if locus.lex.quote:
		
		return leaf

	else:
		quote=legis.Quotation(True,locus)
		qlocus=legis.Locus(quote)
		leaf.relocate(qlocus) 
		quote.append(leaf)
		return quote		

def parseline(line,locus):
	#path=[]
	print "****Called parseline"
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
		raise ParseError, "unrecognised line element"

	aftersectionflag=False

	parseright(act,right,locus)


# parseright parses the right hand side, where there is a marginal note and something on its right.

def parseright(act,right,locus,margin=legis.Margin(),format=''):
	first=True

	while len(right) >0:
		if not first:
			margin=legis.Margin()
			first=False

		m=re.match('\s*<BR><a name="sch(\d+)pt(\d+)"></a>A<FONT size=-1>RTICLE\s*</FONT>(\d+)(?i)',right)
		if m:
			locus.addpart('article',m.group(3))
			leaf=legis.Division(locus,'article',m.group(3),margin)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue


		# Deleting some hanging material

		m=re.match('</ul>',right)
		if m:
			#leafoptions=''
			right=right[m.end():]
			continue
			
		m=re.match('(<BR>|&nbsp;|\s)*$(?i)',right)
		if m:
			#leafoptions=''
			right=right[m.end():]
			continue

		# Number Matching

		# These test attempt to match the normal ways in which
		# section and lower order numbers work

		# main section number

		m=re.match('\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;(?:<b>)?&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9]+)(\.)?(?:</b>)?(&nbsp;&nbsp;&nbsp;&nbsp;)?</b>',right)
		if m:
			#print "***matched section type I"
			section=m.group(1)
			locus.addenum(section)
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			#path=[(section,'numeric','','')]
			#leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True
			continue

		#alternative section, including whole locus

		m=re.match('\s*<B>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+[A-Z]*)"></a>(\d+[A-Z]*)\.</B> -\s(\(\d+\))',right)
		if m:
			print "***matched section type II"
			section=m.group(2)
			#path=[(section,'numeric','','')]
			#leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True
			locus.addenum(m.group(2))
			locus.addenum(m.group(3))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			continue

		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+[A-Z]*)"></a>(\d+[A-Z]*)\.\s*(?:-)?\s*(?=[^\d])',right)
		if m:
			print "***matched section type IIB"
			section=m.group(2)
			#path=[(section,'numeric','','')]
			#leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			continue

		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;(\d+[A-Z]*(?:\.)?)\s*-\s*(\(\d+\))([\s\S]*?)<BR>&nbsp;(?i)',right)
		if m:
			locus.addenum(m.group(1))
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			leaf.content=m.group(3)
			right=right[m.end():]
			continue

		m=re.match('\s*<B>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+)"></a>(\d+)\.</B>',right)
		if m:
			print "***matched section type II - no subsection"
			section=m.group(2)
			path=[(section,'numeric','','')]
			#leafoptions=path2opt(path)+partoption+divoptions+leftoption
			right=right[m.end():]
			aftersectionflag=True

			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			continue
		

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9][0-9]*)(\.)?</b>',right)
		if m:
			#print "***matched section III?"
			right=right[m.end():]
			aftersectionflag=True

			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			continue

		m=re.match('(\s+\.)([^<]*)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

# Matching various patterns used for numbering

		# subsection numbers

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;((?:"|&quot;)?)(\(\d+[A-Z]*\))\s*',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			if len(m.group(1))>0:
				leaf=quotestart(locus,leaf)
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
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		
		# numbers like this (1), usually subsections		

		m=re.match('\s*(?:<br>)*&nbsp;&nbsp;&nbsp;&nbsp;(\([1-9][0-9]*\))&nbsp;',right)
		if m:
			#pathinsert(path,m)
			#leafoptions=path2opt(path)+partoption+divoptions
			locus.addenum(m.group(1))
			leaf=Legis.Leaf('provision',locus,margin)
			leaf.sourcerule='opsi:subsection1'
			right=right[m.end():]
			continue

		# usually lower level numbering like (a)

		m=re.match('\s*<UL>((?:"|&quot;)?)(\([a-z]+\))([\s\S]*?)</UL>(?i)',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			leaf.content=m.group(3)
			leaf.sourcerule='opsi:subsection2'

			if len(m.group(1))>0:
				leaf=quotestart(locus,leaf)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		# often used for lower level numbering in older acts		

		m=re.match('\s*<p>\s*<ul>(\([a-z]+\))(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			leaf.sourcerule='opsi:subsection3'
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		m=re.match('\s*<p>(\([a-z]+\))(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			leaf.sourcerule='opsi:subsetion4'
			locus.lex.append(leaf)
			right=right[m.end():]
			continue


		m=re.match('\s*<ul>&nbsp;(\(\S*\))&nbsp;(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		#lower level, roman numeral like (i) numbers in newer acts

		m=re.match('\s*(?:<UL>)?<UL><UL>(\([ivxlcdm]+\)\s*)([^<]*)(?:</UL>)*(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			leaf.content=m.group(2)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		# left over headings 

		m=re.match('\s*(?:<BR>)+([^<&]+)(?i)',right)
		if m:
			heading=m.group(1)
			lastleaf=locus.lex.last()
			if lastleaf.t=='division':
				lastleaf.content=heading
			else:
				leaf=legis.Heading(locus)
				leaf.content=heading
				locus.lex.append(leaf)

			right=right[m.end():]
			continue


		# unordered lists:
		m=re.match('\s*(<UL>)+([\s\S]*?)(?:&nbsp;)?</UL>(?i)',right)
		if m:
			l=(len(m.group(1))/2)
			leaf=legis.Leaf('item%i'% l,locus,margin)
			leaf.content=m.group(2)
			leaf.sourcerule='opsi:unordered list%i' % l
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		m=re.match('\s*<P>(?:<UL>)?([\s\S]*?)(?:\.|;)(?:</UL>)?(?=\s*<)(?i)',right)
		if m:
			leaf=legis.Leaf('item',locus,margin)
			leaf.content=m.group(1)
			leaf.sourcerule='opsi:paragraph'
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		# not sure what this is or where it occurs

		m=re.match('\s*<td width="10%" valign="top">&nbsp;</td>\s*<td>(\(\d+\))&nbsp;',right)
		if m:
			pathinsert(path,m)
			leafoptions=path2opt(path)+partoption+divoptions
			right=right[m.end():]
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			continue
		

# I found this in s.8 ICTA 1988, a bit yucky, but not exactly wrong. It seems 
# to occur elsewhere in the act.

		m=re.match('\s*<ul>([\s\S]*?)</ul>',right)
		if m:
			#output('leaf','type="text" format="hanging"',
			#	m.group(1))
			leaf=legis.Leaf('text',locus,margin)
			leaf.content=m.group(1)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;([\s\S]*?)(?:</UL></UL>|<BR>&nbsp;)',right)
		if m:
			leaf=legis.Leaf('text',locus,margin)
			leaf.content=m.group(1)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue

		# Some garbage, it might be necessary to take note of the
		# presence of this as signalling some kind of amendment
		# for the momemnt, its better to remove it.

		m=re.match('<a name="unknown"></a></B> <BR>&nbsp;',right)
		if m:
			right=right[m.end():]
			continue
			
		# Table references for freestanding tables

		m=re.match('\s*<tabular n="(\d+)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',right)
		if m:
			print "Handling table n=%s pattype=%s" % (m.group(1),
				m.group(2))
			tablehtml=act.tables[int(m.group(1))]
			tablehtml=re.sub('(<P>|<BR>|&nbsp;)+','',tablehtml)
			tablehtml=deformat(tablehtml)
			tablehtml=defont(tablehtml)
			tablehtml=deamp(tablehtml)	# will need more care
			print "*****tablehtml at %s:" % locus.xml()
			print tablehtml
			leaf=legis.Table(locus)
			leaf.sourcerule="opsi:puretable(%s)" % m.group(2)
			#rows=[re.findall('<td[^<]*>([\s\S]*?)</td>(?i)',x) for x in re.findall('<tr>([\s\S]*?)</tr>(?i)',tablehtml)]
			#print "****table rows:",rows
			leaf.rows=[legis.TableRow(re.findall('<td[^<]*>([\s\S]*?)</td>(?i)',x)) for x in re.findall('<tr>([\s\S]*?)</tr>(?i)',tablehtml)]
			locus.lex.append(leaf)

			right=right[m.end():]
			continue


		m=re.match('<I>Note:</I>(.*)(?i)',right)
		if m:
			leaf=legis.Leaf('note',locus,margin)
			locus.lex.append(leaf)
			right=right[m.end():]
			continue
	
# This should never match (since I hope all such occurances have alaredy been
# removed.)

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


		m=re.match('\s*<quotation n="(\d)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',right)
		if m:
			print "Handling quotation n=%s" % m.group(1)
			#sys.exit()
			if m.group(2)=="rightquote":
				qnumber=int(m.group(1))
				quotation=act.QuotationAsFragment(qnumber)
				pp=quotation.ParseAsQuotation()
				print "****parsed a quotation"
				print pp.xml()
				quote=legis.Quotation(True,locus)
				quote.extend(pp.content)
			else:
				quote=legis.Quotation(False,locus)
				leaf=legis.Leaf('table',locus,margin)
				leaf.sourcetype="opsi:obsolete table"
				leaf.content=act.quotations[int(m.group(1))]
				quote.append(leaf)
			
			locus.lex.append(quote)
			
			right=right[m.end():]
			continue

# Remove "whitespace" and garbage

		m=re.match('(<br>)+\s*',right)
		if m:
			right=right[m.end():]
			continue

		m=re.match('\s*<p>\s*$(?i)',right)
		if m:
			right=right[m.end():]
			continue


		m=re.match('\s*(</ul>)+(?i)',right)
		if m:
			right=right[m.end():]
			continue

		m=re.match('<FONT size=-1>([A-Z ]*)</FONT>$(?i)',right)
		if m:
			leaf=legis.Leaf('text',locus)
			leaf.content=m.group(1)
			leaf.sourcerule='opsi:EmphasizedText1'
			locus.lex.append(leaf)
			right=right[m.end():]
			continue


		m=re.match('<i>|<b>(?i)',right)
		if m:
			right=deformat(right,1)

		m=re.match('<(?!a|format)|&nbsp;',right)
		if m:
			print "unrecognised right line element [[[\n%s\n]]]:" % right
			print right[:256]
			raise ParseError, "unrecognised right line element"
		else:
			(t,right)=gettext(right)
			#output('leaf','type="text"',t)
			leaf=legis.Leaf('text',locus,margin)
			leaf.content=t
			locus.lex.append(leaf)			

# ParseBody should really be a method of act (why isn't it?)
# its second argument is something of class Legis (or subclass thereof)
# ActParseBody will fill it up with leaves generated from parsing the act's 
# text

def ParseBody(act,pp):
	locus=legis.Locus(pp)
	locus.division='main'

	act.txt=re.sub('\s*<hr[^>]*>(?i)','',act.txt)
	justhad3table=False

	RemoveTables(act, act.tables, tablepatterns1, 'tabular')	

	RemoveTables(act, act.quotations, quotepatterns, 'quotation')	

	RemoveTables(act, act.tables, tablepatterns2, 'tabular')

	# Main loop
	
	remain=act.txt

	while  0 < len(remain):

		# Headings
	
		# Heading: SCHEDULE 1

		m=re.match('\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;<BR><BR>&nbsp;\s*</TD>\s*<TD align=center valign=top>&nbsp;<BR>&nbsp;<BR>(?:<a name="(?:sch[^"]*)"></a>)?((?:"|&quot;)?)SCHEDULE( (\d+[A-Z]*))?<BR>&nbsp;</TD></TR>(?i)',remain)
		if m:
			if m.group(2):
				snumber=m.group(2)
			else:
				snumber=''
			print "++++ snumber=%s %s" % (snumber,type(snumber))
			locus.newdivision('schedule',snumber)
			leaf=legis.Division(locus,'schedule',snumber)
			if len(m.group(1))>0:
				leaf=quotestart(locus,leaf)
			pp.append(leaf)
			remain=remain[m.end():]
			continue

		# Heading: SCHEDULE

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center>&nbsp;<BR><BR>\s*<BR><BR><FONT SIZE=5>S C H E D U L E</FONT></TD></TR>\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;&nbsp;</TD>\s*<TD align=center valign=top>&nbsp;&nbsp;<a name="schunnumbered"></a><BR>&nbsp;</TD></TR>',remain)
		if m:
			snumber=''
			locus.newdivision('schedule',snumber)
			leaf=legis.Division(locus,'schedule',snumber)
			pp.append(leaf)
			remain=remain[m.end():]
			continue
			

		#if re.match('\s*',remain):
		#	print "****matched"

		# Heading: SCHEDULES

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center><FONT SIZE=5>S C H E D U L E S</FONT>\s*</TD></TR>(?i)',remain)
		if m:
			print "***** schedule marker"
			leaf=legis.Leaf('schedule marker',locus)
			leaf.content='schedules'
			pp.append(leaf)
			remain=remain[m.end():]
			continue

		# Heading: PART I	

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top><a name="([^"]*)"></a>(P<FONT size=-1>ART|C<FONT size=-1>HAPTER) </FONT>([IVXLDCM]+)</TD></TR>(?i)',remain)
		if m:
			if re.match('P',m.group(2)):
				locus.addpart('part',m.group(3))
				leaf=legis.Division(locus,'part',m.group(3))
			else:
				locus.addpart('chapter',m.group(3))
				leaf=legis.Division(locus,'chapter',m.group(3))
			pp.append(leaf)	
			remain=remain[m.end():]
			continue

		# Heading: PART I 


		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top>(?P<bold><b>)?P<FONT size=-1>ART </FONT>(?P<no>[IVXLDCM]+|\d+)(?(bold)</b>|\s*)</TD></TR>(?i)',remain)
		if m:
			locus.addpart('part',m.group('no'))
			leaf=legis.Division(locus,'part',m.group('no'))
			if m.group('bold'):
				leaf.sourcerule='opsi:PartHeadingBold1'
			else:
				leaf.sourcerule='opsi:PartHeading1'
			pp.append(leaf)	
			remain=remain[m.end():]
			continue
	

		# Italicised heading 1

		m=re.match('\s*<TR><TD valign=top>(?:&nbsp;|<IMG src="/img/amdt-col\.gif">)</TD><TD align=center><BR><(?P<style>I|B)>((?:"|&quot;)?)(.*?)</(?P=style)></TD></TR>(?i)',remain)
		if m:
			leaf=legis.Heading(locus)
			leaf.content=m.group(3)
			if m.group('style')=='B':
				leaf.sourcerule='opsi:HeadingBold1'
			else:
				leaf.sourcerule='opsi:HeadingItalic1'
			if len(m.group(2))>0:
				quotestart(locus,leaf)
			locus.lex.append(leaf)
			remain=remain[m.end():]
			continue
			# need to check there is no preceding heading


		# Italicised heading 2

		m=re.match('\s*<TR valign=top><TD colspan=2 align=center><br><I>([\s\S]*?)</I></TD></TR>(?i)',remain)
		if m:
			heading=m.group(1)
			lastleaf=pp.last()
			if lastleaf and lastleaf.t=='division':	
				lastleaf.content=heading
			else:
				leaf=legis.Heading(locus)
				leaf.content=heading
				leaf.sourcerule="opsi:HeadingItalic2"
				pp.append(leaf)

			remain=remain[m.end():]
			continue

		# Generic heading 1

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center(?: valign=top)?>((?:(?:[^<]*)<FONT size=-1>(?:[^<]*)</FONT>)*)([\s\S]*?)</TD></TR>(?i)',remain)
		if m:
			print "****heading"

			heading=re.sub('(<FONT[^>]*?>|</FONT>)(?i)','',m.group(1))
			nextheading=''

			if re.match('\s*<BR>',m.group(2)):
				nextheading=m.group(2)
			else:
				heading=heading+m.group(2)

			print heading

			lastleaf=pp.last()
			if lastleaf and lastleaf.t=='division':	
				lastleaf.content=heading
			else:
				leaf=legis.Heading(locus)
				leaf.content=heading
				pp.append(leaf)

			if nextheading:
				parseright(act,nextheading,locus)

			remain=remain[m.end():]
			continue

			
		
		# lines with marginal elements

		m=re.match('\s*<TR><TD valign=top><FONT size="?2"?>([\s\S]*?)</FONT></TD>\s*<td[^>]*>(.*?)</td></tr>(?i)',remain)
		if m:
			print "****Margin",m.group(1)[48:]
			parseright(act,m.group(2),locus,legis.Margin(deformat(m.group(1))))
			remain=remain[m.end():]
			continue
			
		# lines with empty margins, all we need to do is pass
		# them on to parseright

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD valign=top( align=center)?>([\s\S]*?)</TD>\s*</TR>(?i)',remain)
		if m:
			if m.group(1):
				format='center'
			else:
				format=''
			parseright(act,m.group(2),locus,legis.Margin(), format)
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD valign=top><IMG SRC="/img/amdt-col\.gif">\s*</TD>\s*<TD valign=top>([\s\S]*?(?i))</TD></TR>',remain)
		if m:
			parseright(act,m.group(1),locus,legis.Margin())
			remain=remain[m.end():]
			continue


		# This should be obsolete

		m=re.match('\s*(?:<p>)?\s*<tr(?: valign="top">|>(?=\s*<td width="(?:20%|10%)" valign="top">))([\s\S]*?)</tr>\s*(?:</p>)?(?i)',remain)
		if m:
			print "****oldmatch"
			sys.exit()
			lineend=m.end()
			line=m.group(1)
			lpos=0
	
			if startschedule:
		 		m=re.match('\s*<td width="20%" valign="top">([\s\S]*?)</td>\s*<td>&nbsp;</td>\s*(?i)',line)
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
			m=re.match('\s*<td width="20%">&nbsp;</td>\s*<td>\s*(<br>)?\s*(<i>)?\s*<center>((?:<a>|</a>|&#160;|[\s0-9a-zA-Z,\(\)\'\-\.: ])*)</center>\s*(</i>)?\s*</td>(?i)',line)
			if m:
				heading=m.group(3)
				m1=re.match('P(?:ART|art) \s*([IVXLDCM]+)',heading)
				if m1:
					#startpart=True
					#part=m1.group(1)
					#partno=part
					#partoption=' part="%s"' % partno
					
					locus.addpart('part',partno)
					leaf=legis.Division(locus,'part',partno)
					pp.append(leaf)	
				else:
					#if startpart:
					#	output('heading',
					#	  'type="part" n="%s"' % partno,
					#	  heading)
					#	startpart=False
					#else:
					#	output('heading', 'type="heading" n="%s"' % heading)
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

		# Sections numbers/"margin notes" in later acts
		m=re.match('\s*<TR><TD align=right valign=top><B><a name="\d+"></a>(\d+)</B>&nbsp;&nbsp;&nbsp;&nbsp;</TD><TD valign=top><B>([\s\S]*?)</B><BR>&nbsp;</TD></TR>',remain)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,legis.Margin(m.group(2)))
			leaf.sourcerule='opsi:section2'
			locus.lex.append(leaf)
			remain=remain[m.end():]
			continue

		# Remaining line matches 


	

		m=re.match('\s*<quotation n="(\d)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',remain)
		if m:
			print "Handling quotation n=%s" % m.group(1)
			sys.exit
			if m.group(2)=="rightquote":
				qnumber=int(m.group(1))
				quotation=act.QuotationAsFragment(qnumber)
				pp=quotation.ParseAsQuotation()
				print "****parsed a quotation"
				print pp.xml()
				quote=legis.Quotation(True,locus)
				quote.extend(pp.content)
			else:
				quote=legis.Quotation(False,locus)
				leaf=legis.Leaf('table',locus)
				leaf.sourcetype="opsi:obsolete table2"
				leaf.content=act.quotations[int(m.group(1))]
				quote.append(leaf)
			
			locus.lex.append(quote)

			remain=remain[m.end()]
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

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top></TD></TR>(?i)',remain)
		if m:
			remain=remain[m.end():]
			continue
	
		m=re.match('\s*<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>',remain)
		if m:
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col\.gif"></TD><TD valign=top>&nbsp;</TD></TR>(?i)',remain)
		if m:
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>(?=\s*<TR>)(?i)',remain)
		if m:
			remain=remain[m.end():]
			continue



		# a hanging text line (in later acts)
		m=re.match('\s*<TR><TD></TD><TD>([^<]*?)</TD>\s*</TR>',remain)
		if m:
			leaf=legis.Leaf('unnumbered text',locus)
			leaf.content=m.group(1)
			leaf.sourcetype="opsi:unnumbered1"
			pp.append(leaf)	
			remain=remain[m.end():]
			continue
			

		# Two ghastly abortions of lines (we didn't go to HTML
		# school clearly)

		m=re.match('\s*<TR><TD></TD><TD>([^<]*)(?=<TR>)(?i)',remain)
		if m:
			leaf=legis.Leaf('unnumbered text',locus)
			leaf.content=m.group(1)
			leaf.sourcetype="opsi:unnumbered2"
			pp.append(leaf)	
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD></TD><TD>([^<]*)</TR></TD>(?i)',remain)
		if m:
			leaf=legis.Leaf('unnumbered text',locus)
			leaf.content=m.group(1)
			leaf.sourcetype="opsi:unnumbered3"
			pp.append(leaf)	
			remain=remain[m.end():]
			continue
	
		# Yuk, the page trimming needs to be improved:
		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD><pageurl [^<]*>',remain)
		if m:
			remain=remain[m.end():]
			continue

		# also yuk
		m=re.match('\s*<BR>&nbsp;</TD></TR>(?i)',remain)
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
		elif	len(remain.strip())==0:
			remain=remain.strip()
			continue
		else:
			print "unrecognised line:"
			print remain[:350].strip()
			raise ParseError, "unrecognised line"

	