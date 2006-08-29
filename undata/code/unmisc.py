import re

undoclinks = "http://seagrass.goatchurch.org.uk/~undocs/cgi-bin/getundoc.py?doc="

bQuiet = False
def IsNotQuiet():
	return not bQuiet
def SetQuiet(lbQuiet):
	global bQuiet
	bQuiet = lbQuiet


def MarkupLinks(paratext):
	stext = re.split("(A/\d+/[\w\d\.]*?\d+(?:/(?:Add|Rev)\.\d+)?|resolution \d+/\d+|</b>\s*<b>|</i>\s*<i>)(?!=\s)", paratext)
	res = [ ]
	for st in stext:
		mres = re.match("resolution (\d+/\d+)", st)
		mdoc = re.match("A/\d+/\S*", st)
		mcan = re.match("</b>\s*<b>|</i>\s*<i>", st)
		if mres:
			res.append('<a href="%sA/RES/%s">%s</a>' % (undoclinks, mres.group(1), st))
		elif mdoc:
			res.append('<a href="%s%s">%s</a>' % (undoclinks, st, st))
		elif mcan:
			res.append(' ')
		else:
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



