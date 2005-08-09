#!/usr/bin/python

version=1.3

import BeautifulSoup
import sys
import re
import string
import xml.sax.saxutils

from Ft.Xml.Domlette import NonvalidatingReader
from Ft.Lib import Uri

#
# Takes a PageElement and reduces it to a string
# tags are removed, and (optionally) &nbsp; is converted to space
#


def textflatten(l, collapsenbsp=True):
	if isinstance(l, BeautifulSoup.Tag):
		stringlist=map (lambda x: x.string, l.fetchText(lambda x:True, True))
		singlestring=''.join(stringlist)
	else:
		singlestring=str(l)
	if collapsenbsp:
		singlestring=singlestring.replace('&nbsp;',' ')

	return singlestring.strip()


def gettool(filename):
	file=open(filename)
	soup=BeautifulSoup.BeautifulSoup(file)
	return soup.td.contents
	
#
# Gets the next unit out of the soup but ignores various lines treated as nulls
# check is an optional regular expression that should be asserted to be present
# in the line.
#

def getnext(bigtable, check=None):
	s=''
	ret=None
	while s=='' and len(bigtable)>0:
		ret=bigtable.pop(0)		
		s=str(ret).strip()
		if s!='':
			s=textflatten(ret)
		if s=='':
			ret=None
	#print "***getnext\n%s"[:100] % ret
	if check:
		assert re.search(check + "(?i)", str(ret)), "expected '%s', got: %s" % (check, str(ret)[:100])

	return ret

def tagattr(chtag):
	if chtag !='':
		chunkattr=' wastag="' + chtag + '"'
	else:
		chunkattr=''
	return chunkattr		
					
def mkchunk(value,col,type='none',tags=''):
	return '<chunk type="%s" col="%s"' % (type, col) + ' ' + tags + '>' + value + '</chunk>\n'

def chunker(taglist, col, check=None):

	acc='' #accumulator string	
	chtag=''

	while len(taglist)>0:
		tag=taglist.pop(0)

		#debugging code
		#print "*****"
		#print "tag=((%s))" % tag
		#print "acc=((%s))" % tag
		#print "chtag=((%s))" % chtag
		#print "-----"
		#print taglist

		if isinstance(tag, BeautifulSoup.Tag):
			#checks to see whether the current tag is a block tag
			mobj=re.match('<(ul|br|p|table|hr)',str(tag))	
			if mobj:
				#print "outputting old chunk"
				# output old chunk				
				if acc!='' or chtag=='hr':			
					chunkattr=tagattr(chtag)
					yield mkchunk(acc,col,'none',chunkattr)
					
				# start new chunk
				acc=''
				chtag=mobj.group(1)
				
				if chtag=='table':
					rows=tag('tr',{},False)
					#print "*****"
					#print rows
					#print "*****"
					for i in tablechunker(rows):
						acc=acc+i
						acc=acc+'\n'

					yield mkchunk(acc,col,'table')
					acc=''
					chtag='' 
				else:				
					taglist=tag.contents+taglist

			else: # a non-block tag, we are only interested in the contents.
				#print "a non-block tag, we are only interested in"
				#print "tag.contents=%s" % tag.contents
				
				#check to see if any block tags are contained
				if tag.fetch(['ul','br','table','p','hr']):	
					taglist=tag.contents+taglist
	
				# no block tags below, so just add to the end.
				else:	
					#print "no block tags, acc=((%s))" % acc
					acc=acc+textflatten(tag)		
					#print "acc set to acc=((%s))" % acc	
	
		#if its not a tag, just add text onto the end of the accumulator
		else:
			#print "extending acc by tag: acc=((%s)) tag is ((%s))" % (acc, tag)
			acc=acc+textflatten(tag)
			#print "acc extended to: acc=((%s))" % acc

	if acc=='' and chtag!='hr':
		yield None
	else:
		chunkattr=tagattr(chtag)
		yield mkchunk(acc, col, 'none', chunkattr)
		
def tablechunker(rows):
	#print "****call to tablechunker nrows=((%s))" % len(rows)
	for row in rows:
		col=0
		for i in row('td',{},False):
			col=col+1
			#print "row=((%s)) col=((%s))" % (row,col)
			for i in chunker(i.contents, col):
				if i:
					#print "yielding i=((%s))" % i
					yield i

