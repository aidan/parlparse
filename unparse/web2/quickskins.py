import os
import sys
import re
import cgi
import urllib, urlparse

import datetime
from basicbits import WriteGenHTMLhead, nowdatetime, monthnames, LongDateNB, EncodeHref

nowyear = nowdatetime[:4]
monthspellings = { "Janurary":"January", "Febuary":"February", "Septmeber":"September" }
def ConvWCDate(day, month, year):
    d = int(day)
    month = monthspellings.get(month, month)
    m = monthnames.index(month) + 1
    y = int(year)
    if 1 <= y <= int(nowdatetime[2:4]):
        y += 2000
    return "%04d-%02d-%02d" % (y, m, d)


reundoc = "A(?:/C.\d)?/\d\d/(?:L\.)?\d+(?:/Add\.\d+)?(?:/Rev\.\d+)?|S(?:/PRST)?/\d\d\d\d/\d+"
respl = re.compile('(?i)(<a\shref="[^"]*"[^>]*>[\s\S]*?</a>|%s|\s)' % reundoc)
def ConvWCText(wctext, url):
    wcs = respl.split(wctext)
    res = [ ]
    for wcss in wcs:
        ma = re.match('(?i)<a\shref="([^"]*)"[^>]*>([\s\S]*?)</a>', wcss)
        if ma:
            lkc = ma.group(2).strip()
            if re.match(reundoc, lkc):
                res.append('<a href="/%s" class="undlink">%s</a>' % (lkc, lkc))
            else:
                res.append('<a href="%s">%s</a>' % (urlparse.urljoin(url, ma.group(1)), ma.group(2)))
        elif re.match(reundoc, wcss):
            res.append('<a href="/%s" class="undlink">%s</a>' % (wcss, wcss))
        else:
            res.append(wcss)

    return "".join(res)

def ScrapeParseWCIndexPage(url):
    fin = urllib.urlopen(url)
    wcindex = fin.read()
    fin.close()

    rows = re.findall("""(?x)<tr[^>]*>\s*<td[^>]*>
                      (?:<(?:font|strong)[^>]*>|\s)*
                      (\d+)\s+(\w+)\s+(\d+)
                      (?:</(?:font|strong)>|\s)*(?:</td>)?\s*
                      <td[^>]*>([\s\S]*?)
                      (?:</td>\s*</tr>|(?=<tr))
                      """, wcindex)
    return [ (ConvWCDate(r[0], r[1], r[2]), ConvWCText(r[3], url))  for r in rows ] 


def WriteWebcastIndexPage(body, wcdate):
    if body == "securitycouncil":
        urlt, year = "sc.html", "2008"
        sbody = "Security Council"
        if wcdate and "2003" <= wcdate[:4] < nowyear:
            year = wcdate[:4]
            if year == "2004":
                urlt = "sc2004.htm" # anomaly
            else:
                urlt = "sc%s.html" % year
    else:  # body == "generalassembly"
        urlt, year = "ga.html", nowyear
        sbody = "General Assembly"
        if wcdate and "2003" <= wcdate[:4] < nowyear:
            year = wcdate[:4]
            if year <= "2004":
                urlt = "ga2004.htm"  # doubling up and no l
            else:
                urlt = "ga%s.html" % year
    url = "http://www.un.org/webcast/%s" % urlt
     
    WriteGenHTMLhead("%s webcast index for %s" % (sbody, year))
    print "<h2>Skinned index page</h2>"
    print '<p>The original webcast archive page for %s is <a href="%s">here</a>.' % (sbody, url)
    print 'Unfortunately, it lacks local anchors to the rows in the table which would have made it '
    print 'possible to directly link to them.  Nor does it include links to the UN documents that are referenced '
    print 'by their code-number.  The main UN page for webcasts is <a href="http://www.un.org/webcast">here</a>.</p>'

    spip = ScrapeParseWCIndexPage(url)
    
    print '<table id="wclist">'
    prevdate = ""
    for rl in spip:
        if rl[0] != prevdate:
            print '<tr id="d%s">' % rl[0]
            prevdate = rl[0]
        else:
            print '<tr>'
        print '<td class="wcdate">%s</td>' % LongDateNB(rl[0])
        print '<td class="wccont">%s</td>' % rl[1]
        print "</tr>"
    print "</table>"

def WebcastLink(body, wcdate):
    if body == "securitycouncil" and wcdate >= "2003-01-09":
        return EncodeHref({"pagefunc":"webcastindex", "body":"securitycouncil", "date":wcdate})
    if body == "generalassembly" and wcdate >= "2003-07-03":
        return EncodeHref({"pagefunc":"webcastindex", "body":"generalassembly", "date":wcdate})
    return ""

