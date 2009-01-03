# -*- coding: latin1 -*-

import re
from nations import FixNationName, GenerateNationsVoteList
from unmisc import unexception, IsNotQuiet, MarkupLinks

#    <blockquote><i>A recorded vote was taken.</i></blockquote>
#    <blockquote><i>In favour:</i> Algeria, Andorra, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bangladesh, Belarus, Belgium, Brazil, Brunei Darussalam, Bulgaria, Burkina Faso, Cameroon, Canada, Cape Verde, Chad, Chile, Colombia, Costa Rica, Côte d'Ivoire, Cuba, Cyprus, Czech Republic, Denmark, Djibouti, Dominican Republic, Ecuador, Egypt, El Salvador, Estonia, Ethiopia, Finland, France, Georgia, Germany, Ghana, Greece, Guinea, Guinea-Bissau, Guyana, Hungary, Indonesia, Iran (Islamic Republic of), Ireland, Israel, Italy, Jamaica, Japan, Kazakhstan, Kuwait, Latvia, Libyan Arab Jamahiriya, Liechtenstein, Lithuania, Luxembourg, Malaysia, Maldives, Mali, Malta, Mauritius, Mexico, Micronesia (Federated States of), Monaco, Mongolia, Morocco, Mozambique, Myanmar, Namibia, Netherlands, New Zealand, Nicaragua, Niger, Norway, Oman, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Republic of Korea, Republic of Moldova, Romania, San Marino, Saudi Arabia, Senegal, Singapore, Slovakia, Slovenia, South Africa, Spain, Sri Lanka, Sudan, Suriname, Swaziland, Sweden, Thailand, the former Yugoslav Republic of Macedonia, Togo, Tunisia, Turkey, Ukraine, United Arab Emirates, United Kingdom of Great Britain and Northern Ireland, United Republic of Tanzania, United States of America, Uruguay, Vanuatu, Venezuela, Yemen</blockquote>
#    <blockquote><i>Against:</i> Democratic People's Republic of Korea</blockquote>
#    <blockquote><i>Abstaining:</i> Bhutan, Botswana, China, India, Lao People's Democratic Republic, Pakistan, Syrian Arab Republic, Viet Nam</blockquote>
recvoterequest = "(?:<i>)?\s*A recorded vote has been requested|(?:<i>)?\s*A recorded vote was taken|<i>In favour|<i>A vote was taken\.</i>$|(?:<i>)?\s*A vote was taken by (?:a )?show of hands"

