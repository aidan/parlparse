#!/usr/bin/python

import sys, os, stat, re
import datetime

from basicbits import WriteGenHTMLhead
from basicbits import indexstuffdir, pdfdir, currentgasession, currentscyear
from basicbits import EncodeHref
from xapsearch import XapLookup
from indexrecords import LoadSecRecords

def LoadDocYearFile(docyearfile):
    dlists = { "PV":[ ], "DOC":[ ], "PRST":[ ], "RES":[ ] }
    fin = open(docyearfile)
    for rl in fin.readlines():
        docid, dl = rl.split()
        dlists[dl].append(docid)
    return dlists


def WriteIndexStuffDocumentsYear(docyearfile):
    msc = re.search("sc(\d+).txt$", docyearfile)
    mga = re.search("ga(\d+).txt$", docyearfile)
    if msc:
        WriteGenHTMLhead("Security Council %s Documents" % msc.group(1))
        nscyear = int(msc.group(1))

        print '<table class="prevnextmeeting"><tr>'
        if nscyear > 1946:
            print '<td><a href="%s">Year %d</td>' % (EncodeHref({"pagefunc":"scdocuments", "scyear":(nscyear - 1)}), nscyear - 1)
        else:
            print '<td></td>'

        nsess = max(1, min(currentgasession, nscyear - 1945))
        print '<td><a href="%s">Session %d</td>' % (EncodeHref({"pagefunc":"gadocuments", "gasession":nsess}), nsess)

        if nscyear < currentscyear:
            print '<td><a href="%s">Year %d</td>' % (EncodeHref({"pagefunc":"scdocuments", "scyear":(nscyear + 1)}), nscyear + 1)
        else:
            print '<td></td>'
        print '</tr></table>'

    else:
        WriteGenHTMLhead("General Assembly Session %s Documents" % mga.group(1))
        nsess = int(mga.group(1))

        print '<table class="prevnextmeeting"><tr>'
        if nsess > 1:
            print '<td><a href="%s">Session %d</td>' % (EncodeHref({"pagefunc":"gadocuments", "gasession":(nsess - 1)}), nsess - 1)
        else:
            print '<td></td>'

        nscyear = max(1946, min(currentscyear, nsess + 1945))
        print '<td><a href="%s">year %d</td>' % (EncodeHref({"pagefunc":"scdocuments", "scyear":nscyear}), nscyear)

        if nsess > 1:
            print '<td><a href="%s">Session %d</td>' % (EncodeHref({"pagefunc":"gadocuments", "gasession":(nsess + 1)}), nsess + 1)
        else:
            print '<td></td>'
        print '</tr></table>'

    dlists = LoadDocYearFile(docyearfile)

    if dlists["RES"]:
        print "<h3>Resolutions</h3>"
        print '<p>'
        for docid in dlists["RES"]:
            print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"document", "docid":docid}), docid)
        print '</p>'

    if dlists["DOC"]:
        print "<h3>Documents</h3>"
        print '<p>'
        for docid in dlists["DOC"]:
            print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"document", "docid":docid}), docid)
        print '</p>'

    if dlists["PRST"]:
        print "<h3>Presidential Statements</h3>"
        for docid in dlists["PRST"]:
            print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"document", "docid":docid}), docid)
        print '</p>'

    if dlists["PV"]:
        print "<h3>Verbatim Reports</h3>"
        for docidh in dlists["PV"]:
            if docidh[-5:] == ".html":
                if msc:
                    print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"meeting", "docid":docidh[:-5]}), docidh)
                else:
                    print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"meeting", "docid":docidh[:-5]}), docidh)
            else:
                print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"document", "docid":docid}), docid)
        print '</p>'


def WriteDocumentListing(body):
    docyearsdir = os.path.join(indexstuffdir, "docyears")
    if body == "securitycouncil":
        bSC, bGA = True, False
        WriteGenHTMLhead("Security Council Documents")
    elif body == "generalassembly":
        bSC, bGA = False, True
        WriteGenHTMLhead("General Assembly Documents")
    else:
        bSC, bGA = True, True
        WriteGenHTMLhead("All Documents")

    print '<p>This is a table of the numbers of UN documents we have obtained for reference '
    print 'of each kind sorted by year or session.  Click on the link to list the codes of all the documents '
    print 'for that year.</p>'

    print '<h2><b>New:</b> Find some <a href="%s">pre-1994 Security Council Transcripts</a>.</h3>' % EncodeHref({"pagefunc":"scyearearly"})
    
    print '<table class="doccounttable">'
    print '<tr><th>Year/Session</th>'
    print '<th>Verbatim<br>reports</th>'
    print '<th>Resolutions</th>'
    print '<th>Presidential<br>Statements</th>'
    print '<th>Documents</th>'
    print '</tr>'

    for s in range(max(currentgasession, currentscyear - 1945), 0, -1):
        gadocyearfile = os.path.join(docyearsdir, "ga%d.txt" % s)
        if bGA and os.path.isfile(gadocyearfile):
            dlist = LoadDocYearFile(gadocyearfile)
            print '<tr class="gadocs">'
            print '<td><a href="%s">Session %d</a>' % (EncodeHref({"pagefunc":"gadocuments", "gasession":s}), s)
            if not bSC:
                print ' (%s-%s)' % (s + 1945, s + 1946)
            print '</td> '
            print '<td>%d</td> <td>%d</td> <td> </td> <td>%d</td>' % (len(dlist["PV"]), len(dlist["RES"]), len(dlist["DOC"]))
            print '</tr>'
        scyear = s + 1945
        scdocyearfile = os.path.join(docyearsdir, "sc%d.txt" % scyear)
        if bSC and os.path.isfile(scdocyearfile):
            dlist = LoadDocYearFile(scdocyearfile)
            print '<tr class="scdocs">'
            print '<td><a href="%s">%d</a></td>' % (EncodeHref({"pagefunc":"scdocuments", "scyear":scyear}), scyear)
            print '<td>%d</td> <td>%d</td> <td>%d</td> <td>%d</td>' % (len(dlist["PV"]), len(dlist["RES"]), len(dlist["PRST"]), len(dlist["DOC"]))
            print '</tr>'

    print '</table>'


def WriteDocumentListingEarly(body):
    if body == "securitycouncil":
        bSC, bGA = True, False
        WriteGenHTMLhead("Security Council early Documents")
    elif body == "generalassembly":
        bSC, bGA = False, True
        WriteGenHTMLhead("General Assembly early Documents")
    else:
        bSC, bGA = True, True
        WriteGenHTMLhead("All early Documents")

    PVlist = [ ]
    for ldocid in os.listdir(pdfdir):
        if bSC:
            mpv = re.match("(S-PV-(\d+).*?)\.pdf$", ldocid)
            if mpv:
                PVlist.append((int(mpv.group(2)), mpv.group(1)))
    PVlist.sort()

    print '<p>Lists of early Security Council meeting transcripts of unknown vintage.'
    nh = -1; 
    for num, docid in PVlist:
        if num >= (nh + 1) * 100:
            nh = int(num / 100)
            print "</p>\n\n<h2>%d00's</h2>\n<p>" % nh
        print '<a href="%s">%s</a>' % (EncodeHref({"pagefunc":"document", "docid":docid}), docid)
    print '</p>'

        






