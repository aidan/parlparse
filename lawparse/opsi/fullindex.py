#!/usr/bin/python

import urllib
import urlparse
import re
import sys
import os
import os.path

# starting point for directories
# actdir = "C:/pwhip/parldata/acts"
actdir = "acts"
iurl = "http://www.opsi.gov.uk/acts.htm"


# set of heading matches, broken down to make it easier to
# discover where the failure is
headlines1 = [ ('first',  '<table(?:cellpadding="?2"?|width="?95%"?|\s)*>\s*<tr>(?i)'),
			  ('middle', '(?:<tr(?:\s*xml\S*)*>)*\s*<td\s*align="?center"?\s*valign="?bottom"?>\s*(?i)'),
			  ('middle', '<img\s*src="/img/royalarm.gif"\s*alt="Royal\ Arms">\s*</td>\s+(?i)'),
			  ('middle', '<td\s*valign="?bottom"?>(?:&nbsp;<br>)?\s+(?i)'),
			  ('name',   '<font\s*size="?\+3"?><b>([\s\S]{1,250}?)</b></font>\s+(?i)'),
			  ('chapt',  '<p>(?:</p>)?<font\s*size="?\+1"?>(?:<b>)?([^<]*)(?:</b>)?</font>\s+(?i)'),
			  ('middle', '</td>\s*</tr>\s+(?i)'),
			  ('middle', '<tr(?:\s*xml\S*)*>\s*<td\s*colspan="?2"?>\s*<hr></td>\s*</tr>\s+(?i)'),
			  ('middle', '<tr>\s*<td\s*valign="?top"?>&nbsp;</td>\s+(?i)'),
			  ('middle', '<td\s*valign="?top"?>\s+(?i)'),
			  ('cright', '<p>&copy;\ Crown\ Copyright\ (\d+<?)</p>\s+(?i)'),
			  ('middle', "<P>\s*Acts of Parliament printed from this website are printed under the superintendence and authority of the Controller of HMSO being the Queen's Printer of Acts of Parliament.\s*"),
			  ('middle', '<P>\s*The legislation contained on this web site is subject to Crown Copyright protection. It may be reproduced free of charge provided that it is reproduced accurately and that the source and copyright status of the material is made evident to users.\s*'),
			  ('middle', "<P>\s*It should be noted that the right to reproduce the text of Acts of Parliament does not extend to the Queen's Printer imprints which should be removed from any copies of the Act which are issued or made available to the public. This includes reproduction of the Act on the Internet and on intranet sites. The Royal Arms may be reproduced only where they are an integral part of the original document.\s*"),
			  ('middle', '<p>The text of this Internet version of the Act is published by the Queen\'s Printer of Acts of Parliament and has been prepared to reflect the text as it received Royal Assent.\s*'),
			  ('name2',  'A print version is also available and is published by The Stationery Office Limited as the <b>(.{0,100}?)\s*</b>,\s*'),
			  ('isbn',   'ISBN ((?:0(?:&nbsp;|\s*)(\d\d)(?:&nbsp;|\s*)(\d{6})?(?:&nbsp;|\s*)(\d|X))?)\s*\.\s*'),
			  ('middle', 'The print version may be purchased by clicking\s*'),
			  ('middle', '<A HREF="(?:/bookstore.htm\?AF=A10075(?:&amp;|&)FO=38383(?:&|&amp;)ACTION=AddItem(?:&amp;|&)|http://www.clicktso.com/portal.asp\?DT=ADDITEM&amp;|http://www.ukstate.com/portal.asp\?CH=YourLife&amp;PR=BookItem&amp;)'),
			  ('prodid', '(?:BI|DI|ProductID)=(?:(\d{9}(?:\d|X)?)\.?)?\s*">\s*here</A>.\s*'),
			  ('middle', 'Braille copies of this Act can also be purchased at the same price as the print edition by contacting\s*'),
			  ('middle', 'TSO Customer Services on 0870 600 5522 or '),
			  ('middle', 'e-mail:\s*<A HREF="mailto:customer.services?@tso.co.uk">customer.services?@tso.co.uk</A>.</p>\s*'),
			  ('middle', '<p>\s*Further information about the publication of legislation on this website can be found by referring to the <a href="http://www.hmso.gov.uk/faqs.htm">Frequently Asked Questions</a>.\s*<p>\s*(?i)'),
			  ('middle', 'To ensure fast access over slow connections, large documents have been segmented into "chunks". Where you see a "continue" button at the bottom of the page of text, this indicates that there is another chunk of text available.\s*(?i)'),
			  ('middle', '</td>\s*</tr>\s*(?i)'),
			  ('middle', '\s*<tr><td colspan="?2"?>\s*<hr></td></tr>\s*(?i)'),
			  ('middle', '\s*<tr>\s*(?:<a name="tcon"><td width="20%">|<td valign=top>)\&nbsp;</td>(?i)'),
			  ('middle', '\s*<td align="?center"?>\s*(?i)'),
		          ('middle', '(?:\&nbsp;<br><a name="aofs"></a>)?(?:<b>\s*|<font size="?\+2"?>){2}(?i)'),
			  ('name3', '([\s\S]{1,250}?)(?:</b>\s*|</font>\s*){2}(?i)'),
			  ('middle', '(?:</a>|<td>|</td>|</tr>|<tr>|<td width="20%">\&nbsp;</td>|\s)*\s*(?i)'),
			  ('chapt2', '<p(?: align="center")?>\s*(?:<font size="4">|<b>)([\s\S]{1,250}?)(</font>|</b>)(?i)'),
			  ('middle', '\s*(?:</p>)?\s*</td>\s*</tr>\s*(?i)')
			  
]

