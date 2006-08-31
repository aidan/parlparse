import re
import os

undoclinks = "http://seagrass.goatchurch.org.uk/~undocs/cgi-bin/getundoc.py?doc="
undoclinks = "../pdf/"

bQuiet = False
def IsNotQuiet():
	return not bQuiet
def SetQuiet(lbQuiet):
	global bQuiet
	bQuiet = lbQuiet


reressplit = """(?x)(
				A/\d+/[\w\d\.]*?\d+(?:/(?:Add|Rev)\.\d+)?|
				resolution\s\d+/\d+|
				(?:resolution\s)?\d+\s\(\d+\)|
				</b>\s*<b>|
				</i>\s*<i>
				)(?!=\s)"""

def MakeCheckLink(ref, link):
	fpdf = os.path.join("../pdf", ref) + ".pdf"
	if os.path.isfile(fpdf):
		return '<a href="%s%s.pdf">%s</a>' % (undoclinks, ref, link)
	return '<a class="nolink" href="%s%s">%s</a>' % (undoclinks, ref, link)

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
			res.append(MakeCheckLink("A-%s-%s" % (mdoc.group(1), mdoc.group(2)), st))
		elif msecres:
			res.append(MakeCheckLink("S-RES-%s-%s" % (msecres.group(1), msecres.group(2)), st))
		elif mcan:
			res.append(' ')
		else:
			assert not re.match(reressplit, paratext)
			res.append(st)
	return "".join(res)


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


# used for exceptions and for generating ids
class paranumC:
	def __init__(self, undocname, sdate, pageno, paragraphno, textcountnumber):
		self.undocname = undocname
		self.sdate = sdate
		self.pageno = pageno
		self.paragraphno = paragraphno
		self.textcountnumber = textcountnumber

	def MakeGid(self):
		return "%d-%d" % (self.pageno, self.paragraphno)

