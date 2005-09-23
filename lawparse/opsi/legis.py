import re
import copy

class Margin:
	def __init__(self,t=''):
		self.margintext=t

	def xml(self):
		if self.margintext=='':
			return ''
		else:
			return ' margin="%s"' % self.margintext

class Legis:
	def __init__(self):
		self.content=[]

	def append(self,a):
		self.content.append(a)
		print a.xml()[:128]

	def last(self):
		return self.content[len(self.content)]

	def xml(self):
		s='<legis\n\tid="%s">\n' % self.id
		for leaf in self.content:
			s=s+leaf.xml()
		s=s+'</legis>\n'
		return s

class Act(Legis):
	def __init__(self, year, session, chapter):
		self.year=year
		self.session=session
		self.chapter=chapter
		self.content=[]
		self.id="ukpga"+year+"c"+chapter
		print "[Legis.Act] year=%s session=%s chapter=%s" % (year, session, chapter)

class SI(Legis):
	def __init__(self, year, number):
		self.year=year
		self.number=number
		self.content=[]
		self.id="uksi"+year+"no"+number

class Leaf:
	def __init__(self, t, locus, margin=Margin()):
		self.t=t
		self.content=''
		self.locus=copy.deepcopy(locus)
		self.margin=margin

	def xml(self):
		return '<leaf type="%s" %s%s>%s</leaf>\n' % (self.t, 
				self.locus.xml(), self.margin.xml(),
				self.content)
class Heading(Leaf):
	def __init__(self,locus,margin=''):
		Leaf.__init__(self,locus,margin)
		self.t='heading'
		self.content=''


class Division(Heading):
	def __init__(self,locus,dheading,dnumber,margin=''):
		Leaf.__init__(self,locus,margin)
		self.t="division"
		self.dheading=dheading
		self.dnumber=dnumber

	def xml(self):
		s=Leaf.xml(self)
		s='%s dheading="%s" dnumber="%s"' % (s,self.dheading,self.dnumber)
		return s

class Locus:
	def __init__(self,lex):
		self.lex=lex
		self.path=[]
		self.division='main'
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

	def addenum(self, s):
		(num,t,left,right)=extractenum(s)

		for x in range(0,len(self.path)):
			if self.path[x][1]==t and self.path[x][2]==left and self.path[x][3]==right:
				self.path[x]=(num,t,left,right)
				return x
		self.path.append((num,t,left,right))
				
	def addpart(self, t, s):
		self.partitions[t]=s
		if s not in set(['part','chapter']):
			print "****unusual division [[%s]]" % s

	def part2xml(self):
		sxml=''
		for k in self.partitions.keys():
			sxml='%s %s="%s"' % (sxml,k,self.partitions[k])
		return sxml


def extractenum(s):
	m=re.match('((?:[\|\(])?)(\w+)([\)\.\]]?)',s)
	if m:
		left=m.group(1)
		num=m.group(2)
		right=m.group(3)
	else:
		print "****Illegal enumeration passed to locus:%s" % num
		sys.exit()

	return (num, enumtype(num), left, right)
	

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
	for (num,t,left,right) in p:
		s='%s %s="%s%s%s"' % (s,sname,left,num,right)
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