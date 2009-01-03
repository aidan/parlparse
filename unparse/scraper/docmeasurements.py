#!/usr/bin/python

import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs, IsNotQuiet, RomanToDecimal
from pdfinfo import PdfInfo
import datetime

# most of the code in this file will become redundant
import unpylons.model as model   

currentyear = datetime.date.today().year
currentsession = currentyear - 1946
if datetime.date.today().month >= 9:
    currentsession += 1

# writes docmeasurements.html
def MakeMeetSeq():
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
        self.gadlist = { }
        self.scdlist = { }
        self.scplist = { }
        self.gavlist = { }
        self.scvlist = { }
        self.scrlist = { }
        self.garlist = { }
        self.nationyearactivity = { }

        self.meetseq = MakeMeetSeq()

        self.nationcounts = { }
        for nation in nationdates:
            self.nationcounts[nation] = MakeNationMeetSeq(nation, self.meetseq)

    def IncrPdfCount(self, docid):
        mgadoc = re.match("A-(\d\d)-[L\d]", docid)
        mscdoc = re.match("S-(\d\d\d\d)-\d", docid)
        mgares = re.match("A-RES-(\d+)-(\d+)", docid)
        mgaresroman = re.match("A-RES-(\d+)\(([IVXL]+)\)", docid)
        mscprst = re.match("S-PRST-(\d\d\d\d)", docid)
        mscres = re.match("S-RES-\d+\((\d\d\d\d)\)", docid)

        if mgadoc:
            if mgadoc.group(1) in self.gadlist:
                self.gadlist[mgadoc.group(1)].append(docid)
            else:
                self.gadlist[mgadoc.group(1)] = [ docid ]
        elif mscdoc:
            if mscdoc.group(1) in self.scdlist:
                self.scdlist[mscdoc.group(1)].append(docid)
            else:
                self.scdlist[mscdoc.group(1)] = [ docid ]
        elif mgares:
            if mgares.group(1) in self.garlist:
                self.garlist[mgares.group(1)].append(docid)
            else:
                self.garlist[mgares.group(1)] = [ docid ]
        elif mgaresroman:
            yr = RomanToDecimal(mgaresroman.group(2))
            syr = "%d" % yr
            if IsNotQuiet():
                print mgaresroman.group(2), "roman", syr
            if syr in self.garlist:
                self.garlist[syr].append(docid)
            else:
                self.garlist[syr] = [ docid ]
        elif mscprst:
            if mscprst.group(1) in self.scplist:
                self.scplist[mscprst.group(1)].append(docid)
            else:
                self.scplist[mscprst.group(1)] = [ docid ]
        elif mscres:
            if mscres.group(1) in self.scrlist:
                self.scrlist[mscres.group(1)].append(docid)
            else:
                self.scrlist[mscres.group(1)] = [ docid ]
        elif not re.search("A-\d\d-PV|S-PV.\d\d\d\d", docid):
            if IsNotQuiet():
                print "What is this?", docid

    def IncrHtmlCount(self, htdoc, ftext):
        maga = re.search("(A-(\d\d)-PV.*?)(\.html)", htdoc)
        masc = re.search("(S-PV.(\d\d\d\d).*?)(\.html)", htdoc)
        if maga:
            docid = htdoc[maga.start(0):]
            if maga.group(2) in self.gavlist:
                self.gavlist[maga.group(2)].append(docid)
            else:
                self.gavlist[maga.group(2)] = [ docid ]
            #SetValuesOnGA(self.nationcounts, "GA%s" % maga.group(1), ftext)

        elif masc:
            docid = htdoc[masc.start(0):]
            mdate = re.search('<span class="date">(\d\d\d\d)-\d\d-\d\d</span>', ftext)
            if mdate.group(1) in self.scvlist:
                self.scvlist[mdate.group(1)].append(docid)
            else:
                self.scvlist[mdate.group(1)] = [ docid ]
            #SetValuesOnGA(self.nationcounts, "SC%s" % mdate.group(1), ftext)

        else:
            print "what is this?", htdoc

    def WriteTablesDocMeasureShort(self, fout):
        fout.write('\n<table class="docmeasuresshort"><caption>Short summary of documents present</caption>\n')
        fout.write('<tr class="heading"><th class="docmeasyear">Year</th><th class="docmeasdocs">Docs</th></tr>\n')
        for meeto in self.meetseq:
            if meeto[1] == "SC":
                sscy = meeto[2]
                scbase = "securitycouncil/%s" % sscy
                fout.write('<tr class="scrow"> <td class="scyear"><a href="%s" title="Security Council">%s</a></td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, scbase, len(self.scvlist.get(sscy, [])) + len(self.scrlist.get(sscy, [])) + len(self.scdlist.get(sscy, []))))
            if meeto[1] == "GA":
                sgas = meeto[2]
                gabase = "generalassembly/%s" % sgas
                fout.write('<tr class="garow"> <td class="gasess"><a href="%s" title="General Assembly">Session %s</a></td> <td class="num"><a href="%s/documents">%d</a></td>\n' % (gabase, sgas, gabase, len(self.gavlist.get(sgas, [])) + len(self.garlist.get(sgas, [])) + len(self.gadlist.get(sgas, []))))
        fout.write("</table>\n")

    def WriteTablesDocMeasures(self, fout):
        fout.write('\n<table class="docmeasures"><caption>Long summary of documents present</caption>\n')
        fout.write('<tr class="heading"><th class="docmeasyear">Year</th> <th class="docmeasmeetings">Number of Meetings</th> <th class="docmeasres">Number of Resolutions</th> <th class="docmeasdocs">Number of Documents</th></tr>\n');
        for meeto in self.meetseq:
            if meeto[1] == "SC":
                sscy = meeto[2]
                scbase = "securitycouncil/%s" % sscy
                fout.write('<tr class="scrow"> <td class="scyear"><a href="%s">%s</a></td> <td>%d</td> <td>%d</td> <td class="num"><a href="%s/documents">%d</a></td> </tr>\n' % (scbase, sscy, len(self.scvlist.get(sscy, [])), len(self.scrlist.get(sscy, [])), scbase, len(self.scdlist.get(sscy, [])) + len(self.scplist.get(sscy, []))))
            if meeto[1] == "GA":
                sgas = meeto[2]
                gabase = "generalassembly/%s" % sgas
                fout.write('<tr class="garow"> <td class="gasess"><a href="%s">Session %s</a></td> <td>%d</td> <td>%d</td> <td><a href="%s/documents">%d</a></td> </tr>\n' % (gabase, sgas, len(self.gavlist.get(sgas, [])), len(self.garlist.get(sgas, [])), gabase, len(self.gadlist.get(sgas, []))))
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

    def WriteDocyear(self, docyearsdir):
        for scyear in range(1946, currentyear + 1):
            fout = open(os.path.join(docyearsdir, "sc%d.txt" % scyear), "w")
            sscyear = "%d" % scyear
            if sscyear in self.scvlist:
                self.scvlist[sscyear].sort()
                for docid in self.scvlist[sscyear]:
                    fout.write("%s PV\n" % docid)
            if sscyear in self.scdlist:
                scdsort = [ (int(re.match("S-\d+-(\d+)", docid).group(1)), docid)  for docid in self.scdlist[sscyear] ]
                scdsort.sort()
                for dk, docid in scdsort:
                    fout.write("%s DOC\n" % docid)
            if sscyear in self.scplist:
                scpsort = [ (int(re.match("S-PRST-\d+-(\d+)", docid).group(1)), docid)  for docid in self.scplist[sscyear] ]
                scpsort.sort()
                for pk, docid in scpsort:
                    fout.write("%s PRST\n" % docid)
            if sscyear in self.scrlist:
                self.scrlist[sscyear].sort()
                for docid in self.scrlist[sscyear]:
                    fout.write("%s RES\n" % docid)
            fout.close()

        for gasess in range(1, currentsession + 1):
            fout = open(os.path.join(docyearsdir, "ga%d.txt" % gasess), "w")
            sgasess = "%d" % gasess
            if sgasess in self.gavlist:
                gavsort = [ (int(re.match("A-\d+-PV.(\d+)", docid).group(1)), docid)  for docid in self.gavlist[sgasess] ]
                gavsort.sort()
                for vk, docid in gavsort:
                    fout.write("%s PV\n" % docid)
            if sgasess in self.gadlist:
                gadsort = [ (int(re.match("A-\d+-(?:L\.)?(\d+)", docid).group(1)), docid)  for docid in self.gadlist[sgasess] ]
                gadsort.sort()
                for dk, docid in gadsort:
                    fout.write("%s DOC\n" % docid)
            if sgasess in self.garlist:
                garsort = [ ]
                for docid in self.garlist[sgasess]:
                    mgar = re.match("A-RES-\d+-(\d+)|A-RES-(\d+)", docid)
                    garsort.append((int(mgar.group(1) or mgar.group(2)), docid))
                garsort.sort()
                for ak, docid in garsort:
                    fout.write("%s RES\n" % docid)
            fout.close()


def UpdatePdfInfoFromPV(pdfinfos, pdfinfo, ftext):
    mtime = re.search('<span class="date">([^<]*)</span>\s*<span class="time">([^<]*)</span>\s*<span class="rosetime">([^<]*)</span>', ftext)
    if mtime:
        pdfinfo.sdate, pdfinfo.time, pdfinfo.rosetime = mtime.group(1), mtime.group(2), mtime.group(3)
    else:
        pdfinfo.sdate, pdfinfo.time, pdfinfo.rosetime = "unknown", "unknown", "unknown"

    gid = ""
    for mdoc in re.finditer('id="([^"]*)"|<a href="../pdf/([\w\-\.()]*?)\.pdf"[^>]*>', ftext):
        if mdoc.group(1):
            gid = mdoc.group(1)
        if mdoc.group(2):
            pdfc = mdoc.group(2)
            #assert re.match("[\w\-\.()]*$", pdfc), docid + "  " + pdfc
            if pdfc not in pdfinfos:
                pdfinfos[pdfc] = PdfInfo(pdfc)
            pdfinfos[pdfc].AddDocRef(pdfinfo.pdfc, gid, pdfinfo.sdate)



# Main file
def WriteDocMeasurements(stem, bforcedocmeasurements, htmldir, pdfdir, pdfinfodir, indexstuffdir):
    for pdf in reversed(sorted(os.listdir(pdfdir))):
        mdocid = re.match("([AS].*?)\.pdf$", pdf)
        if not mdocid:
            continue
        docid = mdocid.group(1)
        if stem and not re.match(stem, docid):
            continue
        if not bforcedocmeasurements and model.Document.query.filter_by(docid=docid).first():
            continue
        model.ProcessDocumentPylon(docid, pdfdir, htmldir)
    print "Quitting after doing the pylons loading"
    return


    rels = GetAllHtmlDocs("", False, False, htmldir)
    doccounts = DocCounts()
    pdfinfos = { }


    for pdf in os.listdir(pdfdir):
        if not re.search("\.pdf$", pdf):
            continue
        pdfc = pdf[:-4]
        pdfinfos[pdfc] = PdfInfo(pdfc)
        doccounts.IncrPdfCount(pdfc)  # should borrow the judgements from the PdfInfo

    for pdfi in os.listdir(pdfinfodir):
        if not re.search("\.txt$", pdfi):
            continue
        pdfc = pdfi[:-4]
        if pdfc not in pdfinfos:
            pdfinfos[pdfc] = PdfInfo(pdfc)  # loading up infos that don't have associated pdfs
        pdfinfos[pdfc].UpdateInfo(pdfinfodir)
        pdfinfos[pdfc].ResetDocmeasureData()
        pdfinfos[pdfc].pvrefs.clear()  # we're going to re-fill it

    for pdfinfo in pdfinfos.values():
        if pdfinfo.pages == -1:
            if sys.platform != "win32":
                pdfinfo.UpdatePages(pdfdir)
            if IsNotQuiet() and pdfinfo.pages != -1:
                print pdfinfo.pdfc, pdfinfo.pages,
                pdfinfo.WriteInfo(pdfinfodir)

    scpvlist = [ ]
    gapvlist = [ ]
    for htdoc in rels:
        fin = open(htdoc)
        ftext = fin.read()
        fin.close()

        docid = re.search("((?:A-\d\d|S-PV).*?)\.html$", htdoc).group(1)
        if IsNotQuiet():
            print docid,
        doccounts.IncrHtmlCount(htdoc, ftext)
        if docid in pdfinfos:
            pdfinfo = pdfinfos[docid]
            UpdatePdfInfoFromPV(pdfinfos, pdfinfo, ftext)
            if pdfinfo.nsess:
                gapvlist.append((pdfinfo.sortkey, pdfinfo))
            elif pdfinfo.nscyear:
                scpvlist.append((pdfinfo.sortkey, pdfinfo))

    # produce the next and previous
    scpvlist.sort()
    gapvlist.sort()
    scprev = None
    for sortkey, scnext in scpvlist:
        scnext.AddPrevMeetingDetails(scprev)
        scprev = scnext
    gaprev = None
    for sortkey, ganext in gapvlist:
        ganext.AddPrevMeetingDetails(gaprev)
        gaprev = ganext

    # write out all the data
    for pdfinfo in pdfinfos.values():
        pdfinfo.WriteInfo(pdfinfodir)

    doccounts.WriteDocyear(os.path.join(indexstuffdir, "docyears"))

    fout = open(os.path.join(indexstuffdir, "docmeasurements.html"), "w")
    doccounts.WriteTablesDocMeasureShort(fout)
    doccounts.WriteTablesDocMeasures(fout)
    doccounts.WriteTablesNationCounts(fout)
    fout.close()


