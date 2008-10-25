#! /usr/bin/env python2.4

import re
import os
import glob
import sys
import time
import tempfile
import shutil
import xml.sax
xmlvalidate = xml.sax.make_parser()

sys.path.append('../')
from resolvemembernames import memberList
from contextexception import ContextException
from BeautifulSoup import BeautifulSoup, Tag
from patchtool import RunPatchTool

import codecs
streamWriter = codecs.lookup('utf-8')[-1]
sys.stdout = streamWriter(sys.stdout)

parldata = '../../../parldata/'

class NISoup(BeautifulSoup):
	# Oh yes, did anyone ever say that I totally ROCK?
	BeautifulSoup.RESET_NESTING_TAGS['b'] = None
	BeautifulSoup.RESET_NESTING_TAGS['i'] = None
	BeautifulSoup.RESET_NESTING_TAGS['font'] = None
	# FrontPage just loves to do things totally wrong
	myMassage = [
		# Remove gumph
		(re.compile('</?center>|<font SIZE="3">'), lambda match: ''),
		# Swap elements that are clearly the wrong way round
		(re.compile('(<p[^>]*>)\s*((</(font|i|b)>)+)'), lambda match: match.group(2) + match.group(1)),
		(re.compile('(<p[^>]*>)\s*(<b>)'), lambda match: match.group(2) + match.group(1)),
		(re.compile('((<(font|i|b)>)+)\s*(</p[^>]*>)'), lambda match: match.group(3) + match.group(1)),
		(re.compile('(<b>)\s*(<p[^>]*>)([^<]*?</b>)'), lambda match: match.group(2) + match.group(1) + match.group(3)),
	]

def ApplyPatches(filein, fileout, patchfile):
	shutil.copyfile(filein, fileout)
	status = os.system("patch --quiet %s <%s" % (fileout, patchfile))
	if status == 0:
		return True
	print "blanking out failed patch %s" % patchfile
	print "---- This should not happen, therefore assert!"
	assert False

