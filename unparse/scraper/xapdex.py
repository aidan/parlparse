#!/usr/bin/python
# -*- coding: latin1 -*-

# unparse/bin/xapdex.py - Index Julian's UN HTML in Xapian. Run with --help
# for command line options.

import sys
import re
import os
import os.path
if sys.platform == "win32":
    import fakexapian as xapian
else:
    import xapian
import distutils.dir_util
import traceback
from unmisc import GetAllHtmlDocs, IsNotQuiet, IsVeryNoisy
from downascii import DownAscii

from nations import nonnationcatmap # this was why the need to moveall into same directory

# TODO:
# Get list of days with stuff in them
# Decide what to do properly with spaces in names etc.
# Index votes themselves (still needed?  This is now in a mysql database)
# A-50-PV.61.html breaks xapdex.py
# Unicode

# Fields are:
# I identifier (e.g. docA61PV4-pg001-bk01)
# J subsidiary identifier (e.g. docA61PV4-pg001-bk02-pa03)
# C class (e.g. italicline boldline)
# S speaker name (with spaces and dots removed XXX remove all punctuation)
# N nation
# L language
# D document id (e.g. A-57-PV.57)
# R referenced document (e.g. A-57-PV.57)
# E date (e.g. 2002-10-01)
# H heading identifier, if speech in a heading section (e.g. docA61PV4-pg001-bk01)
# A agenda number-session number

# Example set of identifiers for a document:
# Cspoken E2006-07-20 RA-60-L.49 Smrbodini Ipg017-bk01 Nsanmarino Hpg001-bk05 L DA-60-PV.94 Jpg017-bk01-pa01 Jpg017-bk01-pa02 Jpg017-bk01-pa03

# Reindex one file
def delete_all_for_doc(document_id, xapian_db):
    xapian_enquire = xapian.Enquire(xapian_db)
    xapian_query = xapian.QueryParser()
    xapian_query.set_stemming_strategy(xapian.QueryParser.STEM_NONE)
    xapian_query.set_default_op(xapian.Query.OP_AND)
    xapian_query.add_boolean_prefix("document", "D")
    query = "document:%s" % document_id
    parsed_query = xapian_query.parse_query(query)
    if IsVeryNoisy():
        print "\tdelete query: %s" % parsed_query.get_description()
    xapian_enquire.set_query(parsed_query)
    xapian_enquire.set_weighting_scheme(xapian.BoolWeight())
    mset = xapian_enquire.get_mset(0, 999999, 999999) # XXX 999999 enough to ensure we get 'em all?
    nmset = 0
    for mdoc in mset:
        if IsVeryNoisy():
            print "\tdeleting existing Xapian doc: %s" % mdoc[4].get_value(0)
        xapian_db.delete_document(mdoc[0]) # Xapian's document id
        nmset += 1
    return nmset

def thinned_docid(document_id):
    mgass = re.match("A-(\d+)-PV\.(\d+)$", document_id)
    if mgass:
        return "APV%03d%04d" % (int(mgass.group(1)), int(mgass.group(2))), mgass.group(1)
    msecc = re.match("S-PV.(\d+)(?:-Part\.(\d+))?(?:-Resu\.(\d+))?$", document_id)
    if msecc:
        subsec = (msecc.group(2) and int(msecc.group(2)) or 0) * 10 + (msecc.group(3) and int(msecc.group(3)) or 0)
        return "SPV%05d%02d" % (int(msecc.group(1)), subsec), None
    assert False, "Cannot parse docid: %s" % document_id

def CharToFlat(st):
    if re.match("[a-z0-9]+$", st):
        return st
    st = st.lower()
    st = st.replace(" ", "")
    if re.match("[a-z0-9]+$", st):
        return st

    st = DownAscii(st).lower()

    if not re.match("[a-z0-9]+$", st):
        print "Writing bad character to tail of downascii.py"
        fout = open("downascii.py", "a")
        fout.write("# " + st + "\n")
        fout.close()
        assert False, "unprocessed st: %s" % st
        
    return st


wsplit = """(?x)(\s+|
            <a[^>]*>[^<]*</a>|
            \$\d+|\d+\.\d+|
            &\w{1,5};|
            [:;.,?!£¥*%@_\"()\[\]+]+|
            '|
            (?<=[a-zA-Z\)"])/(?=[a-zA-Z])|
            <i>\([A-Z0-9a-z\.,\-/\s\(\)\*]*?\)</i>|
            <i>[\d/\.,par\s]*</i>|
            </?[ib]>|
            20/20|9/11|HIV/AIDS|
            [12][90]\d\d/[12][90]\d\d|
            G-?7/|
            )"""
#mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)")?[^>]*>(.*?)^</div>', doccontent, re.S + re.M)
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


