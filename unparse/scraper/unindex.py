import os
import re
import sys
from unmisc import IsNotQuiet

webdocurl = "http://www.freesteel.co.uk/cgi-bin/unview.py?code="

stylehack = """
table.main
{
    border-spacing: 0;
}
table.main td,
table.main th
{
    border: solid 0.4px black;
    vertical-align: top;
    text-align: right;
}
table.votes td
{
    border: none;
}
tr.AA
{
    color: red;
}
a.nolink
{
    color:gray;
}
"""


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
        self.bSecurityCouncil = re.search("S-PV", self.code)
        self.bGeneralAssembly = re.search("A-\d\d-PV", self.code)
        self.date = mhead.group(2)
        self.time = mhead.group(3)
        self.kbytes = len(fd) / 1024.0
        self.pages = int(re.findall('id="pg(\d+)-', fd)[-1])
        self.votes = re.findall('"recvote" id="([^"]*)"[\s\S]*?<p class="votecount">favour=(\d+) against=(\d+) abstain=(\d+) absent=(\d+)</p>', fd)
        self.links = re.findall('<a href="\.\./pdf/([^"]*?)\.pdf"([^>]*)>', fd)
        lspeakers = re.findall('<span class="name">([^<]*)</span> <span class="nation">([^<]*)</span>', fd)
        lspeakers.sort()
        self.speakers = [ ]
        for s in lspeakers:
            if (not self.speakers or (s != self.speakers[-1])) and not re.search("President", s[0]):
                self.speakers.append((s[1], s[0]))

    def GetRow(self):
        res = [ ]
        res.append("<tr>")
        if self.rowspan != 0:
            res.append('<td rowspan="%s">%s</td>' % (self.rowspan, self.date))
        res.append("<td>%s</td>" % self.time)
        res.append('<td><a href="%s%s">%s</td>' % (webdocurl, self.code, self.code))
        res.append("<td>%d</td>" % (self.pages))
        res.append("<td>%d</td>" % len(self.speakers))
        res.append("<td>")


# colours in the votelist block
# reparse then

        if self.votes:
            res.append('<table class="votes">')
            for vote in self.votes:
                scla = ((self.bSecurityCouncil and (int(vote[1]) != 15)) or (self.bGeneralAssembly and 1 <= int(vote[2]) <= 5)) and ' class="AA"' or ''
                res.append('<tr%s><td>-%s</td><td><a href="%s%s#%s">+%s</a></td><td>0%s</td></tr>' % (scla, vote[2], webdocurl, self.code, vote[0], vote[1], vote[3]))
            res.append('</table>')

        res.append("</td>")
        res.append("<td>")
        prevlink = ""
        for link in sorted(self.links):
            if link[0] != prevlink:
                res.append(' <a href="%s%s"%s>%s</a>' % (webdocurl, link[0], link[1], link[0]))
                prevlink = link[0]

        res.append("</td>")
        res.append("</tr>")
        return "".join(res)

    def GetHeadRow(self):
        res = [ ]
        res.append("<tr>")
        res.append("<th>date</th> <th>time</th>")
        res.append("<th>code</th>")
        res.append("<th>pages</th>")
        res.append("<th>speakers</t>")
        res.append("<th>votes</t>")
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
        if IsNotQuiet():
            print undocname,

    undocdatelist.sort()

    # work out the rowspans
    undocdatelast = None
    for undocdate in undocdatelist:
        if undocdatelast and undocdatelast[1].date == undocdate[1].date:
            undocdatelast[1].rowspan += 1
            undocdate[1].rowspan = 0
        else:
            undocdate[1].rowspan = 1
            undocdatelast = undocdate

    undateindex = os.path.join(htmldir, "index.html")
    tmpfile = undateindex + "--temp"
    fout = open(tmpfile, "w")
    fout.write('<html>\n<head>\n')
    #fout.write('<link href="unview.css" type="text/css" rel="stylesheet" media="all">\n')
    fout.write('<style type="text/css">%s</style>' % stylehack)
    fout.write('</head>\n<body>\n')
    fout.write('<table class="main">\n')

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

