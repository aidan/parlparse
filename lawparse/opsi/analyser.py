# analyser.py - bulk of the act parsing engine

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
import parsefun
import legis
import logging

formats=[('i','italic'),('b','bold')]

class UnhandledTagError(parsefun.ParseError):
	pass

class UnhandledEntityError(parsefun.ParseError):
	pass

class ParseTableError(parsefun.ParseError):
	pass

class OpsiSourceRule(legis.SourceRule):
	def __init__(self,name):
		legis.SourceRule.__init__(self,'opsi',name)

def deformat(s,count=0):
	"""Remove italic and bold tags and replace with <format>.

	Image tags are also removed altogether"""

	for (a,b) in formats:
		s=re.sub('<%s>(?i)' % a,'<hint:format charstyle="%s">' % b,s,count)
		s=re.sub('</%s>(?i)' % a,'</hint:format>',s,count)
	s=re.sub('<img[^>]*>(?i)','',s)
	return s

def defont(s):
	"""Remove all <font> tags"""

	s=re.sub('<font[^>]*>|</font>(?i)','',s)
	return s

def deamp(s):
	"""Change incidents of the ampersand to a &amp; entity"""

	s=re.sub('&','&amp;',s)
	return s

def checktext(string):
	m=re.search('<%s' % parsefun.EXCLTAG,string)
	if m:
		errstring="Unhandled Tag:\n%s####%s####%s" % (string[:m.start()],string[m.start():m.end()],string[m.end():])
		raise UnhandledTagError(errstring)

	m=re.search('&nbsp;',string)
	if m:
		raise UnhandledEntityError(string)


def AddText(locus,margin,string):
	"""Adds text to the current legislation.

	If the previous provision already has text as its content, then 
	the text should become part of that provision, otherwise 
	a new text leaf will need to be created.
	"""

	logger=logging.getLogger('')

	last=locus.lex.last()
	if last and last.t=='provision' and len(last.content)==0:
		logging.info("Text:%s" % string[:64])
		AddContent(last,string)
	else:
		leaf=legis.Leaf('text',locus,margin)
		AddContent(leaf,string)
		locus.lex.append(leaf)

def AddContent(leaf,string):
	"""Wrapper for adding content to a leaf

	Checks there are no disallowed tags or entities in the text that forms the content of
	the leaf. The presence of these will, in the first instance, signal the existance of 
	a parse error of some kind
	"""
	
	string=deformat(string)
	
	checktext(string)

	leaf.content=string


def AddTextLeaf(locus,margin,text):
	"""Adds a new text leaf to the current legislation."""

	checktext(text)

	leaf=legis.Text(locus,margin,text)
	locus.lex.append(leaf)

	
def AddHeading(locus,margin,string):
	"""Adds a heading to the current legislation.

	There may already have been a part division, which, if it has not content
	of its own, will be the parent of this heading. Otherwise the heading becomes
	a free-standing heading of its own.
	"""

	last=locus.lex.last()
	if last and last.t=='division' and len(last.content)==0:
		AddContent(last,string)
		#print "****Add Heading, added %s to previous division" % string
		#print last.xml()
		#print locus.lex.last().xml()
	else:
		leaf=legis.Heading(locus,margin)
		AddContent(leaf,string)
		locus.lex.append(leaf)




# assumes no nested tables.

def RemoveTables3(act, tablelist, patternlist, tabtype):
	logger=logging.getLogger('')
	n=0
	for (pat,pattype) in patternlist:
		#print "Pat=%s\n\npattype=%s\n\n" % (pat,pattype)
		while re.search(pat,act.txt):
			m=re.search(pat,act.txt)
			d={}
			for name in ['pre','post']:
				if m.groupdict().has_key(name):
					d[name]=m.group(name)
				else:
					d[name]=''
			
			store=m.expand('%s\\1%s' % (d['pre'],d['post']))
			
			tablelist.append(store)
			#print "****pattype=%s n=%s" % (pattype, n)
			if False: #n==60:
				print "++++pat=%s\n++++act.txt[:128]=%s" % (pat,act.txt[:128])
				print act.txt[m.start()-32:m.end()]
				print "--------------"
				print act.txt[m.start():m.end()]
				print "--------------"
				print act.txt[m.end():m.end()+32]

				sys.exit()
			quote='<%s n="%i" pattype="%s"/>' % (tabtype, 
				n,pattype)
			n=n+1
			act.txt=re.sub(pat,quote,act.txt,1)


			
			# Diagnostic
			s='rightquote'
			#if pattype==s:
				#print "***** diagnostic for %s mstart=%s mend=%s" % (s,m.start(),m.end())
				#print '****act.txt after substitution:'
				#print act.txt[m.start()-32:m.end()+32]
				#print '****m.groups():'
				#print m.groups()
				#print n


	logger.info("****Found %i %s patterns" % (n, tabtype))
	#print act.txt
	i=0
	for t in tablelist:
		#print "***** number:", i
		#print t[:32]
		i=i+1
#	sys.exit()

def PrepareQuote(locus,act,margin,qnumber,pattype):
	'''Handles <quotation and tags.

	Some tabular data is a quotation with the same format as an act and
	therefore requires parsing as an act.
	'''

	logger=logging.getLogger('')

	logger.info("(preparing quote) Handling quotation n=%s pattype=%s" % (qnumber,pattype))

	if pattype in ["rightquote",'simple','withmargin','full','withmargin2','heading','section','error']:
		logger.info("****parsing quotation %s" % qnumber)

		quotation=act.QuotationAsFragment(qnumber,locus)
		pp=quotation.ParseAsQuotation()
		logger.info("****parsed a quotation")
		logger.debug(locus.lex.xml())
		quote=legis.Quotation(True,locus)
		quote.extend(pp.content)
	else:
		quote=legis.Quotation(False,locus)
		leaf=legis.Leaf('table',locus,margin)
		leaf.sourcetype="opsi:obsolete table"
		AddContent(leaf,act.quotations[qnumber])
		quote.append(leaf)

	return quote

