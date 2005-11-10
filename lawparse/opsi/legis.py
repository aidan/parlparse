# legis.py - law object model, stores logical structure of act, emits XML

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
import copy
import logging

doctype='''
	<!DOCTYPE legis [
		<!ENTITY copy "&#169;">
		<!ENTITY amp "&#38;"> 
		<!ENTITY pound "&#163;">
        ]>\n'''

class LegisError(Exception):
	pass

class SourceRule:
	'''A rule applied to generate the current leaf.

	Each leaf of a LOM object may be marked with a list of source rules,
	which are used by the source libary to record its "reasons" for 
	generating that particular leaf. Many rules may have contributed to
	any single leaf.

	The class Source Rule should be subclassed.
	'''

	def __init__(self,owner,name):
		self.owner=owner
		self.name=name

class SourceRuleCollection:
	'''The collection of rules that generate the current leaf.'''

	def __init__(self,owner):
		self.owner=owner
		self.rules=[]

	def addrule(self,rule):
		if self.owner != rule.owner:
			raise SourceRuleOwnerMismatch
		else:
			self.rules.append(rule)

	def text(self):
		s='%s:' % self.owner
		for rule in self.rules:
			s=s+('%s;' % rule.name)
		return s

class Margin:				
	'''A marginal note (if any) applied to the current leaf.

	Each leaf may have a marginal note -- which, in the case of most
	UK materials, will be in the direct left hand margin. Sometimes 
	a marginal note is logically connected to something on a previous line
	(this is the usual style with recent UK acts in marginal noting
	schedules). In such cases the Margin object should be attached to the
	appropriate leaf.
	'''

	def __init__(self,t=''):
		self.margintext=t
		self.used=False

	def xml(self):
		if self.margintext=='':
			return ''
		else:
			return '\n<margin>%s</margin>' % self.margintext

class Legis:				# the unit of legislation
	def __init__(self):
		self.content=[]
		self.id='unknown'
		self.quote=False	# used to indicate whether the legis is
					# being quoted in another legis
		self.preamble=Preamble()
		self.sourceinfo=SourceInfo()
		self.initialsourcerules=SourceRuleCollection(self.sourceinfo.source)
		self.logger=logging.getLogger('legis')
		#self.info={}

	def append(self,leaf):
		self.content.append(leaf)
		xmlofleaf=leaf.xml()
		self.logger.info(leaf.xml()[:255])

	def extend(self,leaflist):
		self.content.extend(leaflist)

	def last(self):
		if len(self.content)>0:
			return self.content[len(self.content)-1]
		else:
			return None
	
	def xml(self):
		s='<?xml version="1.0" encoding="iso-8859-1"?>%s\n<legis xmlns:hint="http://www.google.com" \n\tid="%s">\n%s%s' % (doctype, self.id,self.preamble.xml(),self.sourceinfo.xml())
		
		s=s+'\n<content>\n'
		for leaf in self.content:
			s=s+leaf.xml()
		s=s+'</content>\n</legis>\n'
		return s

	def addsourcerule(self,s):
		self.logger.info("##Rule: (%s) %s" % (s.owner, s.name))
		if len(self.content) > 0:
			self.last().sourcerules.addrule(s)
		else:
			self.initialsourcerules.addrule(s)

class Act(Legis):
	def __init__(self, year, session, chapter):
		Legis.__init__(self)
		self.year=year
		self.session=session
		self.chapter=chapter
		self.id="ukpga"+year+"c"+chapter
		self.preamble=ActPreamble()
		self.logger.info("[Legis.Act] year=%s session=%s chapter=%s" % (year, session, chapter))

class SI(Legis):
	def __init__(self, year, number):
		Legis.__init(self)
		self.quote=False
		self.year=year
		self.number=number
		self.id="uksi"+year+"no"+number

class SourceInfo:
	def __init__(self,source='unknown'):
		self.source=source

	def xml(self):
		return '<sourceinfo source="%s"/>\n' % self.source


class Preamble:
	def __init__(self):
		self.type='empty'

	def xml(self):
		xmlc=self.xmlcontent()
		if xmlc=='':
			return '<preamble />\n'
		else:
			return '<preamble type="%s">\n%s</preamble>\n' % (self.type, xmlc)

	def xmlcontent(self):
		return ''

