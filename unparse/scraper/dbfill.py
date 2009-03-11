#!/usr/bin/python
# -*- coding: latin1 -*-

# unparse/bin/xapdex.py - Index Julian's UN HTML in Xapian. Run with --help
# for command line options.

import sys
import re
import os
import os.path
import distutils.dir_util
import traceback
from unmisc import GetAllHtmlDocs, IsNotQuiet, IsVeryNoisy
from downascii import DownAscii
#from db import GetDBcursor, escape_string
from nations import nonnationcatmap # this was why the need to moveall into same directory

import unpylons.model as model

def MakeBaseXapianDoc(mdiv, tdocument_id, document_date, headingterms):
    div_class = mdiv.group(1)
    div_id = mdiv.group(2)
    div_agendanum = mdiv.group(3)
    div_text = mdiv.group(4)
    #print div_text

    terms = set()
    terms.add("C%s" % div_class)

    mblockid = re.match("pg(\d+)-bk(\d+)$", div_id)
    assert mblockid, "unable to decode blockid:%s" % div_id
    terms.add("I%s" % mblockid.group(0))

    if div_class in ['spoken', 'council-attendees', 'assembly-chairs']:
        for spclass in re.findall('<span class="([^"]*)">([^>]*)</span>', div_text):

            if spclass[0] == "name":
                speaker = re.sub("^\s*(?:Mr|Mrs|Ms|Sir|Miss|Dr|The|Rev)\.?\s+|-|'|`|\"|[A-Z]\.|\.", "", spclass[1]).lower()
                #print "SSS", speaker, spclass
                speakerspl = speaker.split()
                for i in range(max(0, len(speakerspl) - 3), len(speakerspl)):
                    terms.add("S%s" % CharToFlat("".join(speakerspl[i:])))

            if spclass[0] == "language":
                terms.add("L%s" % CharToFlat(spclass[1]))

            if spclass[0] == "nation":
                nationterm = "N%s" % CharToFlat(re.sub("['\-]", "", spclass[1]))
                terms.add(nationterm)
                if div_class == 'spoken':  # leave out just attending cases; that's listed in the terms of the attendee blocks type
                    headingterms.add(nationterm)

            if spclass[0] == "non-nation":
                for nncat in nonnationcatmap.get(spclass[1], "Unknown").split(","):
                    nationterm = "N%s" % CharToFlat(nncat)
                    terms.add(nationterm)
                    assert div_class == 'spoken'  # roll-call only applies to nations
                    headingterms.add(nationterm)
                    #print nationterm


    if div_agendanum:
        mgag = re.match("(address|condolence|show)-\d+$", div_agendanum)
        if mgag:
            terms.add("A%s" % mgag.group(1))
            if mgag.group(1) == "condolence":
                print "  AAAAA  ", div_agendanum
        for agnum in div_agendanum.split(","):  # a comma separated list
            terms.add("A%s" % agnum)

    # in the future we may break everything down to the paragraph level, and have 3 levels of heading backpointers
    textspl = [ ] # all the text broken into words
    rmaraiter = re.finditer('<(?:p|blockquote)(?: class="([^"]*)")? id="(pg(\d+)-bk(\d+)-pa(\d+))">(.*?)</(?:p|blockquote)>', div_text)

    if div_class in ['council-attendees', 'assembly-chairs']:
        rmaraiter = [ ]  # suppress this case (which just contains spans of seats, already loaded)

    if div_class == 'italicline-spokein':
        mitspokin =	re.match('\s*<p[^>]*><i>spoke in (\w+)', div_text)
        assert mitspokin, "Unmatched spokin: %s" % div_text
        terms.add("L%s" % re.sub("[^\w]", "", mitspokin.group(1)).lower())

    for mpara in rmaraiter:
        assert mpara.group(3) == mblockid.group(1) and mpara.group(4) == mblockid.group(2), "paraid disagrees with blockid: %s %s" % (div_id, mpara.group(0))
        # terms.add("J%s" % mpara.group(2))  # or could use mpara.group(5) # not necessary due to well-stemming
        paraclass = mpara.group(1)
        paratext = mpara.group(6).strip()

        if not paraclass or paraclass in ['boldline-p', 'boldline-indent', 'boldline-agenda', 'motiontext']:
            if paraclass == 'boldline-agenda':
                paratext = re.sub("[^;]*;?", paratext) # throw out all, or all up to ';'

            #print paraclass, paratext
            for wtxt in re.split(wsplit, paratext):
                if re.match("\s*$|</?[ib]>$|'$", wtxt):
                    continue
                if re.match("&\w{1,5};|[:;.,?!£¥*%@_\"()\[\]/+]+$|<i>.*?</i>$", wtxt):
                    textspl.append("")  # leave a gap at the end of a sentence, to avoid word grouping
                    continue
                if re.match("(?:20/20|9/11|[12][90]\d\d/[12][90]\d\d|HIV/AIDS)$", wtxt):
                    textspl.append("-".join(wtxt.split("/")))
                    continue
                maref = re.match('<a href="../(?:pdf|html)/([^"]+).(?:pdf|html)"[^>]*>[^<]*</a>$', wtxt)
                if maref:
                    refdoc = "R%s" % re.sub("[\(\)]", "-", maref.group(1))
                    terms.add(refdoc)
                    headingterms.add(refdoc)
                    continue
                assert not re.search("[<>]", wtxt), "spurious <> tags in splitpara:%s" % wtxt
                wtxt = re.sub("['\-\$\.]", "", wtxt).lower()

                if tdocument_id == "SPV0407201" and not re.match("\w+$", wtxt):
                    wtxt = ""   # detune in example when we get a system error

                #if re.search("/", wtxt):
                #    print re.split(wsplit, paratext)
                #    print wtxt, re.split(wsplit, wtxt), re.split("((?<=[a-z])/(?=[a-z]))", wtxt)

                # Stop words are one letter, two letter and the, and g-?7. Also add to web2/xapsearch.py.
                if wtxt and not re.match("[a-z][a-z]?$|the$|g-?7/$", wtxt):
                    #print wtxt,
                    textspl.append(CharToFlat(wtxt))
                else:
                    textspl.append("")

        elif paraclass == 'votecount':
        	#<p class="votecount" id="pg004-bk05-pa02">favour=90 against=48 abstain=21 absent=33</p>
            mfagan = re.match("favour=(\d+) against=(\d+) ", paratext)
            vminority = (int(mfagan.group(1)) >= int(mfagan.group(2)) and "against" or "favour")

        elif paraclass == 'votelist':
            for mvote in re.finditer('<span class="([^"\-]+)(?:-([^"]*))?">([^<]*)</span>', paratext):
                vnation = CharToFlat(re.sub("['\-]", "", mvote.group(3)))
                vvote = mvote.group(2) or mvote.group(1)   # take the latter vote position if there's two
                terms.add("V%s-%s" % (vnation, vvote))
                if vvote == vminority:
                    terms.add("V%s-minority" % vnation)
            del vminority  # make sure that a votecount always comes before a votelist in the recvote div

        else:
            assert False, "Unrecognized paraclass:%s" % paraclass

        textspl.extend(["", "", "", "", ""])  # gap of five slots at the end of a paragraph

    # date, docid, page, blockno
    value0 = "%s%sp%04d%03d" % (re.sub("-", "", document_date), tdocument_id, int(mblockid.group(1)), int(mblockid.group(2)))
    assert len(value0) == 26, len(value0) # nice and tidy; we're generating a value that gives a total global sort

    if IsVeryNoisy():
        print "value0", value0, "words:", len(textspl), " terms:", terms

    # assemble the document
    xapian_doc = xapian.Document()
    xapian_doc.add_value(0, value0)  # it's poss to have more than one value tagged on, but I think sorting is done only on one value

    for term in terms:
        xapian_doc.add_term(term)

    # add the ordered data
    nspl = 0
    for tspl in textspl:
        if tspl:
            xapian_doc.add_posting(tspl.lower(), nspl)
        nspl += 1

    return xapian_doc  # still need to set the data


