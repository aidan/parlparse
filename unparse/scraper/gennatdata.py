#!/usr/bin/python

import sys
import re
import os
from nations import nationdates
from unmisc import GetAllHtmlDocs, IsNotQuiet
from pdfinfo import PdfInfo
import datetime
#from db import GetDBcursor, AddWholeDivision



#        document_id = re.search('<span class="code">([^<]*)</span>', doccontent).group(1)
#        for recvotet in re.findall('<p class="votelist" id="(pg\d+-bk\d+)-pa\d+">(.*?)</p>', doccontent):
#          #print document_id, recvotet[0]
#            for voten in re.findall('<span class="([^"]*)">([^<]*)</span>', recvotet[1]):
#                res[voten[1]][(document_id, recvotet[0])] = re.match(".*?([^\-]*)", voten[0]).group(1)

#<div class="recvote" id="pg004-bk05">
#	<p class="motiontext" id="pg004-bk05-pa01">The draft resolution was adopted by 90 votes to 48, with 21 abstentions (<a href="../pdf/A-RES-57-54.pdf" class="nolink">resolution 57/54</a>).</p>
#	<p class="votecount" id="pg004-bk05-pa02">favour=90 against=48 abstain=21 absent=33</p>
#	<p class="votelist" id="pg004-bk05-pa03"><span class="absent">Afghanistan</span>, <span class="against">Albania</span>, <span class="favour">Algeria</span>, <span class="against">Andorra</span>, <span class="favour">Angola</span>, <span class="absent">Antigua and Barbuda</span>, <span class="abstain">Argentina</span>, <span class="abstain">Armenia</span>, <span class="against">Australia</span>, <span class="against">Austria</span>, <span class="abstain">Azerbaijan</span>, <span class="favour">Bahamas</span>, <span class="favour">Bahrain</span>, <span class="favour">Bangladesh</span>, <span class="absent">Barbados</span>, <span class="abstain">Belarus</span>, <span class="against">Belgium</span>, <span class="favour">Belize</span>, <span class="absent">Benin</span>, <span class="favour">Bhutan</span>, <span class="favour">Bolivia</span>, <span class="against">Bosnia and Herzegovina</span>, <span class="absent">Botswana</span>, <span class="abstain">Brazil</span>, <span class="favour">Brunei Darussalam</span>, <span class="against">Bulgaria</span>, <span class="favour">Burkina Faso</span>, <span class="favour">Burundi</span>, <span class="favour">Cambodia</span>, <span class="favour">Cameroon</span>, <span class="against">Canada</span>, <span class="favour">Cape Verde</span>, <span class="absent">Central African Republic</span>, <span class="absent">Chad</span>, <span class="favour">Chile</span>, <span class="favour">China</span>, <span class="favour">Colombia</span>, <span class="absent">Comoros</span>, <span class="absent">Congo</span>, <span class="favour">Costa Rica</span>, <span class="favour">Cote d'Ivoire</span>, <span class="against">Croatia</span>, <span class="favour">Cuba</span>, <span class="against">Cyprus</span>, <span class="against">Czech Republic</span>, <span class="favour">Democratic People's Republic of Korea</span>, <span class="absent">Democratic Republic of the Congo</span>, <span class="against">Denmark</span>, <span class="favour">Djibouti</span>, <span class="absent">Dominica</span>, <span class="favour">Dominican Republic</span>, <span class="favour">Ecuador</span>, <span class="favour">Egypt</span>, <span class="favour">El Salvador</span>, <span class="absent">Equatorial Guinea</span>, <span class="favour">Eritrea</span>, <span class="against">Estonia</span>, <span class="favour">Ethiopia</span>, <span class="abstain">Fiji</span>, <span class="against">Finland</span>, <span class="against">France</span>, <span class="favour">Gabon</span>, <span class="absent">Gambia</span>, <span class="abstain">Georgia</span>, <span class="against">Germany</span>, <span class="favour">Ghana</span>, <span class="against">Greece</span>, <span class="favour">Grenada</span>, <span class="favour">Guatemala</span>, <span class="favour">Guinea</span>, <span class="absent">Guinea-Bissau</span>, <span class="favour">Guyana</span>, <span class="favour">Haiti</span>, <span class="favour">Honduras</span>, <span class="against">Hungary</span>, <span class="against">Iceland</span>, <span class="favour">India</span>, <span class="favour">Indonesia</span>, <span class="favour">Iran</span>, <span class="absent">Iraq</span>, <span class="against">Ireland</span>, <span class="against">Israel</span>, <span class="against">Italy</span>, <span class="favour">Jamaica</span>, <span class="abstain">Japan</span>, <span class="favour">Jordan</span>, <span class="abstain">Kazakhstan</span>, <span class="favour">Kenya</span>, <span class="absent">Kiribati</span>, <span class="favour">Kuwait</span>, <span class="abstain">Kyrgyzstan</span>, <span class="favour">Laos</span>, <span class="against">Latvia</span>, <span class="favour">Lebanon</span>, <span class="favour">Lesotho</span>, <span class="absent">Liberia</span>, <span class="favour">Libya</span>, <span class="against">Liechtenstein</span>, <span class="against">Lithuania</span>, <span class="against">Luxembourg</span>, <span class="favour">Madagascar</span>, <span class="favour">Malawi</span>, <span class="favour">Malaysia</span>, <span class="favour">Maldives</span>, <span class="favour">Mali</span>, <span class="against">Malta</span>, <span class="absent">Marshall Islands</span>, <span class="favour">Mauritania</span>, <span class="favour">Mauritius</span>, <span class="favour">Mexico</span>, <span class="against">Micronesia</span>, <span class="against">Moldova</span>, <span class="against">Monaco</span>, <span class="favour">Mongolia</span>, <span class="favour">Morocco</span>, <span class="absent-favour">Mozambique</span>, <span class="favour">Myanmar</span>, <span class="absent">Namibia</span>, <span class="favour">Nauru</span>, <span class="favour">Nepal</span>, <span class="against">Netherlands</span>, <span class="against">New Zealand</span>, <span class="favour">Nicaragua</span>, <span class="absent">Niger</span>, <span class="favour">Nigeria</span>, <span class="against">Norway</span>, <span class="favour">Oman</span>, <span class="favour">Pakistan</span>, <span class="absent">Palau</span>, <span class="favour">Panama</span>, <span class="absent">Papua New Guinea</span>, <span class="abstain">Paraguay</span>, <span class="favour">Peru</span>, <span class="favour">Philippines</span>, <span class="against">Poland</span>, <span class="against">Portugal</span>, <span class="favour">Qatar</span>, <span class="against">Republic of Korea</span>, <span class="against">Romania</span>, <span class="abstain">Russia</span>, <span class="favour">Rwanda</span>, <span class="absent">Saint Kitts and Nevis</span>, <span class="favour">Saint Lucia</span>, <span class="abstain">Saint Vincent and the Grenadines</span>, <span class="abstain">Samoa</span>, <span class="against">San Marino</span>, <span class="favour">Sao Tome and Principe</span>, <span class="favour">Saudi Arabia</span>, <span class="favour">Senegal</span>, <span class="absent">Serbia</span>, <span class="absent">Seychelles</span>, <span class="favour">Sierra Leone</span>, <span class="favour">Singapore</span>, <span class="against">Slovakia</span>, <span class="against">Slovenia</span>, <span class="absent">Solomon Islands</span>, <span class="absent">Somalia</span>, <span class="abstain">South Africa</span>, <span class="against">Spain</span>, <span class="favour">Sri Lanka</span>, <span class="favour">Sudan</span>, <span class="absent">Suriname</span>, <span class="favour">Swaziland</span>, <span class="against">Sweden</span>, <span class="against">Switzerland</span>, <span class="favour">Syria</span>, <span class="abstain">Tajikistan</span>, <span class="favour">Tanzania</span>, <span class="favour">Thailand</span>, <span class="against">The former Yugoslav Republic of Macedonia</span>, <span class="absent">Timor-Leste</span>, <span class="favour">Togo</span>, <span class="abstain">Tonga</span>, <span class="favour">Trinidad and Tobago</span>, <span class="favour">Tunisia</span>, <span class="against">Turkey</span>, <span class="abstain">Turkmenistan</span>, <span class="absent">Tuvalu</span>, <span class="favour">Uganda</span>, <span class="abstain">Ukraine</span>, <span class="favour">United Arab Emirates</span>, <span class="against">United Kingdom</span>, <span class="against">United States</span>, <span class="abstain">Uruguay</span>, <span class="abstain">Uzbekistan</span>, <span class="absent">Vanuatu</span>, <span class="favour">Venezuela</span>, <span class="favour">Viet Nam</span>, <span class="favour">Yemen</span>, <span class="against">Yugoslavia</span>, <span class="favour">Zambia</span>, <span class="absent">Zimbabwe</span></p>
#</div>