class ActPreamble(Preamble):
		def __init__(self):
			Preamble.__init__(self)
			self.longtitle=''
			self.date=''
			self.enactment=''
			self.whereas=[]
			self.type='act'

		def xmlcontent(self):
			s='<longtitle \n\tdate="%s"\n>%s</longtitle>\n<enactment>%s</enactment>\n' % (self.date,self.longtitle,self.enactment)
			return s
	
class SupplyActPreamble(Preamble):
		def __init__(self):
			Preamble.__init__(self)
			self.apply=''
			self.date=''
			self.petition=''
			self.whereas=[]
			self.type='supply act'

		def xmlcontent(self):
			s='<apply \n\tdate="%s"\n>%s</apply>\n<petition>%s</petition>\n' % (self.date, self.apply, self.petition)
			return s

class SIPreamble(Preamble):
		def __init__(self):
			Preamble.__init__(self)
			self.type='SI'

		def xmlcontent(self):
			return ''

# These will need tidying up, at the moment there are far too many.

ValidLeafTypes=['provision', # the basic unit of legislation
	'text', # text, which may belong to a provision or may not
	'quotation', # a leaf that contains a quotation of further leaves
	'item',
	'note', 
	'table', # an unparsed table
	'schedule marker', # marks the beginning of the schedules
	'division', # a heading that marks a new division (such as Part 1)
	'heading', # a heading
	'item1', # no idea what these are?
	'item2',
	'item3']

class Leaf:
	"""A single unit (or paragraph) of legislation."""

	def __init__(self, t, locus, margin=Margin()):
		self.t=t
		if t not in ValidLeafTypes:
			print t
			sys.exit()
		assert(t in ValidLeafTypes)
		self.content=''
		self.locus=copy.deepcopy(locus)
		if margin.used:
			self.margin=Margin()
		else:
			self.margin=margin
			margin.used=True
		self.attributes=[]
		self.sourcerules=SourceRuleCollection(locus.lex.sourceinfo.source)

	def xml(self,options=''):
		#print "****xml of leaf", self.content
		contents=self.xmlcontent()
		#print "****xml contents were",contents
		#if len(self.sourcerule)>0:
		#	sourcerule=' sourcerule="%s"' % self.sourcerule
		#else:
		#	sourcerule=''
		sourcerules=' sourcerule="%s"'  % self.sourcerules.text()
		result= '\n<leaf type="%s" %s%s%s>%s%s</leaf>\n' % (self.t, 
				self.locus.xml(), 
				sourcerules,
				options,
				self.margin.xml(),
				contents)
		#print "****results of xml(self) on leaf were", result
		return result

	def xmlcontent(self):
		return self.content

	def relocate(self,newlocus):
		self.locus=copy.deepcopy(newlocus)
		# do we need to free up the old locus here?

class Quotation(Legis,Leaf):
	def __init__(self,parsed,locus, margin=Margin()):
		Leaf.__init__(self,'quotation',locus,margin)
		self.parsed=parsed
		#self.leaves=[]
		self.quote=True
		self.content=[]
		self.id='quotation in(%s)' % locus.text()
		self.preamble=Preamble()
		self.sourceinfo=SourceInfo(locus.lex.sourceinfo.source)
		self.initialsourcerules=SourceRuleCollection(locus.lex.sourceinfo.source)
		self.logger=logging.getLogger('legis')

	def addleaf(self,l):
		#print "****quote adding leaf %s" % l.xml()
		self.content.append(l)

	def xmlcontent(self):
		#print "****xmlcontent called with %s" % self.content
		if self.content:
			s=''
			for i in self.content:#self.leaves:
				#print "****first leaf: %s" %i
				s=s+i.xml()
			return s
		else:
			return ''

	def xml(self):
		#print "****xml of quotation %s" % (type(self)), self, self.parsed,self.quote
		return Leaf.xml(self)

class Heading(Leaf):
	def __init__(self,locus,margin=Margin()):
		Leaf.__init__(self,'heading',locus,margin)
		#self.t='heading'
		self.content=None

class HeadingDivision(Heading):
	def __init__(self,locus,margin=Margin()):
		Leaf.__init__(self,'division',locus,margin)

#	def xml(self,u=''):
#		t=' %s' % (self.dheading,self.dnumber,u)
#		s=Leaf.xml(self,t)
#		return s

class Text(Leaf):
	"""A leaf representing a new text paragraph, without numbering."""

	def __init__(self,locus,margin,text):
		Leaf.__init__(self,'text',locus,margin)
		self.content=text
		

