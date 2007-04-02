import re
from unmisc import unexception


# list of nations and their dates as part of the General Assembly can be found at
# http://www.un.org/Overview/unmember.html
# The following list should be made consistent with it.

nationdates = {
        "Afghanistan":        ("1946-11-19", "9999-12-31"),
        "Albania":            ("1955-12-14", "9999-12-31"),
        "Algeria":            ("1962-10-08", "9999-12-31"),
        "Andorra":            ("1993-07-28", "9999-12-31"),
        "Angola":            ("1976-12-01", "9999-12-31"),
        "Antigua and Barbuda":("1981-11-11", "9999-12-31"),
        "Argentina":        ("1945-10-24", "9999-12-31"),
        "Armenia":            ("1992-03-02", "9999-12-31"),
        "Australia":        ("1945-11-01", "9999-12-31"),
        "Austria":            ("1955-12-14", "9999-12-31"),
        "Azerbaijan":        ("1992-03-02", "9999-12-31"),
        "Bahamas":            ("1973-09-18", "9999-12-31"),
        "Bahrain":            ("1971-09-21", "9999-12-31"),
        "Bangladesh":        ("1974-09-17", "9999-12-31"),
        "Barbados":            ("1966-12-09", "9999-12-31"),
        "Belarus":            ("1945-10-24", "9999-12-31"),
        "Belgium":            ("1945-12-27", "9999-12-31"),
        "Belize":            ("1981-09-25", "9999-12-31"),
        "Benin":            ("1960-09-20", "9999-12-31"),
        "Bhutan":            ("1971-09-21", "9999-12-31"),
        "Bolivia":            ("1945-11-14", "9999-12-31"),
        "Bosnia and Herzegovina":("1992-05-22", "9999-12-31"),
        "Botswana":            ("1966-10-17", "9999-12-31"),
        "Brazil":            ("1945-10-24", "9999-12-31"),
        "Brunei Darussalam":("1984-09-21", "9999-12-31"),
        "Bulgaria":            ("1955-12-14", "9999-12-31"),
        "Burkina Faso":        ("1960-09-20", "9999-12-31"),
        "Burundi":            ("1962-09-18", "9999-12-31"),
        "Cambodia":            ("1955-12-14", "9999-12-31"),
        "Cameroon":            ("1960-09-20", "9999-12-31"),
        "Canada":            ("1945-11-09", "9999-12-31"),
        "Cape Verde":        ("1975-09-16", "9999-12-31"),
        "Central African Republic":("1960-09-20", "9999-12-31"),
        "Chad":                ("1960-09-20", "9999-12-31"),
        "Chile":            ("1945-10-24", "9999-12-31"),
        "China":            ("1945-10-24", "9999-12-31"),
        "Colombia":            ("1945-11-05", "9999-12-31"),
        "Comoros":            ("1975-11-12", "9999-12-31"),
        "Congo":            ("1960-09-20", "9999-12-31"),
        "Zaire":            ("1960-09-20", "1997-05-17"), # name changed to "Democratic Republic of the Congo"
        "Democratic Republic of the Congo":("1997-05-17", "9999-12-31"),
        "Costa Rica":        ("1945-11-02", "9999-12-31"),
        "Cote d'Ivoire":    ("1960-09-20", "9999-12-31"),
        "Croatia":            ("1992-05-22", "9999-12-31"),
        "Cuba":                ("1945-10-24", "9999-12-31"),
        "Cyprus":            ("1960-09-20", "9999-12-31"),
        "Czech Republic":    ("1993-01-19", "9999-12-31"),
        "Democratic People's Republic of Korea":("1991-09-17", "9999-12-31"),
        "Denmark":            ("1945-10-24", "9999-12-31"),
        "Djibouti":            ("1977-09-20", "9999-12-31"),
        "Dominica":            ("1978-12-18", "9999-12-31"),
        "Dominican Republic":("1945-10-24", "9999-12-31"),
        "Ecuador":            ("1945-12-21", "9999-12-31"),
        "Egypt":            ("1945-10-24", "9999-12-31"),
        "El Salvador":        ("1945-10-24", "9999-12-31"),
        "Equatorial Guinea":("1968-11-12", "9999-12-31"),
        "Eritrea":            ("1993-05-28", "9999-12-31"),
        "Estonia":            ("1991-09-17", "9999-12-31"),
        "Ethiopia":            ("1945-11-13", "9999-12-31"),
        "Fiji":                ("1970-10-13", "9999-12-31"),
        "Finland":            ("1955-12-14", "9999-12-31"),
        "France":            ("1945-10-24", "9999-12-31"),
        "Gabon":            ("1960-09-20", "9999-12-31"),
        "Gambia":            ("1965-09-21", "9999-12-31"),
        "Georgia":            ("1992-07-31", "9999-12-31"),
        "Germany":            ("1973-09-18", "9999-12-31"),
        "Ghana":            ("1957-03-08", "9999-12-31"),
        "Greece":            ("1945-10-25", "9999-12-31"),
        "Grenada":            ("1974-09-17", "9999-12-31"),
        "Guatemala":        ("1945-11-21", "9999-12-31"),
        "Guinea":            ("1958-12-12", "9999-12-31"),
        "Guinea-Bissau":    ("1974-09-17", "9999-12-31"),
        "Guyana":            ("1966-09-20", "9999-12-31"),
        "Haiti":            ("1945-10-24", "9999-12-31"),
        "Honduras":            ("1945-12-17", "9999-12-31"),
        "Hungary":            ("1955-12-14", "9999-12-31"),
        "Iceland":            ("1946-11-19", "9999-12-31"),
        "India":            ("1945-10-30", "9999-12-31"),
        "Indonesia":        ("1950-09-28", "9999-12-31"),
        "Iran":                ("1945-10-24", "9999-12-31"),
        "Iraq":                ("1945-12-21", "9999-12-31"),
        "Ireland":            ("1955-12-14", "9999-12-31"),
        "Israel":            ("1949-05-11", "9999-12-31"),
        "Italy":            ("1955-12-14", "9999-12-31"),
        "Jamaica":            ("1962-09-18", "9999-12-31"),
        "Japan":            ("1956-12-18", "9999-12-31"),
        "Jordan":            ("1955-12-14", "9999-12-31"),
        "Kazakhstan":        ("1992-03-02", "9999-12-31"),
        "Kenya":            ("1963-12-16", "9999-12-31"),
        "Kiribati":            ("1999-09-14", "9999-12-31"),
        "Kuwait":            ("1963-05-14", "9999-12-31"),
        "Kyrgyzstan":        ("1992-03-02", "9999-12-31"),
        "Laos":("1955-12-14", "9999-12-31"),
        "Latvia":            ("1991-09-17", "9999-12-31"),
        "Lebanon":            ("1945-10-24", "9999-12-31"),
        "Lesotho":            ("1966-10-17", "9999-12-31"),
        "Liberia":            ("1945-11-02", "9999-12-31"),
        "Libya":            ("1955-12-14", "9999-12-31"),
        "Liechtenstein":    ("1990-09-18", "9999-12-31"),
        "Lithuania":        ("1991-09-17", "9999-12-31"),
        "Luxembourg":        ("1945-10-24", "9999-12-31"),
        "Madagascar":        ("1960-09-20", "9999-12-31"),
        "Malawi":            ("1964-12-01", "9999-12-31"),
        "Malaysia":            ("1957-09-17", "9999-12-31"),
        "Maldives":            ("1965-09-21", "9999-12-31"),
        "Mali":                ("1960-09-28", "9999-12-31"),
        "Malta":            ("1964-12-01", "9999-12-31"),
        "Marshall Islands":    ("1991-09-17", "9999-12-31"),
        "Mauritania":        ("1961-10-27", "9999-12-31"),
        "Mauritius":        ("1968-04-24", "9999-12-31"),
        "Mexico":            ("1945-11-07", "9999-12-31"),
        "Micronesia":        ("1991-09-17", "9999-12-31"),
        "Moldova":            ("1992-03-02", "9999-12-31"),
        "Monaco":            ("1993-05-28", "9999-12-31"),
        "Mongolia":            ("1961-10-27", "9999-12-31"),
        "Montenegro":        ("2006-06-28", "9999-12-31"),
        "Morocco":            ("1956-11-12", "9999-12-31"),
        "Mozambique":        ("1975-09-16", "9999-12-31"),
        "Myanmar":            ("1948-04-19", "9999-12-31"),
        "Namibia":            ("1990-04-23", "9999-12-31"),
        "Nauru":            ("1999-09-14", "9999-12-31"),
        "Nepal":            ("1955-12-14", "9999-12-31"),
        "Netherlands":        ("1945-12-10", "9999-12-31"),
        "New Zealand":        ("1945-10-24", "9999-12-31"),
        "Nicaragua":        ("1945-10-24", "9999-12-31"),
        "Niger":            ("1960-09-20", "9999-12-31"),
        "Nigeria":            ("1960-10-07", "9999-12-31"),
        "Norway":            ("1945-11-27", "9999-12-31"),
        "Oman":                ("1971-10-07", "9999-12-31"),
        "Pakistan":            ("1947-09-30", "9999-12-31"),
        "Palau":            ("1994-12-15", "9999-12-31"),
        "Panama":            ("1945-11-13", "9999-12-31"),
        "Papua New Guinea":    ("1975-10-10", "9999-12-31"),
        "Paraguay":            ("1945-10-24", "9999-12-31"),
        "Peru":                ("1945-10-31", "9999-12-31"),
        "Philippines":        ("1945-10-24", "9999-12-31"),
        "Poland":            ("1945-10-24", "9999-12-31"),
        "Portugal":            ("1955-12-14", "9999-12-31"),
        "Qatar":            ("1971-09-21", "9999-12-31"),
        "Republic of Korea":("1991-09-17", "9999-12-31"),
        "Romania":            ("1955-12-14", "9999-12-31"),
        "Russia":            ("1945-10-24", "9999-12-31"),
        "Rwanda":            ("1962-09-18", "9999-12-31"),
        "Saint Kitts and Nevis":("1983-09-23", "9999-12-31"),
        "Saint Lucia":        ("1979-09-18", "9999-12-31"),
        "Saint Vincent and the Grenadines":("1980-09-16", "9999-12-31"),
        "Samoa":            ("1976-12-15", "9999-12-31"),
        "San Marino":        ("1992-03-02", "9999-12-31"),
        "Sao Tome and Principe":("1975-09-16", "9999-12-31"),
        "Saudi Arabia":        ("1945-10-24", "9999-12-31"),
        "Senegal":            ("1960-09-28", "9999-12-31"),
        "Serbia":            ("2000-11-01", "9999-12-31"),
        "Seychelles":        ("1976-09-21", "9999-12-31"),
        "Sierra Leone":        ("1961-09-27", "9999-12-31"),
        "Singapore":        ("1965-09-21", "9999-12-31"),
        "Slovakia":            ("1993-01-19", "9999-12-31"),
        "Slovenia":            ("1992-05-22", "9999-12-31"),
        "Solomon Islands":    ("1978-09-19", "9999-12-31"),
        "Somalia":            ("1960-09-20", "9999-12-31"),
        "South Africa":        ("1945-11-07", "9999-12-31"),
        "Spain":            ("1955-12-14", "9999-12-31"),
        "Sri Lanka":        ("1955-12-14", "9999-12-31"),
        "Sudan":            ("1956-11-12", "9999-12-31"),
        "Suriname":            ("1975-12-04", "9999-12-31"),
        "Swaziland":        ("1968-09-24", "9999-12-31"),
        "Sweden":            ("1946-11-19", "9999-12-31"),
        "Switzerland":        ("2002-09-10", "9999-12-31"),
        "Syria":            ("1945-10-24", "9999-12-31"),
        "Tajikistan":        ("1992-03-02", "9999-12-31"),
        "Tanzania":            ("1961-12-14", "9999-12-31"),
        "Thailand":            ("1946-12-16", "9999-12-31"),
        "The former Yugoslav Republic of Macedonia":("1993-04-08", "9999-12-31"),
        "Timor-Leste":        ("2002-09-27", "9999-12-31"),
        "Togo":                ("1960-09-20", "9999-12-31"),
        "Tonga":            ("1999-09-14", "9999-12-31"),
        "Trinidad and Tobago":("1962-09-18", "9999-12-31"),
        "Tunisia":            ("1956-11-12", "9999-12-31"),
        "Turkey":            ("1945-10-24", "9999-12-31"),
        "Turkmenistan":        ("1992-03-02", "9999-12-31"),
        "Tuvalu":            ("2000-09-05", "9999-12-31"),
        "Uganda":            ("1962-10-25", "9999-12-31"),
        "Ukraine":            ("1945-10-24", "9999-12-31"),
        "United Arab Emirates":("1971-12-09", "9999-12-31"),
        "United Kingdom":    ("1945-10-24", "9999-12-31"),
        "United States":("1945-10-24", "9999-12-31"),
        "Uruguay":            ("1945-12-18", "9999-12-31"),
        "Uzbekistan":        ("1992-03-02", "9999-12-31"),
        "Vanuatu":            ("1981-09-15", "9999-12-31"),
        "Venezuela":        ("1945-11-15", "9999-12-31"),
        "Viet Nam":            ("1977-09-20", "9999-12-31"),
        "Yemen":            ("1947-09-30", "9999-12-31"),
        "Zambia":            ("1964-12-01", "9999-12-31"),
        "Zimbabwe":            ("1980-08-25", "9999-12-31"),

        "Yugoslavia":        ("1945-10-24", "2002-12-21"), # day after last appearance
        #"Zaire":     ("1945", "1999-12-31"),
                }

