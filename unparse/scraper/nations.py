# -*- coding: utf8 -*-

import re
import unpylons.model as model

# this is used only in the parsed and used to pull from a CSV file.  Now takes from the database

# list of nations and their dates as part of the General Assembly can be found at
# http://www.un.org/Overview/unmember.html
# The following list should be made consistent with it.

# convert the mapping of nations into a local object for lookup (legacy code as it used to do it by loading a CSV)
# we could upgrade it in due course to use m = Member.query.filter_by(name=name).first()
nationdates = { }
for nation in model.Member.query.filter_by(isnation=True).all():
    nationdates[nation.name] = { "Date entered UN":nation.started, "Date left UN":nation.finished }


# includes typos, short names, and name changes
nationmapping = {
        "United Kingdom of Great Britain and Northern Ireland":"United Kingdom",
        u"C\xf4te d'Ivoire":"Cote d'Ivoire",
        "C\xf4te d'Ivoire":"Cote d'Ivoire",
        "the former Yugoslav Republic of Macedonia":"The former Yugoslav Republic of Macedonia",
        "Federal Republic of Yugoslavia":"Yugoslavia",
        "Syrian Arab Republic":"Syria",
        "Libyan Arab Jamahiriya":"Libya",
        "Iran (Islamic Republic of)":"Iran",
        "Islamic Republic of Iran":"Iran",
        "Serbia and Montenegro":"Serbia",
        "Sao Tome":"Sao Tome and Principe", # a version without and
        "Saint Vincent":"Saint Vincent and the Grenadines", # a version without and
        "Venezuela (Bolivarian Republic of)":"Venezuela",
        "Bolivarian Republic of Venezuela":"Venezuela",
        "United Republic of Tanzania":"Tanzania",
        "Commonwealth of Dominica":"Dominica",
        "United States of America":"United States",
        "of Great Britain and Northern Ireland":"INVALID",
        "(Islamic Republic of)":"INVALID",
        "Micronesia (Federated States of)":"Micronesia",
        "Federated States of Micronesia":"Micronesia",
        "Russian Federation":"Russia",
        "Republic of Croatia":"Croatia",
        "Principality of Monaco":"Monaco",
        "Republic of Moldova":"Moldova",
        "Republic of Azerbaijan":"Azerbaijan",
        "Kazakstan":"Kazakhstan",
        "Vietnam":"Viet Nam",
        "Slovak Republic":"Slovakia",
        "People's Democratic Republic of Korea":"Democratic People's Republic of Korea",
        "Guinea Bissau":"Guinea-Bissau",
        "The Former Yugoslav Republic of Macedonia":"The former Yugoslav Republic of Macedonia",
        "Lao People's Democratic Republic":"Laos",
        "Brunei Darussalam":"Brunei",
                }



nationswithoutspaces = {}
for nation in nationdates:
    if re.search(" ", nation):
        nationswithoutspaces[re.sub(" ", "", nation)] = nation


prenations = ["Switzerland"]
# deals with problem that sometimes the spaces between characters are added
def IsPrenation(lnation, sdate):
    lnation = nationmapping.get(lnation, lnation)
    dr = nationdates.get(lnation)
    if dr and sdate < dr["Date entered UN"]:
        assert lnation in prenations
        return lnation
    return None

# deals with problem that sometimes the spaces between characters are added
def FixNationName(lnation, sdate):
    if re.search("\[", lnation):
        print lnation

    lnation = nationmapping.get(lnation, lnation)
    if lnation == "INVALID":
        return lnation
    dr = nationdates.get(lnation)
    if not dr:
        lnationwithoutspaces = re.sub(" ", "", lnation)
        llnation = nationswithoutspaces.get(lnationwithoutspaces, lnationwithoutspaces)
        dr = nationdates.get(llnation)
        if not dr:
            return None
        lnation = llnation

    if not dr["Date entered UN"] <= sdate < dr["Date left UN"]:
        print lnation, dr, sdate
        print "nation out of date range"
        assert False
    return lnation