class NationDataG:
    def __init__(self, lnation):
        self.nationname = lnation
        self.votetable = { }   # maps from votesum tuple to vote
        self.scvoteminority = [ ]
        self.voteminority = [ ]
        self.scminority = [ ]
        self.fname = re.sub(" ", "_", lnation) + ".txt"
        self.ambassadors = [ ]
        self.nationdatacsv = None

    # votesum = (docid, mdiv.group(2), vnum, mvote.group(1))  # this 4-tuple identifies a vote
    def AddVoteMade(self, votesum, vote):
        self.votetable[votesum] = vote

        if re.match("S-", votesum[0]):
            if vote == "favour" and votesum[2][0] <= 7:
                self.scvoteminority.append((votesum[2][0], votesum))
            elif vote == "against" and votesum[2][1] <= 7:
                self.scvoteminority.append((votesum[2][1], votesum))
            elif vote == "abstain" and (votesum[2][2] + votesum[2][1]) <= 7:
                self.scvoteminority.append((votesum[2][2] + votesum[2][1], votesum))  # captures minority abstentions when very few against
        else:
            if vote == "favour":
                self.voteminority.append((votesum[2][0], votesum))
            elif vote == "against":
                self.voteminority.append((votesum[2][1], votesum))
            elif vote == "abstain":
                self.voteminority.append((votesum[2][2] + votesum[2][1], votesum))  # captures minority abstentions when very few against

    def AddSpoken(self, name, docid, gid, sdate):
        self.ambassadors.append((name, sdate, docid, gid))

    def WriteData(self, nationactivitydir):
        fname = os.path.join(nationactivitydir, self.fname)
        fout = open(fname, "w")
        fout.write("nationdatacsv = %s\n" % self.nationdatacsv)
        self.voteminority.sort()
        self.scvoteminority.sort()
        for vm, votesum in self.voteminority[:10]:
            vmdat = "%d/%d/%d/%d" % votesum[2]
            fout.write("minorityvote = %s %s %s %s %s\n" % (vmdat, votesum[0], votesum[1], votesum[3], votesum[4]))
            # votebreakdown  docid, gid, date, motiontext
        for vm, votesum in self.scvoteminority[:10]:
            vmdat = "%d/%d/%d/%d" % votesum[2]
            fout.write("scminorityvote = %s %s %s %s %s\n" % (vmdat, votesum[0], votesum[1], votesum[3], votesum[4]))
        self.ambassadors.sort()
        for amb in self.ambassadors:
            fout.write("ambassador = %s %s %s %s\n" % (amb[2], amb[3], amb[1], amb[0]))
        fout.close()