# includes typos, short names, and name changes
nationmapping = {
        "United Kingdom of Great Britain and Northern Ireland":"United Kingdom",
        "Côte d'Ivoire":"Cote d'Ivoire",
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
    if dr and sdate < dr[0]:
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
    if not dr[0] <= sdate < dr[1]:
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
            if dr[0] <= sdate < dr[1]:
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

American:
    Caribbean Community
    Caribbean Community CARICOM
    Ibero-American Conference
    Latin American Economic System
    Organization of American States
    Secretary-General of the Caribbean Community
    Secretary-General, Central American Integration System

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
    World Trade Organization

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
    Flora Tristan Centre for Peruvian Women
    Inter-Parliamentary Union
    International Confederation of Free Trade Unions
    International Organization of La Francophonie
    International Organization of la Francophonie
    League of Arab States
    Organization of the Islamic Conference
    Organization on the Islamic Conference
    Permanent Observer of Switzerland
    Social Watch
    South Pacific Forum
    former Yugoslav Republic of Macedonia

Health:
    Global Fund to Fight AIDS, Tuberculosis and Malaria
    International Committee of the Red Cross
    International Federation of Red Cross and Red Crescent Societies
    International Federation of the Red Cross and Red Crescent Societies
    Joint United Nations Programme on HIV/AIDS
    MTV Networks International/Global Media AIDS Initiative
    Observer for the International Federation of Red Cross and Red Crescent Societies
    Treatment Action Campaign
    World Health Organization

Legal:
    International Court of Justice
    International Criminal Court
    International Criminal Police Organization-Interpol
    International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    Organization for Security and Cooperation in Europe
    Permanent Court of Arbitration
    President of the International Court
    President of the International Court of Justice
    President of the International Criminal Tribunal for Rwanda
    President of the International Criminal Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    President of the International Tribunal
    President of the International Tribunal for Rwanda
    President of the International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    President, International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991
    Secretary General of the Conference on Security and Cooperation in Europe
    The Legal Counsel

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
    General Assembly Affairs Branch
    High Commissioner for Human Rights
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
    UNICEF
    Under Secretary-General for General Assembly and Conference Management
    Under-Secretary-General for General Assembly Affairs and Conference Services
    Under-Secretary-General for General Assembly and Conference Management
    Under-Secretary-General for Humanitarian Affairs
    Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator
    Under-Secretary-General for Peacekeeping Operations
    Under-Secretary-General for Policy Coordination and Sustainable Development
    Under-Secretary-General for Political Affairs
    Under-Secretary-General, Department of General Assembly Affairs and Conference Management
    Under-Secretary-General, Department of General Assembly Affairs and Conference Services
    United Nations Children's Fund
    United Nations Conference on Trade and Development
    United Nations Development Fund for Women
    United Nations Development Programme
    United Nations Educational, Scientific and Cultural Organization
    United Nations High Commissioner for Human Rights
    United Nations High Commissioner for Refugees
    United Nations Population Fund
    Vice-President of the Economic and Social Council

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