def GenerateNationsVoteList(vlfavour, vlagainst, vlabstain, sdate, paranum, seccouncilmembers):
    nationvotes = { }
    if seccouncilmembers:
        for nation in seccouncilmembers:
            nationvotes[nation] = "absent"
    else:  # general assembly case
        for nation, dr in nationdates.iteritems():
            if dr["Date entered UN"] <= sdate < dr["Date left UN"]:
                nationvotes[nation] = "absent"

    #print "\n\n\n"
    for vn in vlfavour:
        if vn not in nationvotes:
            print vn, sdate
            raise unexception("country not list of nations", paranum)
        if nationvotes[vn] != "absent":
            print vn, sdate, nationvotes[vn]
            raise unexception("country vote already set", paranum)
        nationvotes[vn] = "favour"
    for vn in vlagainst:
        assert nationvotes[vn] == "absent"
        nationvotes[vn] = "against"
    for vn in vlabstain:
        if nationvotes[vn] != "absent":
            print vn, nationvotes[vn]
            raise unexception("country already voted", paranum)
        nationvotes[vn] = "abstain"

    vlabsent = [nation  for nation, vote in nationvotes.iteritems()  if vote == "absent"]
    vlabsent.sort()
    assert not seccouncilmembers or len(vlabsent) <= 1 # only one case of missing vote so far found
    return nationvotes, vlabsent


# many of the following are organizations granted observer status,
# listed in http://lib-unique.un.org/lib/unique.nsf/Link/R02020

# sdate can be used for Switzerland special case which was later a UN nation
def IsNonnation(nonnation, sdate):
    if nonnation[0] == "*":  # prepended
        nonnation = nonnation[1:]
        if nonnation not in nonnationscount:
            nonnationscount[nonnation] = 0
            print "   *** new nonnation:", nonnation
            fout = open("nations.py", "a")
            fout.write('nonnationscount["%s"] = 0\n' % nonnation)
            fout.close()
    if nonnation not in nonnationscount:
        return False
    nonnationscount[nonnation] += 1
    return nonnation


