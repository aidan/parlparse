import os
import re
import sys
from nations import FixNationName, nonnations
from unmisc import unexception, IsNotQuiet, MarkupLinks, paranumC
from unglue import GlueUnfile
from speechblock import SpeechBlock
from voteblock import VoteBlock, recvoterequest


class UndocData:
	def __init__(self, undocname, undocfile):
		fin = open(undocfile)
		fd = fin.read()
		fin.close()

		mhead = re.search('<span class="code">([^<]*)</span> <span class="date">([^<]*)</span> <span class="time">([^<]*)</span>', fd)
		if not mhead:
			self.code = ""
			return

		self.code = mhead.group(1)  # same as the title from undocname
		self.date = mhead.group(2)
		self.time = mhead.group(3)
		self.kbytes = len(fd) / 1024.0
		self.pages = int(re.findall('id="pg(\d+)-', fd)[-1])
		self.votes = len(re.findall('<div class="(recvote)"', fd))
		self.links = re.findall('<a href="\.\./pdf/([^"]*?)\.pdf"(?: class="(nolink)")?>', fd)
		lspeakers = re.findall('<span class="name">([^<]*)</span> <span class="nation">([^<]*)</span>', fd)
		lspeakers.sort()
		self.speakers = [ ]
		for s in lspeakers:
			if (not self.speakers or (s != self.speakers[-1])) and not re.search("President", s[0]):
				self.speakers.append((s[1], s[0]))

	def GetRow(self):
		res = [ ]
		res.append("<tr>")
		res.append("<td>%s</td> <td>%s</td>" % (self.date, self.time))
		res.append("<td>%s</td>" % (self.code))
		res.append("<td>%d</td>" % (self.pages))
		res.append("<td>%d</td>" % len(self.speakers))
		res.append("<td>%d</td>" % len(self.links))
		res.append("</tr>")
		return "".join(res)

	def GetHeadRow(self):
		res = [ ]
		res.append("<tr>")
		res.append("<th>date</th> <th>time</th>")
		res.append("<th>code</th>")
		res.append("<th>pages</th>")
		res.append("<th>speakers</t>")
		res.append("<th>links</th>")
		res.append("</tr>")
		return "".join(res)


# generates date index table, useful for look-ups
# generates document lists
def MiscIndexFiles(htmldir):

	# sort out the index/unindexed repeats
	undocmap = { }
	for undoc in os.listdir(htmldir):
		mrecdoc = re.match("(A-\d\d-PV\.\d+(?:.*?\d)?|S-PV-\d\d\d\d(?:.*?\d)?)(\.unindexed)?\.html$", undoc)
		if not mrecdoc:
			print undoc
			assert re.search("\.css|index|\.svn", undoc)
			continue
		undocname =  mrecdoc.group(1)
		lundoc = os.path.join(htmldir, undoc)
		if mrecdoc.group(2):
			undocmap[undocname] = lundoc
		elif undocname not in undocmap:
			undocmap[undocname] = lundoc

	undocdatelist = [ ]
	for undocname in undocmap.keys():
		lundocdata = UndocData(undocname, undocmap[undocname])
		if not lundocdata.code:
			continue
		undocdatelist.append(((lundocdata.date, lundocdata.time), lundocdata))
	undocdatelist.sort()


	undateindex = os.path.join(htmldir, "dateindex.html")
	tmpfile = undateindex + "--temp"
	fout = open(tmpfile, "w")
	fout.write('<html>\n<head>\n')
	fout.write('<link href="unview.css" type="text/css" rel="stylesheet" media="all">\n')
	fout.write('</head>\n<body>\n')
	fout.write('<table>\n')

	fout.write(undocdatelist[0][1].GetHeadRow())
	fout.write('\n')
	for undocdate in undocdatelist:
		fout.write(undocdate[1].GetRow())
		fout.write('\n')
	fout.write('</table>\n')
	fout.write('</body>\n</html>\n')
	fout.close()

	if os.path.isfile(undateindex):
		os.remove(undateindex)
	os.rename(tmpfile, undateindex)