class VoteBlock:
    # problem is overflowing paragraphs across pages, where double barrelled country names can get split
    def DetectNationList(self, ptext, fromlast, paranum):
        bforce = (not not fromlast)
        if fromlast and fromlast not in ["FIRST", "ANDLIST"]:
            print "carryingforward $%s$" % fromlast
            ptext = "%s %s" % (fromlast, ptext)
        if ptext == "None":
            return "presentcomplete", [ ], None
        ptext = re.sub("</?i>", "", ptext)
        votelist = [ c.strip()  for c in re.split("[,\.]", ptext)  if not re.match("\s*$", c) ]

        if fromlast == "ANDLIST":
            #print "vvvv", votelist
            assert votelist
            if not FixNationName(votelist[-1], self.sdate):
                mand = re.search("(.*?) and (.*)$", votelist[-1])
                if mand:
                    votelist[-1] = mand.group(1)
                    votelist.append(mand.group(2))

        if re.match("<i>", ptext):
            if bforce:
                print fromlast, bforce, ptext
                assert False
            return "nothingmore", -1, -1

        if votelist and not FixNationName(votelist[-1], self.sdate) and (ptext[-1] != ",") and fromlast != "ANDLIST":
            carryforward = votelist[-1]
            votelist = votelist[:-1]
        else:
            carryforward = None

        res = [ ]
        fres = [ ]
        for lnation in votelist:
            nation = FixNationName(lnation, self.sdate)
            if not nation and fromlast == "ANDLIST" and re.match("[Tt]he ", lnation):
                nation = FixNationName(lnation[4:], self.sdate)
            if nation:
                if nation != "INVALID":
                    res.append(nation)
            else:
                fres.append(lnation)
        if bforce and fres:
            print votelist
            print "****", fres
            print "cccccc", carryforward
            raise unexception("votelist problem", self.tlcall[self.i].paranum)
        if res and not fres:
            return "present", res, carryforward
        if bforce:
            assert not fres
            return "presentblank", res, ""  # the "In favour" is followed by a new page
        #print fres
        return "nothingmore", -1, -1

    def DetectVote(self, votere):
        tlc = self.tlcall[self.i]
        votem = re.match(votere, tlc.paratext)
        if not votem:
            # missing abstain column case
            bAftervote = re.match("<i>\s*(?:The )?[Dd]raft|<b>\s*The President|<i>\s*Operative paragraph|<i>.*?did not participate", tlc.paratext)
            if bAftervote and re.search("Abstain", votere):
                # and self.undocname in ["A-53-PV.81", "A-55-PV.103", "A-55-PV.83", "A-55-PV.86", "A-56-PV.105", "A-56-PV.68", "A-56-PV.82", "A-56-PV.86", "A-57-PV.57", "A-57-PV.66", "A-57-PV.77", "A-58-PV.55", "A-58-PV.72"]:
                return [ ]
            if bAftervote and re.search("Against", votere) and self.bSecurityCouncil:
                return [ ]
            if re.search("Against|Abstaining", votere) and re.search("Subsequently", tlc.paratext) and self.bSecurityCouncil:
                return [ ]
            if self.undocname in ["A-55-PV.44"] and re.search("Against", votere) and re.match("<i>Abstaining", tlc.paratext):
                return [ ]
            if re.search("Against", votere) and re.match("<i>Abstaining:?</i>", tlc.paratext):
                return [ ]
            print "failed with:", votere, tlc.paratext
            raise unexception("votelist detectvote match", tlc.paranum)

        #print tlc.paratext
        mess, natlist, carryforward = self.DetectNationList(tlc.paratext[votem.end(0):].strip(), "FIRST", tlc.paranum)
        assert mess != "nothingmore"
        self.i += 1

        # deal with nation names merging across pages.
        while True:
            mess, cnatlist, carryforward = self.DetectNationList(self.tlcall[self.i].paratext, carryforward, self.tlcall[self.i].paranum)
            if mess == "nothingmore":
                #print self.tlcall[self.i].paratext
                break
            natlist.extend(cnatlist)
            self.i += 1
        return natlist

    #<blockquote indent="31"><i>Draft resolution A/53/L.52 was adopted by 149 votes</i> <i>to 1, with 7 abstentions </i>(resolution 53/37).</blockquote>

    #  and the following should affect the vote, by making it Haiti: absent-favour
    #<blockquote indent="32">[Subsequently, the delegations of Haiti and Mozambique informed the Secretariat that they had intended to vote in favour.]</blockquote>
    def DetectAdoption(self):
        adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
        madtext = re.search("(adopted|carried|retained.*?|rejected)(?:, as amended,|, as a whole,)?\s+by(?: votes)?\s+(\d+)(?:\s+votes)? to\s+(\d+|none)(?:,? with (\d+) abstentions?)?", adtext)
        if not madtext:
            madtext = re.match("(By)\s+(\d+)(?:\s+votes)? to\s+(\d+|none)(?:,? with (\d+) abstentions?)?", adtext)
        if not madtext:
            print "--%s-- %d" % (adtext, self.i)
            raise unexception("by votes problem", self.tlcall[self.i].paranum)
        ifavour = int(madtext.group(2))
        iagainst = (madtext.group(3) != "none" and int(madtext.group(3)) or 0)
        #if madtext.group(1) == "rejected":
        #    i = ifavour;  ifavour = iagainst;  iagainst = i
        iabstain = (madtext.group(4) and int(madtext.group(4)) or 0)
        if madtext.group(1) == "rejected":
            il = (iagainst, ifavour, iabstain)
        else:
            il = (ifavour, iagainst, iabstain)
        ivl = (len(self.vlfavour), len(self.vlagainst), len(self.vlabstain))
        if il != ivl:
            if IsNotQuiet():
                print "wrong-count", self.undocname, il, ivl
            # wrong values are found on A-57-PV.73 s(favour=154, 152)
            if self.undocname not in [ "A-56-PV.82", "A-57-PV.73", "A-58-PV.54", "A-52-PV.69", "A-50-PV.90", "A-49-PV.83", ]:
                raise unexception("wrong votecount", self.tlcall[self.i].paranum)
        self.motiontext = MarkupLinks(adtext, self.undocname, self.paranum)
        self.i += 1

    def DetectSubsequentVoteChange(self, gnv):
        adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
        msubseq = re.match("\[Subsequently,? (.*?)\.?\]", adtext)
        self.votechanges = {}
        if not msubseq:
            if re.search("Subsequently", adtext):
                print adtext
                raise unexception("unexpected subsequently", self.tlcall[self.i].paranum)
            return

        for sadtext in re.split(";\s*", msubseq.group(1)):
            if not sadtext:
                continue
            msadtext = re.match("the delegations? of (.*?) (?:informed|advised) the [Ss]ecretariat that (?:it|they) (?:had )?intended to (vote in favour|vote against|abstain)$", sadtext)
            if not msadtext:
                msadtext = re.match("the delegations? of (.*?)(?:(?:informed|advised) the Secretariat that (?:it|they))? had (not) intended to participate(?: in the voting)?$", sadtext)
            if not msadtext:
                msadtext = re.match("the delegations? of (.*?) had intended to (vote in favour|vote against|abstain)$", sadtext)
            if not msadtext:
                print "---%s---" % sadtext
                #print re.match("the delegations? of (.*?) (?:informed|advised) the Secretariat that (?:it|they) had", sadtext)
                raise unexception("change vote advice unrecognized", self.tlcall[self.i].paranum)

            mess, natlist, carryforward = self.DetectNationList(msadtext.group(1), "ANDLIST", self.tlcall[self.i].paranum)
            assert natlist
            #print sadtext, msadtext.group(1)
            #print natlist, "(", msadtext.group(2)
            assert not carryforward
            for nat in natlist:
                assert nat not in self.votechanges
                if re.search("favour", msadtext.group(2)):
                    vch = "favour"
                elif re.search("against", msadtext.group(2)):
                    vch = "against"
                elif re.search("abstain", msadtext.group(2)):
                    vch = "abstain"
                elif re.search("not", msadtext.group(2)):
                    vch = "absent"
                else:
                    assert False
                self.votechanges[nat] = vch

        self.votechange = adtext
        self.i += 1
        for nat in self.votechanges:
            gnv[nat] = "%s-%s" % (gnv[nat], self.votechanges[nat])

    def DetectDidnotparticipate(self, gnv, vlabsent):
        adtext = re.sub("</?i>", "", self.tlcall[self.i].paratext)
        mnotparticipate = re.match("(.*?)\s*did not participate in the voting.", adtext)
        if mnotparticipate:
            assert len(vlabsent) == 1
            if vlabsent[0] == mnotparticipate.group(1):
                self.i += 1
            else:
                print "nonparcitipation name wrong", vlabsent[0], mnotparticipate.group(1)
                #if self.undocname != "S-PV-4305":
                raise unexception("mismatch nonparticipationvoting", self.tlcall[self.i].paranum)
        else:
            msubvote = re.match("\[Subsequently.*? (Jamaica) .*? voted? in (favour)", adtext)
            if msubvote:
                nat = msubvote.group(1)
                gnv[nat] = "%s-%s" % (gnv[nat], msubvote.group(2))
                self.i += 1
            elif len(vlabsent) != 0:
                if self.undocname not in ["S-PV-3412", "S-PV-3413", "S-PV-3407", "S-PV-3409"]: # cases where Rwanda is absent
                    raise unexception("unaccounted nonparticipationvoting", self.tlcall[self.i].paranum)

    def __init__(self, tlcall, i, lundocname, lsdate, seccouncilmembers):
        self.tlcall = tlcall
        self.i = i
        self.sdate = lsdate
        self.undocname = lundocname
        self.bSecurityCouncil = re.match("S-PV.\d+", self.undocname)
        self.bGeneralAssembly = re.match("A-\d+-PV", self.undocname)
        assert self.bGeneralAssembly or self.bSecurityCouncil
        if not self.bSecurityCouncil:
            seccouncilmembers = None

        self.pageno, self.paranum = tlcall[i].txls[0].pageno, tlcall[i].paranum

        vtext = re.sub("</?i>", "", tlcall[self.i].paratext).strip()
        if self.bGeneralAssembly and re.match("A recorded vote has been requested(?: for this item| on (?:the|this) motion|\. We shall now begin the voting process)?\.?$", vtext):
            self.i += 1
            vtext = re.sub("</?i>", "", tlcall[self.i].paratext).strip()
        if self.bGeneralAssembly and re.match("A recorded vote was taken\s*\.?$", vtext):
            self.i += 1
        if self.bSecurityCouncil and re.match("A vote was taken(?: by (?:a )?show of hands)?.$", vtext):
            self.i += 1

        if not (self.i != i or self.undocname in ["A-55-PV.86", "A-50-PV.90", "A-49-PV.90"]):
            print "--%s--" % tlcall[self.i - 1].paratext
            if not re.match("<i>", tlcall[self.i - 1].paratext):
                print "  --[should this line be italic?]"
            print tlcall[self.i].paratext
            raise unexception("requested vote not followed through", tlcall[self.i].paranum)

        self.vlfavour = self.DetectVote("<i>In favour:?\s*</i>:?")
        self.vlagainst = self.DetectVote("(?:<i>)?Against:?\s*(?:</i>)?:?")
        self.vlabstain = self.DetectVote("(?:<i>)?Abstaining:?(?:</i>)?:?")
        gnv, self.vlabsent = GenerateNationsVoteList(self.vlfavour, self.vlagainst, self.vlabstain, self.sdate, self.paranum, seccouncilmembers)
        self.votecount = "favour=%d against=%d abstain=%d absent=%d" % (len(self.vlfavour), len(self.vlagainst), len(self.vlabstain), len(self.vlabsent))
        if IsNotQuiet():
            print "  ", self.votecount
        if self.bGeneralAssembly:
            self.DetectAdoption()
            self.DetectSubsequentVoteChange(gnv)
        if self.bSecurityCouncil:
            self.motiontext = ""
            self.DetectDidnotparticipate(gnv, self.vlabsent)

        #res = [ '\t\t<div style="border:1px solid black; margin-left:2em"><b>VOTE ', votecount, "</b><br>\n", "\t\t<i>", self.motiontext, "</i>\n" ]
        #res.append('\t\t<div style="font-size:6">')
        lvotelist = [ ]
        for nation, vote in sorted(gnv.items()):
            lvotelist.append('<span class="%s">%s</span>' % (vote, nation))
        self.votelist = ", ".join(lvotelist)
        #res.append("</div></div>\n")
        #self.parafout = "".join(res)
        self.typ = "vote"

    def writeblock(self, fout):
        bgid = self.paranum.MakeGid()
        fout.write('\n<div class="recvote" id="%s">\n' % bgid)
        fout.write('\t<p class="motiontext" id="%s-pa01">%s</p>\n' % (bgid, self.motiontext))
        fout.write('\t<p class="votecount" id="%s-pa02">%s</p>\n' % (bgid, self.votecount))
        fout.write('\t<p class="votelist" id="%s-pa03">%s</p>\n' % (bgid, self.votelist))
        fout.write('</div>\n')