# this gets parsed and used to generate nation-like tags for the speaker
nonnationlist = """
African:
    African Development Bank
    African Network of Religious Leaders Living with or Personally Affected by HIV/AIDS
    African Union
    African, Caribbean and Pacific Group of States
    Organization of African Unity
    Secretary-General of the Asian-African Legal Consultative Committee
    Secretary-General of the Organization of African Unity
    Permanent Observer for the Organization of African Unity

American:
    Caribbean Community
    Caribbean Community CARICOM
    Ibero-American Conference
    Latin American Economic System
    Organization of American States
    Secretary-General of the Caribbean Community
    Secretary-General, Central American Integration System
    Secretary-General of the Agency for the Prohibition of Nuclear Weapons in Latin America and the Caribbean
    President of the Latin American Parliament
    Director of Functional Integration at the General Secretariat of the Central American Integration System

Asian:
    Black Sea Economic Cooperation Organization
    Asian Development Bank
    Asian-African Consultative Committee
    Asian-African Legal Consultative Committee
    Asian-African Legal Consultative Organization
    Officer-in-Charge of the Asia and the Pacific Division of the Department of Political Affairs
    Secretary-General, Eurasian Economic Community

Business:
    BHI Holdings Limited
    International Monetary Fund
    McKinsey and Company
    Shanghai Cooperation Organization
    World Bank
    Vice-President of the World Bank
    President of the World Bank
    World Trade Organization
    President and Chief Executive Officer of Siemens
    Secretary General of CARE International
    Vice President of the International Center for Transitional Justice

Communities:
    Commonwealth Secretariat
    Community of Portuguese-Speaking Countries
    Conference of Non-Governmental Organizations in Consultative Relationship with the United Nations
    Conference of Presiding Officers of National Parliaments
    Economic Community of Central African States
    Economic Community of West African States
    Economic Cooperation Organization
    Economic and Social Commission for Western Africa
    European Commission
    European Community
    Special Representative of the EU Presidency
	European Union
	Flora Tristan Centre for Peruvian Women
    Inter-Parliamentary Union
    International Confederation of Free Trade Unions
    International Organization of La Francophonie
    International Organization of la Francophonie
    Permanent Council of Francophonie
    League of Arab States
    Permanent Observer of Switzerland
    Social Watch
    South Pacific Forum
    former Yugoslav Republic of Macedonia
	Transitional Cabinet of East Timor
	Second Transitional Government of East Timor
	East Timor
	President of the National Council of Timorese Resistance
    Coordinator of the NGO Working Group on Women, Peace and Security

Health:
    Global Fund to Fight AIDS, Tuberculosis and Malaria
    International Committee of the Red Cross
    President of the International Committee of the Red Cross
    International Federation of Red Cross and Red Crescent Societies
    International Federation of the Red Cross and Red Crescent Societies
    Joint United Nations Programme on HIV/AIDS
    MTV Networks International/Global Media AIDS Initiative
    Observer for the International Federation of Red Cross and Red Crescent Societies
    Treatment Action Campaign
    World Health Organization
    Executive Director of the World Food Programme
    Partners in Population and Development

Legal:
    International Court of Justice
    International Criminal Court
    International Criminal Police Organization-Interpol
    International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    Organization for Security and Cooperation in Europe
    Permanent Court of Arbitration
    President of the International Court
    President of the International Criminal Court
    President of the International Court of Justice
    President of the International Criminal Tribunal for Rwanda
    President of the International Criminal Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    President of the International Tribunal
    President of the International Tribunal for Rwanda
    President of the International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    President, International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    President of the International Tribunal for the Former Yugoslavia
    Prosecutor of the International Tribunal for the Former Yugoslavia
    Prosecutor of the International Criminal Tribunal for Rwanda
    President of the International Criminal Tribunal for the Former Yugoslavia
    Secretary General of the Conference on Security and Cooperation in Europe
    The Legal Counsel
    United Nations International Independent Investigation Commission

Oceans:
    Commission on the Limits of the Continental Shelf
    International Hydrographic Organization
    International Seabed Authority
    International Tribunal for the Law of the Sea
    Judge, International Tribunal for the Law of the Sea
    New Zealand, President, Twelfth Meeting of States Parties to the United Nations Convention on the Law of the Sea
    President of the Assembly of the International Seabed Authority
    President, Third United Nations Conference on the Law of the Sea
    Secretary-General of the International Seabed Authority

Palistinian:
    Chairman of the Committee on the Exercise of the Inalienable Rights of the Palestinian People
    Committee on the Exercise of the Inalienable Rights of the Palestinian People
    Observer for Palestine
    Palestine
    Rapporteur of the Committee on the Exercise of the Inalienable Rights of the Palestinian People

Religion:
    Holy See
    Organization of the Islamic Conference
    Permanent Observer of the Organization of the Islamic Conference
    Secretary General of the Organization of the Islamic Conference

Refugees:
    International Centre for Migration Policy Development
    International Organization for Migration
    Office of the United Nations High Commissioner for Refugees

Technology:
    Agency for Cultural and Technical Cooperation
    Chairman of the Committee on the Peaceful Uses of Outer Space
    Chairman of the Information and Communication Technologies Task Force
    Digital Opportunity Task Force
    Director General of the International Atomic Energy Agency
    Director General, International Atomic Energy Agency
    International Atomic Energy Agency
    International Telecommunication Union
    International Union for the Conservation of Nature and Natural Resources


United Nations:
    Assistant Secretary-General for Peacekeeping Operations
    Assistant Secretary-General for Political Affairs
    Chairman of the Monitoring Group
    Chief, General Assembly Affairs Branch
    Chief, General Assembly Affairs Branch, Department for General Assembly and Conference Management
    Chief, General Assembly Servicing Branch
    Council of Europe
    Co-Chair of the Millennium Forum
    Customs Cooperation Council
    Secretary-General of the Department for General Assembly and Conference Management
    Department for General Assembly and Conference Management
    Deputy Secretary-General
    Deputy Secretary-General of the South Pacific Forum
    Director of General Assembly and ECOSOC Affairs
    Director of General Assembly and Economic and Social Council Affairs
    Director of General Assembly and Trusteeship Council Affairs Division
    Director of the General Assembly Affairs Division
    Director of the General Assembly and Trusteeship Council Affairs Division
    Director of the Security Council Affairs Division
    Director, General Assembly Affairs
    Director, General Assembly Affairs Division
    Director, General Assembly Affairs Division, Department of Political Affairs
    Director, General Assembly and ECOSOC Affairs Division, Department of General Assembly Affairs and Conference Services
    Director, General Assembly and Economic and Social Council Affairs Division
    Director, General Assembly and Economic and Social Council Affairs Division of the Department of General Assembly Affairs and Conference Management Services
    Director, General Assembly and Economic and Social Council Affairs Division, Department for General Assembly and Conference Management
    Executive Director of the United Nations Children's Fund
    Executive Director of the United Nations Development Fund for Women
    General Assembly Affairs Branch
    High Commissioner for Human Rights
    Deputy High Commissioner for Human Rights
	President of the Human Rights Council
    Officer-in-Charge of the Security Council Affairs Division
    President of the Economic and Social Council
    Rapporteur
    Representative of the Secretariat
    Secretary-General
    Secretary-General of the Economic Cooperation Organization
    Secretary-General of the Organization for Security and Cooperation in Europe
    Special Adviser on Gender Issues and Advancement of Women
    Special Adviser to the Secretary-General on General Assembly Matters
    Special Representative and Transitional Administrator in East Timor
    Special Adviser on Africa
    Special Adviser to the Secretary-General
    UNICEF
    Under Secretary-General for General Assembly and Conference Management
    Under-Secretary-General for General Assembly Affairs and Conference Services
    Under-Secretary-General for General Assembly and Conference Management
    Under-Secretary-General for Humanitarian Affairs
    Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator
	Office for the Coordination of Humanitarian Affairs
    Under-Secretary-General for Peacekeeping Operations
    Under-Secretary-General for Policy Coordination and Sustainable Development
    Under-Secretary-General for Political Affairs
    Under-Secretary-General, Department of General Assembly Affairs and Conference Management
    Under-Secretary-General, Department of General Assembly Affairs and Conference Services
	Under-Secretary-General for Legal Affairs
	Under-Secretary-General for Disarmament Affairs
    United Nations Children's Fund
    United Nations Conference on Trade and Development
    United Nations Development Fund for Women
    United Nations Development Programme
    United Nations Educational, Scientific and Cultural Organization
    United Nations High Commissioner for Human Rights
    United Nations High Commissioner for Refugees
    United Nations Population Fund
    Vice-President of the Economic and Social Council
    President of the Security Council
    Representative of the Secretary-General
    Special Envoy of the Secretary-General
    Chairman of the Security Council Committee
    Chairman of the Independent Inquiry into the actions of the United Nations during the 1994 genocide in Rwanda
    High Representative for the Implementation of the Peace Agreement on Bosnia and Herzegovina
    Special Representative of the Secretary-General
    Personal Representative of the Secretary-General
    Secretary-General of the Council of the European Union
	Acting Chairman of the Organizational Committee of the Peacebuilding Commission
    Special Coordinator for the Middle East Peace Process
	President of the General Assembly
	Chairperson of the Panel of Experts on the Illegal Exploitation of Natural Resources and Other Forms of Wealth in the Democratic Republic of the Congo
    Deputy Emergency Relief Coordinator
	Chairman of the Committee of Experts
	Chairman of the Panel of Experts on Liberia
	United Nations Humanitarian Coordinator for Angola
	Security Council mission to Eritrea and Ethiopia
	Chairman of the Security Council ad hoc Working Group
	Chairman of the Security Council Working Group on Peacekeeping Operations
	Chairman of the Security Council Working Group
	Head of the Security Council Mission
	Programme for Coordination and Assistance for Security and Development
	Executive Director of Sustainable Development and Health Environments
    Security Council mission to Central Africa
    Security Council mission to Afghanistan
    Chairman of the Ad Hoc Advisory Group
	Head of the United Nations Political Office in Bougainville
	Legal Counsel of the United Nations
	Senior Deputy High Representative
	Chairman of the Counter-Terrorism Committee
    Executive Director of the Office of the Iraq Programme
	Senior Gender Adviser of the United Nations Organization Mission in the Democratic Republic of the Congo
    Chairman of the Peacebuilding Commission

Weapons:
    Comprehensive Nuclear-Test-Ban Treaty Organization
    Chairman of the Committee on the Peaceful Uses of Outer Space
    Director General of the International Atomic Energy Agency
    Director General, International Atomic Energy Agency
    Executive Secretary of the Preparatory Commission for the Comprehensive Nuclear-Test-Ban Treaty Organization
    Geneva International Centre for Humanitarian Demining
    International Atomic Energy Agency
    Organization for the Prohibition of Chemical Weapons
    Preparatory Commission for the Comprehensive Nuclear-Test-Ban Treaty Organization
    Sovereign Military Order of Malta
    Sudan People's Liberation Movement/Army
    Director of the World Campaign against Military and Nuclear Collaboration with South Africa
	Executive Chairman of the United Nations Monitoring, Verification and Inspection Commission
	Director General of the United Nations Office at Vienna
"""