def MakeTableLeaf(act, locus, no, pattype):
	logger=logging.getLogger('')
	logger.info("Handling table n=%s pattype=%s" % (no, pattype))

	tablehtml=act.tables[int(no)]
	tablehtml=re.sub('(<P>|<BR>|&nbsp;)+','',tablehtml)
	tablehtml=deformat(tablehtml)
	tablehtml=defont(tablehtml)
	tablehtml=deamp(tablehtml)	# will need more care

	logger.info("*****tablehtml at %s:" % locus.xml())
	# print tablehtml

	leaf=legis.Table(locus)

	locus.lex.addsourcerule(OpsiSourceRule("puretable(%s)" % pattype))

	leaf.rows=[legis.TableRow(re.findall('<td[^<]*>([\s\S]*?)</td>(?i)',x)) for x in re.findall('<tr>([\s\S]*?)</tr>(?i)',tablehtml)]
	locus.lex.append(leaf)


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


# call this when we run across the start of a quote, pass it the leaf that
# we would have output, if it wasn't the start of a quotation.

def quotestart(locus,leaf,quotestatus,limit='none'):
	# if we are already inside a quotation, we don't try starting
	# another
	if locus.lex.quote:
		assert(quotestatus!='none') # must be in a quote
		return (locus,leaf,quotestatus)

	# if the quotation is "inline" we need to make a new quotation leaf,
	# and then start parsing inside the quotation. We also need to instruct
	# the parser to end the quote after the end of our current parse
	
	else:
		assert(quotestatus=='none') # must not be in a quote already
		quotestatus=limit

		quote=legis.Quotation(True,locus)
		qlocus=legis.Locus(quote)
		leaf.relocate(qlocus) 
		quote.append(leaf)

		return (qlocus,quote,quotestatus)		

def quoteend(locus):
	assert(locus.lex.quote)
		
	locus=locus.lex.locus
	return locus

def parseline(line,locus):
	#path=[]
	print "****Called parseline"
	sys.exit()
	#leaf=legis.Leaf('provision',locus)
	# extract left and right parts of the line


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
		raise parsefun.ParseError, "unrecognised line element [[[\n%s\n]]]:" % line

	aftersectionflag=False

	parseright(act,right,locus,quotestatus)


# parseright parses the right hand side, where there is a marginal note and something on its right.

def parseright(act,right,locus,quotestatus,margin=legis.Margin(),format=''):
	first=True
	trace=[]
	logger=logging.getLogger('')

	while len(right) >0:
		trace.append(right)
		logging.debug('Right=%s' % right)
		if not first:
			margin=legis.Margin()
			first=False

		m=re.match('\s*<hint:',right)
		if m:
			(this,right)=parsefun.gettext(right)
			AddText(locus,margin,this)
			continue	

		# Article 1

		m=re.match('\s*<BR><a name="sch(\d+)pt(\d+)"></a>A<FONT size=-1>RTICLE\s*</FONT>(\d+)(?i)',right)
		if m:
			locus.addpart('article',m.group(3))
			leaf=legis.HeadingDivision(locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('article'))

			right=right[m.end():]
			continue


		# Deleting some hanging material

		m=re.match('</ul>',right)
		if m:
			#leafoptions=''
			locus.lex.addsourcerule(OpsiSourceRule('HangingCloseUL'))
			right=right[m.end():]
			continue
			
		m=re.match('(<BR>|&nbsp;|\s)*$(?i)',right)
		if m:
			#leafoptions=''
			locus.lex.addsourcerule(OpsiSourceRule('WhiteSpaceEnd'))
			right=right[m.end():]
			continue

		# Number Matching

		# These test attempt to match the normal ways in which
		# section and lower order numbers work

		# main section number

		m=re.match('\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;(?:<b>)?("|&quot;)?&nbsp;&nbsp;&nbsp;&nbsp;<b>(\d+[A-Z]*(?:\.)?)\s*(?:</b>)*(&nbsp;&nbsp;&nbsp;&nbsp;(&#151;&nbsp;&nbsp;(\(\d+[A-Z]*\))&nbsp;)?)?(?:</b>)?(?i)',right)
		if m:
			locus.addenum(m.group(2))
			sourcerule='section1'
			if m.group(3) and m.group(4):
				locus.addenum(str(m.group(5)))
				sourcerule=sourcerule+'subsection1'
				#section1subsection1
			leaf=legis.Leaf('provision',locus,margin)
			if m.group(1):
				(locus,leaf,quotestatus)=quotestart(locus,leaf,'right')

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule(sourcerule))

			right=right[m.end():]
			continue

		#alternative section, including whole locus

		m=re.match('\s*<B>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+[A-Z]*)"></a>(\d+[A-Z]*)\.</B> -\s(\(\d+[A-Z]*\))',right)
		if m:
			locus.addenum(m.group(2))
			locus.addenum(m.group(3))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('section2A'))

			right=right[m.end():]
			continue

		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+[A-Z]*)"></a>(\d+[A-Z]*)\.\s*(?:-)?\s*(?=[^\d])',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('section2B'))

			right=right[m.end():]
			continue

		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;(\d+[A-Z]*(?:\.)?)\s*-\s*(\(\d+[A-Z]*\))([\s\S]*?)<BR>&nbsp;(?i)',right)
		if m:
			locus.addenum(m.group(1))
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			AddContent(leaf,m.group(3))
			locus.lex.addsourcerule(OpsiSourceRule('sectionsubsection1'))
			right=right[m.end():]
			continue

		m=re.match('\s*<B>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+[A-Z]*)"></a>(\d+[A-Z]*)\.</B>',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('sectionsubsection2'))
			right=right[m.end():]
			continue
		

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>([1-9][0-9]*)(\.)?</b>(?:&nbsp;&nbsp;&nbsp;&nbsp;)?',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('section6'))
			right=right[m.end():]
			continue