'''
(next set of lines, which has repeated info that's worth cross-checking)

<TR><TD width=120 align=center valign=bottom><img src="/img/ra-col.gif"></TD><TD valign=top>&nbsp;</TD></TR>


<TR valign=top><TD valign=top>&nbsp;</TD><TD valign=top><TABLE width=100%>
'''

preamblepattern='((?:An )?\s*(?:\[A\.D\.\s*\S*\])?\s*Act(, as respects Scotland,)? to ([a-zA-Z- \.;/,\[\]&\(\)0-9\']|</?i>)*)'

headlines2=[ ('middle','\s*<tr(?: valign="top")?>\s*<td(?: width="10%"| width=120 align=center valign=bottom)>(?i)'),
			('middle', '(?:<img src="/img/ra-col\.gif">)?\s*(?:<br>|&nbsp;)?\s*</td>(?i)'),
			('middle', '\s*(?:<td valign=top>&nbsp;</td>)?\s*'),
			('middle', '(\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*)?(?i)'),
			('middle', '<td(?: valign=top)?>(?i)'),
			('middle','\s*(?:<br>&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;</td></tr>\s*<TR><TD valign=top>&nbsp;</TD><TD valign=top>)(?i)'),
			('preamble','(?:' + preamblepattern + '</td>\s*</tr>\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td |\s*<p>' + preamblepattern +'\s*<p)(?i)'),
			('date','\s*align="?right"?>\s*\[(\d+\w*\s*\w+\s*\d{4})\]\s*(?:<br><br>)?(?i)'),
			('middle','(?:\s*</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;|\s*<p>)(?i)'),
			('consideration','\s*(Whereas [a-zA-Z ;,&\(\)0-9\']*:)?'),
			('petition1','(Most Gracious Sovereign,\s*(?:</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?\s*(?:<p>)?WE, Your Majesty\'s most dutiful and loyal subjects,? the Commons of the United Kingdom in Parliament assembled, (towards making good the supply which we have cheerfully granted to Your Majesty in this Session of Parliament,? have resolved to grant unto Your Majesty the sums? hereinafter mentioned|towards raising the necessary supplies to defray Your Majesty\'s public expenses, and making an addition to the public revenue, have freely and voluntarily resolved to give and grant unto Your Majesty the several duties hereinafter mentioned); and do therefore most humbly beseech Your Majesty that it may be enacted,? and )?\s*(?i)'),
			('middle','(</td>\s*</tr>\s*<tr valign="top">\s*<td width="10%">\s*<br>\s*</td>\s*<td>\s*<br>&nbsp;&nbsp;&nbsp;&nbsp;)?(?i)'),
			('enact','(Be it (?:therefore )?enacted  ?by the Queen\'s most Excellent Majesty,? by and with the advice and consent of the Lords Spiritual and Temporal,? and Commons, in this present Parliament assembled,? and by the authority of the same,? as follows)(?:<br>|&nbsp;|:|\.|-|&#151;|\s)*</td>\s*</tr>(?i)')]

sorts='(SECTIONS|PARTS|CLAUSES)'

headlines3=[ ('contentsheading', '(?:<sup><a name="fnf1"></a><a href="#tfnf1">\[1\]</a></sup>)?<br><a name="aofr"></a>\s*<tr>\s*<td width="20%">&nbsp;</td>\s*<td>\s*<center>\s*<font size="\+1">\s*<br><br>(ARRANGEMENT OF '+sorts+')</font>\s*</center>\s*(?i)'),
	('middle','\s*<br>\s*<center>\s*(?=<table)')]

