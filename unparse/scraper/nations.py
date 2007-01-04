import re
from unmisc import unexception


# list of nations and their dates as part of the General Assembly can be found at
# http://www.un.org/Overview/unmember.html
# The following list should be made consistent with it.

nationdates = {
		"Afghanistan":		("1946-11-19", "9999-12-31"),
		"Albania":			("1955-12-14", "9999-12-31"),
		"Algeria":			("1962-10-08", "9999-12-31"),
		"Andorra":			("1993-07-28", "9999-12-31"),
		"Angola":			("1976-12-01", "9999-12-31"),
		"Antigua and Barbuda":("1981-11-11", "9999-12-31"),
		"Argentina":		("1945-10-24", "9999-12-31"),
		"Armenia":			("1992-03-02", "9999-12-31"),
		"Australia":		("1945-11-01", "9999-12-31"),
		"Austria":			("1955-12-14", "9999-12-31"),
		"Azerbaijan":		("1992-03-02", "9999-12-31"),
		"Bahamas":			("1973-09-18", "9999-12-31"),
		"Bahrain":			("1971-09-21", "9999-12-31"),
		"Bangladesh":		("1974-09-17", "9999-12-31"),
		"Barbados":			("1966-12-09", "9999-12-31"),
		"Belarus":			("1945-10-24", "9999-12-31"),
		"Belgium":			("1945-12-27", "9999-12-31"),
		"Belize":			("1981-09-25", "9999-12-31"),
		"Benin":			("1960-09-20", "9999-12-31"),
		"Bhutan":			("1971-09-21", "9999-12-31"),
		"Bolivia":			("1945-11-14", "9999-12-31"),
		"Bosnia and Herzegovina":("1992-05-22", "9999-12-31"),
		"Botswana":			("1966-10-17", "9999-12-31"),
		"Brazil":			("1945-10-24", "9999-12-31"),
		"Brunei Darussalam":("1984-09-21", "9999-12-31"),
		"Bulgaria":			("1955-12-14", "9999-12-31"),
		"Burkina Faso":		("1960-09-20", "9999-12-31"),
		"Burundi":			("1962-09-18", "9999-12-31"),
		"Cambodia":			("1955-12-14", "9999-12-31"),
		"Cameroon":			("1960-09-20", "9999-12-31"),
		"Canada":			("1945-11-09", "9999-12-31"),
		"Cape Verde":		("1975-09-16", "9999-12-31"),
		"Central African Republic":("1960-09-20", "9999-12-31"),
		"Chad":				("1960-09-20", "9999-12-31"),
		"Chile":			("1945-10-24", "9999-12-31"),
		"China":			("1945-10-24", "9999-12-31"),
		"Colombia":			("1945-11-05", "9999-12-31"),
		"Comoros":			("1975-11-12", "9999-12-31"),
		"Congo":			("1960-09-20", "9999-12-31"),
		"Zaire":			("1960-09-20", "1997-05-17"), # name changed to "Democratic Republic of the Congo"
		"Democratic Republic of the Congo":("1997-05-17", "9999-12-31"),
		"Costa Rica":		("1945-11-02", "9999-12-31"),
		"Cote d'Ivoire":	("1960-09-20", "9999-12-31"),
		"Croatia":			("1992-05-22", "9999-12-31"),
		"Cuba":				("1945-10-24", "9999-12-31"),
		"Cyprus":			("1960-09-20", "9999-12-31"),
		"Czech Republic":	("1993-01-19", "9999-12-31"),
		"Democratic People's Republic of Korea":("1991-09-17", "9999-12-31"),
		"Denmark":			("1945-10-24", "9999-12-31"),
		"Djibouti":			("1977-09-20", "9999-12-31"),
		"Dominica":			("1978-12-18", "9999-12-31"),
		"Dominican Republic":("1945-10-24", "9999-12-31"),
		"Ecuador":			("1945-12-21", "9999-12-31"),
		"Egypt":			("1945-10-24", "9999-12-31"),
		"El Salvador":		("1945-10-24", "9999-12-31"),
		"Equatorial Guinea":("1968-11-12", "9999-12-31"),
		"Eritrea":			("1993-05-28", "9999-12-31"),
		"Estonia":			("1991-09-17", "9999-12-31"),
		"Ethiopia":			("1945-11-13", "9999-12-31"),
		"Fiji":				("1970-10-13", "9999-12-31"),
		"Finland":			("1955-12-14", "9999-12-31"),
		"France":			("1945-10-24", "9999-12-31"),
		"Gabon":			("1960-09-20", "9999-12-31"),
		"Gambia":			("1965-09-21", "9999-12-31"),
		"Georgia":			("1992-07-31", "9999-12-31"),
		"Germany":			("1973-09-18", "9999-12-31"),
		"Ghana":			("1957-03-08", "9999-12-31"),
		"Greece":			("1945-10-25", "9999-12-31"),
		"Grenada":			("1974-09-17", "9999-12-31"),
		"Guatemala":		("1945-11-21", "9999-12-31"),
		"Guinea":			("1958-12-12", "9999-12-31"),
		"Guinea-Bissau":	("1974-09-17", "9999-12-31"),
		"Guyana":			("1966-09-20", "9999-12-31"),
		"Haiti":			("1945-10-24", "9999-12-31"),
		"Honduras":			("1945-12-17", "9999-12-31"),
		"Hungary":			("1955-12-14", "9999-12-31"),
		"Iceland":			("1946-11-19", "9999-12-31"),
		"India":			("1945-10-30", "9999-12-31"),
		"Indonesia":		("1950-09-28", "9999-12-31"),
		"Iran":				("1945-10-24", "9999-12-31"),
		"Iraq":				("1945-12-21", "9999-12-31"),
		"Ireland":			("1955-12-14", "9999-12-31"),
		"Israel":			("1949-05-11", "9999-12-31"),
		"Italy":			("1955-12-14", "9999-12-31"),
		"Jamaica":			("1962-09-18", "9999-12-31"),
		"Japan":			("1956-12-18", "9999-12-31"),
		"Jordan":			("1955-12-14", "9999-12-31"),
		"Kazakhstan":		("1992-03-02", "9999-12-31"),
		"Kenya":			("1963-12-16", "9999-12-31"),
		"Kiribati":			("1999-09-14", "9999-12-31"),
		"Kuwait":			("1963-05-14", "9999-12-31"),
		"Kyrgyzstan":		("1992-03-02", "9999-12-31"),
		"Laos":("1955-12-14", "9999-12-31"),
		"Latvia":			("1991-09-17", "9999-12-31"),
		"Lebanon":			("1945-10-24", "9999-12-31"),
		"Lesotho":			("1966-10-17", "9999-12-31"),
		"Liberia":			("1945-11-02", "9999-12-31"),
		"Libya":			("1955-12-14", "9999-12-31"),
		"Liechtenstein":	("1990-09-18", "9999-12-31"),
		"Lithuania":		("1991-09-17", "9999-12-31"),
		"Luxembourg":		("1945-10-24", "9999-12-31"),
		"Madagascar":		("1960-09-20", "9999-12-31"),
		"Malawi":			("1964-12-01", "9999-12-31"),
		"Malaysia":			("1957-09-17", "9999-12-31"),
		"Maldives":			("1965-09-21", "9999-12-31"),
		"Mali":				("1960-09-28", "9999-12-31"),
		"Malta":			("1964-12-01", "9999-12-31"),
		"Marshall Islands":	("1991-09-17", "9999-12-31"),
		"Mauritania":		("1961-10-27", "9999-12-31"),
		"Mauritius":		("1968-04-24", "9999-12-31"),
		"Mexico":			("1945-11-07", "9999-12-31"),
		"Micronesia":		("1991-09-17", "9999-12-31"),
		"Moldova":			("1992-03-02", "9999-12-31"),
		"Monaco":			("1993-05-28", "9999-12-31"),
		"Mongolia":			("1961-10-27", "9999-12-31"),
		"Montenegro":		("2006-06-28", "9999-12-31"),
		"Morocco":			("1956-11-12", "9999-12-31"),
		"Mozambique":		("1975-09-16", "9999-12-31"),
		"Myanmar":			("1948-04-19", "9999-12-31"),
		"Namibia":			("1990-04-23", "9999-12-31"),
		"Nauru":			("1999-09-14", "9999-12-31"),
		"Nepal":			("1955-12-14", "9999-12-31"),
		"Netherlands":		("1945-12-10", "9999-12-31"),
		"New Zealand":		("1945-10-24", "9999-12-31"),
		"Nicaragua":		("1945-10-24", "9999-12-31"),
		"Niger":			("1960-09-20", "9999-12-31"),
		"Nigeria":			("1960-10-07", "9999-12-31"),
		"Norway":			("1945-11-27", "9999-12-31"),
		"Oman":				("1971-10-07", "9999-12-31"),
		"Pakistan":			("1947-09-30", "9999-12-31"),
		"Palau":			("1994-12-15", "9999-12-31"),
		"Panama":			("1945-11-13", "9999-12-31"),
		"Papua New Guinea":	("1975-10-10", "9999-12-31"),
		"Paraguay":			("1945-10-24", "9999-12-31"),
		"Peru":				("1945-10-31", "9999-12-31"),
		"Philippines":		("1945-10-24", "9999-12-31"),
		"Poland":			("1945-10-24", "9999-12-31"),
		"Portugal":			("1955-12-14", "9999-12-31"),
		"Qatar":			("1971-09-21", "9999-12-31"),
		"Republic of Korea":("1991-09-17", "9999-12-31"),
		"Romania":			("1955-12-14", "9999-12-31"),
		"Russia":			("1945-10-24", "9999-12-31"),
		"Rwanda":			("1962-09-18", "9999-12-31"),
		"Saint Kitts and Nevis":("1983-09-23", "9999-12-31"),
		"Saint Lucia":		("1979-09-18", "9999-12-31"),
		"Saint Vincent and the Grenadines":("1980-09-16", "9999-12-31"),
		"Samoa":			("1976-12-15", "9999-12-31"),
		"San Marino":		("1992-03-02", "9999-12-31"),
		"Sao Tome and Principe":("1975-09-16", "9999-12-31"),
		"Saudi Arabia":		("1945-10-24", "9999-12-31"),
		"Senegal":			("1960-09-28", "9999-12-31"),
		"Serbia":			("2000-11-01", "9999-12-31"),
		"Seychelles":		("1976-09-21", "9999-12-31"),
		"Sierra Leone":		("1961-09-27", "9999-12-31"),
		"Singapore":		("1965-09-21", "9999-12-31"),
		"Slovakia":			("1993-01-19", "9999-12-31"),
		"Slovenia":			("1992-05-22", "9999-12-31"),
		"Solomon Islands":	("1978-09-19", "9999-12-31"),
		"Somalia":			("1960-09-20", "9999-12-31"),
		"South Africa":		("1945-11-07", "9999-12-31"),
		"Spain":			("1955-12-14", "9999-12-31"),
		"Sri Lanka":		("1955-12-14", "9999-12-31"),
		"Sudan":			("1956-11-12", "9999-12-31"),
		"Suriname":			("1975-12-04", "9999-12-31"),
		"Swaziland":		("1968-09-24", "9999-12-31"),
		"Sweden":			("1946-11-19", "9999-12-31"),
		"Switzerland":		("2002-09-10", "9999-12-31"),
		"Syria":			("1945-10-24", "9999-12-31"),
		"Tajikistan":		("1992-03-02", "9999-12-31"),
		"Tanzania":			("1961-12-14", "9999-12-31"),
		"Thailand":			("1946-12-16", "9999-12-31"),
		"The former Yugoslav Republic of Macedonia":("1993-04-08", "9999-12-31"),
		"Timor-Leste":		("2002-09-27", "9999-12-31"),
		"Togo":				("1960-09-20", "9999-12-31"),
		"Tonga":			("1999-09-14", "9999-12-31"),
		"Trinidad and Tobago":("1962-09-18", "9999-12-31"),
		"Tunisia":			("1956-11-12", "9999-12-31"),
		"Turkey":			("1945-10-24", "9999-12-31"),
		"Turkmenistan":		("1992-03-02", "9999-12-31"),
		"Tuvalu":			("2000-09-05", "9999-12-31"),
		"Uganda":			("1962-10-25", "9999-12-31"),
		"Ukraine":			("1945-10-24", "9999-12-31"),
		"United Arab Emirates":("1971-12-09", "9999-12-31"),
		"United Kingdom":	("1945-10-24", "9999-12-31"),
		"United States":("1945-10-24", "9999-12-31"),
		"Uruguay":			("1945-12-18", "9999-12-31"),
		"Uzbekistan":		("1992-03-02", "9999-12-31"),
		"Vanuatu":			("1981-09-15", "9999-12-31"),
		"Venezuela":		("1945-11-15", "9999-12-31"),
		"Viet Nam":			("1977-09-20", "9999-12-31"),
		"Yemen":			("1947-09-30", "9999-12-31"),
		"Zambia":			("1964-12-01", "9999-12-31"),
		"Zimbabwe":			("1980-08-25", "9999-12-31"),

		"Yugoslavia":		("1945-10-24", "2002-12-21"), # day after last appearance
		#"Zaire": 	("1945", "1999-12-31"),
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
	if nonnation[0] == "*":
		nonnation = nonnation[1:]
		if nonnation not in nonnations:
			nonnations[nonnation] = 0
			print "   *** new nonnation:", nonnation
			fout = open("nations.py", "a")
			fout.write('nonnations["%s"] = 0\n' % nonnation)
			fout.close()
	if nonnation not in nonnations:
		return False
	nonnations[nonnation] += 1
	return nonnation

def PrintNonnationOccurrances():
	for nn in reversed(sorted([(nonnations[n], n)  for n in nonnations.keys()  if nonnations[n]])):
		print nn

nonnations = { }

nonnations["African Development Bank"] = 0
nonnations["African Union"] = 0
nonnations["Asian Development Bank"] = 0
nonnations["Asian-African Legal Consultative Committee"] = 0
nonnations["Asian-African Legal Consultative Organization"] = 0
nonnations["Black Sea Economic Cooperation Organization"] = 0
nonnations["Caribbean Community"] = 0
nonnations["Chairman of the Committee on the Exercise of the Inalienable Rights of the Palestinian People"] = 0
nonnations["Chairman of the Committee on the Peaceful Uses of Outer Space"] = 0
nonnations["Chairman of the Information and Communication Technologies Task Force"] = 0
nonnations["Chief, General Assembly Affairs Branch"] = 0
nonnations["Chief, General Assembly Affairs Branch, Department for General Assembly and Conference Management"] = 0
nonnations["Chief, General Assembly Servicing Branch"] = 0
nonnations["Co-Chair of the Millennium Forum"] = 0
nonnations["Commission on the Limits of the Continental Shelf"] = 0
nonnations["Commonwealth Secretariat"] = 0
nonnations["Comprehensive Nuclear-Test-Ban Treaty Organization"] = 0
nonnations["Conference of Non-Governmental Organizations in Consultative Relationship with the United Nations"] = 0
nonnations["Conference of Presiding Officers of National Parliaments"] = 0
nonnations["Council of Europe"] = 0
nonnations["Customs Cooperation Council"] = 0
nonnations["Department for General Assembly and Conference Management"] = 0
nonnations["Deputy Secretary-General"] = 0
nonnations["Digital Opportunity Task Force"] = 0
nonnations["Director of General Assembly and ECOSOC Affairs"] = 0
nonnations["Director, General Assembly and ECOSOC Affairs Division, Department of General Assembly Affairs and Conference Services"] = 0
nonnations["Director, General Assembly and Economic and Social Council Affairs Division"] = 0
nonnations["Director, General Assembly and Economic and Social Council Affairs Division of the Department of General Assembly Affairs and Conference Management Services"] = 0
nonnations["Director, General Assembly and Economic and Social Council Affairs Division, Department for General Assembly and Conference Management"] = 0
nonnations["Economic Community of Central African States"] = 0
nonnations["Economic Cooperation Organization"] = 0
nonnations["Economic and Social Commission for Western Africa"] = 0
nonnations["European Commission"] = 0
nonnations["European Community"] = 0
nonnations["Executive Secretary of the Preparatory Commission for the Comprehensive Nuclear-Test-Ban Treaty Organization"] = 0
nonnations["General Assembly Affairs Branch"] = 0
nonnations["Holy See"] = 0
nonnations["Inter-Parliamentary Union"] = 0
nonnations["International Atomic Energy Agency"] = 0
nonnations["International Committee of the Red Cross"] = 0
nonnations["International Confederation of Free Trade Unions"] = 0
nonnations["International Court of Justice"] = 0
nonnations["International Criminal Court"] = 0
nonnations["International Federation of Red Cross and Red Crescent Societies"] = 0
nonnations["International Federation of the Red Cross and Red Crescent Societies"] = 0
nonnations["International Hydrographic Organization"] = 0
nonnations["International Monetary Fund"] = 0
nonnations["International Organization for Migration"] = 0
nonnations["International Organization of La Francophonie"] = 0
nonnations["International Organization of la Francophonie"] = 0
nonnations["International Seabed Authority"] = 0
nonnations["International Telecommunication Union"] = 0
nonnations["International Tribunal for the Law of the Sea"] = 0
nonnations["International Union for the Conservation of Nature and Natural Resources"] = 0
nonnations["Joint United Nations Programme on HIV/AIDS"] = 0
nonnations["Judge, International Tribunal for the Law of the Sea"] = 0
nonnations["League of Arab States"] = 0
nonnations["McKinsey and Company"] = 0
nonnations["New Zealand, President, Twelfth Meeting of States Parties to the United Nations Convention on the Law of the Sea"] = 0
nonnations["Observer for the International Federation of Red Cross and Red Crescent Societies"] = 0
nonnations["Organization for Security and Cooperation in Europe"] = 0
nonnations["Organization for the Prohibition of Chemical Weapons"] = 0
nonnations["Organization of African Unity"] = 0
nonnations["Organization of American States"] = 0
nonnations["Organization of the Islamic Conference"] = 0
nonnations["Palestine"] = 0
nonnations["Partners in Population and Development"] = 0
nonnations["Permanent Court of Arbitration"] = 0
nonnations["Preparatory Commission for the Comprehensive Nuclear-Test-Ban Treaty Organization"] = 0
nonnations["President of the Assembly of the International Seabed Authority"] = 0
nonnations["President of the Economic and Social Council"] = 0
nonnations["President of the International Court"] = 0
nonnations["President of the International Court of Justice"] = 0
nonnations["President of the International Tribunal"] = 0
nonnations["President of the International Tribunal for Rwanda"] = 0
nonnations["President of the Security Council"] = 0
nonnations["President, Third United Nations Conference on the Law of the Sea"] = 0
nonnations["Rapporteur"] = 0
nonnations["Rapporteur of the Committee on the Exercise of the Inalienable Rights of the Palestinian People"] = 0
nonnations["Representative of the Secretariat"] = 0
nonnations["Secretary-General"] = 0
nonnations["Secretary-General of the International Seabed Authority"] = 0
nonnations["Secretary-General, Eurasian Economic Community"] = 0
nonnations["Shanghai Cooperation Organization"] = 0
nonnations["Social Watch"] = 0
nonnations["Sovereign Military Order of Malta"] = 0
nonnations["The Legal Counsel"] = 0
nonnations["UNICEF"] = 0
nonnations["Under-Secretary-General for General Assembly Affairs and Conference Services"] = 0
nonnations["Under-Secretary-General for General Assembly and Conference Management"] = 0
nonnations["Under-Secretary-General, Department of General Assembly Affairs and Conference Management"] = 0
nonnations["Under-Secretary-General, Department of General Assembly Affairs and Conference Services"] = 0
nonnations["United Nations Children's Fund"] = 0
nonnations["United Nations Conference on Trade and Development"] = 0
nonnations["United Nations Development Programme"] = 0
nonnations["United Nations Educational, Scientific and Cultural Organization"] = 0
nonnations["United Nations High Commissioner for Human Rights"] = 0
nonnations["United Nations Population Fund"] = 0
nonnations["Vice-President of the Economic and Social Council"] = 0
nonnations["World Bank"] = 0
nonnations["World Health Organization"] = 0
nonnations["World Trade Organization"] = 0
nonnations["African Development Bank"] = 0
nonnations["African Development Bank"] = 0
nonnations["Flora Tristan Centre for Peruvian Women"] = 0
nonnations["BHI Holdings Limited"] = 0
nonnations["Treatment Action Campaign"] = 0
nonnations["Global Fund to Fight AIDS, Tuberculosis and Malaria"] = 0
nonnations["MTV Networks International/Global Media AIDS Initiative"] = 0
nonnations["African Network of Religious Leaders Living with or Personally Affected by HIV/AIDS"] = 0
nonnations["Agency for Cultural and Technical Cooperation"] = 0
nonnations["Latin American Economic System"] = 0
nonnations["International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991"] = 0
nonnations["President of the International Criminal Tribunal for Rwanda"] = 0
nonnations["International Criminal Police Organization-Interpol"] = 0
nonnations["Caribbean Community CARICOM"] = 0
nonnations["Director, General Assembly Affairs Division"] = 0
nonnations["President of the International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991"] = 0
nonnations["Secretary-General of the Economic Cooperation Organization"] = 0
nonnations["Secretary-General, Central American Integration System"] = 0
nonnations["Deputy Secretary-General of the South Pacific Forum"] = 0
nonnations["Secretary-General of the Caribbean Community"] = 0
nonnations["Secretary-General of the Organization of African Unity"] = 0
nonnations["Secretary-General of the Organization for Security and Cooperation in Europe"] = 0
nonnations["Secretary-General of the Asian-African Legal Consultative Committee"] = 0
nonnations["Under-Secretary-General for Policy Coordination and Sustainable Development"] = 0
nonnations["Director General, International Atomic Energy Agency"] = 0
nonnations["President of the International Criminal Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991"] = 0
nonnations["Assistant Secretary-General for Political Affairs"] = 0
nonnations["Assistant Secretary-General for Peacekeeping Operations"] = 0
nonnations["Director, General Assembly Affairs"] = 0
nonnations["Director, General Assembly Affairs Division, Department of Political Affairs"] = 0
nonnations["Director General of the International Atomic Energy Agency"] = 0
nonnations["South Pacific Forum"] = 0
nonnations["Director of the General Assembly and Trusteeship Council Affairs Division"] = 0
nonnations["Special Adviser to the Secretary-General on General Assembly Matters"] = 0
nonnations["Asian-African Consultative Committee"] = 0
nonnations["Director of General Assembly and Trusteeship Council Affairs Division"] = 0
nonnations["President, International Tribunal for the Prosecution of Persons Responsible for Serious Violations of International Humanitarian Law Committed in the Territory of the Former Yugoslavia since 1991"] = 0
nonnations["Secretary General of the Conference on Security and Cooperation in Europe"] = 0
nonnations["Observer for Palestine"] = 0
nonnations["Director of the General Assembly Affairs Division"] = 0
nonnations["Director of General Assembly and Economic and Social Council Affairs"] = 0
nonnations["Under Secretary-General for General Assembly and Conference Management"] = 0
nonnations["Community of Portuguese-Speaking Countries"] = 0
nonnations["African, Caribbean and Pacific Group of States"] = 0
nonnations["Ibero-American Conference"] = 0
nonnations["International Centre for Migration Policy Development"] = 0
nonnations["Under-Secretary-General for Peacekeeping Operations"] = 0
nonnations["Officer-in-Charge of the Security Council Affairs Division"] = 0
nonnations["High Commissioner for Human Rights"] = 0
nonnations["Under-Secretary-General for Humanitarian Affairs and Emergency Relief Coordinator"] = 0
nonnations["United Nations High Commissioner for Refugees"] = 0
nonnations["Special Representative and Transitional Administrator in East Timor"] = 0
nonnations["Director of the Security Council Affairs Division"] = 0
nonnations["Office of the United Nations High Commissioner for Refugees"] = 0
nonnations["Under-Secretary-General for Humanitarian Affairs"] = 0
nonnations["former Yugoslav Republic of Macedonia"] = 0
nonnations["Organization on the Islamic Conference"] = 0
nonnations["United Nations Development Fund for Women"] = 0
nonnations["Permanent Observer of Switzerland"] = 0
nonnations["Economic Community of West African States"] = 0
nonnations["Special Adviser on Gender Issues and Advancement of Women"] = 0
nonnations["Chairman of the Monitoring Group"] = 0
nonnations["Geneva International Centre for Humanitarian Demining"] = 0