#		m=re.match('\s*&#151;<ul>&nbsp;\([a-z]+\)&nbsp;',right)
#		if m:
#			locus.addenum(m.group(1))
#			locus.lex.addsourcerule(OpsiSourceRule('subsection4B'))

#			right=right[m.end():]
#			continue


		m=re.match('\s*(\d+[A-Z]*\.)\s*([^<]*)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			AddContent(leaf,m.group(2))
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection5A'))
			right=right[m.end():]
			continue

# Matching various patterns used for numbering

		# subsection numbers

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;((?:"|&quot;)?)(\(\d+[A-Z]*\))(?:&nbsp;)*\s*',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)

			if len(m.group(1))>0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus,'right')

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection4'))

			right=right[m.end():]
			continue


		m=re.match('&\#151;(\([1-9][0-9]*[A-Z]*\))(?:&nbsp;)+',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection7'))
			right=right[m.end():]
			continue

		
		# numbers like this (1), usually subsections		

		m=re.match('\s*(?:<br>)*&nbsp;&nbsp;&nbsp;&nbsp;(\([1-9][0-9]*\))(?:&nbsp;)+',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection2C'))
			right=right[m.end():]
			continue


		# usually lower level numbering like (a)

		# It looks to me like there's an error here.

		m=re.match('\s*<UL>((?:"|&quot;)?)(\([a-z]+\))(?:&nbsp;)*([\s\S]*?)(?:</UL>)?(?i)',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			(text,rest)=parsefun.gettext(m.group(3))
			logging.debug("text,rest=%s,%s" % (text,rest))
			AddContent(leaf,text)

			if len(m.group(1))>0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus,'right')

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection2D'))

			if len(rest)>0:
				parseright(act,rest,locus,quotestatus,margin)

			right=right[m.end():]
			continue

		# often used for lower level numbering in older acts		

		m=re.match('\s*<p>\s*<ul>(\([a-z]+\))(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection3'))
			right=right[m.end():]
			continue

		m=re.match('\s*<p>(\([a-z]+\))(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection4'))
			right=right[m.end():]
			continue


		m=re.match('\s*<ul>&nbsp;(\(\S*\))&nbsp;(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection5B'))
			right=right[m.end():]
			continue

		#lower level, roman numeral like (i) numbers in newer acts

		m=re.match('\s*(?:<UL>)?<UL><UL>(\([ivxlcdm]+\)\s*)([^<]*)(?:</UL>)*(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			AddContent(leaf,m.group(2))
		
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('NumberDepth3'))
			right=right[m.end():]
			continue

		m=re.match('\s*&nbsp;(\([ivxlcdm]+)\)&nbsp;(?i)',right)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,margin)
			
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('NumberDepth4'))
		
			right=right[m.end():]
			continue


		# left over headings 

		m=re.match('\s*(?:<BR>)+([^<&]+)(?i)',right)
		if m:
			heading=m.group(1)
			AddHeading(locus,margin,heading)
			locus.lex.addsourcerule(OpsiSourceRule('HeadingMinor1'))			
			right=right[m.end():]
			continue


		# unordered lists:
		m=re.match('\s*(<UL>)+([\s\S]*?)(?:&nbsp;)?(?:<BR>|&nbsp;)*(?:</UL>)?%s(?i)' % parsefun.TEXTEND,right)
		if m:
			l=(len(m.group(1))/2)
			leaf=legis.Leaf('item%i'% l,locus,margin)
			AddContent(leaf,m.group(2))
		
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('opsi:unordered list%i' % l))
			right=right[m.end():]
			continue

		# This may now be too generic

		m=re.match('\s*<P>(?:<UL>)?([\s\S]*?)(?:<BR>|&nbsp;)*(?:</UL>)\s*(?=<(?!hint:|/hint:))(?=</p>)?(?i)',right)
		if m:
			leaf=legis.Leaf('item',locus,margin)
			(text,rest)=parsefun.gettext(m.group(1))

			AddContent(leaf,text)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('subsection2D'))

			if len(rest)>0:
				parseright(act,rest,locus,quotestatus,margin)
	
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('paragraph'))
			right=right[m.end():]
			continue

		# Very miscellaneous matchings

		# not sure what this is or where it occurs

		m=re.match('\s*((?:"|&quot;)?)(\(\d+[A-Z]*\))&nbsp;',right)
		if m:
			locus.addenum(m.group(2))
			leaf=legis.Leaf('provision',locus,margin)
			if len(m.group(1)) >0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus,'right')

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('NumberMisc1'))

			right=right[m.end():]
			continue
		

# I found this in s.8 ICTA 1988, a bit yucky, but not exactly wrong. It seems 
# to occur elsewhere in the act.

		m=re.match('\s*<ul>([\s\S]*?)</ul>',right)
		if m:
		
			AddText(locus,margin,m.group(1))
			locus.lex.addsourcerule(OpsiSourceRule('TextHanging1'))

			right=right[m.end():]
			continue

		m=re.match('&nbsp;&nbsp;&nbsp;&nbsp;([^<&]*?)(?:(?:</UL>)+|<BR>&nbsp;)(?i)',right)
		if m:

			AddText(locus,margin,m.group(1))
			locus.lex.addsourcerule(OpsiSourceRule('TextIndent1'))
			right=right[m.end():]
			continue

		# Some garbage, it might be necessary to take note of the
		# presence of this as signalling some kind of amendment
		# for the momemnt, its better to remove it.

		m=re.match('<a name="unknown"></a></B> <BR>&nbsp;',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('MiscUnknownAnchor'))
			right=right[m.end():]
			continue
			
		# Table references for freestanding tables

		m=re.match('\s*<tabular n="(\d+)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',right)
		if m:
			#raise Exception

			MakeTableLeaf(act,locus,m.group(1),m.group(2))
			locus.lex.addsourcerule(OpsiSourceRule('TableLeaf(%s)' % m.group(2)))
			right=right[m.end():]
			continue


		# A Note: under a table.
		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b></b>&nbsp;&nbsp;&nbsp;&nbsp;<i>Note:</i>([^\(<\&]*?)',right)
		if m:
			logger.debug("**** note under table")
			leaf=legis.Leaf('note',locus)
			AddContent(leaf,m.group(1))
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('NoteItalic1'))
			right=right[m.end():]
			continue
			

		m=re.match('<I>Note:</I>(.*)(?i)',right)
		if m:
			leaf=legis.Leaf('note',locus,margin)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('Note'))
			right=right[m.end():]
			continue
	
