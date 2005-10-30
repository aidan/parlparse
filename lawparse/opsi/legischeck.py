#!/usr/bin/python
# vim:sw=4:ts=4:noet:nowrap

# legischeck.py - lint for XML act files

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

import xml.sax.saxutils

from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Lib import Uri

import xml.dom
import sys
import re

import miscfun

def divider(string):
	print "==== %s" % string

def snumconvert(string):
	m=re.match('[(]*(\d+)[).]*',string)
	return int(m.group(1))

name='ukpga%s.xml' % sys.argv[1]
#name='ukpga1997c2.xml'

file_uri=Uri.OsPathToUri("acts/xml/%s" % name)
doc=NonvalidatingReader.parseUri(file_uri)

from xml.dom.minidom import parse, parseString

leaves=doc.xpath('//legis/content/leaf')
#for l in leaves:
#	section=l.xpath('@s')
#	print section[0].nodeValue
#


sections=doc.xpath('//legis/content/leaf')
id=doc.xpath('//legis/@id')

divider(id[0].nodeValue)

sectionno=0
for s in sections:

	leaftype=s.xpath('@type')[0].nodeValue

	if leaftype=='provision':
		try:
			sno=snumconvert(s.xpath('@s')[0].nodeValue)
		except ValueError:
			print s
			print s.xpath('@s')[0].nodeValue
			raise		

		if sno > sectionno:
			if sno==sectionno+1:
				pass
			else:
				print "jump forwards %i to %i" % (sectionno,sno)
		elif sno==sectionno:
			continue
		elif sno==1:
			print "++++ Numbering restarted"
		else:
			print "jump backwards %i to %i" % (sectionno,sno)

		sectionno=sno
		print sectionno

	elif leaftype=='division':
		divider("Division(%s)" % s.xpath('child::node()')[0].nodeValue)
	elif leaftype=='heading':
		t=s.xpath('child::node()')
		if len(t)>0:
			content=t[0].nodeValue
		else:
			content=''
		divider("Heading(%s)" % content)

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