def GenerateNationData(nationactivitydir, htmldir):
    rels = GetAllHtmlDocs("", False, False, htmldir)
    # collection nation speeches and votes
    # make this big mapping of votes
    # also collect the full names of the ambassadors
    #c = GetDBcursor()

    nationdict = { }  # used for measuring vote distances (maps from voteids to vote directions)
    for nation in nationdates:
        nationdict[nation] = NationDataG(nation)
    nationdict["Brunei Darussalam"] = nationdict["Brunei"]    # quick fix

    fin = open("nationdata.csv")
    for nd in fin.readlines():
        md = re.match('"([^"]*)"', nd)
        if md and md.group(1) != "Name":
            assert md.group(1) in nationdict, nd
            nationdict[md.group(1)].nationdatacsv = nd.strip()
    for nation in nationdict:
        assert nationdict[nation].nationdatacsv, nation

    for htdoc in rels:
        fin = open(htdoc)
        ftext = fin.read()
        fin.close()

        docid = re.search("((?:A-\d\d|S-PV).*?)\.html$", htdoc).group(1)
        body = (docid[0] == "A" and "GA" or "SC")
        sdate = re.search('<span class="date">([^<]*)</span>', ftext).group(1)
        if IsNotQuiet():
            print docid,

        for mdiv in re.finditer('(?s)<div class="(spoken|recvote|italicline)" id="([^"]*)">(.*?)</div>', ftext):

            gid = mdiv.group(2)
            if mdiv.group(1) == "recvote":
                mvote = re.match('\s*<p class="motiontext"[^>]*>(.*?)</p>\s*<p class="votecount"[^>]*>(.*?)</p>\s*<p class="votelist"[^>]*>(.*?)</p>', mdiv.group(3))
                assert mvote, mdiv.group(2)
                mvnum = re.match("favour=(\d+)\s+against=(\d+)\s+abstain=(\d+)\s+absent=(\d+)", mvote.group(2))
                vnum = [int(mvnum.group(1)), int(mvnum.group(2)), int(mvnum.group(3)), int(mvnum.group(4))]
                #vnum.append(float(vnum[0] + vnum[1] + vnum[2] + vnum[3]))
                motiontext = mvote.group(1)
                motiontext = re.sub('<a [^>]*>([^<]*)</a>', "\\1", motiontext)
                motiontext = re.sub("<[^>]*>", " ", motiontext)
                motiontext = re.sub(" (?:was|were) (?:retained|adopted|rejected) by (?:.*? abstentions?|\d+ votes to \d+)", "", motiontext)
                votesum = (docid, gid, tuple(vnum), sdate, motiontext)  # this 4-tuple identifies a vote
                
                #print "adding to database", mvote.group(2)

                for mvoten in re.finditer('<span class="([^"\-]*)-?([^"]*)">([^<]*)</span>', mvote.group(3)):
                    nation = mvoten.group(3)
                    vote = mvoten.group(1)
                    intendedvote = mvoten.group(2) or vote

                    nationdict[nation].AddVoteMade(votesum, intendedvote)  # big mapping table

            elif mdiv.group(1) == "spoken":
                mspeaker = re.search('<h3 class="speaker"> <span class="name">([^<]*)</span>(?: <span class="(nation|non-nation)">([^<]*)</span>)?(?: <span class="language">[^<]*</span>)? </h3>', mdiv.group(3))
                assert mspeaker, mdiv.group(0)
                if mspeaker.group(2) == "nation":
                    nationdict[mspeaker.group(3)].AddSpoken(mspeaker.group(1), docid, gid, sdate)

                pass # check for ambassador speech

        #if nationdict["United States"].votetable:
        #    break

    # output the data
    for nation in nationdates:
        nationdict[nation].WriteData(nationactivitydir)

    return


