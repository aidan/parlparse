import os
import re
from nations import FixNationName
from unmisc import unexception, paranumC, IsNotQuiet, MarkupLinks
from speechblock import CleanupTags

page1bit = '<page number="1" position="absolute" top="0" left="0" height="1188" width="918">(?:<fontspec[^>]*>|\s)*$'
pageibit = '<page number="(\d+)" position="absolute" top="0" left="0" height="1188" width="918">(?:\s*<fontspec[^>]*>|\s)*(?=<text)'
pagebitmap = '<page number="(\d+)" position="absolute" top="0" left="0" height="\d+" width="\d+">(?:<fontspec[^>]*>|\s)*$'
footertext = '<i><b>\*\d+v?n?\*\s*</b></i>|\*\d+\*|<i><b>\*</b></i>|<i><b>\d</b></i>|(?:\d* )?\d*-\d*S? \(E\)|`````````'
months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

twopageagendas = ["S-PV-5697", "S-PV-5796", "S-PV-6041"]

misnumberedpages = ["S-PV-3454-Resu.2", "S-PV-3536-Resu.1", "S-PV-4684-Resu.1", "S-PV-4999", "S-PV-4999-Resu.1", "S-PV-5016", "S-PV-5086", "S-PV-5199", "S-PV-5328", "S-PV-5453", "S-PV-5594"]
def StripPageTags(xfil, undocname):
    xpages = re.findall("(<page.*\s[\s\S]*?)</page>", xfil)
    mpage1head = re.match("([\s\S]*?)(?=<text)", xpages[0])
    #print len(xpages), undoc
    if not mpage1head:
        if IsNotQuiet():
            print " -- bitmap type"
        for xpage in xpages:
            if not re.match(pagebitmap, xpage):
                print xpage
                print undocname
                assert False
        return False
    if not re.match(page1bit, mpage1head.group(1)):
        if IsNotQuiet():
            print "Probably is a bitmap type"
            print mpage1head.group(1)
            assert False
        return False
    res = [ xpages[0][mpage1head.end(0):] ]

    for i in range(1, len(xpages)):
        mpageihead = re.match(pageibit, xpages[i])
        if int(mpageihead.group(1)) != i + 1:
            if undocname not in misnumberedpages:
                print "misnumberedpages", mpageihead.group(1), i + 1, undocname, "not in list:", misnumberedpages
                assert False


        res.append(xpages[i][mpageihead.end(0):])
    return res



