import re
import copy

# need correct value for amp

doctype='''
	<!DOCTYPE legis [
		<!ENTITY copy "&#169;">
		<!ENTITY amp "&#38;"> 
		<!ENTITY pound "&#163;">
        ]>\n'''


class Margin:				# represents marginal notes
	def __init__(self,t=''):
		self.margintext=t

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
		#self.info={}

	def append(self,leaf):
		self.content.append(leaf)
		#print "****appending leaf to Legis", leaf
		xmlofleaf=leaf.xml()
		#print "**** after append, xml of leaf",xmlofleaf 
		print leaf.xml()[:128]

	def extend(self,leaflist):
		self.content.extend(leaflist)

	def last(self):
		return self.content[len(self.content)-1]

	def xml(self):
		s='<?xml version="1.0" encoding="iso-8859-1"?>%s\n<legis\n\tid="%s">\n%s%s' % (doctype, self.id,self.preamble.xml(),self.sourceinfo.xml())
		
		s=s+'\n<content>\n'
		for leaf in self.content:
			s=s+leaf.xml()
		s=s+'</content>\n</legis>\n'
		return s

class Act(Legis):
	def __init__(self, year, session, chapter):
		Legis.__init__(self)
		self.year=year
		self.session=session
		self.chapter=chapter
		self.id="ukpga"+year+"c"+chapter
		self.preamble=ActPreamble()
		print "[Legis.Act] year=%s session=%s chapter=%s" % (year, session, chapter)

class SI(Legis):
	def __init__(self, year, number):
		Legis.__init(self)
		self.quote=False
		self.year=year
		self.number=number
		self.id="uksi"+year+"no"+number

class SourceInfo:
	def __init__(self):
		self.source='unknown'

	def xml(self):
		return '<sourceinfo source="%s"/>\n' % self.source
		
class Preamble:
		def __init__(self):
			pass

		def xml(self):
			return ''

class ActPreamble(Preamble):
		def __init__(self):
			Preamble.__init__(self)
			self.longtitle=''
			self.date=''
			self.enactment=''
			self.whereas=[]

		def xml(self):
			s='<preamble>\n<longtitle \n\tdate="%s"\n>%s</longtitle>\n<enactment>%s</enactment>\n</preamble>\n' % (self.date,self.longtitle,self.enactment)
			return s
	
class SIPreamble(Preamble):
		def __init__(self):
			Preamble.__init__(self)

		def xml(self):
			return '\n<preamble />\n'

class Leaf:
	def __init__(self, t, locus, margin=Margin()):
		self.t=t
		self.content=''
		self.locus=copy.deepcopy(locus)
		self.margin=margin
		self.attributes=[]
		self.sourcerule=''

	def xml(self,options=''):
		#print "****xml of leaf", self.content
		contents=self.xmlcontent()
		#print "****xml contents were",contents
		if len(self.sourcerule)>0:
			sourcerule=' sourcerule="%s"' % self.sourcerule
		else:
			sourcerule=''
		result= '\n<leaf type="%s" %s%s%s>%s%s</leaf>\n' % (self.t, 
				self.locus.xml(), 
				sourcerule,
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

class Division(Heading):
	def __init__(self,locus,dheading,dnumber,margin=Margin()):
		Leaf.__init__(self,'division',locus,margin)
		#self.t="division"
		self.dheading=dheading
		self.dnumber=dnumber

	def xml(self,u=''):
		t=' dheading="%s" dnumber="%s"%s' % (self.dheading,self.dnumber,u)
		s=Leaf.xml(self,t)
		return s

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
			s=s + '<cell>%s</cell>' % i
		return '<row %s>%s</row>\n' % (locus.xml(), s)

class Locus:
	def __init__(self,lex):
		self.lex=lex
		self.path=[]
		self.division=''
		self.partitions={}

	def __deepcopy__(self,memo):
		newlocus=Locus(self.lex)
		newlocus.path=copy.deepcopy(self.path,memo)
		newlocus.division=self.division
		newlocus.partitions=copy.deepcopy(self.partitions,memo)
		return newlocus

	def xml(self):
		s='lex="%s" division="%s"%s%s' % (self.lex.id,
				self.division,
				pathprint(self.path),
				self.part2xml())
		return s

	def text(self):
		s='%s/%s' % (self.lex.id, self.division)

		for n in self.path:
			s=s+('/%s' % n.text())
	
		return s

	def addenum(self, s):
		new=PathElement(s)

		for x in range(0, len(self.path)):
			if self.path[x].matches(new):
				self.path=self.path[:x]
				self.path.append(new)
				return x

		self.path.append(new)

	def newdivision(self,t,s):
		print "***new division:%s%s" % (t,s)
		self.partitions={}
		self.division=t+s	
		self.path=[]					

	def addpart(self, t, s):
		self.partitions[t]=s
		if s not in set(['part','chapter']):
			print "****unusual division [[%s]]" % s

	def part2xml(self):
		sxml=''
		for k in self.partitions.keys():
			sxml='%s %s="%s"' % (sxml,k,self.partitions[k])
		return sxml


class PathElement:
	def __init__(self,s):
		m=re.match('((?:[\|\(])?)(\w+)([\)\.\]]?)',s)
		if m:
			left=m.group(1)
			num=m.group(2)
			right=m.group(3)
		else:
			print "****Illegal enumeration passed to locus:%s" % num
			sys.exit()

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
		print "****unknown enumeration:%s" % s



def pathprint(p):
	s=''
	sname='s'
	for pe in p:
		s='%s %s="%s"' % (s,sname,pe.text())
		sname=sname + 's'
	return s


if __name__ == '__main__':
	act=Act('1988','','1')
	print "legis"
	a=Locus(act)
	a.addenum('1')
	print a.xml()
	a.addenum('(1)')
	print a.xml()
	a.addenum('(b)')
	print a.xml()
	a.addenum('(2)')
	print a.xml()
	print extractenum('(iv)')
	print a.path
	print pathprint(a.path)