#!/usr/bin/python2.4
import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs
from pdfinfo import PdfInfo
import datetime

# writes docmeasurements.html
def MakeMeetSeq():
    currentyear = datetime.date.today().year
    currentsession = currentyear - 1946
    if datetime.date.today().month >= 9:
        currentsession += 1

    meetseq = [ ]  # used to sort the SC and GAs
    for gas in range(currentsession, 47, -1):
        meetseq.append(("%4d-09-01" % (gas + 1945), "GA", "%2d" % gas))
    for scs in range(currentyear, 1992, -1):
        meetseq.append(("%4d-01-01" % scs, "SC", "%4d" % scs))
    meetseq.sort()
    meetseq.reverse()
    return meetseq


def SetValuesOnGA(nationcounts, gacode, ftext):
    for nation in re.findall('<span class="nation">([^<]+)</span>', ftext):
        if nation == "Brunei Darussalam":
            continue
        if nation != "None":
            if gacode not in nationcounts[nation]:
                print nation, gacode
            nationcounts[nation][gacode][0] += 1


def MakeNationMeetSeq(nation, meetseq):
    nationparams = nationdates[nation]
    res = { }
    for meeto in meetseq:
        if meeto[1] == "GA":
            prevsdate = "%4d%s" % (int(nationparams["Date entered UN"][:4]) - 1, nationparams["Date entered UN"][4:])
            if prevsdate <= meeto[0] <= nationparams["Date left UN"]:
                res["GA%s" % meeto[2]] = [ 0, 0 ]
        if meeto[1] == "SC":
            if nationparams["Date entered UN"][:4] <= meeto[0][:4] <= nationparams["Date left UN"][:4]:
                res["SC%s" % meeto[2]] = [ 0, 0 ]
    return res

