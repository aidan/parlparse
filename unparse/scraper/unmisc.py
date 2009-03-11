import re
import os
import datetime

undatadir = "/home/undemocracy/svn-undata"

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


#undatadir = os.path.join("..", "..", "undata")
pdfdir = os.path.join(undatadir, "pdf")
pdfxmldir = os.path.join(undatadir, "pdfxml")
htmldir = os.path.join(undatadir, "html")
xapdir = os.path.join(undatadir, "xapdex.db")
pdfpreviewdir = os.path.join(undatadir, "pdfpreview")
pdfinfodir = os.path.join(undatadir, "pdfinfo")
tmppdfpreviewdir = os.path.join(undatadir, "tmppdfpreview")
commentsdir = os.path.join(undatadir, "comments")
indexstuffdir = os.path.join(undatadir, "indexstuff")

sCallScrape = None  # set by one of the

bQuiet = False
def IsNotQuiet():
    return not bQuiet
def IsVeryNoisy():
    return False
def SetQuiet(lbQuiet):
    global bQuiet
    bQuiet = lbQuiet
def SetCallScrape(lsCallScrape):
    global sCallScrape
    sCallScrape = lsCallScrape

reressplit = """(?x)(
                (?:[Dd]ocument\s)?A/(?:[A-Z][\-\.\d]*/)?\d+/[\w\d\.]*?[l\d]+(?:/(?:Add|Rev)\.[l\d]+)?(?:/(?:Add|Rev)\.[l\d]+)?(?:/Corr.\d)?|
                (?:General\sAssembly\s|Economic\sand\sSocial\sCouncil\s)?[Rr]esolutions?\s\d+/[\dCLXVI]+[A-Y]?|
                draft\sresolution\sA/\d\d/L\.\d+(?:/Add.\d)?(?:/Rev.\d)?|
                A/RES/\d+/\d+|
                S/PRST/\d+/\d+|
                S/\d+/PRST/\d+|
                S/PV\.\d+|
                A/(?:CONF|INF|HRC)[\./]\d+/(?:L\.)?\d+(?:/(?:Rev\.)?[l\d])?(?:/(?:Add\.)?[l\d])?|
                GC\([\dLXIV]*\)(?:/RES|/DEC)?/\d+[A-X]?|
                SG/SM/\d+|
                S-\d+/\d|
                MAG/\d+/\d+|
                AG/\d+|
                CP/\d+|
                (?:[Rr]egulation|presidential\sdecree)\s\d+/\d+|
                press\s(?:release|statement)\s\(?SC/\d\d\d\d\)?|
                HIV/AIDS/CRP.\d(?:/Add.\d)?|
                E/CN.\d+/\d+/(?:L\.)?\d+(?:/Add.\d)?|
                A/AC.\d+/(?:L\.)?\d+(?:/(?:CRP\.|WP\.)?\d+)?(?:/Rev\.2)?|
                A/C\.\d/\d+/INF/\d|
                JIU/REP/\d+/\d+|
                CS?D/\d+(?:/\d+)?|
                ISBA/A/L.\d/Rev.\d|
                NPT/CONF.\d+/(?:TC.\d/)?\d+|
                WGAP/\d+/\d|
                WGFS/\d+|
                SPLOS/\d+|
                C/E/RES.27|
                INFCIRC/\d+|
                CLCS/\d|
                OAU/OL/\d+/\d+/\d+|
                A/BUR/\d+/\d|
                GOV/\d{4}(?:/Rev.\d+|/\d+)?|
                E/\d{4}/(?:L\.)?\d+|
                (?:A/)?ES-\d+/\d+|
                Economic\sand\sSocial\sCouncil\sdecision\s\d+/\d+|
                decision\s\d\d/\d+(?!\sof\sthe\sCommission)|
                (?:[Dd]ocument\s)?S/\d+/\d+(?:/Add\.\d+)?(?:/Rev\.\d+)?(?:/Add\.\d+)?(?:/Corr\.\d)?|
                (?:[Dd]ocument\s)?S/\d{3,6}|
                (?:the\s)?resolution\s\(\d\d/\d+\)|
                (?:Security\sCouncil\s)?(?:[Rr]esolutions?\s)?(?:S/RES/)?\d+\s\(\d\d\d\d\)|
                Corr.\d|
                Add.\d|
                (?<=\s)[3-6]\d/\d{1,3}(?=[\s,\.])|
                </b>\s*<b>|
                </i>\s*<i>|
                <i>\((?!resolution|A/\d\d)[A-Z0-9paresolutindubcfxvmgyh\*\.,\-\s/\(\)]*?\)</i>  # used to hide of complicated (buggered up) links which have two brackets
                )(?=$|\W)"""

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
        mresc = re.match("([3-6]\d)/(\d{1,3})$", st)
        meres = re.match("Economic and Social Council (?:resolution|decision) (\d+)/([\dCLXVI]+)(?:\s*(\w))?", st)
        mdoc = re.match("(?:[Dd]ocument |draft resolution )?A/(?:(C\.\d|INF|HRC|S-\d+)/)?(\d+)/(\S*)", st)
        mscdoc = re.match("(?:[Dd]ocument )?S/(\d+)(?:/(\d+))?(?:/Add\.(\d+))?(?:/Rev\.(\d+))?(?:/Add\.(\d))?(?:/Corr\.(\d))?$", st)
        mscprst = re.match("S/PRST/(\d+)/(\d+)", st)
        mscprst2 = re.match("S/(\d\d\d\d)/PRST/(\d+)", st)
        mscpv = re.match("S/PV[\./](\d+)", st)
        msecres = re.match("(?:Security Council )?(?:[Rr]esolutions? )?(?:S/RES/)?(\d+) \((\d\d\d\d)\)", st)
        mcan = re.match("</b>\s*<b>|</i>\s*<i>", st)
        mcorr = re.match("Corr.(\d)", st)
        madd = re.match("Add.(\d)", st)
        maltreg = re.match("(?:[Rr]egulation|presidential\sdecree)\s\d+/\d+", st)
        msecpress = re.match("(press (?:release|statement)) SC/(\d\d\d\d)", st)
        #print st, mdoc

        # final dustbin for all the rest
        mflat0 = re.match("""(?x)A/CONF[\./]\d+/(?:L\.)?\d+(?:/(?:Add|Rev)\.\w)?|
                                 GC\([\dLXIV]*\)(?:/RES|/DEC)?/\d+[A-X]?|
                                 MAG/\d+/\d+|
                                 AG/\d+|SG/SM/\d+|CP/\d+|
                                 HIV/AIDS/CRP.\d(?:/Add.\d)?|
                                 E/CN.\d+/\d+/(?:L\.)?\d+(?:/Add.\d)?|
                                 S-\d+/\d|
                                 A/AC.\d+/(?:L\.)?\d+(?:/(?:CRP\.|WP\.)?\d+)?(?:/Rev\.2)?|
                                 A/C\.\d/\d+/INF/\d|
                                 C/E/RES.27|
                                 JIU/REP/\d+/\d+|
                                 NPT/CONF.\d+/(?:TC.\d/)?\d+|
                                 ISBA/A/L.\d/Rev.\d|
                                 CS?D/\d+(?:/\d+)?|WGAP/\d+/\d|WGFS/\d+|SPLOS/\d+|(?:A/)?ES-\d+/\d+|CLCS/\d|
                                 INFCIRC/\d+|
                                 OAU/OL/\d+/\d+/\d+|
                                 A/BUR/\d+/\d|
                                 GOV/\d+(?:/Rev.\d+|/\d+)?|
                                 E/\d+/(?:L\.)?\d+""", st)

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
        elif msecpress:
            res.append(msecpress.group(1))
            link = "SC/%s" % msecpress.group(2)
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

        elif maltreg:
            res.append("<i>(%s)</i>" % maltreg.group(0))

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
            if mscdoc.group(4):
                link = "%s-Rev.%s" % (link, mscdoc.group(4))
            if mscdoc.group(5):
                link = "%s-Add.%s" % (link, mscdoc.group(5))
            if mscdoc.group(6):
                link = "%s-Corr.%s" % (link, mscdoc.group(6))

            res.append(MakeCheckLink(link, st, undocname))
        elif mscprst:
            link = "S-PRST-%s-%s" % (mscprst.group(1), mscprst.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mscprst2:
            link = "S-PRST-%s-%s" % (mscprst2.group(1), mscprst2.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mscpv:
            link = "S-PV-%s" % (mscpv.group(1))
            res.append(MakeCheckLink(link, st, undocname))
        elif msecres:
            if not (1945 < int(msecres.group(2)) < 2009):  # should use current document year
                print st
                raise unexception("year on resolution not possible", paranum)
            link = "S-RES-%s(%s)" % (msecres.group(1), msecres.group(2))
            res.append(MakeCheckLink(link, st, undocname))
        elif mcorr:
            if link and re.search("Corr", link):
                link = re.sub("-Corr.\w$", "", link)
            link = "%s-Corr.%s" % (link, mcorr.group(1))
            res.append(MakeCheckLink(link, st, undocname))
        elif madd:
            if link and re.search("Add", link):
                link = re.sub("-Add.\w$", "", link)
            link = "%s-Add.%s" % (link, madd.group(1))
            res.append(MakeCheckLink(link, st, undocname))
        elif mcan:
            res.append(' ')

        else:

            if re.match("<i>(?:.*?/.*?|\(.{1,190}?\))</i>$", st):
                pass
            elif re.match(reressplit, st):
                print "unmatched-link  :%s:" % st
                raise unexception("unmatched-link", paranum)

            elif re.search("/", st):
                #print re.split(reressplit, st)
                jjst = re.sub("(?:[a-zA-Z<)\"]|G-7)/[a-zA-Z]|20/20|9/11|HIV/AIDS|[12][90]\d\d/[12][90]\d\d", "", st)
                if re.search("/", jjst):
                    print "Failed with ", st
                    raise unexception("bad / in paratext", paranum)
            res.append(st)
        #print st,
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



def GetAllHtmlDocs(stem, bunindexed, bforce, htmldir):

    # this has to be able to sift between the unindexed and indexed types
    relsm = {}
    relsum = {}

    filelist = os.listdir(htmldir)
    filelist.sort(reverse = True)
    for d in filelist:
        if re.search("(?:\.css|\.svn|\.js|~)$", d):
            continue
        if stem and not re.match(stem, d):
            continue

        p = os.path.join(htmldir, d)
        mux = re.match("(.*?)(\.unindexed)?\.html$", d)
        assert mux, "unmatched file:%s" % d
        if mux.group(2):
            relsum[mux.group(1)] = p  # .unindexed
        else:
            relsm[mux.group(1)] = p   # without that label

    if bunindexed:
        res = relsum.values()
        if bforce:
            res.extend([relsm[r]  for r in relsm  if r not in relsum])
    else:
        res = relsm.values()
        res.extend([relsum[r]  for r in relsum  if r not in relsm])

    res.sort()
    return res


# can't be bothered to code them all properl
romantodecmap = { "XXIX":29 }

def RomanToDecimal(rn):
    res = romantodecmap.get(rn)
    if res:
        return res
    
    lrn = list(rn)
    res = 0
    while lrn and lrn[-1] == "I":
        res += 1
        del lrn[-1]
    if not lrn:
        return res
    if lrn[-1] == "V":
        res += 5;
        del lrn[-1]
        if lrn and lrn[-1] == "I":
            res -= 1
            del lrn[-1]
    if not lrn:
        return res
    while lrn and lrn[-1] == "X":
        res += 10
        del lrn[-1]
    if lrn and lrn[-1] == "I":
        res -= 1
        del lrn[-1]
    assert not lrn, rn
    return res