def PrintNonnationOccurrances():
    for nn in reversed(sorted([(nonnationscount[n], n)  for n in nonnationscount.keys()  if nonnationscount[n]])):
        print nn

nonnationscount = { }
nonnationcatmap = { }
#nonnationcat = ""
for nonnation in nonnationlist.split("\n"):
    mcat = re.match("(\w.*?):$", nonnation)
    if mcat:
        nonnationcat = mcat.group(1)
        continue
    lnonnation = nonnation.strip()
    if lnonnation:
        nonnationscount[lnonnation] = 0
        if lnonnation in nonnationcatmap:
            nonnationcatmap[lnonnation] = "%s,%s" % (nonnationcatmap[lnonnation], nonnationcat)
        else:
            nonnationcatmap[lnonnation] = nonnationcat


#jj = nonnationcatmap.keys(); jj.sort()
#for i in jj:   print i[:15], ":", nonnationcatmap[i]

# further non-nations will get appended here during parsing, for later incorporation
# it's a map because because it adds up how many of each one have occurred

nonnationscount["International Institute for Democracy and Electoral Assistance"] = 0
nonnationscount["Eurasian Economic Community"] = 0
nonnationscount["Special Representative of the Secretary-General for Children and Armed Conflict"] = 0
nonnationscount["Watchlist on Children and Armed Conflict"] = 0
nonnationscount["PLAN International"] = 0
nonnationscount["Executive Director of the Counter-Terrorism Committee Executive Directorate"] = 0
nonnationscount["Commissioner of the United Nations International Independent Investigation Commission"] = 0
nonnationscount["United Nations Peacebuilding Support Office in Guinea-Bissau"] = 0
nonnationscount["Commission of the African Union"] = 0
nonnationscount["Assistant Secretary-Genral for Political Affairs"] = 0
nonnationscount["Director and Deputy to the High Representative for Disarmament Affairs"] = 0
nonnationscount["Office for Disarmament Affairs"] = 0
nonnationscount["Assistant Secretary-General"] = 0
nonnationscount["Under-Secretary-General for Peacekeeping Affairs"] = 0
nonnationscount["High Representative of the Peace Agreement on Bosnia and Herzegovina"] = 0
nonnationscount["Prosecutor of the International Criminal Court"] = 0
nonnationscount["International Tribunal for the Former Yugoslavia"] = 0
nonnationscount["International Criminal Tribunal for Rwanda"] = 0
nonnationscount["Kosovo"] = 0
nonnationscount["Special Adviser on the International Compact with Iraq and Other Political Issues"] = 0
nonnationscount["Assistant Secretary-General and Controller, Office of Programme Planning, Budget and Accounts"] = 0
nonnationscount["Department of Political Affairs"] = 0
nonnationscount["United Nations office in Vienna"] = 0
nonnationscount["Committee of the Watchlist on Children and Armed Conflict"] = 0
nonnationscount["Coordination of Action Research on AIDS"] = 0
nonnationscount["Department of Peacekeeping Affairs"] = 0
nonnationscount["Working Group on Women, Peace and Security"] = 0
nonnationscount["Special Envoy for the Implementation of Security Council Resolution"] = 0
nonnationscount["High Representative for Disarmament Affairs"] = 0
nonnationscount["Department of Peacekeeping Operations"] = 0
nonnationscount["International Maritime Organization"] = 0
nonnationscount["International Criminal Tribunal for the Former Yugoslavia"] = 0
nonnationscount["Eurasian Development Bank"] = 0
nonnationscount["Organization for Security and Co-operation in Europe"] = 0
nonnationscount["Department of General Assembly and Conference Management"] = 0