class DocCounts:
    def __init__(self):
        self.gadcount = { }
        self.scdcount = { }
        self.scpcount = { }
        self.gavcount = { }
        self.scvcount = { }
        self.scrcount = { }
        self.garcount = { }
        self.nationyearactivity = { }

        self.meetseq = MakeMeetSeq()

        self.nationcounts = { }
        for nation in nationdates:
            self.nationcounts[nation] = MakeNationMeetSeq(nation, self.meetseq)

    def IncrPdfCount(self, pdf):
        mgadoc = re.match("A-(\d\d)-[L\d]", pdf)
        mscdoc = re.match("S-(\d\d\d\d)-\d", pdf)
        mgares = re.match("A-RES-(\d\d)", pdf)
        mscprst = re.match("S-PRST-(\d\d\d\d)", pdf)
        mscres = re.match("S-RES-\d+\((\d\d\d\d)\)", pdf)

        if mgadoc:
            self.gadcount[mgadoc.group(1)] = self.gadcount.setdefault(mgadoc.group(1), 0) + 1
        elif mscdoc:
            self.scdcount[mscdoc.group(1)] = self.scdcount.setdefault(mscdoc.group(1), 0) + 1
        elif mgares:
            self.garcount[mgares.group(1)] = self.garcount.setdefault(mgares.group(1), 0) + 1
        elif mscprst:
            self.scpcount[mscprst.group(1)] = self.scpcount.setdefault(mscprst.group(1), 0) + 1
        elif mscres:
            self.scrcount[mscres.group(1)] = self.scrcount.setdefault(mscres.group(1), 0) + 1
        elif not re.search("A-\d\d-PV|S-PV-\d\d\d\d", pdf):
            print "What is this?", pdf

    def IncrHtmlCount(self, htdoc, ftext):
        maga = re.search("A-(\d\d)-PV", htdoc)
        masc = re.search("S-PV-(\d\d\d\d)", htdoc)
        if maga:
            self.gavcount[maga.group(1)] = self.gavcount.setdefault(maga.group(1), 0) + 1
            SetValuesOnGA(self.nationcounts, "GA%s" % maga.group(1), ftext)

        elif masc:
            mdate = re.search('<span class="date">(\d\d\d\d)-\d\d-\d\d</span>', ftext)
            self.scvcount[mdate.group(1)] = self.scvcount.setdefault(mdate.group(1), 0) + 1
            SetValuesOnGA(self.nationcounts, "SC%s" % mdate.group(1), ftext)

        else:
            print "what is this?", htdoc

    def WriteTablesDocMeasureShort(self, fout):
        fout.write('\n<table class="docmeasuresshort"><caption>Short summary of documents present</caption>\n')
        fout.write('<tr class="heading"><th class="docmeasyear">Year</th><th class="docmeasdocs">Docs</th></tr>\n')
        for meeto in self.meetseq:
            if meeto[1] == "SC":
                sscy = meeto[2]
                scbase = "securitycouncil/%s" % sscy
                fout.write('<tr class="scrow"> <td class="scyear"><a href="%s" title="Security Council">%s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, self.scvcount.get(sscy, 0) + self.scrcount.get(sscy, 0) + self.scdcount.get(sscy, 0)))
            if meeto[1] == "GA":
                sgas = meeto[2]
                gabase = "generalassembly/%s" % sgas
                fout.write('<tr class="garow"> <td class="gasess"><a href="%s" title="General Assembly">Session %s</a></td> <td class="num"><a href="%s/documents">%d</a></td>\n' % (gabase, sgas, gabase, self.gavcount.get(sgas, 0) + self.garcount.get(sgas, 0) + self.gadcount.get(sgas, 0)))
        fout.write("</table>\n")

    def WriteTablesDocMeasures(self, fout):
        fout.write('\n<table class="docmeasures"><caption>Long summary of documents present</caption>\n')
        fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Meetings</th> <th class="docmeasres">Number of Resolutions</th> <th class="docmeasdocs">Number of Documents</th></tr>\n');
        for meeto in self.meetseq:
            if meeto[1] == "SC":
                sscy = meeto[2]
                scbase = "securitycouncil/%s" % sscy
                fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td>%d</td> <td>%d</td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, self.scvcount.get(sscy, 0), self.scrcount.get(sscy, 0), scbase, self.scdcount.get(sscy, 0) + self.scpcount.get(sscy, 0)))
            if meeto[1] == "GA":
                sgas = meeto[2]
                gabase = "generalassembly/%s" % sgas
                fout.write('<tr class="garow"> <td class="gasess"><a href="%s">Session %s</a></td> <td>%d</td> <td>%d</td> <td><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, self.gavcount.get(sgas, 0), self.garcount.get(sgas, 0), gabase, self.gadcount.get(sgas, 0)))
        fout.write("</table>\n")

    def WriteTablesNationCounts(self, fout):
        for nation in self.nationcounts:
            nmeetseq = self.nationcounts[nation]
            fout.write('\n<table class="nationmeas" id="%s"><caption>Document summary for spoken by %s</caption>\n' % (nation, nation))
            fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Speeches</th></tr>\n');
            for meeto in self.meetseq:
                nmeeto = "%s%s" % (meeto[1], meeto[2])
                if nmeeto not in nmeetseq:
                    continue
                if meeto[1] == "SC":
                    sscy = meeto[2]
                    scbase = "securitycouncil/%s" % sscy
                    fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, self.nationcounts[nation][nmeeto][0]))
                if meeto[1] == "GA":
                    sgas = meeto[2]
                    gabase = "generalassembly/%s" % sgas
                    fout.write('<tr class="scrow"> <td class="gayear"><a href="%s">Session %s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, gabase, self.nationcounts[nation][nmeeto][0]))
            fout.write("</table>\n")


def UpdatePdfInfoFromPV(pdfinfos, ftext):
    mdatecode = re.search('<span class="code">([^<]*)</span> <span class="date">([^<]*)</span>', ftext)
    assert mdatecode, ftext[:200]
    docid = mdatecode.group(1)
    sdate = mdatecode.group(2)

    # will need to split by divs and ids etc
    mdate = re.search('<span class="date">(\d\d\d\d)-\d\d-\d\d</span>', ftext)
    gid = ""
    for mdoc in re.finditer('id="([^"]*)"|<a href="../pdf/([\w\-\.()]*?)\.pdf"[^>]*>', ftext):
        if mdoc.group(1):
            gid = mdoc.group(1)
        if mdoc.group(2):
            pdfc = mdoc.group(2)
            #assert re.match("[\w\-\.()]*$", pdfc), docid + "  " + pdfc
            if pdfc not in pdfinfos:
                pdfinfos[pdfc] = PdfInfo(pdfc)
            pdfinfos[pdfc].AddDocRef(docid, gid, sdate)

# Main file
def WriteDocMeasurements(htmldir, pdfdir, pdfinfodir, fout):
    rels = GetAllHtmlDocs("", False, False, htmldir)
    doccounts = DocCounts()
    pdfinfos = { }

    for pdf in os.listdir(pdfdir):
        if not re.search("\.pdf$", pdf):
            continue
        pdfc = pdf[:-4]
        #doccounts.IncrPdfCount(pdfc)
        pdfinfos[pdfc] = PdfInfo(pdfc)

    for pdfi in os.listdir(pdfinfodir):
        if not re.search("\.txt$", pdfi):
            continue
        pdfc = pdfi[:-4]
        if pdfc not in pdfinfos:
            pdfinfos[pdfc] = PdfInfo(pdfc)
        pdfinfos[pdfc].UpdateInfo(pdfinfodir)
        pdfinfos[pdfc].pvrefs.clear()  # we're going to re-fill it

    for htdoc in rels:
        fin = open(htdoc)
        ftext = fin.read()
        fin.close()
        #doccounts.IncrHtmlCount(htdoc, ftext)
        UpdatePdfInfoFromPV(pdfinfos, ftext)

    for pdfinfo in pdfinfos.values():
        pdfinfo.WriteInfo(pdfinfodir)

    doccounts.WriteTablesDocMeasureShort(fout)
    doccounts.WriteTablesDocMeasures(fout)
    doccounts.WriteTablesNationCounts(fout)