class Table(Leaf):
	def __init__(self,locus):
		Leaf.__init__(self,'table',locus)
		self.heading=''
		self.rows=[]
		self.locus=locus

	def xml(self,u=''):
		if len(self.heading)>0:
			t=' heading="%s"%s' % (self.heading, u)
		else:
			t=''
		s=Leaf.xml(self,t)
		return s

	def xmlcontent(self):
		s=''
		for row in self.rows:
			s=s+row.xml(self.locus)
		return s


class TableRow:
	def __init__(self,cells):
		self.cells=cells
		self.content=''

	def xml(self,locus):
		s=''
		for i in self.cells:
			s=s + '<cell>%s</cell>\n' % i
		return '<row %s>\n%s</row>\n' % (locus.xml(), s)

class Locus:
	def __init__(self,lex):
		self.lex=lex
		self.path=[]
		self.division=Division()
		self.partitions={}

	def __deepcopy__(self,memo):
		newlocus=Locus(self.lex)
		newlocus.path=copy.deepcopy(self.path,memo)
		newlocus.division=copy.deepcopy(self.division,memo)
		newlocus.partitions=copy.deepcopy(self.partitions,memo)
		return newlocus

	def xml(self):
		s='lex="%s"%s%s%s' % (self.lex.id,
				self.division.xml(),
				pathprint(self.path),
				self.part2xml())
		return s

	def text(self):
		s='%s/%s' % (self.lex.id, self.division.text())

		for n in self.path:
			s=s+('/%s' % n.text())
	
		return s

	def resetpath(self):
		self.path=[]

	def addenum(self, s):
		new=PathElement(s)

		for x in range(0, len(self.path)):
			if self.path[x].matches(new):
				self.path=self.path[:x]
				self.path.append(new)
				return x

		self.path.append(new)

	def newdivision(self,D):
		self.lex.logger.debug("***new division:%s" % D.text())
		self.partitions={}
		self.division=D
		self.path=[]					

	def addpart(self, t, s):
		self.partitions[t]=s
		if t not in set(['part','chapter','article']):
			self.lex.logger.debug("****unusual division [[%s]]" % s)

	def part2xml(self):
		sxml=''
		for k in self.partitions.keys():
			sxml='%s %s="%s"' % (sxml,k,self.partitions[k])
		return sxml

# Acts and Statutory Instruments are usually divided into an (unnamed) main 
# part and a number of schedules

class Division:
	def __init__(self):
		pass

	def xml(self):
		return ' division="%s"' % self.text()

	def text(self):
		return ''

class MainDivision(Division):
	def __init__(self):
		Division.__init__(self)
	
	def text(self):
		return 'main'

class Schedule(Division):
	def __init__(self, no=''):
		Division.__init__(self)
		self.number=no

	def text(self):
		return 'schedule%s' % self.number
		

class PathElement:
	def __init__(self,elementstring):
		logger=logging.getLogger('legis')
		m=re.match('((?:[\|\(])?)(\w+)([\)\.\]]?)',elementstring)
		if m:
			left=m.group(1)
			num=m.group(2)
			right=m.group(3)
		else:
			raise LegisError,  "****Illegal enumeration passed to locus:%s" % elementstring

		self.num=num
		self.enumtype=enumtype(num)
		self.left=left
		self.right=right

	def text(self):
		return '%s%s%s' % (self.left,self.num,self.right)

	def matches(self,pe):
		if self.enumtype==pe.enumtype and self.left==pe.left and self.right==pe.right:
			return True
		else:
			return False

#def extractenum(s):
#	m=re.match('((?:[\|\(])?)(\w+)([\)\.\]]?)',s)
#	if m:
#		left=m.group(1)
#		num=m.group(2)
#		right=m.group(3)
#	else:
#		print "****Illegal enumeration passed to locus:%s" % num
#		sys.exit()
#
#	return (num, enumtype(num), left, right)
#	

def enumtype(s):
	if re.match('[1-9][0-9]*',s):
		return 'numeric'
	if re.match('[a-z]',s):
		return 'lalpha'
	if re.match('[A-Z]',s):
		return 'ualpha'
	if re.match('[ivxdlcm]',s):
		return 'lroman'
	if re.match('[IVXDLCM]',s):
		return 'uroman'
	else:
		logger=logging.getLogger('legis')
		logger.warning("****unknown enumeration:%s" % s)



def pathprint(p):
	s=''
	sname='s'
	for pe in p:
		s='%s %s="%s"' % (s,sname,pe.text())
		sname=sname + 's'
	return s


if __name__ == '__main__':
	act=Act('1988','','1')