#<text top="1062" left="342" width="486" height="11" font="2">xxxx</text>
class TextLine:
    def __init__(self, txline, lundocname, lpageno, textcountnumber):
        mxline = re.match('<text top="(\d+)" left="(\d+)" width="-?(\d+)" height="(\d+)" font="(\d+)">(.*?)</text>', txline)
        if not mxline:
            print txline, "tttttt"
        self.top = int(mxline.group(1))
        self.left = int(mxline.group(2))
        self.width = int(mxline.group(3))
        self.height = int(mxline.group(4))
        self.font = int(mxline.group(5))
        self.pageno = lpageno
        self.undocname = lundocname
        self.textcountnumber = textcountnumber
        self.ltext = mxline.group(6).strip()

        self.ltext = re.sub("<i>\s*</i>|<b>\s*</b>", " ", self.ltext)
        if re.match("<[ib]>\s*</[ib]>|\s*$", self.ltext):
            self.ltext = ""

        # will be removed
        if not self.ltext:
            return

        self.bfootertype = (self.left < 459 and self.left + self.width > 459) or re.match(footertext, self.ltext)
        #if self.bfootertype:
        #    print self.ltext

        # move on any short bits that are like 13^(th)
        if self.height == 11 and not self.bfootertype and self.width <= 10:
            #print self.left, self.width, "'%s'" % self.ltext
            assert self.width <= 10
            if self.ltext not in ["th", "rd", "st", "nd"]:
                if IsNotQuiet():
                    print self.ltext
                raise unexception("unrecognized shortbit", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
            self.top += 2  # push the step down from 16 to 18

def TextLineTopKey(textline):
    return (textline.top, textline.left)


class TextLineCluster:
    def __init__(self, ltxl):
        if ltxl:
            self.txls = [ ltxl ]
            self.indents = [ [ltxl.indent, 1, 1] ]

    def AddLine(self, ltxl):
        if ltxl.vgap != 0:
            if self.indents[-1][0] != ltxl.indent:
                self.indents.append([ltxl.indent, 1, 0])
            else:
                self.indents[-1][1] += 1
        self.indents[-1][2] += 1

        self.txls.append(ltxl)


# work backwards looking for paragraph heads
familiarvgaps = (0, 16, 17, 18, 19, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 43, 45, 48, 53, 54, 55, 63, 72, 83)
def AppendToCluster(txlcol, txl):

    # frig the indentation on the most common mistakes
    if re.match("<i>The meeting (?:was called|was suspended|rose at|was resumed)", txl.ltext) and (txl.indent == 0):
        txl.indent = 31

    if not txlcol:
        txlcol.append(TextLineCluster(txl))
        return
    txl.vgap = txl.top - txlcol[-1].txls[-1].top

    #print txlcol[-1].txls[-1].ltext
    #print txl.vgap, txl.width, txl.height, txl.top,  txl.ltext  # zzzz

    # frig vgaps in some cases where the spacing was wider than normal
    if txl.undocname in ["A-50-PV.84", "A-50-PV.88"]:
        if txl.vgap == 21 or txl.vgap == 22:
            txl.vgap = 18
        if txl.vgap == 42:
            txl.vgap = 43
    if txl.undocname == "S-PV-5584":
        if txl.vgap == 20:
            txl.vgap = 19

    if not txl.vgap in familiarvgaps:
        if IsNotQuiet():
            print "\n\n   vgap=", txl.vgap, "\n\nwidth/height/top", txl.width, txl.height, txl.top,  txl.ltext  # zzzz
            print " familiar vgaps:", familiarvgaps
        raise unexception("vgap not familiar", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
    if txl.vgap in (0, 17, 18, 19) or txl.vgap == 0:
        txlcol[-1].AddLine(txl)
    else:
        #print txl.vgap, "vvvv", txl.ltext
        txlcol.append(TextLineCluster(txl))

def AppendCluster(res, tlc, sclusttype):
    # check if we should merge to the next paragraph
    assert sclusttype in ["gapcluster", "newpage", "newcolumn"]

    if res and sclusttype != "gapcluster" and len(tlc.indents) == 1:
        indentp = res[-1].indents[-1][0]
        indentn = tlc.indents[0][0]

        bbothindented = ((indentp in [31, 32]) and (indentn in [31, 32])) or \
                        ((indentp in [0, 1]) and (indentn in [0, 1])) or \
                        ((indentp in [36, 33]) and (indentp == indentn))
        bonelineparacont = (len(res[-1].indents) == 1) and (res[-1].indents[0][1] == 1) and (indentp in [31, 32]) and (indentn in [0, 1])

        td0 = res[-1].txls[-1].ltext[:3]
        td1 = tlc.txls[0].ltext[:3]
        if not re.match("<[ib]>", td0):
            td0 = ""
        if not re.match("<[ib]>", td1):
            td1 = ""
        bstylematches = (td0 == td1)
        #assert not (bbothindented and not bstylematches)
        if re.match("<i>In favour", tlc.txls[0].ltext):
            bstylematches = False
        if re.match("<b>Agenda", res[-1].txls[-1].ltext):
            bstylematches = False

        # likely continuation of paragraph
        if bbothindented and bstylematches:
            res[-1].txls.extend(tlc.txls)
            #print tlc.txls[0].ltext
            return
        else:
            if bonelineparacont:
                if IsNotQuiet():
                    pass
                    #print "checkthiscontinuation case"
                    #print indentp, indentn, bstylematches, bonelineparacont, res[-1].indents
                    #print " ----", tlc.txls[0].ltext
                if bstylematches:
                    if IsNotQuiet():
                        pass #print "merging"
                    res[-1].txls.extend(tlc.txls)
                    return


    # new cluster; check the indenting pattern is good
    if len(tlc.indents) == 2:
        if tlc.indents[0] <= tlc.indents[1]:
            #print tlc.indents, tlc.txls[0].ltext
            #assert re.match("<[ib]>.*?</[ib]>", tlc.txls[0].ltext) # <i>In favour:</i>
            pass

    # two paragraphs may have been merged, try to separate them out
    elif len(tlc.indents) == 4 and tlc.indents[0][0] == tlc.indents[2][0] and tlc.indents[1][0] == tlc.indents[3][0]:
        if IsNotQuiet():
            pass  #print tlc.indents
        assert tlc.indents[0][0] == tlc.indents[2][0]
        assert tlc.indents[1][0] == tlc.indents[3][0]
        si = tlc.indents[0][2] + tlc.indents[1][2]
        tlcf = TextLineCluster(None)
        tlcf.txls = tlc.txls[:si]
        del tlc.txls[:si]
        tlcf.indents = tlc.indents[:2]
        del tlc.indents[:2]
        res.append(tlcf)
        if IsNotQuiet():
            pass
            #print "# paragraphs", si
            #print " ", tlc.txls[0].ltext
            #print tlcf.indents, tlc.indents

    elif len(tlc.indents) != 1:
        if IsNotQuiet():
            print tlc.indents, "jjjj"
        prevtop = -1
        for txl in tlc.txls:
            if IsNotQuiet():
                if prevtop == txl.top:
                    print " ",
                print txl.indent, txl.ltext
            prevtop = txl.top
        raise unexception("unrecognized indent pattern", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
        assert False
    res.append(tlc)
    return


# maybe shouldn't be a class
class TextPage:
    def ExtractDateTime(self, txline, ltext):
        # extract the date out if poss
        mdate = re.match("\w+\s*, (\d+)\s+(\w+)\s+(\d+),\s*(?:at )?(\d+)[\.:]?(\d*)(?:\s+([ap])\.?\s*m\.?| noon\.?)?(?: \(closed\))?$", ltext)
        if not mdate:  #Tuesday, 3 December 2002, 10 a.m.
            if re.search("Friday", ltext) and IsNotQuiet():
                print ltext, re.match("\w+\s*, (\d+)\s+(\w+)\s+(\d+),\s*(?:at )?(\d+)[\.:]?(\d*)(?:\s+([ap])\.?m\.?| noon\.?)?(?: \(closed\))?", ltext)
            return

        #print txlines[ih].ltext
        iday = int(mdate.group(1))
        if mdate.group(2) not in months:
            if IsNotQuiet():
                print mdate.group(2), months
            raise unexception("unrecognized month", paranumC(txline.undocname, None, 0, -1, txline.textcountnumber))
        imonth = months.index(mdate.group(2))
        syear = mdate.group(3)
        if not re.match("(?:20\d\d|19\d\d)$", syear):
            raise unexception("bad year", paranumC(txline.undocname, None, 0, -1, txline.textcountnumber))
        ihour = int(mdate.group(4))
        imin = mdate.group(5) and int(mdate.group(5)) or 0
        if mdate.group(6) and mdate.group(6) == "a" and ihour == 12:
            ihour = 0
        elif mdate.group(6) and mdate.group(6) == "p" and ihour != 12:
            ihour += 12
        if self.date:
            raise unexception("date redefined", paranumC(txline.undocname, None, 0, -1, txline.textcountnumber))
        if not (0 <= ihour <= 23) or not (0 <= imin <= 59):
            if IsNotQuiet():
                print ltext
            raise unexception("bad time", paranumC(txline.undocname, None, 0, -1, txline.textcountnumber))
        self.date = "%s-%02d-%02d %02d:%02d" % (syear, imonth + 1, iday, ihour, imin)

    def ExtractDotLineChair(self, txlines, ih):
        assert self.pageno == 1
        #<text top="334" left="185" width="584" height="17" font="2">Mr.  Kavan  . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . (Czech Republic)</text>
        while True:
            #print "------" + txlines[ih].ltext
            mchair = re.search("([^>:]*?)\s*\. \. \. \. \.", txlines[ih].ltext)
            if mchair:
                break

            # fix missing year date
            #if self.undocname == "A-55-PV.44" and txlines[ih].ltext == "Monday, 30 October, 10 a.m.":
            #    txlines[ih].ltext = "Monday, 30 October 2000, 10 a.m."
            self.ExtractDateTime(txlines[ih], txlines[ih].ltext)

            ih += 1
            if ih == len(txlines):
                return -1

        if not self.date:
            if IsNotQuiet():
                for i in range(ih):
                    print "--%s--" % txlines[i].ltext
            raise unexception("dotlinechair date problem", paranumC(txlines[ih].undocname, None, 0, -1, txlines[ih].textcountnumber))
            assert False

        # when country name for the president . . . . is not on same line
        mcountry = re.search("\((.*?)\)$", txlines[ih].ltext)
        if not mcountry:
            ih += 1
            #print txlines[ih].ltext
            mcountry = re.match("\((.*?)\)$", txlines[ih].ltext)
            if not mcountry:
                if IsNotQuiet():
                    print txlines[ih].ltext
                raise unexception("unable to extract country from  ...-line", paranumC(txlines[ih].undocname, None, 0, -1, txlines[ih].textcountnumber))
        ih += 1
        chairname = re.sub("\s\s+", " ", mchair.group(1)).strip()
        self.chairs.append((chairname, FixNationName(mcountry.group(1), self.date)))
        return ih

    def ExtractDotLineChairHead(self, txlines):
        self.date = None
        self.chairs = [ ]
        self.agenda = None  # used only in sec council
        ih = self.ExtractDotLineChair(txlines, 0)
        ihcochair = self.ExtractDotLineChair(txlines, ih)

        if ihcochair != -1:
            return ihcochair
        return ih

    def ExtractSeccounFrontPage(self, txlines):
        self.date = None
        self.chairs = [ ]
        self.seccouncilmembers = [ ]
        self.agenda = [ ]

        lasttop = -1
        jtxlines = [ ]
        ih = 0
        while ih < len(txlines):
            if txlines[ih].top == lasttop:
                jtxlines[-1] = "%s %s" % (jtxlines[-1], txlines[ih].ltext)
            else:
                jtxlines.append(txlines[ih].ltext)
                lasttop = txlines[ih].top
            ih += 1

        del txlines # just deletes the reference to this object
        ih = 0
        while ih < len(jtxlines):
            self.ExtractDateTime(None, jtxlines[ih])
            mpresseat = re.match("<i>(President|Chairman|later)(?:</i>:|:\s*</i>)\s*((?:Mr.|Mrs.|Ms.|Sir\.?|Miss|Sheikh|Baroness|Lord|Nana) .*?)\s+\.(?: \.)*\s*(\(.*)?$", jtxlines[ih])
            #print jtxlines[ih], mpresseat
            if mpresseat:
                if not self.date:
                    if IsNotQuiet():
                        for i in range(ih):
                            print jtxlines[i]
                    raise unexception("missingg date", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                if mpresseat.group(1) in ["President", "Chairman"]:
                    assert len(self.chairs) == 0   # first one
                else:
                    assert len(self.chairs) == 1   # later president
                ih += 1
                if mpresseat.group(3):
                    scountry = mpresseat.group(3)
                else:
                    scountry = ""
                if re.search("\(", scountry) and not re.search("\)", scountry):
                    scountry = "%s %s" % (scountry, jtxlines[ih])
                    ih += 1
                mcountry = re.match("\((.*?)\)$", scountry)
                lfscountry = re.sub("\s+", " ", mcountry.group(1))
                fscountry = FixNationName(lfscountry, self.date)
                if not fscountry:
                    if IsNotQuiet():
                        print "--%s--" % mcountry.group(1)
                    raise unexception("unrecognized nationA", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                chairname = re.sub("\s\s+", " ", mpresseat.group(2)).strip()
                self.chairs.append((chairname, fscountry, "president"))

                if fscountry in self.seccouncilmembers:
                    assert len(self.seccouncilmembers) == 1
                    assert fscountry == "New Zealand"
                    assert self.undocname == "S-PV-3370"
                    assert len(self.chairs) == 2
                    del self.chairs[0]
                    del self.seccouncilmembers[0]

                self.seccouncilmembers.append(fscountry)
                continue

            mcountryseat = re.match("(<i>Members(?:</i>:|:\s*</i>))?\s*([\w\-\s]*?)\s*\.(?: \.)*\s*((?:Mr.|Ms.|Mrs.|Miss|Dr.|Sir\.?|Sheikh|Baroness|Lord|Nana) [^<>]*|absent)$", jtxlines[ih])
            if mcountryseat:
                if mcountryseat.group(1):
                    if len(self.chairs) not in [1, 2]:  # in case of second president
                        if IsNotQuiet():
                            print self.chairs, "chchchch"
                        raise unexception("chairs not thereB", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                else:
                    if len(self.chairs) == 0:
                        if not self.date:  # prob a closed meeting
                            break
                        if IsNotQuiet():
                            print ih, jtxlines[ih]
                        raise unexception("seat without chair", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                lfscountry = re.sub("\s+", " ", mcountryseat.group(2))
                fscountry = FixNationName(lfscountry, self.date)
                if not fscountry:
                    if IsNotQuiet():
                        print "--%s--" % mcountryseat.group(2)
                    raise unexception("unrecognized nationB", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                chairname = re.sub("\s\s+", " ", mcountryseat.group(3)).strip()
                self.chairs.append((chairname, fscountry, "member"))
                if fscountry not in self.seccouncilmembers:
                    self.seccouncilmembers.append(fscountry)
                else:
                    if IsNotQuiet():
                        print "Repeat-country on council", fscountry
            else:
                if re.search(" \. \. \. \. \. \. ", jtxlines[ih]):
                    if IsNotQuiet():
                        print "--%s--" % jtxlines[ih]
                    raise unexception("missing country", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
            if re.match("<b>Agenda\s*</b>$", jtxlines[ih]):
                ih += 1
                break
            if re.search("Agenda", jtxlines[ih]):
                print ih, jtxlines
                raise unexception("unextracted Agenda (should be <b>?)", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
            ih += 1

        # could be a closed meeting
        if not self.date:
            alltext = " ".join(jtxlines)
            if re.search("OFFICIAL COMMUNIQU..*?Held in private (?:in the Security Council Chamber )?at Headquarters(?i)", alltext):
                return False
            return True

        while ih < len(jtxlines):
            if re.match("\d\d-\d\d", jtxlines[ih]):
                break
            if re.match("\d\d.?\d\d\d\d\d \(E\)", jtxlines[ih]):
                break
            if re.match("This record contains the text of speeches delivered in English", jtxlines[ih]):
                break
            #print "agagag", jtxlines[ih]
            assert not re.search("text of speeches|verbatim(?i)", jtxlines[ih])
            self.agenda.append(jtxlines[ih].strip())
            ih += 1

        #print "ccccc", self.chairs
        lparanum = paranumC(self.undocname, None, 0, -1, self.textcountnumber)
        if len(self.chairs) not in (15, 17) or len(self.seccouncilmembers) != 15:
            if self.undocname == "S-PV-3446":
                return False
            if IsNotQuiet():
                print len(self.seccouncilmembers), len(self.chairs), "wrong number of members or chairs\n", self.chairs
                print self.seccouncilmembers
            raise unexception("wrongnumber on council", lparanum)

        self.agenda = " ".join(self.agenda)
        self.agenda = re.sub("</?b>", " ", self.agenda)
        self.agenda = re.sub("\s\s+", " ", self.agenda)
        self.agenda = MarkupLinks(CleanupTags(self.agenda, "council-agenda", lparanum), self.undocname, lparanum)
        return True

    def __init__(self, xpage, lundocname, lpageno, textcountnumber):
        self.pageno = lpageno
        self.undocname = lundocname
        self.textcountnumber = textcountnumber
        self.bSecurityCouncil = re.match("S-PV.(\d+)", self.undocname)
        self.nSecurityCouncilSession = self.bSecurityCouncil and int(self.bSecurityCouncil.group(1)) or 0
        self.bGeneralAssembly = re.match("A-\d+-PV", self.undocname)
        assert self.bSecurityCouncil or self.bGeneralAssembly

        # for right column, if not left justified, this adds a bit more to the right
        if self.bGeneralAssembly and int(re.match("A-(\d+)", lundocname).group(1)) <= 52:
            rightcolstartindentincrement = 1
        else:
            rightcolstartindentincrement = 0

        # set the column starts from some of the special cases we get
        leftcolstart = 90
        if self.bGeneralAssembly and int(re.match("A-(\d+)", lundocname).group(1)) <= 54:
            rightcolstart = 481
        else:
            rightcolstart = 468

        if lundocname in ["A-54-PV.100", "A-54-PV.96", "A-54-PV.98", "A-54-PV.99", "S-PV-4143", "S-PV-4143-Resu.1"]:
            rightcolstart = 468
        elif lundocname in ["A-54-PV.97"]:
            rightcolstart = 486
        elif re.match("S-PV-335[0-8]", lundocname):
            rightcolstart = 468
        elif re.match("S-PV-334", lundocname):
            rightcolstart = 468
        elif self.nSecurityCouncilSession >= 4144:
            rightcolstart = 468

        #re.match("S-PV-414[4-9]", lundocname):
        #    rightcolstart = 468
        #elif re.match("S-PV-41[5-9]", lundocname):
        #    rightcolstart = 468
        #elif re.match("S-PV-4[2-9]", lundocname):
        #    rightcolstart = 468
        #elif re.match("S-PV-5", lundocname):
        #    rightcolstart = 468

        elif self.bSecurityCouncil:
            rightcolstart = 481
            rightcolstartindentincrement = 1


        # generate the list of lines, sorted by vertical position
        ftxlines = re.findall("<text.*?</text>", xpage)

        txlines = [ ]
        for txline in ftxlines:
            txl = TextLine(txline, lundocname, lpageno, self.textcountnumber)
            self.textcountnumber += 1
            if txl.ltext:
                if txlines and txlines[-1].bfootertype and txlines[-1].top == txl.top:
                    txl.bfootertype = True
                txlines.append(txl)
        txlines.sort(key=TextLineTopKey)

        # the half divider is at 459

        # try to separate out the header and footers
        if self.pageno == 1 and self.bGeneralAssembly:
            ih = self.ExtractDotLineChairHead(txlines)
            #for Dtxl in txlines[-10:]:
            #    print Dtxl.top, Dtxl.left, Dtxl.ltext

            ie = len(txlines) - 1
            while txlines[ie].bfootertype:
                #print "FOOTER:", txlines[ie].ltext
                ie -= 1
            #print "**NON-FOOTER:", txlines[ie].ltext
            ie += 1

            # the whole first page gets parsed separately
            assert not self.bSecurityCouncil

        elif self.bSecurityCouncil and self.pageno == 1:
            if not self.ExtractSeccounFrontPage(txlines):
                self.bSecurityCouncil = "ClosedSession"
            return

        # special case where the agenda spills to a second page (don't forget the outer application of this if)
        elif self.bSecurityCouncil and lundocname in twopageagendas and self.pageno == 2:
            ih = 0
            self.agenda = [ ]
            while ih < len(txlines):
                if 132 <= txlines[ih].top < 1000:
                    self.agenda.append(txlines[ih].ltext)
                ih += 1
            self.agenda = " ".join(self.agenda)
            self.agenda = re.sub("</?b>", " ", self.agenda)
            self.agenda = re.sub("\s\s+", " ", self.agenda)
            lparanum = paranumC(self.undocname, None, 0, -1, self.textcountnumber)
            self.agenda = MarkupLinks(CleanupTags(self.agenda, "council-agenda", lparanum), self.undocname, lparanum)
            return

        elif self.bGeneralAssembly:
            if re.match("<b>\w[/.]\d+/PV.\d+\s*</b>", txlines[0].ltext):
                ih = 1
            elif re.match("\d", txlines[0].ltext) and re.match("<b>\w[/.]\d+/PV.\d+\s*</b>", txlines[1].ltext):
                ih = 2
            else:
                #print txlines[0].ltext
                assert re.match("General Assembly", txlines[0].ltext), txlines[0].ltext
                assert re.match("\d+(?:th|st|nd|rd) (?:plenary )?meeting", txlines[1].ltext)
                assert re.match("\S+ [Ss]ession", txlines[2].ltext)
                assert re.match("\d+ \w+ \d\d\d\d", txlines[3].ltext) or (lundocname in ["A-50-PV.38", "A-50-PV.40"])
                ih = 4;
            ie = len(txlines) - 1
            if re.match("\d\d\-\d\d\d\d\d", txlines[ie].ltext):
                ie -= 1
            pagenumtext = re.sub("<..?>", "", txlines[ie].ltext).strip()
            if re.match("\d\d\-\d\d\d\d\d", txlines[ie - 1].ltext):
                ie -= 1
            if not re.match("\d+$", pagenumtext):
                if IsNotQuiet():
                    print "jjjj", pagenumtext, txlines[ie].ltext
                raise unexception("pagenum error not a number", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))
            if int(pagenumtext) != self.pageno:
                if IsNotQuiet():
                    print pagenumtext, self.pageno
                raise unexception("pagenum serror of speaker-intro", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))

        elif self.bSecurityCouncil:
            #if len(txlines) < 4:
            #    raise unexception("intro too short", paranumC(self.undocname, None, 0, -1, txlines[0].textcountnumber))

            bl0 = len(txlines) > 4 and re.match("Security Council", txlines[0].ltext)
            bl1 = len(txlines) > 4 and re.match("\d+(?:th|st|nd|rd)? (?:\(Resumption(?: \d)?\) )?(?:meeting)?", txlines[1].ltext)
            bl2 = len(txlines) > 4 and re.match("(\w+-\w+|\w+) [Yy]ear", txlines[2].ltext)
            bl3 = len(txlines) > 4 and re.match("\d+ \w+ \d\d\d\d", txlines[3].ltext)

            bl4 = re.match("<b>S/PV.\d+\s*(?:\(Resumption [\d|I]\)|\(Part [I]+\))?\s*</b>", txlines[0].ltext)
            bl4r = (self.undocname[5:] >= "4143")

            if bl4 and bl4r:
                ih = 1
            elif bl0 and bl1 and bl2 and bl3:
                ih = 4;
            else:
                if IsNotQuiet():
                    print "\nFirst four lines on page:", self.pageno, bl4, bl4r
                    print bl0, txlines[0].ltext
                    print bl1, txlines[1].ltext
                    print bl2, txlines[2].ltext
                    print bl3, txlines[3].ltext
                    print bl4, bl4r
                raise unexception("bad page header", paranumC(self.undocname, None, 0, -1, txlines[0].textcountnumber))

            ie = len(txlines) - 1
            if re.match("\d\d\-\d\d\d\d\d", txlines[ie].ltext):
                ie -= 1
            pagenumtext = txlines[ie].ltext
            mpagenumtext = re.match("(?:<b>)?(\d+)\s*(?:</b>)?$", pagenumtext)
            if not mpagenumtext:
                if IsNotQuiet():
                    print "jkjk", pagenumtext
                raise unexception("pagenum error not a number", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))
            pgoffset = int(mpagenumtext.group(1)) - self.pageno
            if pgoffset != 0 and self.undocname not in misnumberedpages:
                if IsNotQuiet():
                    print "pagenum-offset not in list", self.undocname, mpagenumtext.group(1), self.pageno
                raise unexception("page pagenum error of speaker-intro", paranumC(self.undocname, None, 0, -1, txlines[ie].textcountnumber))
            if re.match("\d\d-\d\d\d\d\d$", txlines[ie - 1].ltext):
                ie -= 1

        else:
            assert False

        # separate out the header and footers
        self.txlheader = txlines[:ih]
        self.txlfooter = txlines[ie:]

        # separate the body into the two columns
        self.txlcol1 = [ ]
        self.txlcol2 = [ ]
        self.minindentleft = 9999
        self.minindentright = 9999
        for txl in txlines[ih:ie]:
            if txl.left < 459:
                #print txl.bfootertype, txl.left, txl.width, txl.top, txl.ltext  # zzzz
                # there's a bit of spilling out where the region is larger than it should be for the words as in A-56-PV.64
                if not (txl.left + txl.width <= 459):
                    if txl.left + txl.width > 501:
                        if IsNotQuiet():
                            print txl.left, txl.width, txl.left + txl.width
                            print txl.ltext
                            print "might have page no. 1 on first page (or add to twopageagendas)"
                        raise unexception("right-hand extension excessive", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
                    if not (txl.left <= 165):
                        bc = -1
                        while True:
                            assert self.txlcol1[-1].txls[bc].top == txl.top  # in-line but shorter
                            if (self.txlcol1[-1].txls[bc].left <= 165):
                                break
                            bc -= 1

                txl.indent = txl.left - leftcolstart
                if txl.indent < 0:
                    if IsNotQuiet():
                        print txl.indent, txl.ltext
                    raise unexception("negative indentation", paranumC(txl.undocname, None, 0, -1, txl.textcountnumber))
                self.minindentleft = min(txl.indent, self.minindentleft)
                txl.brightcol = False
                AppendToCluster(self.txlcol1, txl)

            else:
                txl.indent = txl.left - rightcolstart
                if txl.indent != 0:
                    txl.indent += rightcolstartindentincrement
                if txl.indent < 0:
                    if IsNotQuiet():
                        print txl.indent, txl.left, rightcolstart
                        print txl.ltext
                    raise unexception("negative indent on righthand column", paranumC(self.undocname, None, 0, -1, self.textcountnumber))
                self.minindentright = min(txl.indent, self.minindentright)
                txl.brightcol = True
                AppendToCluster(self.txlcol2, txl)

        #if self.txlcol1 and self.minindentleft != 0:
        #    print "minindentleft", self.minindentleft
        #if self.txlcol2 and self.minindentright != 0:
        #    print "minindentright", self.minindentright


# clusters are paragraphs after the lines have been clustered together
class GlueUnfile:
    def __init__(self, xfil, undocname):
        self.sdate = None
        self.chairs = None
        self.agenda = None
        self.tlcall = None
        self.seccouncilmembers = None
        self.bSecurityCouncil = re.match("S-PV.\d+", undocname)
        self.bGeneralAssembly = re.match("A-\d+-PV", undocname)

        xpages = StripPageTags(xfil, undocname)
        if not xpages:
            return  # bitmap type encountered
        txpages = [ ]
        self.tlcall = [ ]

        for i in range(len(xpages)):
            txpage = TextPage(xpages[i], undocname, i + 1, (txpages or 0) and txpages[-1].textcountnumber)
            if i == 0 and txpage.bSecurityCouncil == "ClosedSession":
                if IsNotQuiet():
                    print " -- closedsession"
                self.tlcall = None
                return  # closed session encountered
            txpages.append(txpage)

            if txpage.bSecurityCouncil and i == 0:
                continue

            # special cases of agenda overflowing into two pages
            if txpage.bSecurityCouncil and i == 1 and undocname in twopageagendas:
                txpages[0].agenda = "%s %s" % (txpages[0].agenda, txpage.agenda) # ram it all into one paragraph (who cares)
                continue

            bmissingcolumns = undocname in ["A-61-PV.106", "A-52-PV.39"]
            if txpage.txlcol1:
                AppendCluster(self.tlcall, txpage.txlcol1[0], "newpage")
                for tlc in txpage.txlcol1[1:]:
                    AppendCluster(self.tlcall, tlc, "gapcluster")
            elif not bmissingcolumns:
                #assert i == len(xpages) - 1  # only last page can have missing columns (sometimes it's the first)
                print "page", i, "of", len(xpages)
                #print txpages[-1].textcountnumber
                raise unexception("missing column not on last page", paranumC(undocname, None, 0, -1, txpages[-1].textcountnumber))

            # have had a case where the first column was the blank one
            if txpage.txlcol2:
                AppendCluster(self.tlcall, txpage.txlcol2[0], "newcolumn")
                for tlc in txpage.txlcol2[1:]:
                    AppendCluster(self.tlcall, tlc, "gapcluster")
            elif not bmissingcolumns:
                assert i == len(xpages) - 1, "%d != %d" % (i, len(xpages) - 1)

        # assign ids to the clusters
        self.sdate = txpages[0].date
        paranumlast = paranumC(undocname, self.sdate, 0, -1, 0)
        for tlc in self.tlcall:
            if tlc.txls[0].pageno == paranumlast.pageno:
                paranumlast = paranumC(undocname, self.sdate, paranumlast.pageno, paranumlast.paragraphno + 1, tlc.txls[0].textcountnumber)
            else:
                paranumlast = paranumC(undocname, self.sdate, tlc.txls[0].pageno, 1, tlc.txls[0].textcountnumber)
            tlc.paranum = paranumlast


        # merge the lines together and remove double bold/italics that happen across lines
        for tlc in self.tlcall:
            jparatext = [ ]  # don't insert spaces where there is a hyphen
            for txl in tlc.txls:
                if jparatext and not (re.search("\w[-/]$", jparatext[-1]) and re.match("\w", txl.ltext)):
                    jparatext.append(" ")
                jparatext.append(txl.ltext)
            tlc.paratext = "".join(jparatext)

            tlc.paratext = re.sub("-</i> <i>", "-", tlc.paratext)
            tlc.paratext = re.sub("-</b> <b>", "-", tlc.paratext)
            tlc.paratext = re.sub("</b>\s*\.\s*<b>", ". ", tlc.paratext)
            tlc.paratext = re.sub("Secretary- General", "Secretary-General", tlc.paratext)
            tlc.paratext = re.sub("\s*(?:</i>\s*<i>|</b>\s*<b>|<b>\s*</b>|<i>\s*</i>|<b>\s*<i>\s*</b>\s*</i>)\s*", " ", tlc.paratext)
            tlc.paratext = tlc.paratext.strip()

            tlc.paratext = re.sub("^<b>(The(?: Acting)? Co-Chairperson) \(([^\)]*)\)\s*(?:</b>\s*:|:\s*</b>)", "<b>\\1</b> (\\2):", tlc.paratext)
            tlc.lastindent = tlc.indents[-1][0]

        self.agenda = txpages[0].agenda
        self.chairs = txpages[0].chairs
        if self.bSecurityCouncil:
            self.seccouncilmembers = txpages[0].seccouncilmembers



