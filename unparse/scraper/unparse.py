import os
import re
import sys
from nations import FixNationName
from unmisc import unexception, IsNotQuiet, MarkupLinks, paranumC
from unglue import GlueUnfile
from speechblock import SpeechBlock
from voteblock import VoteBlock, recvoterequest


def GroupParas(tlcall, undocname, sdate, seccouncilmembers):
    res = [ ]
    i = 0
    currentspeaker = None
    curragendanum = ""
    while i < len(tlcall):
        tlc = tlcall[i]
        if re.match(recvoterequest, tlc.paratext):
            lblock = VoteBlock(tlcall, i, undocname, sdate, seccouncilmembers)
            i = lblock.i

        # non-voting line to be processed
        else:

            speakerbeforetookchair = ""
            if (len(res) > 2) and (res[-1].typ in ["italicline-tookchair", "italicline-spokein"]) and (res[-2].typ == "spoken"):
                speakerbeforetookchair = res[-2].speaker
                if res[-1].typ == "italicline-spokein":
                    assert len(res[-1].paragraphs) == 1
                    mspokein = re.search("spoke in (\w+)", res[-1].paragraphs[0][1])
                    if not mspokein:
                        if IsNotQuiet():
                            print "unrecognized spokein", res[-1].paragraphs
                    #print "converting spokein", speakerbeforetookchair[2], mspokein.group(1)
                    speakerbeforetookchair = (speakerbeforetookchair[0], speakerbeforetookchair[1], mspokein.group(1), speakerbeforetookchair[3])

            lblock = SpeechBlock(tlcall, i, undocname, sdate, speakerbeforetookchair, curragendanum)
            if lblock.agendanum:
                curragendanum = lblock.agendanum

            i = lblock.i

        if res and res[-1].paranum.pageno == lblock.paranum.pageno:
            lblock.paranum.blockno = res[-1].paranum.blockno + 1
        else:
            lblock.paranum.blockno = 1
        res.append(lblock)

    # find the rosetime
    if res:
        res[-1].rosetime = res[-1].ExtractRoseTime(sdate[10:].strip())
        if undocname in ["S-PV-3698", "S-PV-3698-Resu.1", "S-PV-3765-Resu.2", "S-PV-4072-Resu.1", "S-PV-4174", "S-PV-4223", "S-PV-5100"]:
            assert not res[-1].rosetime
            res[-1].rosetime = sdate[10:].strip() # the missing rosetimes
        if not res[-1].rosetime:
            if undocname == "A-62-PV.79":
                res[-1].rosetime = "06:05"
            else:
                res[-1].writeblock(sys.stdout)
                raise unexception("can't find rosetime", res[-1].paranum)

    return res