singleendmatch='<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=("?2"?|"?top"?)>\s*(<a name="end"(\s*xml\S*)*></a>)?\s*<hr(\s*xml\S*)*>\s*</td>\s*</tr>\s*<tr>(?i)'

multiendmatch='<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=("?2"?|"?top"?)>\s*<a href=\S*(\s*xml\S*)*>\s*<img src="/img/nav-conu\.gif"(?i)'

multimidendmatch='(</table>\s*<table width="100%">\s*)?<td valign=("2"|"top")>\s*<a href="\S*"(\s*xml\S*)*><img src="/img/nav-conu\.gif" align="top" alt="continue" border=("0"|"right")( width="25%")?></a>'

#<a href="\S*"><img align="top" alt="previous section" border="0" src="/img/navprev2\.gif"></a><a href="\S*"><img align="top" alt="contents" border="0" src="/img/nav-cont\.gif"></a><a name="end"></a>(?i)'

finalendmatch='(</table>\s*<table width="100%">\s*)?<tr>\s*<td valign="?top"?>&nbsp;</td>\s*<td valign=("?2"?|"?top"?)>\s*<a href="\S*"(\s*xml\S*)*>\s*<img align="top" alt="previous section" border="0" src="/img/navprev2\.gif">(?i)'

def GrabRest(aurl,nexturl):
	urlbase=re.search('(.*/)[^/]*$',aurl).group(1)
	
	singlepage=False
	pageacc=''
	#print "(nexturl=(%s) of type (%s))" % (nexturl, type(nexturl))

	scrapelist=[('first','<tr(?:\s+xml\S*)*>\s*<td colspan="2">\s*<hr>\s*</td>\s*</tr>'),
			('backbutton','\s*<tr(?:\s+xml\S*)*>\s*<td colspan="2" align="right">\s*<a href="?(\S*)"?>back to previous page</a>'),
			('middle','\s*</td>\s*</tr>\\s*(<p>)?')]

	while not singlepage:
		page=urllib.urlopen(urlbase+nexturl).read()	
		print nexturl
		(page,values)=ScrapeTool(scrapelist,page)
		contbutton=re.search('<a href="(\S*.htm)"(?:\s*xml\S*)*>\s*<img (?:\s*(?:border="?0"?|align="?top"?|src="/img/nav-conu.gif"|alt="continue")){4}(?i)',page)
		if contbutton:
			singlepage=False
			nexturl=contbutton.group(1)
			m=re.search(multimidendmatch, page)
			if m:
				pageacc=pageacc+page[:m.start()]
			else:
				print "Failed to find multimidendmatch=(%s) at:" % multimidendmatch
				print page[-128:]
				sys.exit()
		else:
			singlepage=True
			m=re.search(finalendmatch, page)
			if m:
				pageacc=pageacc+page[:m.start()]
			else:
				print "Failed to find finalendmatch=(%s) at:" % finalendmatch
				print page[-128:]
				sys.exit()
			
	return pageacc		
						

def TableBalance(tablestring):
	s=tablestring
	pos=0
	total=0
	m=re.match('<table(?i)',s)
	if not m:
		print "failed to find first table in:"
		print tablestring
		sys.exit()
	t=1
	total=m.end()

	while t>0:
		if total>=len(tablestring):
			print "error balancing table (t=%s):" % t
			print tablestring
			sys.exit()
		s=tablestring[total:]
		m=re.search('(<table|</table>)(?i)',s)
		if m:
			#print m.group(1),pos,t,total
			if re.match('<table(?i)',m.groups(1)[0]):
				t=t+1
			else:
				t=t-1
			pos=m.end()
			
		#print t,pos
		total=total+pos
	#print "****tablestring ending with:"
	#print tablestring[total-16:total]
	#print "****next begins with:"
	#print tablestring[total:total+32]
	#print
	return total		

def ScrapeTool(lines,tpg,forward=True):
	values=dict([])
	for hline in lines:
#		print "1 hline=(%s)" % hline[1]
		if hline[0] == 'first':
			mline = re.search(hline[1], tpg)
		else:
			mline = re.match(hline[1], tpg)
		if not mline:
			print 'failed at:', hline
			print 'on:'
			print tpg[:1000]
			# drop through to create exit error
#		print "2"

		#these really ought not to be here
		#preamble=''
		#date=''


		if hline[0] != 'middle':
			if len(mline.groups(0)) > 0:
				values[hline[0]]=mline.group(1)
			elif hline[0] != 'first':
				print "empty match on (%s)" % hline[0]
				print "failed on:"
				print tpg[:128]
				sys.exit()

		# extract any strings
		# (perhaps make a class that has all these fields in it)