# This should never match (since I hope all such occurances have alaredy been
# removed.)

		m=re.match('\s*<center>\s*(<table>[\S\s]*?<table>\s*<tr>)',
			right)

		if m:
			logger.warning("****Warning matched a table special")
			sys.exit()
			output('tablespecial','',m.group(1))
			right=right[m.end():]
			continue

# Parsing XML entities that have been inserted earlier by me

		m=re.match('<excision n="(\d*)"\s*/>',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('Excision'))
			right=right[m.end():]
			continue			


		m=re.match('\s*(?:&#151;)?<quotation n="(\d)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',right)
		if m:
			quote=PrepareQuote(locus,act,margin,int(m.group(1)),m.group(2))
			
			locus.lex.append(quote)
			locus.lex.addsourcerule(OpsiSourceRule('Quotation(%s)' % m.group(2)))
			
			right=right[m.end():]
			continue


		m=re.match('\s*&nbsp;&nbsp;&nbsp;(?:&nbsp;)+(?=[^\d\(])([^<]*?)(?i)',right)
		if m:
			leaf=legis.Leaf('provision',locus,margin)
			locus.lex.append(leaf)
			AddContent(leaf,m.group(1))
			locus.lex.addsourcerule(OpsiSourceRule('section8'))
			right=right[m.end():]
			continue

		# these occur in the badly formatted schedule 5 of the
		# Merchant Shipping Act 1988, which may need attention.

		m=re.match('\s*&nbsp;&nbsp;&nbsp;&nbsp;([^<\(&]*?)(?i)',right)
		if m:
			logger.debug("****debug, MSA rule")
			if locus.lex.id=='ukpga1988c12':
				locus.resetpath()
				leaf=legis.Leaf('provision',locus,margin)
				locus.lex.append(leaf)
				right=right[m.end():]
				continue
			else:
				leaf=legis.Leaf('provision',locus,margin)
				locus.lex.append(leaf)
				AddContent(leaf,m.group(1))
				right=right[m.end():]
				continue			

			locus.lex.addsourcerule(OpsiSourceRule('TextHanging2'))

		m=re.match('\s*<p>',right)
		if m:
			right=right[m.end():]
			while len(right)>0:
				(first,right)=parsefun.gettext(right)
				AddTextLeaf(locus,margin,first)
				qmobj=re.match('(?:&#151;)?<quotation n="(\d)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',right)
				pmobj=re.match('</p>',right)
				if qmobj:
					quote=PrepareQuote(locus,act,margin,int(qmobj.group(1)),qmobj.group(2))
					locus.lex.append(quote)
					locus.lex.addsourcerule(OpsiSourceRule('ParQuote'))				
					right=right[qmobj.end():]
					continue
				elif pmobj:
					right=right[pmobj.end():]
					break
				break
			continue			

	# Remove "whitespace" and garbage

		m=re.match('(<br>)+\s*',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedBRMultiple'))
			right=right[m.end():]
			continue

		m=re.match('\s*<p>\s*$(?i)',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedParAtEnd1'))
			right=right[m.end():]
			continue

		m=re.match('\s*</p>(?i)',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedEndPar1'))
			right=right[m.end():]
			continue

		m=re.match('&#151;(?i)',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedEntity151'))
			right=right[m.end():]
			continue


		m=re.match('\s*(</ul>)+(?i)',right)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedULClose'))
			right=right[m.end():]
			continue

		m=re.match('<FONT size=-1>([A-Z ]*)</FONT>$(?i)',right)
		if m:
			AddText(locus,margin,m.group(1))

			locus.lex.addsourcerule(OpsiSourceRule('EmphasizedText1'))
			right=right[m.end():]
			continue


#		m=re.match('<i>|<b>(?i)',right)
#		if m:
#			right=deformat(right,1)

		m=re.match('%s|&nbsp;' % parsefun.TEXTEND,right)
		if m:
			print "unrecognised right line element [[[\n%s\n]]]:" % right
			print right[:256]
			print "****Trace:"
			tn=0
			for r in trace:
				print tn, r
				tn=tn+1
			raise parsefun.ParseError, "unrecognised right line element [[[\n%s\n]]]:" % right
		else:
			(t,right)=parsefun.gettext(right)
			#output('leaf','type="text"',t)
			
			AddText(locus,margin,t)

	else:
		if quotestatus=='right':
			locus=quoteend(locus)


# ParseBody should really be a method of act (why isn't it?)
# its second argument is something of class Legis (or subclass thereof)
# ActParseBody will fill it up with leaves generated from parsing the act's 
# text


def ParseBody(act,pp,quotestatus):
	locus=legis.Locus(pp)
	locus.division=legis.MainDivision()
	logger=logging.getLogger('')
	logger.info("Parsing %s", act.ShortID())

	act.Tidy(locus.lex.quote)		

	justhad3table=False

	# Main loop
	
	remain=act.txt

	while  0 < len(remain):

		#print "*******************************"
		#print locus.lex.xml()
		#print "*******************************"

		# <pageurl ....
		m=re.match('\s*<pageurl[^>]*?>',remain)
		if m:
			logger.info("**** page break")
			remain=remain[m.end():]
			continue

		# Remove various address of acts that use <a> tags.

		remain=re.sub('<a[^>]*>(\d+)\s*c\.&#160;(\d+)</a>?((?:\.)?)','''<hint:actref year="\\1" chapter="\\2">\\1 c.\\2\\3</hint:actref>''',remain)
		remain=re.sub('''S\.I\.&#160;<a[^>]*>(\d+)/(\d+)</a>((?:\.)?)''','''<hint:siref year="\\1" number="\\2">S.I.(?:&#160;)?\s*\\1/\\2\\3</hint:siref>''',remain)
		remain=re.sub('<a[^>]*>(\d+)\s*\(c\.&#160;(\d+)\)</a>?((?:\.)?)','''<hint:actref year="\\1" chapter="\\2">\\1 (c.\\2\\3)</hint:actref>''',remain)

		# Horrid special cases

		# section 14 of the Licensing Act 1988
		m=re.match('\s*<tr valign="top">\s*<td width="20%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>&nbsp;&nbsp;&nbsp;&nbsp;<b></b>&nbsp;&nbsp;&nbsp;&nbsp;</b>([\s\S]*?)(\(\d+\))&nbsp;([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
			leaf=legis.Leaf('provision',locus)
			AddContent(leaf,m.group(1))

			locus.addenum(m.group(2))
		
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('GhastlyHangingText1'))
			remain=remain[m.end():]
			continue

		# Headings
	
		# Heading: SCHEDULE 1

		m=re.match('\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;<BR><BR>&nbsp;\s*</TD>\s*<TD align=center valign=top>&nbsp;<BR>&nbsp;<BR>(?:<a name="(?:sch[^"]*)"></a>)?((?:"|&quot;)?)SCHEDULE( (\d+[A-Z]*))?<BR>&nbsp;</TD></TR>(?i)',remain)
		if m:
			if m.group(2):
				snumber=m.group(2)
			else:
				snumber=''
			#print "++++ snumber=%s %s" % (snumber,type(snumber))
			locus.newdivision(legis.Schedule(snumber))
			leaf=legis.HeadingDivision(locus)

			if len(m.group(1))>0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus)
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('HeadingScheduleNumbered1'))
			remain=remain[m.end():]
			continue

		# Heading: SCHEDULE

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center>&nbsp;<BR><BR>\s*<BR><BR><FONT SIZE=5>S C H E D U L E</FONT></TD></TR>\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;&nbsp;</TD>\s*<TD align=center valign=top>&nbsp;&nbsp;<a name="schunnumbered"></a><BR>&nbsp;</TD></TR>',remain)
		if m:
			snumber=''
			locus.newdivision(legis.Schedule())
			leaf=legis.HeadingDivision(locus)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('HeadingScheduleUnnumbered1'))
			remain=remain[m.end():]
			continue
			
		m=re.match('\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;<BR><BR>&nbsp;</TD>\s*<TD align=center valign=top>&nbsp;<BR>&nbsp;<BR>\s*<a name="schunnumbered"></a> <BR>&nbsp;</TD></TR>(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('StripBlankLineAnchor1'))
			remain=remain[m.end():]
			continue
			

		# Heading: SCHEDULES

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center><FONT SIZE=5>S C H E D U L E S</FONT>\s*</TD></TR>(?i)',remain)
		if m:
			logger.info("***** schedule marker")
			leaf=legis.Leaf('schedule marker',locus)
			AddContent(leaf,'schedules')
	
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('HeadingSchedulesDivision'))
			remain=remain[m.end():]
			continue

		# Heading: PART I	

		m=re.match('\s*<TR><TD valign=top>(?:&nbsp;|<IMG src="/img/amdt-col\.gif">)</TD>\s*<TD align=center valign=top>(<a name="([^"]*)"></a>)?((?:"|&quot;)?)(P<FONT size=-1>ART|C<FONT size=-1>HAPTER) </FONT>([A-Z]+)</TD></TR>(?i)',remain)
		if m:
			if re.match('P',m.group(4)):
				locus.addpart('part',m.group(5))
				leaf=legis.HeadingDivision(locus)
				sourcerule='opsi:HeadingPart1'
			else:
				locus.addpart('chapter',m.group(5))
				leaf=legis.HeadingDivision(locus)
				sourcerule='opsi:HeadingChapter1'

			if len(m.group(3))>0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus)