# we should lose the .unindexed stuff because it'll be done with the timestamp
def ParsetoHTML(stem, pdfxmldir, htmldir, bforceparse, beditparse, bcontinueonerror):
    undocnames = [ ]
    for undoc in os.listdir(pdfxmldir):
        undocname = os.path.splitext(undoc)[0]
        if undoc[-1] == "~":
            continue
        if not re.match(stem, undocname):
            continue
        if re.search("Corr", undocname): # skip corregendas
            continue
        if not bforceparse:
            undochtml = os.path.join(htmldir, undocname + ".html")
            undochtmlunindexed = os.path.join(htmldir, undocname + ".unindexed.html")
            if os.path.isfile(undochtml) or os.path.isfile(undochtmlunindexed):
                continue
        undocnames.append(undocname)

    undocnames.sort()
    if IsNotQuiet():
        print "Preparing to parse %d files" % len(undocnames)

    for undocname in undocnames:
        undocpdfxml = os.path.join(pdfxmldir, undocname + ".xml")
        undochtml = os.path.join(htmldir, undocname + ".html")  # used to be ".unindexed.html"

        gparas = None
        lbeditparse = beditparse
        while not gparas:
            fin = open(undocpdfxml)
            xfil = fin.read()
            fin.close()

            if IsNotQuiet():
                print "parsing:", undocname,
            try:
                if lbeditparse:
                    lbeditparse = False
                    raise unexception("editparse", None)
                glueunfile = GlueUnfile(xfil, undocname)
                if not glueunfile.tlcall:
                    break   # happens when it's a bitmap type, or communique
                if IsNotQuiet():
                    print glueunfile.sdate#, chairs
                gparas = GroupParas(glueunfile.tlcall, undocname, glueunfile.sdate, glueunfile.seccouncilmembers)

            except unexception, ux:
                assert not gparas
                if ux.description != "editparse":
                    if bcontinueonerror:
                        break
                    print "\n\nError: %s on page %s textcounter %s" % (ux.description, ux.paranum.pageno, ux.paranum.textcountnumber)
                print "\nHit RETURN to launch your editor on the pdfxml file (or type 's' to skip, or 't' to throw)"
                rl = sys.stdin.readline()
                if rl[0] == "s":
                    break
                if rl[0] == "t":
                    raise

                if ux.description != "editparse":
                    fin = open(undocpdfxml, "r")
                    finlines = fin.read()
                    fin.close()
                    mfinlines = re.match("(?s)(.*?<text ){%d}" % ux.paranum.textcountnumber, finlines)
                    ln = mfinlines.group(0).count("\n")
                else:
                    ln = 1

                #editor = os.getenv('EDITOR')
                if sys.platform == "win32":
                    os.system('"C:\Program Files\ConTEXT\ConTEXT" %s /g00:%d' % (undocpdfxml, ln + 2))
                else:
                    os.system('vim "%s" +%d' % (undocpdfxml, ln + 2))

        if not gparas:
            continue

        # actually write the file
        tmpfile = undochtml + "--temp"
        fout = open(tmpfile, "w")
        fout.write('<html>\n<head>\n')
        fout.write('<link href="unview.css" type="text/css" rel="stylesheet" media="all">\n')
        fout.write('</head>\n<body>\n')

        fout.write('\n<div class="heading" id="pg000-bk00">\n')

        sdate, stime = glueunfile.sdate[:10], glueunfile.sdate[10:].strip()
        fout.write('\t<span class="code">%s</span> <span class="date">%s</span> <span class="time">%s</span>' % (undocname, sdate, stime))
        if gparas:
            fout.write('<span class="rosetime">%s</span>' % gparas[-1].rosetime)

        fout.write('\n</div>\n')

        if glueunfile.bSecurityCouncil:
            fout.write('\n<div class="council-agenda" id="pg000-bk01">\n')
            fout.write('\t<p class="boldline-p" id="pg000-bk01-pa01">%s</p>\n' % glueunfile.agenda)
            fout.write('</div>\n')
            fout.write('\n<div class="council-attendees" id="pg000-bk02">\n')
            ichairn = 0
            for chair in glueunfile.chairs:
                ichairn += 1
                fout.write('\t<p id="pg000-bk02-pa%02d">' % ichairn)
                for chperson in chair[0].split("/"):  # just for the extremely rare case we get two people sharing the seat
                    fout.write('<span class="name">%s</span> ' % chperson.strip())
                fout.write('<span class="nation">%s</span> <span class="place">%s</span></p>\n' % (chair[1], chair[2]))
            fout.write('</div>')

        if glueunfile.bGeneralAssembly:
            fout.write('\n<div class="assembly-chairs" id="pg000-bk03">\n')
            ichairn = 0
            for chair in glueunfile.chairs:
                ichairn += 1
                fout.write('\t<p id="pg000-bk03-pa%02d"><span class="name">%s</span> <span class="nation">%s</span> <span class="place">president</span></p>\n' % (ichairn, chair[0], chair[1]))
            fout.write('</div>\n')

        for gpara in gparas:
            gpara.writeblock(fout)

        # this for making the parsing a little easier
        fout.write('\n<div class="end-document" id="pg999-bk99">\n')
        fout.write('</div>\n')

        fout.write('\n</body>\n</html>\n')
        fout.close()
        if os.path.isfile(undochtml):
            os.remove(undochtml)
        os.rename(tmpfile, undochtml)



