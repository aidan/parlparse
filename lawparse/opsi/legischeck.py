#!/usr/bin/python

import xml.sax.saxutils

from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Lib import Uri

import xml.dom
import sys

name='ukpga1997c2.xml'

file_uri=Uri.OsPathToUri("acts/xml/%s" % name)
doc=NonvalidatingReader.parseUri(file_uri)

from xml.dom.minidom import parse, parseString

leaves=doc.xpath('//legis/content/leaf')
#for l in leaves:
#	section=l.xpath('@s')
#	print section[0].nodeValue
#


sections=doc.xpath('//legis/content/leaf')

sectionno=0
for s in sections:

	leaftype=s.xpath('@type')[0].nodeValue

	if leaftype=='provision':
		sno=int(s.xpath('@s')[0].nodeValue)
		
		if sno > sectionno:
			if sno==sectionno+1:
				pass
			else:
				print "jump forwards %i to %i" % (sectionno,sno)
		elif sno==sectionno:
			continue
		elif sno==1:
			print "------- Restart Numbering"
		else:
			print "jump backwards %i to %i" % (sectionno,sno)

		sectionno=sno
		print sectionno

	elif leaftype=='division':
		print "========== Division(%s)" % s.xpath('child::node()')[0].nodeValue
	elif leaftype=='heading':
		t=s.xpath('child::node()')
		if len(t)>0:
			content=t[0].nodeValue
		else:
			content=''
		print "========== Heading(%s)" % content

sys.exit()


#sections=doc.xpath('//legis/content/leaf/@s[../preceding-sibling::leaf/@s!=.]')
#sections=doc.xpath('//legis/content/leaf[preceding-sibling::leaf[position()=1]/@s=1]/@s')





sections=doc.xpath('//legis/content/leaf[preceding-sibling::leaf[position()=1]/@s!=@s]')


for s in sections:
	#print s.nodeValue
	print s
	print s.xpath('@type')[0].nodeValue
	print s.xpath('@s')[0].nodeValue
#print leaves


#
#
#dom=xml.dom.getDOMImplementation()

#dom1 = parse('acts/xml/ukpga1997c1.xml') # parse an XML file by name
#
#print dom1.nodeType
#print dom1.childNodes
#
#print doc.nodeType
#print doc.childNodes
#
#print doc.xpath('//legis')
#print dom1.xpath('//legis')