# come  back here
			locus.lex.append(leaf)
	
			remain=remain[m.end():]
			continue

		# Heading: PART I 


		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center valign=top>(?P<bold><b>)?P<FONT size=-1>ART </FONT>(?P<no>[IVXLDCM]+|\d+)(?(bold)</b>|\s*)</TD></TR>(?i)',remain)
		if m:
			locus.addpart('part',m.group('no'))
			leaf=legis.HeadingDivision(locus)
			if m.group('bold'):
				sourcerule='HeadingPart2Bold'
			else:
				sourcerule='HeadingPart2'

			locus.lex.append(leaf)	
			locus.lex.addsourcerule(OpsiSourceRule(sourcerule))
			remain=remain[m.end():]
			continue
	

		# Italicised heading 1

		m=re.match('\s*<TR><TD valign=top>(?:&nbsp;|<IMG src="/img/amdt-col\.gif">)</TD><TD align=center><BR><(?P<style>I|B)>((?:"|&quot;)?)(.*?)</(?P=style)></TD></TR>(?i)',remain)
		if m:
			leaf=legis.Heading(locus)
			heading=m.group(3)
			mh=re.search('\s*article\s*(\d+)',heading)
			if mh:
				locus.addpart('article',m.group(1))
			else:
				AddContent(leaf,heading)

			if m.group('style')=='B':
				sourcerule='HeadingBold1'
			else:
				sourcerule='HeadingItalic1'
			if len(m.group(2))>0:
				(locus,leaf,quotestatus)=quotestart(locus,leaf,quotestatus)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule(sourcerule))

			remain=remain[m.end():]
			continue
			# need to check there is no preceding heading


		# Italicised heading 2

		m=re.match('\s*<TR valign=top><TD colspan=2 align=center><br><I>([\s\S]*?)</I></TD></TR>(?i)',remain)
		if m:
			heading=m.group(1)
			AddHeading(locus,legis.Margin(),heading)

			locus.lex.addsourcerule(OpsiSourceRule('HeadingItalic2'))
			remain=remain[m.end():]
			continue

		# Heading, eg SCHEDULE, using FONT=5
		
		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center><FONT SIZE=5>([^<]*)</FONT></TD></TR>',remain)
		if m:
			if m.group(1)=='S C H E D U L E':
				snumber=''
				locus.newdivision(legis.Schedule(snumber))
				leaf=legis.HeadingDivision(locus)
				sourcerule="DivisionSchedule1"
			else:
				leaf=legis.Heading(locus)
				AddContent(leaf,m.group(1))
				sourcerule="HeadingLarge"

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule(sourcerule))
			remain=remain[m.end():]
			continue
		

		m=re.match('\s*(?:<p>)?\s*<tr valign="top">\s*<td width="20%">&nbsp;</td>\s*<td>\s*(<br>)*\s*(<i>)?\s*<center>([\s\S]*?)</center>\s*(</i>)?\s*</td>\s*</tr>(?i)',remain)
		if m:
			heading=m.group(3)
			m1=re.match('P(?:ART|art) \s*([IVXLDCM]+)',heading)
			if m1:
				partno=m1.group(1)
				locus.addpart('part',partno)
				leaf=legis.HeadingDivision(locus)
				locus.lex.append(leaf)	
				sourcerule='HeadingDivision1'
			else:
				AddHeading(locus,legis.Margin(),heading)
				sourcerule='Heading'

			locus.lex.addsourcerule(OpsiSourceRule(sourcerule))
			remain=remain[m.end():]
			continue


		# Anchor before heading

		m=re.match('\s*<TR><TD valign=top>&nbsp;<BR>&nbsp;<BR><BR>&nbsp;</TD>\s*<TD align=center valign=top>&nbsp;<BR>&nbsp;<BR><a name="[^"]*"></a><BR>&nbsp;</TD></TR>\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center>((?:(?:[^<]*)<FONT size=-1>(?:[^<]*)</FONT>)+)</TD></TR>',remain)
		if m:
			heading=defont(m.group(1))
			
			AddHeading(locus,legis.Margin(),heading)

			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('HeadingAnchor'))
			remain=remain[m.end():]
			continue

		# Generic heading 1

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>\s*<TD align=center(?: valign=top)?>((?:(?:[^<]*)<FONT size=-1>(?:[^<]*)</FONT>)*)([\s\S]*?)</TD></TR>(?i)',remain)
		if m:
			#print "****heading"

			heading=m.group(1)
			nextheading=''

			if re.match('\s*<BR>',m.group(2)):
				nextheading=m.group(2)
			else:
				heading=heading+m.group(2)

			# Can this be done away with??

			heading=defont(heading)

			lastleaf=locus.lex.last()
			if lastleaf and lastleaf.t=='division':	
				AddContent(lastleaf,heading)
			else:
				leaf=legis.Heading(locus)
				AddContent(leaf,heading)
			# Needs attention
			#	leaf.sourcerule='opsi:HeadingGeneric'
				locus.lex.append(leaf)

			if nextheading:
				parseright(act,nextheading,locus,quotestatus)

			remain=remain[m.end():]
			continue

			
		
		# lines with marginal elements

		
		# Margins found in some pre-1997 acts

		m=re.match('\s*<tr valign="top">\s*<td width="20%">\s*(?:<a name="mdiv(?:[1-9][0-9]*)"></a><br>)?\s*<font size="2">([\s\S]*?)</font>\s*<br>\s*</td>\s*<td>((\s|\S)*?)</td>\s*</tr>(?i)',remain)
		if m:
			parseright(act,m.group(2),locus,quotestatus,legis.Margin(deformat(m.group(1))))

			locus.lex.addsourcerule(OpsiSourceRule('LineMargin1'))

			remain=remain[m.end():]
			continue

		m=re.match('\s*<tr valign="top">\s*<td width="20%">\s*<a name="mdiv(?:[1-9][0-9]*)"></a><br>\s*</td>\s*<td>((\s|\S)*?)</td>\s*</tr>(?i)',remain)
		if m:
			parseright(act,m.group(1),locus,quotestatus,legis.Margin())

			locus.lex.addsourcerule(OpsiSourceRule('LineNoMargin1'))

			remain=remain[m.end():]
			continue



		m=re.match('\s*<TR><TD valign=top><FONT size="?2"?>([\s\S]*?)</FONT></TD>\s*<td[^>]*>(.*?)</td></tr>(?i)',remain)
		if m:
			#print "****Margin",m.group(1)[48:]
			parseright(act,m.group(2),locus,quotestatus,legis.Margin(deformat(m.group(1))))
			remain=remain[m.end():]
			continue
			
		# lines with empty margins, all we need to do is pass
		# them on to parseright

		m=re.match('\s*<TR><TD(?: valign=top)?>(?:&nbsp;)?</TD>\s*<TD valign=top( align=center)?>([\s\S]*?)</TD>\s*</TR>(?i)',remain)
		if m:
			if m.group(1):
				format='center'
			else:
				format=''
			parseright(act,m.group(2),locus,quotestatus,legis.Margin(), format)
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD valign=top><IMG SRC="/img/amdt-col\.gif">\s*</TD>\s*<TD valign=top>([\s\S]*?(?i))</TD></TR>',remain)
		if m:
			parseright(act,m.group(1),locus,quotestatus,legis.Margin())
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD width=120 align=center valign=top><IMG SRC="/img/amdt-col\.gif">\s*</TD>\s*<TD valign=top>([\s\S]*?(?i))</TD></TR>',remain)
		if m:
			parseright(act,m.group(1),locus,quotestatus,legis.Margin())
			remain=remain[m.end():]
			continue

		# empty lines
		m=re.match('\s*<TR><TD valign=top>(<BR>|&nbsp;)*</TD></TR>(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('BlankLine1'))
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD valign=top>(<BR>|&nbsp;)*</TD><TD valign=top>(\s|<BR>|&nbsp;)*</TD></TR>',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('BlankLine2'))
			remain=remain[m.end():]
			continue

		# This should be obsolete

		m=re.match('\s*(?:<p>)?\s*<tr(?: valign="top">|>(?=\s*<td width="(?:20%|10%)" valign="top">))([\s\S]*?)</td>\s*<td>([\s\S]*?)</td></tr>\s*(?:</p>)?(?i)',remain)
		if m:
			logger.warning("****oldmatch")
			raise parsefun.ParseError
			#sys.exit()
#			#sys.exit()
#			#lineend=m.end()
#			#line=m.group(1)
#			#lpos=0
#	
			parseright(act,m.group(1),locus)
			locus.lex.addsourcerule(OpsiSourceRule('ObsoleteLine'))
			remain=remain[m.end():]
			continue
#
		# Detects marginal notes after the bottom of schedule openings
		m=re.match('\s*<tr>\s*<td width="20%" valign="top">([^<]*?)</td>\s*<td>&nbsp;</td>\s*</tr>(?i)',remain)
		if m:
			margin=legis.Margin(m.group(1))
			if locus.lex.last().t=='division':
				locus.lex.last().margin=margin
			else:
				logger.warning("**** inexplicable marginal note to empty right hand side\n%s\n%s" % (locus.text(),locus.lex.last().xml()))

			remain=remain[m.end():]
			continue
	
		#check for centered heading

		m=re.match('\s*<tr>\s*<td width="20%" valign="top">&nbsp;</td>\s*<td align="center">\s*<br><br>\s*<font size="4">SCHEDULES</font>\s*<br>\s*</td>\s*</tr>(?i)',remain)		
		if m:
			leaf=legis.Heading(locus)
			AddContent(leaf,'schedules')
			# do we want another kind of division leaf?
			# this is an awkward heading [misfeature]
			locus.lex.append(leaf)
		
			remain=remain[m.end():]
			continue
		
		m=re.match('\s*<tr>\s*<td width="20%" valign="top">\s*<br>&nbsp;</td>\s*<td align="center">\s*<br><a name="sdiv(\d+)"></a>SCHEDULE (\d+)</td>\s*</tr>',remain)	
		if m:
			div=legis.Schedule(m.group(1))
			locus.newdivision(div)
			leaf=legis.HeadingDivision(locus)
			locus.lex.append(leaf)
			if not m.group(1)==m.group(2):
				logger.warning("++++insignificant error, schedule and sdiv number do not match at schedule %s" % m.group(2))
		
			remain=remain[m.end():]
			continue

		#print "****Checking for single schedule"

		m=re.match('\s*<tr>\s*<td width="20%" valign="top">\s*<br>&nbsp;</td>\s*<td align="center">\s*<br><a name="sdivsched"></a>SCHEDULE</td>\s*</tr>(?i)',remain)	
		if m:
			logger.info("****schedule detected")
			div=legis.Schedule()
			locus.newdivision(div)
			leaf=legis.HeadingDivision(locus)
			#leaf.sourcerule="opsi:HeadingScheduleUnnumbered2"
			locus.lex.addsourcerule(OpsiSourceRule('HeadingScheduleUnnumbered2'))
			locus.lex.append(leaf)
					
			remain=remain[m.end():]
			continue

		
		m=re.match('\s*<tr>\s*<td width="20%" valign="top">&nbsp;</td>\s*<td align="center">([\s\S]*?)</td>\s*</tr>',remain)
		if m:
			AddHeading(locus,legis.Margin(),m.group(1))
			#print "***********************************"
			#print locus.lex.xml()
			#print "***********************************"
			#heading=m.group(1)
			#output('heading', 'type="heading" n="%s"' % heading)
			remain=remain[m.end():]
			continue


		# Section numbers (whole line)
		m=re.match('\s*<tr valign="top">\s*<td width="20%">\s*<a name="[^"]*?"></a><br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;<b>&nbsp;&nbsp;&nbsp;&nbsp;<b>(\d+\.)</b>&nbsp;&nbsp;&nbsp;&nbsp;</b>([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus)			
		
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('section4'))
			parseright(act,m.group(2),locus,quotestatus)
			remain=remain[m.end():]
			continue


		# Sections numbers/"margin notes" in later acts
		m=re.match('\s*<TR><TD align=right valign=top><B><a name="\d+"></a>(\d+)</B>&nbsp;&nbsp;&nbsp;&nbsp;</TD><TD valign=top><B>([\s\S]*?)</B><BR>&nbsp;</TD></TR>',remain)
		if m:
			locus.addenum(m.group(1))
			leaf=legis.Leaf('provision',locus,legis.Margin(m.group(2)))
			locus.lex.append(leaf)
			locus.lex.addsourcerule(OpsiSourceRule('section2'))
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col\.gif"></TD>\s*<TD valign=top>&nbsp;&nbsp;&nbsp;&nbsp;<a name="(\d+)"></a>(\d+[A-Z]*)\. - (\(\d+\))([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:

			locus.addenum(m.group(2))
			locus.addenum(m.group(3))
			leaf=legis.Leaf('provision',locus)
			if m.group(3)!=1:
				logger.warning("****peculiar number after section number: %s at %s" % (m.group(3), locus.text()))
	
			locus.lex.append(leaf)
			locus.addsourcerule(OpsiSourceRule('section3'))
			parseright(act,m.group(4),locus,quotestatus)
			remain=remain[m.end():]
			continue


		# unspecific line match in early acts WARNING: may not be
		# rigid enough.
		m=re.match('\s*<tr valign="top">\s*<td width="20%">\s*</td>\s*<td>([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
			logger.debug("****unspecified line match, could be too generic")
			locus.lex.addsourcerule(OpsiSourceRule('linematch1'))
			parseright(act,m.group(1),locus,quotestatus)
			remain=remain[m.end():]
			continue


		#print "+++++",remain[:200]
		#print "length=%s" % len(remain)

		# very similar
		m=re.match('\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td>([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
			#print "*****",remain[:92]
			#print "*****",m.group(1)
			#print "*****",quotestatus
			
			locus.lex.addsourcerule(OpsiSourceRule('linematch2'))
			parseright(act,m.group(1),locus,quotestatus)
			remain=remain[m.end():]
			continue

		m=re.match('\s*<tr>\s*<td width="10%" valign="top">&nbsp;</td>\s*<td>([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
						
			locus.lex.addsourcerule(OpsiSourceRule('linematch3'))
			parseright(act,m.group(1),locus,quotestatus)
			if not locus.lex.quote:
				logger.warning("Narrow width occuring outside quotation context (linematch3)")
			remain=remain[m.end():]
			continue

		m=re.match('\s*<tr\s*valign="top">\s*<td width="5%">\s*<br>\s*</td>\s*<td>([\s\S]*?)</td>\s*</tr>(?i)',remain)
		if m:
						
			locus.lex.addsourcerule(OpsiSourceRule('linematch4'))
			parseright(act,m.group(1),locus,quotestatus)
			if not locus.lex.quote:
				logger.warning("Narrow width occuring outside quotation context (linematch4)")
			remain=remain[m.end():]
			continue


		# Remaining line matches 

		# Tabular material
		
		m=re.match('\s*<TR><TD valign=top align=center>&nbsp;</TD><TD valign=top><tabular n="(\d+)*"\s+pattype="([a-z\w\s\d]+)"/></TD></TR>', remain)
		if m:
			raise Exception
			MakeTableLeaf(act, locus, m.group(1), m.group(2))
			
			locus.lex.addsourcerule(OpsiSourceRule('TabularMaterial(%s)' % m.group(2)))

			remain=remain[m.end():]
			continue

		#	

		m=re.match('\s*(?:&#151;)?<quotation n="(\d)*"\s+pattype="([a-z\w\s\d]+)"\s*/>',remain)
		if m:
			logger.info("(matching quote) Handling quotation n=%s" % m.group(1))
			sys.exit
			if m.group(2)=="rightquote":
				qnumber=int(m.group(1))
				quotation=act.QuotationAsFragment(qnumber,locus)
				pp=quotation.ParseAsQuotation()
				logger.debug("****parsed a quotation")
				logger.debug(pp.xml())
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
	
		m=re.match('''
			\s*<tr\s*valign="top">
			\s*<td\s*width="15%">
			\s*<br>
			\s*<font\s*size="2">
			([\s\S]*?)
			</font>
			\s*<br>
			\s*</td>
			\s*<td>([\s\S]*?)</td>
			\s*</tr>(?ix)''',remain)
		if m:
			parseright(act,m.group(2),locus,quotestatus,legis.Margin(deformat(m.group(1))))

			locus.lex.addsourcerule(OpsiSourceRule('LineMargin3'))

			remain=remain[m.end():]
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
	
#		# Found this one in a quote -- its a subsection number

#		m=re.match('<tr>\s*<td width="10%" valign="top">&nbsp;</td>\s*<td>((?:&quot;|")?)(\(\s+[A-Z]*\))&nbsp;([\s\S]*?)</td>\s*</tr>',remain)
#		if m:
#			locus.addenum(m.group2)
#			parseright(act,m.group(3),locus,quotestatus)
#			
#			remain=remain[m.end():]
#			continue

		m=re.match('\s*<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('TrimEmptyLine1'))
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col\.gif"></TD>\s*<TD valign=top>&nbsp;</TD></TR>(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('TrimEmptyLine2'))
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD valign=top>&nbsp;</TD>(?=\s*<TR>)(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('TrimEmptyLine3'))
			remain=remain[m.end():]
			continue



		# a hanging text line (in later acts)
		m=re.match('\s*<TR><TD></TD><TD>([^<]*?)</TD>\s*</TR>',remain)
		if m:
			AddTextLeaf(locus,legis.Margin(),m.group(1))

			locus.lex.addsourcerule(OpsiSourceRule('Unnumbered1'))
			remain=remain[m.end():]
			continue
			

		# Two ghastly abortions of lines (we didn't go to HTML
		# school clearly)

		m=re.match('\s*<TR><TD></TD><TD>([^<]*)(?=<TR>)(?i)',remain)
		if m:
			AddTextLeaf(locus,legis.Margin(),m.group(1))

			locus.lex.addsourcerule(OpsiSourceRule('Unnumbered2'))
			remain=remain[m.end():]
			continue

		m=re.match('\s*<TR><TD></TD><TD>([^<]*)</TR></TD>(?i)',remain)
		if m:
			AddTextLeaf(locus,legis.Margin(),m.group(1))

			locus.lex.addsourcerule(OpsiSourceRule('Unnumbered3'))
			remain=remain[m.end():]
			continue
	
		# Yuk, the page trimming needs to be improved:
		m=re.match('\s*<TR>\s*<TD valign="?top"?>&nbsp;</TD>\s*<pageurl [^<]*>(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('PageBreak1'))
			remain=remain[m.end():]
			continue

		# also yuk
		m=re.match('\s*<BR>&nbsp;</TD></TR>(?i)',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('TrimBrokenLine1'))
			remain=remain[m.end():]
			continue


		m=re.match('\s*</p>',remain)
		if m:
			locus.lex.addsourcerule(OpsiSourceRule('SnippedParEnd'))
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
			#print "unrecognised line:"
			#print remain[:350].strip()
			#logging.debug("line end=%s" % remain[1000:])
			endline=re.search('</tr>',remain)
			if endline:
				ending="\n...\n%s\n%s\n%s\n" % (remain[endline.start()-128:endline.start()],remain[endline.start():endline.end()],remain[endline.end():endline.end()+128])
			else:
				ending="\n... ????\n"
			raise parsefun.ParseError, "unrecognised line: \n%s\n%s" % (remain[:350].strip(),ending)

	