#		if hline[0] == 'name':
#			name = mline.group(1)
		if hline[0] == 'chapt':
			chapt = mline.group(1)
			m=re.match('(\d{4})\s*(?:c\s*\.|chapter)\s*(\d+)(?i)',chapt)
			if m:
				year=m.group(1)
				chapter=m.group(2)
			else:
				print "error decoding chapter (%s), at:\n" % chapt
				print tpg[:64]
				sys.exit()
			values['year']=year
			values['chapter']=chapter
#		elif hline[0] == 'cright':
#			cright = mline.group(1)
#		elif hline[0] == 'name2':
#			name2 = mline.group(1)
		elif hline[0] == 'isbn':
			if len(mline.group(1)) == 0:
				isbn="XXXXXXXXXXX"
			else:
				isbn = "%s %s %s" % (mline.group(2), mline.group(3), mline.group(4))
			values['isbn']=isbn
#		elif hline[0] == 'prodid':
#			prodid = mline.group(1)
#		elif hline[0] == 'preamble':
#			preamble = mline.group(1)
#		elif hline[0] == 'date':
#			date = mline.group(1)
		

		# move on
		if forward:
			tpg = tpg[mline.end(0):]
		else:
			tpg = tpg[:mline.start()]

	return (tpg,values)

def ScrapeAct(aurl):
	tpg = urllib.urlopen(aurl).read()
	print aurl

	contbutton=re.search('<a href="(\S*.htm)"(?:\s*xml\S*)*>\s*<img (?:\s*(?:border="?0"?|align="?top"?|src="/img/nav-conu.gif"|alt="continue")){4}(?i)',tpg)

	arrsections=re.search('<center>.*ARRANGEMENT OF '+sorts+'.*</center>(?si)',tpg)

	if arrsections:
		istoc=True
		headlines=headlines1+headlines3
	else:
		istoc=False
		headlines=headlines1
		
	if contbutton:
		singlepage=False
		nextpage=contbutton.group(1)
	else:
		singlepage=True
		assert(istoc==False)

	if singlepage:
		print "***singlepage***"
	else:
		#print "nextpage=%s" % nextpage
		if istoc==False:
			print "***multiple pages, no table of contents"


	(tpg,values)=ScrapeTool(headlines,tpg)

	name=values['name']
	name2=values['name2']
	isbn=values['isbn']
	chapt=values['chapt']
	prodid=values['prodid']
	cright=values['cright']

	if name != name2:
		print "--------------------mismatching names, /%s/ <> /%s/" % (name, name2)
	if isbn=="XXXXXXXXXXX":
		print "--------------------missing ISBN"

	# chop out the table of contents if its there
	if istoc:
		endtable=TableBalance(tpg)
		#print endtable
		#print "chopping, before:"
		#print tpg[:64]
		tpg=tpg[endtable:]
		#print "chopping, after:"
		#print tpg[:64]
		(tpg,discard1)=ScrapeTool([('middle','\s*</center>')],tpg)

	m=re.match('\s*<center>\s*(?=<table)',tpg)
	if m:
		print "*****additional tables of contents"
		tpg=tpg[m.end():]
		endtable=TableBalance(tpg)
		tpg=tpg[endtable:]
		(tpg,discard2)=ScrapeTool([('middle','\s*</center>\s*')],tpg)

	if istoc:
		(tpg,discard3)=ScrapeTool([('middle','\s*<br><br><br><br>\s*</td>\s*</tr>\s*')],tpg)

	print chapt, name, prodid 

	# this is for debugging
	print tpg[:32]
	if re.search('<i>notes:</i>(?i)',tpg):
		print "****suspected footnote"
		(x1,x2)=ScrapeTool([('first','<tr>\s*<td WIDTH="20%">&nbsp;</td>(?i)'),
			('middle','\s*<td>\s*<br>\s*<hr>\s*<i>notes:</i><br><br>\s*<p>\s*<a name="tcnc1">(?i)'),
		('middle','\[1\]</a>(<b>)?(\[)?([a-zA-Z\.,;\s]*)(\])?\s*(</b>)?\s*<a href="#cnc1">back</a>(?i)'),
		('middle','\s*</p>\s*</td>\s*</tr>\s*(<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>)(?i)')],tpg)

	m=re.search('<tr>\s*<td WIDTH="20%">&nbsp;</td>\s*<td>\s*<br>\s*<hr>\s*<i>notes:</i><br><br>\s*<p>\s*<a name="tcnc1">\[1\]</a>(<b>)?(\[)?([a-zA-Z\.,;\s]*)(\])?\s*(</b>)?\s*<a href="#cnc1">back</a>\s*</p>\s*</td>\s*</tr>\s*(<tr>\s*<td width="10%">&nbsp;</td>\s*</tr>)(?i)',tpg)
	if m:
		tpg=tpg[:m.start()]+tpg[m.end():]
		print "****footnote found"

	if singlepage:
			m=re.search(singleendmatch, tpg)
			if m:
				tpg=(tpg[:m.start()])
			else:
				print "Failed to find singleendmatch=(%s) at:" % endmatch
				print tpg[-128:]
				sys.exit()
	else:
			m=re.search(multiendmatch, tpg)
			if m:
				tpg=(tpg[:m.start()])
			else:
				print "Failed to find multiendmatch=(%s) at:" % multiendmatch
				print tpg[:180]
				sys.exit()
			page=GrabRest(aurl,nextpage)
			tpg=tpg+page

	logfile=file("log","w")
	logfile.write(tpg)
	(tpg,values2)=ScrapeTool(headlines2,tpg)
	preamble=values2['preamble']
	enact=values2['enact']
	date=values2['date']
	print preamble, date

	if not os.path.exists(actdir):
		os.mkdir(actdir)

	year=values['year']
	chapter=values['chapter']
	#title=values['title']

	if not os.path.exists(actdir + "/" + year):
		os.mkdir(actdir + "/" + year)

	actfile=file(actdir + "/" + year + "/" + chapter + ".xml", "w")
	OutputHeader(actfile, [("title",name),
		("url",aurl),
		("year",year),
		("chapter_number",chapter),
		("preamble",preamble),
		("date",date),
		("words_of_enactment",enact),
		("isbn",isbn)])
	
	actfile.write(tpg)

	OutputFooter(actfile)

	return (cright, chapt, name, aurl)