def nuttin():			
		tdchildren=row('td',{},False)
		
		#print "len(tdchildren)=((%s))" % len(tdchildren)
		#print tdchildren


		# at the moment this ignores all table rows which do not have
		# two columns. Many repeal tables have multiple columns
		# also this marks far too many rows as "abonormal"
		# <tr><tr> rows are treated as abnormal
		# as are colspan="2"
		if len(tdchildren) == 2:
			(left,right)=tdchildren
		else:
			yield mkchunk(str(row),2,"abnormalrow")
		#	continue
		
		#left hand column
		lhc=textflatten(left)
		if lhc!='':
			#print "*****"
			#print "left hand column=((%s))" % lhc
			yield mkchunk(lhc,1, 'marginpar')
		#print "*****"
		#print "right hand column"
		#print "right.contents=((%s))" % right.contents	
		#right hand column

		for i in chunker(right.contents, 2):
			print "looking at i=((%s))" % i
			if i:		
				print "chunkout = ((%s))" % i
				yield i

def printxmlpar(type, node, out):
	escapedtext=xml.sax.saxutils.escape(textflatten(node))
	out.write ('<chunk type="%s">%s</chunk>' % (type, escapedtext))
#	out.write ('<chunk type="%s">%s</chunk>' % (type, node))


def metaoptions(infilename):
	file_uri=Uri.OsPathToUri("meta-" + infilename)
	doc=NonvalidatingReader.parseUri(file_uri)
	source=doc.xpath('string(//source/@name)')
	if source != 'opsi':
		print "ERROR: source is not identified as opsi"
		sys.exit()
	conglomtype=str(doc.xpath('string(//opsi/@type)'))
	return conglomtype
	

def gethead(soup, out, conglomtype):
#	rowlist=soup.html.body.div.table('tr',{},False)
	rowlist=soup.html.body.div.contents

	#debugging code
	#print "*****"
	#print soup.html.body.div.table
	#print "*******"
	#print rowlist
	#sys.exit()

	bigtable=list(soup.html.body.div.table)
	print "length=", len(bigtable)
	print "-------"
	out.write('</head>\n')	

	out.write('<body>\n')
	return(rowlist)

	#ignore after here for the moment.
		
	royalcoat=getnext(bigtable,'royalarm\.gif')
	crowncopy=getnext(bigtable,'Crown Copyright')
	
	if conglomtype=="singlepage":
		print "Processing a single page document"
	elif conglomtype=="multipage":
		print "Processing a multiple page document"
		chaptitle=getnext(bigtable,'Chapter')
		arrsections=getnext(bigtable)
	else:
		print "Error: unknown conglomtype=%s" % conglomtype
		sys.exit()
	
	return(bigtable('tr',{},False))

def opsi2flat(infilename, outfilename):

	infile=open(infilename)	
	soup=BeautifulSoup.BeautifulSoup(infile)
	meta=soup.fmeta

	if meta.opsi:
		conglomtype=meta.opsi['type']
	else:
		print "error: input file not generated from opsi source"
		sys.exit()

	title=soup.html.head.title.string
	print "title=", title

	#print "****conglomtype=%s\n" % conglomtype

	# setup headers in output file
	out=file(outfilename,"w")
	
	#print necessary header and preamble

	out.write('<?xml version="1.0" encoding="iso-8859-1"?>\n')
	out.write('<!DOCTYPE flat [\n')
	out.write('<!ENTITY copy "&#169;">\n')
	out.write('<!ENTITY nbsp "&#160;">\n')
	out.write('<!ENTITY pound "&#163;">\n')
	out.write(']>\n')
	out.write('<flat type="statute">\n')
	out.write("<head>\n")
	out.write(meta.source.prettify())
	out.write("\n<title>%s</title>\n" % title)
	

	#process headings and extract the main table
	rowlist=gethead(soup, out, conglomtype)

	#print rowlist
	#sys.exit

#	for i in tablechunker(rowlist):
	for i in chunker(rowlist, 1):
		if i:
			out.write(i)
			out.write("\n")
	
	out.write('</body>')
	out.write('</flat>')

# 
# Main program
#

if len(sys.argv) > 1:
	filename=sys.argv[1]
else:
	filename='conglom-s2005c15.html'	

outfile=re.sub('conglom','chunk',re.sub('.html','.xml',filename))

print "opsi2flat version %s" % version
print "processing file=%s" % filename
print "writing file=%s" % outfile

opsi2flat(filename,outfile)
