import re
import os

class unexception(Exception):
	def __init__(self, description, lparanum):
		self.description = description
		self.paranum = lparanum

	def __str__(self):
		ret = ""
		if self.fragment:
			ret = ret + "Fragment: " + self.paranum + "\n\n"
		ret = ret + self.description + "\n"
		return ret


undoclinks = "../pdf/"

pdfdir = os.path.join("..", "pdf")
pdfxmldir = os.path.join("..", "pdfxml")
htmldir = os.path.join("..", "html")
sCallScrape = None  # set by one of the

bQuiet = False
def IsNotQuiet():
	return not bQuiet
def SetQuiet(lbQuiet):
	global bQuiet
	bQuiet = lbQuiet
def SetCallScrape(lsCallScrape):
	global sCallScrape
	sCallScrape = lsCallScrape

reressplit = """(?x)(
				A/\d+/[\w\d\.]*?\d+(?:/(?:Add|Rev)\.\d+)?|
				resolution\s\d+/\d+|
				(?:resolution\s)?\d+\s\(\d+\)|
				</b>\s*<b>|
				</i>\s*<i>
				)(?!=\s)"""

from unscrape import ScrapePDF

def MakeCheckLink(ref, link):
	fpdf = os.path.join("..", "pdf", ref) + ".pdf"
	if not os.path.isfile(fpdf):
		if not sCallScrape or not ScrapePDF(ref):
			return '<a class="nolink" href="%s%s">%s</a>' % (undoclinks, ref, link)
		assert os.path.isfile(fpdf)
	return '<a href="%s%s.pdf">%s</a>' % (undoclinks, ref, link)

def MarkupLinks(paratext):
	stext = re.split(reressplit, paratext)
	res = [ ]
	for st in stext:   # don't forget to change the splitting regexp above
		mres = re.match("resolution (\d+)/(\d+)", st)
		mdoc = re.match("A/(\d+)/(\S*)", st)
		msecres = re.match("(?:resolution )?(\d{3,4}) \(((?:19|20)\d\d)\)", st)
		mcan = re.match("</b>\s*<b>|</i>\s*<i>", st)
		if mres:
			res.append(MakeCheckLink("A-RES-%s-%s" % (mres.group(1), mres.group(2)), st))
		elif mdoc:
			doccode = re.sub("/", "-", mdoc.group(2))
			res.append(MakeCheckLink("A-%s-%s" % (mdoc.group(1), doccode), st))
		elif msecres:
			res.append(MakeCheckLink("S-RES-%s(%s)" % (msecres.group(1), msecres.group(2)), st))
		elif mcan:
			res.append(' ')
		else:
			assert not re.match(reressplit, paratext)
			res.append(st)
	return "".join(res)




# used for exceptions and for generating ids
class paranumC:
	def __init__(self, undocname, sdate, pageno, paragraphno, textcountnumber):
		self.undocname = undocname
		self.sdate = sdate
		self.pageno = pageno
		self.paragraphno = paragraphno
		self.textcountnumber = textcountnumber

	def MakeGid(self):
		return "pg%03d-bk%02d" % (int(self.pageno), self.blockno)