class ParseDay:
	def id(self):
		return '%s.%s.%s' % (self.date, self.idA, self.idB)

	def parse_day(self, date):
		self.date = date

		# Special case for 2002-10-08
		if not re.search('i$', date):
			self.idA = 0
			self.idB = 0

		filename = '%scmpages/ni/ni%s.html' % (parldata, date)
		patchfile = '%spatches/ni/ni%s.html.patch' % (parldata, date)
		if os.path.isfile(patchfile):
			patchtempfilename = tempfile.mktemp("", "ni-applypatchtemp-", '%stmp/' % parldata)
			ApplyPatches(filename, patchtempfilename, patchfile)
			filename = patchtempfilename
		fp = open(filename)
		soup = NISoup(fp, markupMassage=NISoup.myMassage)
		fp.close()
		#print soup.prettify().decode('utf-8')
		#sys.exit()
		tempfilename = '%sscrapedxml/ni/ni%s.xml.new' % (parldata, date)
		self.out = open(tempfilename, 'w')
		self.out = streamWriter(self.out)
		self.out.write('<?xml version="1.0" encoding="utf-8"?>\n')
		self.out.write('''
<!DOCTYPE publicwhip
[
<!ENTITY pound   "&#163;">
<!ENTITY euro    "&#8364;">

<!ENTITY agrave  "&#224;">
<!ENTITY aacute  "&#225;">
<!ENTITY egrave  "&#232;">
<!ENTITY eacute  "&#233;">
<!ENTITY ecirc   "&#234;">
<!ENTITY iacute  "&#237;">
<!ENTITY ograve  "&#242;">
<!ENTITY oacute  "&#243;">
<!ENTITY uacute  "&#250;">
<!ENTITY Aacute  "&#193;">
<!ENTITY Eacute  "&#201;">
<!ENTITY Iacute  "&#205;">
<!ENTITY Oacute  "&#211;">
<!ENTITY Uacute  "&#218;">
<!ENTITY Uuml    "&#220;">
<!ENTITY auml    "&#228;">
<!ENTITY euml    "&#235;">
<!ENTITY iuml    "&#239;">
<!ENTITY ntilde  "&#241;">
<!ENTITY ouml    "&#246;">
<!ENTITY uuml    "&#252;">
<!ENTITY fnof    "&#402;">

<!ENTITY nbsp    "&#160;">
<!ENTITY shy     "&#173;">
<!ENTITY deg     "&#176;">
<!ENTITY sup2    "&#178;">
<!ENTITY middot  "&#183;">
<!ENTITY ordm    "&#186;">
<!ENTITY frac14  "&#188;">
<!ENTITY frac12  "&#189;">
<!ENTITY frac34  "&#190;">
<!ENTITY ndash   "&#8211;">
<!ENTITY mdash   "&#8212;">
<!ENTITY lsquo   "&#8216;">
<!ENTITY rsquo   "&#8217;">
<!ENTITY ldquo   "&#8220;">
<!ENTITY rdquo   "&#8221;">
<!ENTITY hellip  "&#8230;">
<!ENTITY bull    "&#8226;">
]>

<publicwhip>
''')
		if re.match('200[6789]', date):
			self.parse_day_new(soup)
		else:
			body = soup('p')
			self.parse_day_old(body)
		self.out.write('</publicwhip>\n')
		self.out.close()

		# Check the XML; in win32 this function leaves the file open and stops it being renamed
		if sys.platform != "win32":
			xmlvalidate.parse(tempfilename) # validate XML before renaming
		os.rename(tempfilename, '%sscrapedxml/ni/ni%s.xml' % (parldata, date))

	def display_speech(self):
		if self.text:
			if self.speaker[0]:
				speaker_str = self.speaker[0]
			else:
				speaker_str = 'nospeaker="true"'
			timestamp = self.speaker[1]
			if timestamp:
				timestamp = ' time="%s"' % timestamp
			self.idB += 1
			self.out.write('<speech id="uk.org.publicwhip/ni/%s" %s%s url="%s">\n%s</speech>\n' % (self.id(), speaker_str, timestamp, self.url, self.text))
			self.text = ''
	
	def display_heading(self, text, timestamp, type):
		if timestamp:
			timestamp = ' time="%s"' % timestamp
		self.out.write('<%s-heading id="uk.org.publicwhip/ni/%s"%s url="%s">%s</%s-heading>\n' % (type, self.id(), timestamp, self.url, text, type))

	def parse_day_old(self, body):
		match = re.match('\d\d(\d\d)-(\d\d)-(\d\d)(i?)$', self.date)
		urldate = '%s%s%s%s' % match.groups()
		self.baseurl = 'http://www.niassembly.gov.uk/record/reports/%s.htm' % urldate
		self.url = self.baseurl

		# Heading check
		if not re.match('Northern\s+Ireland\s+Assembly', body[0].find(text=True)):
			raise Exception, 'Missing NIA heading!'
		date_head = body[1].find(text=True)
		if not re.match('Contents', body[2].find(text=True)):
			raise Exception, 'Missing contents heading!'
		body = body[3:]
	
		timestamp = ''
		in_oral_answers = False
		oral_qn = 0
		self.speaker = (None, timestamp)
		self.text = ''
		for p in body:
			if not p(text=True): continue
			ptext = re.sub("\s+", " ", ''.join(p(text=True)))
			phtml = re.sub("\s+", " ", p.renderContents()).decode('utf-8')
			#print phtml
			if (p.a and p.a.get('href', ' ')[0] == '#') or (p.a and re.match('\d', p.a.get('href', ''))) or ptext=='&nbsp;':
				continue
			if p.findParent('i'):
				match = re.match('(\d\d?)\.(\d\d) (a|p)m', ptext)
				if match:
					hour = int(match.group(1))
					if hour<12 and match.group(3) == 'p':
						hour += 12
					timestamp = "%s:%s" % (hour, match.group(2))
					continue
				#if self.speaker[0]:
				#	display_speech()
				#	self.speaker = (None, timestamp)
				match = re.search('(?:\(|\[)(?:Mr|Madam) Deputy Speaker (?:\[|\()(.*?)(?:\]|\))', phtml)
				if match:
					#print "Setting deputy to %s" % match.group(1)
					memberList.setDeputy(match.group(1))
				match = re.match('The Assembly met at (\d\d\.\d\d|noon)', phtml)
				if match:
					if match.group(1) == 'noon':
						timestamp = '12:00'
					else:
						timestamp = match.group(1)
					self.speaker = (self.speaker[0], timestamp)
				self.text += '<p class="italic">%s</p>\n' % phtml
				continue
			if p.findParent('font', size=1):
				self.text += '<p class="small">%s</p>\n' % phtml
				continue
			if (p.get('align', '') == 'center' and (p.b or p.parent.name == 'b')) or (p.parent.name == 'b' and re.search('Stage$', ptext)):
				self.display_speech()
				self.speaker = (None, timestamp)
				aname = p.a and p.a.get('name', '')
				if ptext == 'Oral Answers':
					self.out.write('<oral-heading>\n')
					in_oral_answers = True
					if aname and re.match('#?\d+$', aname):
						self.idA = int(re.match('#?(\d+)$', aname).group(1))
						self.idB = 0
						self.url = '%s#%s' % (self.baseurl, aname)
				elif aname and re.match('#?\d+$', aname):
					if in_oral_answers:
						self.out.write('</oral-heading>\n')
						in_oral_answers = False
					self.idA = int(re.match('#?(\d+)$', aname).group(1))
					self.idB = 0
					self.url = '%s#%s' % (self.baseurl, aname)
					self.display_heading(ptext, timestamp, 'major')
				elif aname:
					self.idB += 1
					self.display_heading(ptext, timestamp, 'major')
				else:
					self.idB += 1
					self.display_heading(ptext, timestamp, 'minor')
				continue
			elif p.b or p.parent.name == 'b':
				if p.b:
					new_speaker = p.b.find(text=True)
				else:
					new_speaker = ptext
				if not re.match('\s*$', new_speaker):
					self.display_speech()
					speaker = re.sub("\s+", " ", new_speaker).strip()
					speaker = re.sub(':', '', speaker)
					id, str = memberList.match(speaker, date)
					self.speaker = (str, timestamp)
				if p.b and p.b.nextSibling:
					p.b.extract()
					phtml = re.sub("\s+", " ", p.renderContents()).decode('utf-8')
					self.text += "<p>%s</p>\n" % phtml
				continue
			match = re.match('(\d+)\.$', phtml)
			if match:
				oral_qn = match.group(1)
				continue
			if p.a and re.match('#\d+$', p.a.get('name', '')):
				raise ContextException, 'Uncaught title!'
			if re.match('Mr\w*(\s+\w)?\s+\w+:$', phtml):
				raise ContextException, 'Uncaught speaker! ' + phtml
			if oral_qn:
				phtml = "%s. %s" % (oral_qn, phtml)
				oral_qn = 0
			self.text += "<p>%s</p>\n" % phtml
		self.display_speech()
		if in_oral_answers:
			self.out.write('</oral-heading>\n')
			in_oral_answers = False

	def parse_day_new(self, soup):
		for s in soup.findAll(lambda tag: tag.name=='strong' and tag.contents == []):
			s.extract()

		body = soup('p')
		self.url = ''

		if not re.match('(THE\s+)?(transitional(<br>)?\s+)?(Northern\s+Ireland\s+)?ASSEMBLY(?i)', ''.join(body[0](text=True))):
			raise ContextException, 'Missing NIA heading!'
		date_head = body[1].find(text=True)
		body = body[2:]
		timestamp = ''
		self.speaker = (None, timestamp)
		self.text = ''
		for p in body:
			ptext = re.sub("\s+", " ", ''.join(p(text=True)))
			phtml = re.sub("\s+", " ", p.renderContents()).decode('utf-8')
			#print p, "\n---------------------\n"
			if p.a and re.match('[^h/]', p.a.get('href', '')):
				continue
			if ptext == '&nbsp;':
				continue
			cl = p['class']
			cl = re.sub(' style\d', '', cl)

			if cl == 'OralWrittenQuestion':
				cl = 'B1SpeakersName'
			if cl == 'OralWrittenAnswersHeading':
				cl = 'H3SectionHeading'
			if cl == 'B3BodyText' and (phtml[0:8] == '<strong>' or re.match('\d+\.( |&nbsp;)+<strong>', phtml)):
				cl = 'B1SpeakersName'
			if cl == 'TimePeriod' and re.search('in the chair(?i)', phtml):
				cl = 'B3SpeakerinChair'
			if p.em and len(p.contents) == 1:
				cl = 'B3BodyTextItalic'

			if cl == 'H3SectionHeading':
				self.display_speech()
				self.speaker = (None, timestamp)
				self.idA += 1
				self.idB = 0
				self.display_heading(ptext, timestamp, 'major')
			elif cl == 'H4StageHeading' or cl == 'H5StageHeading':
				self.display_speech()
				self.speaker = (None, timestamp)
				self.idB += 1
				self.display_heading(ptext, timestamp, 'minor')
			elif cl == 'B1SpeakersName':
				self.display_speech()
				m = re.match('.*?:', phtml)
				if not p.strong and m:
					newp = Tag(soup, 'p', [('class', 'B1SpeakersName')])
					newspeaker = Tag(soup, 'strong')
					newspeaker.insert(0, m.group())
					newp.insert(0, phtml.replace(m.group(), ''))
					newp.insert(0, newspeaker)
					p = newp
				speaker = p.strong.find(text=True)
				speaker = re.sub('&nbsp;', '', speaker)
				speaker = re.sub("\s+", " ", speaker).strip()
				speaker = re.sub(':', '', speaker)
				id, str = memberList.match(speaker, date)
				self.speaker = (str, timestamp)
				p.strong.extract()
				phtml = p.renderContents()
				phtml = re.sub('^:\s*', '', phtml)
				phtml = re.sub("\s+", " ", phtml).decode('utf-8')
				self.text += "<p>%s</p>\n" % phtml
			elif cl == 'B3BodyTextItalic' or cl == 'Q3Motion' or cl == 'AyesNoes' or cl == 'AyesNoesParties' or cl == 'AyesNoesVotes' or cl == 'D3PartyMembers' or cl == 'B3SpeakerinChair':
				match = re.match('The Assembly met at ((\d\d?)\.(\d\d) (am|pm)|noon)', phtml)
				if match:
					if match.group(1) == 'noon':
						timestamp = '12:00'
					else:
						hour = int(match.group(2))
						if hour<12 and match.group(4) == 'pm':
							hour += 12
						timestamp = "%s:%s" % (hour, match.group(3))
					self.speaker = (self.speaker[0], timestamp)
				match = re.search('\(((?:Mr|Madam) Speaker)', ptext)
				if not match:
					match = re.search('\(Mr Deputy Speaker \[(.*?)\]', ptext)
				if match:
					#print "Setting deputy to %s" % match.group(1)
					memberList.setDeputy(match.group(1))
				self.text += '<p class="italic">%s</p>\n' % phtml
			elif cl == 'Q3MotionBullet':
				self.text += '<p class="indentitalic">%s</p>\n' % phtml
			elif cl == 'B3BodyText' or cl == 'B3BodyTextnoindent' or cl == 'RollofMembersList':
				self.text += '<p>%s</p>\n' % phtml
			elif cl == 'Q1QuoteIndented' or cl == 'Q1Quote':
				self.text += '<p class="indent">%s</p>\n' % phtml
			elif cl == 'TimePeriod':
				match = re.search('(\d\d?)\.\s*(\d\d) ?(am|pm|noon)', ptext)
				hour = int(match.group(1))
				if hour<12 and match.group(3) == 'pm':
					hour += 12
				timestamp = "%s:%s" % (hour, match.group(2))
			elif cl == 'MsoNormal':
				continue
			else:
				raise ContextException, 'Uncaught paragraph! %s' % cl
		self.display_speech()


# Main function
quiet = False
force = False
patchtool = False
if len(sys.argv)==2 and sys.argv[1] == '--patchtool':
	patchtool = True
g = glob.glob('%scmpages/ni/ni*.html' % parldata)
g.sort()
parser = ParseDay()
for file in g:
	m = re.match('%scmpages/ni/ni(.*?).html' % parldata, file)
	date = m.group(1)
	outfile = '%sscrapedxml/ni/ni%s.xml' % (parldata, date)
	parsefile = not os.path.isfile(outfile) or force
	while parsefile:
		try:
			print "NI parsing %s..." % date
			parser.parse_day(date)
			fil = open('%sscrapedxml/ni/changedates.txt' % parldata, 'a+')
			fil.write('%d,ni%s.xml\n' % (time.time(), date))
			fil.close()
			break
		except ContextException, ce:
			if patchtool:
				print "Problem parsing...", ce
				RunPatchTool('ni', date, ce)
				continue
			elif quiet:
				print ce.description
				print "\tERROR! Failed on %s, quietly moving to next day" % (date)
				break
			else:
				raise