# Reindex one file
def process_file(pfnameunindexed, xapian_db):
    mdocid = re.match(r".*?(html[\\/])([\-\d\w\.]+?)(\.unindexed)?(\.html)$", pfnameunindexed)
    assert mdocid, "unable to match: %s" % pfnameunindexed
    document_id = mdocid.group(2)

    fin = open(pfnameunindexed)
    doccontent = fin.read()
    fin.close()

    mdocument_date = re.search('<span class="date">(\d\d\d\d-\d\d-\d\d)</span>', doccontent)
    assert mdocument_date, "not found date in file %s" % pfnameunindexed
    document_date = mdocument_date.group(1)

    if IsNotQuiet():
        print "indexing %s %s" % (document_id, document_date)

    while delete_all_for_doc(document_id, xapian_db):
        pass   # keep calling delete until all clear

    # Loop through each speech, and batch up the headings so they can be updated with the correct info
    xapian_doc_heading = None
    sdiv_headingdata = None
    xapian_doc_subheading = None
    sdiv_subheadingdata = None

    headingtermsubheading = set()
    headingtermheading = set()

    lastend = 0

    tdocument_id, gasssess = thinned_docid(document_id)
    docterms = set()
    docterms.add("D%s" % document_id)
    docterms.add("E%s" % document_date[:4])  # year
    docterms.add("E%s" % document_date[:7])  # year+month
    docterms.add("E%s" % document_date)      # full date
    #if document_date > "2001-09-11":
    #    docterms.add("Epost911")      # "9/11 changed everything"

    if gasssess:
        docterms.add("Zga")
        docterms.add("Zga%s" % gasssess)
    else:
        docterms.add("Zsc")

    mdivs = re.finditer('^<div class="([^"]*)" id="([^"]*)"(?: agendanum="([^"]*)")?[^>]*>(.*?)^</div>', doccontent, re.S + re.M)
    for mdiv in mdivs:
        # used to dereference the string as it is in the file
        div_class = mdiv.group(1)
        div_data = (document_id, mdiv.start(), mdiv.end() - mdiv.start(), mdiv.group(2))

        xapian_doc = MakeBaseXapianDoc(mdiv, tdocument_id, document_date, headingtermsubheading)
        for dterm in docterms:
            xapian_doc.add_term(dterm)

        if div_class == "heading":
            assert not xapian_doc_heading, "Only one heading per document"
            xapian_doc_heading = xapian_doc
            sdiv_headingdata = div_data

        # the data put into a xapian object is: speech | document-id | offset | length | heading-id containing this speech | length of full section if this is a heading
        elif div_class in ["subheading", "end-document"]:
            assert xapian_doc_heading
            if xapian_doc_subheading:
                for hterm in headingtermsubheading:
                    xapian_doc_subheading.add_term(hterm)
                dsubheadingdata = "%s|%s|%d|%d|%s|%d" % (sdiv_subheadingdata[3], sdiv_subheadingdata[0], sdiv_subheadingdata[1], sdiv_subheadingdata[2], sdiv_headingdata[3], lastend - sdiv_subheadingdata[1])
                xapian_doc_subheading.set_data(dsubheadingdata)
                xapian_db.add_document(xapian_doc_subheading)

            headingtermheading.update(headingtermsubheading)
            if div_class == "subheading":
                headingtermsubheading.clear()
                xapian_doc_subheading = xapian_doc
                sdiv_subheadingdata = div_data
            else:
                headingtermsubheading = None
                xapian_doc_subheading = None
                sdiv_subheadingdata = None

            if div_class == "end-document":
                for hterm in headingtermheading:
                    xapian_doc_heading.add_term(hterm)
                dheadingdata = "%s|%s|%d|%d|%s|%d" % (sdiv_headingdata[3], sdiv_headingdata[0], sdiv_headingdata[1], sdiv_headingdata[2], "", lastend - sdiv_headingdata[1])
                xapian_doc_heading.set_data(dheadingdata)
                xapian_db.add_document(xapian_doc_heading)
                xapian_doc_heading = None

        else:
            assert div_class in ["assembly-chairs", "council-agenda", "council-attendees", "spoken", "italicline", "italicline-tookchair", "italicline-spokein", "recvote"], "unknown divclass:%s" % div_class
            assert sdiv_subheadingdata or sdiv_headingdata
            ddata = "%s|%s|%d|%d|%s|" % (div_data[3], div_data[0], div_data[1], div_data[2], (sdiv_subheadingdata or sdiv_headingdata)[3])
            xapian_doc.set_data(ddata)
            xapian_db.add_document(xapian_doc)

        lastend = mdiv.end()

    # the end-document tag helps us close these headings off
    assert not xapian_doc_subheading and not xapian_doc_heading

    # Note that the document has been indexed
    xapian_db.flush()

    if mdocid.group(3): # unindexed
        pfnameindexed = re.sub(r"\.unindexed", "", pfnameunindexed)
        if os.path.exists(pfnameindexed):
            os.unlink(pfnameindexed)
        #print pfnameunindexed, pfnameindexed
        os.rename(pfnameunindexed, pfnameindexed)


def GoXapdex(stem, bforcexap, nlimit, bcontinueonerror, htmldir, xapdir):
    rels = GetAllHtmlDocs(stem, True, bforcexap, htmldir)

    # Create new database
    os.environ['XAPIAN_PREFER_FLINT'] = '1' # use newer/faster Flint backend
    xapian_db = xapian.WritableDatabase(xapdir, xapian.DB_CREATE_OR_OPEN)

    # having gone through the list, now load each
    if nlimit and len(rels) > nlimit:
        rels = rels[:options.limit]
    for rel in rels:
        try:
            process_file(rel, xapian_db)
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

    # Flush and close
    xapian_db.flush()
    del xapian_db