def MakeTables(c):
    c.execute("DROP TABLE IF EXISTS un_scheadings")
    c.execute("CREATE TABLE un_scheadings (docid VARCHAR(30), ldate DATETIME, heading TEXT, shortheading TEXT, veryshortheading TEXT, numvotes INT, UNIQUE(docid))")
    import unpylons.model as model
    model.metadata.drop_all()
    model.metadata.create_all()

def ClearDatabaseValues(docid, c):
    pass

 

# Reindex one file
def process_file(pfnameunindexed, c):
    mdocid = re.match(r".*?(html[\\/])([\-\d\w\.]+?)(\.unindexed)?(\.html)$", pfnameunindexed)
    assert mdocid, "unable to match: %s" % pfnameunindexed
    docid = mdocid.group(2)

    fin = open(pfnameunindexed)
    doccontent = fin.read()
    fin.close()

    body = (docid[0] == "A" and "GA" or "SC")
    mdocument_date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', doccontent)
    assert mdocument_date, "not found date in file %s" % pfnameunindexed
    document_date = mdocument_date.group(1)

    if IsNotQuiet():
        print "indexing %s %s" % (docid, document_date)

    doccitations = { }

    mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)")?[^>]*>(.*?)^</div>', doccontent, re.S + re.M)
    for mdiv in mdivs:
        # used to dereference the string as it is in the file
        div_class = mdiv.group(1)
        div_href = mdiv.group(2)
        div_data = (docid, mdiv.start(), mdiv.end() - mdiv.start(), mdiv.group(2))
        div_content = mdiv.group(4)

        pgid = div_href
        for mdoc in re.finditer('id="([^"]*)"|<a href="../(?:pdf|html)/([\w\-\.()]*?)\.(?:pdf|html)"[^>]*>', div_content):
            if mdoc.group(1):
                pgid = mdoc.group(1)
            if mdoc.group(2):
                doccitations.setdefault(mdoc.group(2), []).append(pgid)

        if div_class == "recvote":
            mvote = re.match('\s*<p class="motiontext"[^>]*>(.*?)</p>\s*<p class="votecount"[^>]*>(.*?)</p>\s*<p class="votelist"[^>]*>(.*?)</p>', div_content)
            assert mvote, div_content
            mvnum = re.match("favour=(\d+)\s+against=(\d+)\s+abstain=(\d+)\s+absent=(\d+)", mvote.group(2))
            vnum = [int(mvnum.group(1)), int(mvnum.group(2)), int(mvnum.group(3)), int(mvnum.group(4))]
            motiontext = mvote.group(1)
            motiontext = re.sub('<a [^>]*>([^<]*)</a>', "\\1", motiontext)
            motiontext = re.sub("<[^>]*>", " ", motiontext)
            motiontext = re.sub(" (?:was|were) (?:retained|adopted|rejected) by (?:.*? abstentions?|\d+ votes to \d+)", "", motiontext)
            #print "adding to database", mvote.group(2)
            c.execute("""REPLACE INTO un_divisions (docid, href, body, motiontext, ldate, favour, against, abstain, absent)
                         VALUES ('%s', '%s', '%s', '%s', '%s', %d, %d, %d, %d);
                      """ % (docid, div_href, body, motiontext, document_date, vnum[0], vnum[1], vnum[2], vnum[3]))
            totalv = float(vnum[0] + vnum[1] + vnum[2] + vnum[3])
            minorityscores = { 'favour':vnum[0]/totalv, 'against':vnum[1]/float(vnum[0]+vnum[1]),
                               'abstain':vnum[2]/totalv, 'absent':vnum[3]/totalv }

            for mvoten in re.finditer('<span class="([^"\-]*)-?([^"]*)">([^<]*)</span>', mvote.group(3)):
                nation = mvoten.group(3)
                vote = mvoten.group(1)
                intendedvote = mvoten.group(2) or vote
                if mvoten.group(2):
                    print "mmm", mvoten.group(0)
                c.execute("""REPLACE INTO un_votes (docid, href, nation, vote, intended_vote, minority_score)
                             VALUES ('%s', '%s', "%s", '%s', '%s', '%s')
                          """ % (docid, div_href, nation, vote, intendedvote, minorityscores[intendedvote]))

        if div_class == "heading":
            pass

        if div_class == "council-agenda":
            if body == "SC":
                t = DownAscii(div_content)
                t = escape_string(t)
                #model.load_sc_fromfile(docid, div_content, document_date)
                c.execute("REPLACE INTO un_scheadings (docid, heading, ldate, shortheading, veryshortheading, numvotes) VALUES ('%s', '%s', '%s', '', '', 0)" % (docid, t, document_date))

    # add into the new pylons code using sqlalchemy
    for m in model.DocumentRefDocument.query.filter_by(document1_docid=docid):
        model.Session.delete(m)        
    for docid2, lcount in doccitations.iteritems():
        #print docid, docid2
        doccite = model.DocumentRefDocument(document1_docid=docid, document2_docid=docid2, count=len(lcount))
    model.Session.flush()

# could move the table constructions to here; if it's a force case
def DBfill(stem, bforcedbfill, nlimit, bcontinueonerror, htmldir):
    c = GetDBcursor()
    if bforcedbfill:  # and not stem
        MakeTables(c)
    
    
    # does just the unindexed if not forced
    rels = GetAllHtmlDocs(stem, True, bforcedbfill, htmldir)

    # having gone through the list, now load each
    if nlimit and len(rels) > nlimit:
        rels = rels[:options.limit]
    for rel in rels:
        try:
            process_file(rel, c)
        except KeyboardInterrupt, e:
            print "  ** Keyboard interrupt"
            traceback.print_exc()
            sys.exit(1)
        except Exception, e:
            print e
            if bcontinueonerror:
                traceback.print_exc()
            else:
                traceback.print_exc()
                sys.exit(1)




