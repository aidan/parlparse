#!/usr/bin/python

import urllib
import urlparse
import re
import sys

cversion="1.0" # the version of the conglom file output 
pversion="1.2" # the version of the conglom parser/scraper
	
#
# firstpage is a flag indicating whether getpage is accessing the first page or not. The first
# page is treated differently because it has a different structure
# getpage returns the url for the next page (if any) and accumulated contents from the current page

# First page structure is:
# Royal arms and header <HR> copyright <HR> table of contents (optional) <HR> text of the Act ...
# Normal page is:
# Heading <HR> text of page ...
# where ... indicates everything from the continue button onwards.
# we want to leave the HR's in for the moment, as they provide important structuring information


def getpage(url, firstpage):
    page=urllib.urlopen(url).readlines()    
    contents=''				 #accumulator for page contents
    hrcount=0				 #number of <HR> tags encountered so far
    nextpage=False

    for line in page:
    	line=re.sub('<img src="/img/ra-col.gif">','',line) #removes royal coat of arms gif

    	continueline=re.search('\<a href="(.+?)".*?alt="continue"(?i)',line)
    	hrline=re.search('\<HR\>(?i)', line)

	if continueline:
    		nextpage=urlparse.urljoin(url,continueline.group(1))
		break

	#Fails to work when firstpage and last page are the same. 
	#Maybe this is not the best place to do this.
	#	if (hrline and hrcount > 0  and not firstpage):
	#		print "(should skip line) hrcount=%s line=(%s)" % (hrcount, line[:25])
	#		break
	
	#isbackpointer=re.search('back to previous (text|page)',line)	
	isbackpointer=False	
	
	## ignore everything from before the first HR except on the first page
	## ignore silly back pointers if they exist

	if (hrcount > 0 or firstpage) and not isbackpointer:
    		contents=contents+line 
    	
	#contents=contents+line

    	if hrline:
    		hrcount=hrcount+1
		#print "(incrementing hrcount) hrcount=%s line=(%s)" % (hrcount, line[:25])
    	
	
    #contents=contents+"<pagethrow />"
    return (nextpage, contents, hrcount, continueline)	


#
# Convenience wrapper that does the file IO and calls getpage.
#

def conglomfile(url):
	(year,chapter)=re.search('/\D*(\d\d\d\d)(\d+)\D',url).groups()
	filename='conglom-s%sc%d.html' % (year,int(chapter))
	print "outputting to file ((%s))" % filename
	out=open(filename,'w')
	

	out.write('<fmeta>\n<source\nclass="opsi"\n')
	out.write('url="%s"\n</source>\n' % url)
	out.write('<conglom cversion="%s" />' % cversion)

	firstpage=True
	while url:
		print "Processing ((%s))" % url
		(url, contents, hrcount, continueline)=getpage(url, firstpage)
		if firstpage:
			if url:
				out.write('<opsi type="multipage" />\n')				
			else:
				out.write('<opsi type="singlepage" />\n')
		
			firstpage=False
			out.write('</fmeta>\n')
		
		out.write(contents)


# 
# Main program
#

if len(sys.argv) > 1:
	url=sys.argv[1]
else:
	#url='http://www.opsi.gov.uk/acts/acts1996/1996018.htm'
	#url='http://www.opsi.gov.uk/acts/acts2005/20050015.htm'
	url='http://www.opsi.gov.uk/acts/acts1988/Ukpga_19880028_en_1.htm'

print "conglomfile, parser version=%s file version=%s" % (pversion, cversion)
#print "processing url=%s" % url
conglomfile(url)