def OutputHeader(actfile, tags):
	actfile.write("<html>\n")
	actfile.write('<head>\n<meta name="lawparseroptions">\n')
	for p in tags:
		if p:
			actfile.write("<" + str(p[0]) + ">" + str(p[1]) + "</" + str(p[0]) + ">\n")
		else:
			print "*****unable to write",p[0],"or",p[1]
	actfile.write("</meta>\n")
	actfile.write("</head>\n")
	actfile.write("<body>\n")
	actfile.write('<table width="95%" cellpadding="2">\n')

def OutputFooter(actfile):
	actfile.write("</body></html>")	

def GetActsFromYear(iyurl):
	pg = urllib.urlopen(iyurl).read()
	mpubact = re.search("<h4>Alphabetical List</h4>([\s\S]*?)<h4>Numerical List</h4>", pg)
	alphacts = mpubact.group(1)
	eachacts = re.findall('<a href="([^"]*)">([^<]*)</a>', alphacts)
	res = [ ]
	for eact in eachacts:
		if re.match("acts\d{4}/[\d\-_\w]*\.htm$", eact[0]):
			assert re.match("[\w\d\s\.,'\-()]*$", eact[1])
			res.append(urlparse.urljoin(iyurl, eact[0]))
		else:
			assert re.match("\#num|.*\.pdf", eact[0])
	return res



def GetYearIndexes(iurl):
	pg = urllib.urlopen(iurl).read()
	mpubact = re.search("<h3>Full text Public Acts</h3>([\s\S]*?)<h3>Full text\s*Local Acts</h3>", pg)
	pubacts = mpubact.group(1)
	yearacts = re.findall('<a href="(acts/acts\d{4}.htm)">(\d{4})\s*</a>', pubacts)

	res = [ ]
	for yact in yearacts:
		assert re.search('\d{4}', yact[0]).group(0) == yact[1]
		res.append(urlparse.urljoin(iurl, yact[0]))
	return res


#res=ScrapeAct('http://www.opsi.gov.uk/acts/acts1988/Ukpga_19880046_en_1.htm')
#sys.exit


# main running part
# just collects links to all the first pages
# then extracts name and chapter from the page itself
yiurl = GetYearIndexes(iurl)
allacts = [ ]
#yiurl = yiurl[2:8]
for yiur in yiurl:
	allacts.extend(GetActsFromYear(yiur))
print "lenlen", len(allacts)
fout = open("listacts1.xml", "w")
i = 0    # numbering helps work out where to restart for error examining
allacts.reverse()
for aurl in allacts[130:]:  # start in middle when chasing an error
	res = ScrapeAct(aurl)
	print i, res
	fout.write('<act year="%s" chapter="%s"\tname="%s" url="%s">\n' % res)
	fout.flush()
	i += 1
fout.close()


#130