import re
import os
import datetime

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


undocpdflinks = "../pdf"
undochtmllinks = "../html"

pdfdir = os.path.join("..", "..", "undata", "pdf")
pdfxmldir = os.path.join("..", "..", "undata", "pdfxml")
htmldir = os.path.join("..", "..", "undata", "html")
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
                ECESA/1/Rev.1|
                (?:[Dd]ocument\s)?A/(?:[A-Z][\.\d]*/)?\d+/[\w\d\.]*?[l\d]+(?:/(?:Add|Rev)\.[l\d]+)?|
                A/RES/\d+/\d+|
                A/(?:CONF|INF)[\./]\d+/\d+(?:/Add.[l\d])?|
                GC\([LXIV]*\)/RES/\d+|
                SG/SM/\d+|
                AG/\d+|
                Economic\sand\sSocial\sCouncil\sdecision\s\d+/\d+|
                decision\s\d\d/\d+(?!\sof\sthe\sCommission)|
                (?:[Dd]ocument\s)?S/\d+/\d+(?:/Add\.\d+)?|
                (?:[Dd]ocument\s)?S/\d{5,6}|
                S/PRST/\d+/\d+|
                S/PV\.\d+|
                (?:General\sAssembly\s|Economic\sand\sSocial\sCouncil\s)?[Rr]esolutions?\s\d+/[\dCLXVI]+|
                (?:the )?resolution\s\(\d\d/\d+\)|
                (?:Security\sCouncil\s)?(?:[Rr]esolutions?\s)?\d+\s\(\d\d\d\d\)|
                Corr.\d|
                (?<=\s)[3-6]\d/\d\d\d?(?=[\s,\.])|
                </b>\s*<b>|
                </i>\s*<i>
                )(?!=\s)"""

from unscrape import ScrapePDF

# the file maintaining the links we cannot scrape
faileddoclinkfile = "faileddoclinks.txt"
fin = open(faileddoclinkfile)
faileddoclinks = [ re.search("file=(\S+)", fd).group(1)  for fd in fin.readlines()  if not re.match("\s*$", fd) ]
fin.close()
faileddoclinks = [ ]


# the file maintaining the pairs of links; from documents to their sources
pdfbacklinksfile = "pdfbacklinks.html"
def pdfbacklinkform(pr):
    #print pr
    if len(pr) != 2:
        print "ERROR", pr
    return '<tr><td><a href="%s/%s.pdf">%s</a></td> <td><a href="%s/%s.unindexed.html">%s</a></td></td>\n' % (pdfdir, pr[0], pr[0], htmldir, pr[1], pr[1])

finbacklinks = [ ]
if os.path.isfile(pdfbacklinksfile):
    fin = open(pdfbacklinksfile)
    finbacklinks = [ tuple(re.findall('>([\w\.\-\d()]*)</a>', fd))  for fd in fin.readlines()  if not re.match("(?:\s|<table>)*$", fd) ]
    fin.close()

finbacklinks.sort()
fout = open(pdfbacklinksfile, "w")
fout.write("<table>\n")
for pr in finbacklinks:
    fout.write(pdfbacklinkform(pr))
fout.close()


def MakeCheckLink(ref, link, undocname, bRecurse=False):
    global faileddoclinks
    pr = (ref, undocname)
    if pr not in finbacklinks:
        fout = open(pdfbacklinksfile, "a")
        fout.write(pdfbacklinkform(pr))
        fout.close()
        finbacklinks.append(pr)

    fhtml = os.path.join(htmldir, "%s.html" % ref)
    if os.path.isfile(fhtml):
        assert link not in faileddoclinks
        return '<a href="%s/%s.html">%s</a>' % (undochtmllinks, ref, link)

    fpdf = os.path.join(pdfdir, "%s.pdf" % ref)
    if os.path.isfile(fpdf):
        return '<a href="%s/%s.pdf" class="pdf">%s</a>' % (undocpdflinks, ref, link)

    fpdfsupp = os.path.join(pdfdir, "%s(SUPP).pdf" % ref)
    if os.path.isfile(fpdfsupp):
        return '<a href="%s/%s(SUPP).pdf" class="pdf">%s</a>' % (undocpdflinks, ref, link)

    assert not bRecurse
    bknownfaileddoc = ref in faileddoclinks
    if sCallScrape and (not bknownfaileddoc) and (ScrapePDF(ref) or (False and re.match("S-(\d\d\d\d)-(\d+)", ref) and ScrapePDF("%s(SUPP)" % ref))):
        return MakeCheckLink(ref, link, undocname, True)

    if sCallScrape and (not bknownfaileddoc) and (not re.match("A-[56]\d-PV|S-[3-9]\d\d\d-PV", undocname)):
        fout = open(faileddoclinkfile, "a")
        fout.write("undocname=%s\t\tfile=%s\n" % (undocname, ref))
        fout.close()
        faileddoclinks.append(ref)
    return '<a href="%s/%s.pdf" class="nolink">%s</a>' % (undocpdflinks, ref, link)


def MarkupLinks(paratext, undocname, paranum):
    stext = re.split(reressplit, paratext)
    res = [ ]
    link = ""  # used for finding corragendas
    for st in stext:   # don't forget to change the splitting regexp above
        mres = re.match("(?:(?:General Assembly )?[Rr]esolutions? |[Dd]ecision |A/RES/)(\d+)/(\d+)(?:\s*(\w))?", st)
        mresb = re.match("(?:the )?resolution \((\d+)/(\d+)\)$", st)
        mresc = re.match("([3-6]\d)/(\d\d\d?)$", st)
        meres = re.match("Economic and Social Council (?:resolution|decision) (\d+)/([\dCLXVI]+)(?:\s*(\w))?", st)
        mdoc = re.match("(?:[Dd]ocument )?A/(?:(C\.\d|INF)/)?(\d+)/(\S*)", st)
        mscdoc = re.match("(?:[Dd]ocument )?S/(\d+)(?:/(\d+))?(?:/Add\.(\d+))?$", st)
        mscprst = re.match("S/PRST/(\d+)/(\d+)", st)
        mscpv = re.match("S/PV[\./](\d+)", st)
        mflat0 = re.match("A/CONF[\./]\d+/\d+(?:/Add\.\w)?|GC\([LXIV]*\)/RES/\d+|AG/\d+|SG/SM/\d+", st)
        msecres = re.match("(?:Security Council )?(?:[Rr]esolutions? )?(\d+) \((\d\d\d\d)\)", st)
        mcan = re.match("</b>\s*<b>|</i>\s*<i>", st)
        mcorr = re.match("Corr.(\d)", st)
        if mres:
            spart = (mres.group(3) and (".%s" % mres.group(3)) or "")
            link = "A-RES-%s-%s%s" % (mres.group(1), mres.group(2), spart)
            res.append(MakeCheckLink(link, st, undocname))

        elif mresb:
            link = "A-RES-%s-%s" % (mresb.group(1), mresb.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mresc:
            link = "A-RES-%s-%s" % (mresc.group(1), mresc.group(2))
            res.append(MakeCheckLink(link, st, undocname))

        elif meres:
            spart = (meres.group(3) and (".%s" % meres.group(3)) or "")
            link = "E-RES-%s-%s%s" % (meres.group(1), meres.group(2), spart)
            res.append(MakeCheckLink(link, st, undocname))
        elif mdoc:
            doccode = re.sub("/", "-", mdoc.group(3))
            doccode = re.sub("L\.l", "L.1", doccode)
            if mdoc.group(1):
                link = "A%s-%s-%s" % (mdoc.group(1), mdoc.group(2), doccode)
            else:
                link = "A-%s-%s" % (mdoc.group(2), doccode)
            res.append(MakeCheckLink(link, st, undocname))

        elif mflat0:
            link = re.sub("/", "-", mflat0.group(0))
            res.append(MakeCheckLink(link, st, undocname))

        elif mscdoc:
            if mscdoc.group(2):
                link = "S-%s-%s" % (mscdoc.group(1), mscdoc.group(2))
            else:
                link = "S-%s" % mscdoc.group(1)
            if mscdoc.group(3):
                link = "%s-Add.%s" % (link, mscdoc.group(3))

            res.append(MakeCheckLink(link, st, undocname))
        elif mscprst:
            link = "S-PRST-%s-%s" % (mscprst.group(1), mscprst.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mscpv:
            link = "S-PV-%s" % (mscpv.group(1))
            res.append(MakeCheckLink(link, st, undocname))
        elif msecres:
            if not (1945 < int(msecres.group(2)) < 2008):  # should use current document year
                print st
                raise unexception("year on resolution not possible", paranum)
            link = "S-RES-%s(%s)" % (msecres.group(1), msecres.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mcorr:
            if link and not re.search("Corr", link):
                link = "%s-Corr.%s" % (link, mcorr.group(1))
                res.append(MakeCheckLink(link, st, undocname))
            else:
                print "Cant apply corr to :::  %s -- %s" % (link, st)
                res.append(st)
        elif mcan:
            res.append(' ')
        else:
            if re.match(reressplit, st):
                print "unmatched-link  :%s:" % st
                assert False

            if re.search("/", st):
                jjst = re.sub("[a-zA-Z<]/[a-zA-Z]|20/20", "", st)
                if re.search("/", jjst):
                    print "Failed with "+st
                    raise unexception("bad / in paratext", paranum)
            res.append(st)
    return "".join(res)


# used for exceptions and for generating ids
class paranumC:
    def __init__(self, undocname, sdate, pageno, paragraphno, textcountnumber):
        self.undocname = undocname
        self.undocnamegid = re.sub("[\.\-]", "", undocname)
        self.sdate = sdate
        self.pageno = pageno
        self.paragraphno = paragraphno
        self.textcountnumber = textcountnumber

    def MakeGid(self):
        #return "doc%s-pg%03d-bk%02d" % (self.undocnamegid, int(self.pageno), self.blockno)
        return "pg%03d-bk%02d" % (int(self.pageno), self.blockno)


accessdate = datetime.date.today().isoformat()
def LinkTemplate(undocname, docdate, gid):
    mgid = re.search("pg(\d+)-bk(\d+)(?:-pa(\d+))?", gid)
    page = int(mgid.group(1))
    block = int(mgid.group(2))
    para = int(mgid.group(3) or "-1")

    wikidocdate = docdate and docdate.strftime("[[%d %B]] [[%Y]]")
    bdocdate = docdate and docdate.strftime("%d %B, %Y")

    mares = re.match("A-RES-(\d+)-(\d+)$", undocname)
    meres = re.match("E-RES-(\d\d\d\d)-(\d+)$", undocname)  # don't know what the code is
    madoc = re.match("A-(\d\d)-((?:L\.|CRP\.)?\d+)([\w\.\-]*)$", undocname)
    msres = re.match("S-RES-(\d+)\((\d+)\)$", undocname)
    mapv  = re.match("A-(\d\d)-PV.(\d+)(-Corr.\d|)$", undocname)
    mspv = re.match("S-PV.(\d+)", undocname)
    scdoc = re.match("S-(\d\d\d\d)-(\d+)$", undocname)
    munknown = re.match("(?:ECESA/1/Rev.1|S-26-2)$", undocname)

    wikiref, blogref = "", ""
    if mares:
        wikiref = "<ref>{{UNdoc|body=A|doctype=RES|session=%s|code=%s|accessdate=%s}}</ref>" % (mares.group(1), mares.group(2), accessdate)
        blogref = '<a href="http://www.undemocracy.org/pdfdoc/%s#%s">General Assembly resolution %s/%s on %s</a>' % (undocname, gid, mares.group(1), mares.group(2), bdocdate)

    elif mapv:
        wikiref = "<ref>{{UNdoc|body=A|doctype=PV|session=%s|plenary=%s|date=[[%s]] [[%s]]|accessdate=%s}}</ref>"
        blogref = '<a href="http://www.undemocracy.org/pdfdoc/%s#%s">General Assembly session %s meeting %s on %s, page %s</a>'

    else:
        wikiref = ""
        blogref = ""

    return wikiref, blogref

