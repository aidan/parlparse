import re

nationdates = {
        "Afghanistan": 	("1945", "9999-12-31"),
		"Albania": 	("1945", "9999-12-31"),
		"Algeria": 	("1945", "9999-12-31"),
		"Andorra": 	("1945", "9999-12-31"),
		"Angola": 	("1945", "9999-12-31"),
		"Antigua and Barbuda": 	("1945", "9999-12-31"),
		"Argentina": 	("1945", "9999-12-31"),
		"Armenia": 	("1945", "9999-12-31"),
		"Australia": 	("1945", "9999-12-31"),
		"Austria": 	("1945", "9999-12-31"),
		"Azerbaijan": 	("1945", "9999-12-31"),
		"Bahamas": 	("1945", "9999-12-31"),
		"Bahrain": 	("1945", "9999-12-31"),
		"Bangladesh": 	("1945", "9999-12-31"),
		"Barbados": 	("1945", "9999-12-31"),
		"Belarus": 	("1945", "9999-12-31"),
		"Belgium": 	("1945", "9999-12-31"),
		"Belize": 	("1945", "9999-12-31"),
		"Benin": 	("1945", "9999-12-31"),
		"Bhutan": 	("1945", "9999-12-31"),
		"Bolivia": 	("1945", "9999-12-31"),
		"Bosnia and Herzegovina": ("1945", "9999-12-31"),
		"Botswana": 	("1945", "9999-12-31"),
		"Brazil": 	("1945", "9999-12-31"),
		"Brunei Darussalam": 	("1945", "9999-12-31"),
		"Bulgaria": 	("1945", "9999-12-31"),
		"Burkina Faso": 	("1945", "9999-12-31"),
		"Burundi": 	("1945", "9999-12-31"),
		"Croatia": 	("1945", "9999-12-31"),
		"Cambodia": 	("1945", "9999-12-31"),
		"Cameroon": 	("1945", "9999-12-31"),
		"Canada": 	("1945", "9999-12-31"),
		"Cape Verde": 	("1945", "9999-12-31"),
		"Central African Republic": 	("1945", "9999-12-31"),
		"Chad": 	("1945", "9999-12-31"),
		"Chile": 	("1945", "9999-12-31"),
		"China": 	("1945", "9999-12-31"),
		"Colombia": 	("1945", "9999-12-31"),
		"Comoros": 	("1945", "9999-12-31"),
		"Congo": 	("1945", "9999-12-31"),
		"Costa Rica": 	("1945", "9999-12-31"),
		"Croatia": 	("1945", "9999-12-31"),
		"Cuba": 	("1945", "9999-12-31"),
		"Cyprus": 	("1945", "9999-12-31"),
		"Czech Republic": 	("1945", "9999-12-31"),
		"C�te d'Ivoire": 	("1945", "9999-12-31"),
		"Democratic People's Republic of Korea": 	("1945", "9999-12-31"),
		"Democratic Republic of the Congo": 	("1945", "9999-12-31"),
		"Denmark": 	("1945", "9999-12-31"),
		"Dominica": 	("1945", "9999-12-31"),
		"Dominican Republic": 	("1945", "9999-12-31"),
		"Djibouti": 	("1945", "9999-12-31"),
		"Ecuador": 	("1945", "9999-12-31"),
		"Egypt": 	("1945", "9999-12-31"),
		"El Salvador": 	("1945", "9999-12-31"),
		"Equatorial Guinea": 	("1945", "9999-12-31"),
		"Eritrea": 	("1945", "9999-12-31"),
		"Estonia": 	("1945", "9999-12-31"),
		"Ethiopia": 	("1945", "9999-12-31"),
		"Fiji": 	("1945", "9999-12-31"),
		"Finland": 	("1945", "9999-12-31"),
		"France": 	("1945", "9999-12-31"),
		"Gabon": 	("1945", "9999-12-31"),
		"Gambia": 	("1945", "9999-12-31"),
		"Georgia": 	("1945", "9999-12-31"),
		"Germany": 	("1945", "9999-12-31"),
		"Ghana": 	("1945", "9999-12-31"),
		"Greece": 	("1945", "9999-12-31"),
		"Grenada": 	("1945", "9999-12-31"),
		"Guatemala": 	("1945", "9999-12-31"),
		"Guinea": 	("1945", "9999-12-31"),
		"Guinea-Bissau": 	("1945", "9999-12-31"),
		"Guyana": 	("1945", "9999-12-31"),
		"Haiti": 	("1945", "9999-12-31"),
		"Honduras": 	("1945", "9999-12-31"),
		"Hungary": 	("1945", "9999-12-31"),
		"Iceland": 	("1945", "9999-12-31"),
		"India": 	("1945", "9999-12-31"),
		"Indonesia": 	("1945", "9999-12-31"),
		"Iran": 	("1945", "9999-12-31"),
		"Iraq": 	("1945", "9999-12-31"),
		"Ireland": 	("1945", "9999-12-31"),
		"Israel": 	("1945", "9999-12-31"),
		"Italy": 	("1945", "9999-12-31"),
		"Jamaica": 	("1945", "9999-12-31"),
		"Japan": 	("1945", "9999-12-31"),
		"Jordan": 	("1945", "9999-12-31"),
		"Kazakhstan": 	("1945", "9999-12-31"),
		"Kiribati":("1999-09-12", "9999-12-31"),
		"Kenya": 	("1945", "9999-12-31"),
		"Kuwait": 	("1945", "9999-12-31"),
		"Kyrgyzstan": 	("1945", "9999-12-31"),
		"Lao People's Democratic Republic": 	("1945", "9999-12-31"),
		"Latvia": 	("1945", "9999-12-31"),
		"Lebanon": 	("1945", "9999-12-31"),
		"Lesotho": 	("1945", "9999-12-31"),
		"Liberia": 	("1945", "9999-12-31"),
		"Libya": 	("1945", "9999-12-31"),
		"Liechtenstein": 	("1945", "9999-12-31"),
		"Lithuania": 	("1945", "9999-12-31"),
		"Luxembourg": 	("1945", "9999-12-31"),
		"Madagascar": 	("1945", "9999-12-31"),
		"Malawi": 	("1945", "9999-12-31"),
		"Malaysia": 	("1945", "9999-12-31"),
		"Maldives": 	("1945", "9999-12-31"),
		"Mali": 	("1945", "9999-12-31"),
		"Malta": 	("1945", "9999-12-31"),
		"Marshall Islands": 	("1945", "9999-12-31"),
		"Mauritania": 	("1945", "9999-12-31"),
		"Mauritius": 	("1945", "9999-12-31"),
		"Mexico": 	("1945", "9999-12-31"),
		"Micronesia (Federated States of)": 	("1945", "9999-12-31"),
		"Monaco": 	("1945", "9999-12-31"),
		"Mongolia": 	("1945", "9999-12-31"),
		"Morocco": 	("1945", "9999-12-31"),
		"Mozambique": 	("1945", "9999-12-31"),
		"Myanmar": 	("1945", "9999-12-31"),
		"Namibia": 	("1945", "9999-12-31"),
		"Nauru": 	("1999-09-14", "9999-12-31"),
		"Nepal": 	("1945", "9999-12-31"),
		"Netherlands": 	("1945", "9999-12-31"),
		"New Zealand": 	("1945", "9999-12-31"),
		"Nicaragua": 	("1945", "9999-12-31"),
		"Niger": 	("1945", "9999-12-31"),
		"Nigeria": 	("1945", "9999-12-31"),
		"Norway": 	("1945", "9999-12-31"),
		"Oman": 	("1945", "9999-12-31"),
		"Papua New Guinea": 	("1945", "9999-12-31"),
		"Pakistan": 	("1945", "9999-12-31"),
		"Palau": 	("1994-12-15", "9999-12-31"),
		"Panama": 	("1945", "9999-12-31"),
		"Paraguay": 	("1945", "9999-12-31"),
		"Peru": 	("1945", "9999-12-31"),
		"Philippines": 	("1945", "9999-12-31"),
		"Poland": 	("1945", "9999-12-31"),
		"Portugal": 	("1945", "9999-12-31"),
		"Qatar": 	("1945", "9999-12-31"),
		"Republic of Korea": 	("1945", "9999-12-31"),
		"Republic of Moldova": 	("1945", "9999-12-31"),
		"Romania": 	("1945", "9999-12-31"),
		"Russian Federation": 	("1945", "9999-12-31"),
		"Rwanda": 	("1945", "9999-12-31"),
		"Saint Kitts and Nevis": 	("1945", "9999-12-31"),
		"Saint Lucia": 	("1945", "9999-12-31"),
		"Saint Vincent and the Grenadines": 	("1945", "9999-12-31"),
		"Samoa": 	("1945", "9999-12-31"),
		"San Marino": 	("1945", "9999-12-31"),
		"Sao Tome and Principe": 	("1945", "9999-12-31"),
		"Saudi Arabia": 	("1945", "9999-12-31"),
		"Senegal": 	("1945", "9999-12-31"),
		"Serbia": 	("2000-11-01", "9999-12-31"),
		"Seychelles": 	("1945", "9999-12-31"),
		"Sierra Leone": 	("1945", "9999-12-31"),
		"Singapore": 	("1945", "9999-12-31"),
		"Slovakia": 	("1945", "9999-12-31"),
		"Slovenia": 	("1945", "9999-12-31"),
		"Solomon Islands": 	("1945", "9999-12-31"),
		"Somalia":		("1960-09-20", "9999-12-31"),
		"South Africa": 	("1945", "9999-12-31"),
		"Spain": 	("1945", "9999-12-31"),
		"Sri Lanka": 	("1945", "9999-12-31"),
		"Sudan": 	("1945", "9999-12-31"),
		"Suriname": 	("1945", "9999-12-31"),
		"Swaziland": 	("1945", "9999-12-31"),
		"Sweden": 	("1945", "9999-12-31"),
		"Switzerland": ("2002-09-10", "9999-12-31"),
		"Syria": 	("1945", "9999-12-31"),
		"Tajikistan": 	("1945", "9999-12-31"),
		"Thailand": 	("1945", "9999-12-31"),
 		"Timor-Leste":	("2002-09-27", "9999-12-31"),
 		"Togo": 	("1945", "9999-12-31"),
		"Tonga": 	("1945", "9999-12-31"),
		"Trinidad and Tobago": 	("1945", "9999-12-31"),
		"Tunisia": 	("1945", "9999-12-31"),
		"Turkey": 	("1945", "9999-12-31"),
		"Turkmenistan": 	("1945", "9999-12-31"),
		"Tuvalu": 	("2000-09-05", "9999-12-31"),
		"Uganda": 	("1945", "9999-12-31"),
		"Ukraine": 	("1945", "9999-12-31"),
		"United Arab Emirates": 	("1945", "9999-12-31"),
		"United Kingdom": 	("1945", "9999-12-31"),
		"United Republic of Tanzania": 	("1945", "9999-12-31"),
		"United States of America": 	("1945", "9999-12-31"),
		"Uruguay": 	("1945", "9999-12-31"),
		"Uzbekistan": 	("1945", "9999-12-31"),
		"Vanuatu": 	("1945", "9999-12-31"),
		"Venezuela": 	("1945", "9999-12-31"),
		"Viet Nam": 	("1945", "9999-12-31"),
		"Yemen": 	("1945", "9999-12-31"),
		"Yugoslavia": 	("1945", "2003"),
		"Zambia": 	("1945", "9999-12-31"),
		"Zimbabwe": 	("1945", "9999-12-31"),
		"The former Yugoslav Republic of Macedonia": 	("1945", "9999-12-31"),
				}

nationmapping = {
		"United Kingdom of Great Britain and Northern Ireland":"United Kingdom",
		"Cote d'Ivoire":"C�te d'Ivoire",
		"the former Yugoslav Republic of Macedonia":"The former Yugoslav Republic of Macedonia",
		"Syrian Arab Republic":"Syria",
		"Libyan Arab Jamahiriya":"Libya",
		"Iran (Islamic Republic of)":"Iran",
		"Islamic Republic of Iran":"Iran",
		"Serbia and Montenegro":"Serbia",
		"Venezuela (Bolivarian Republic of)":"Venezuela",
		"Libyan Arab amahiriya":"Libya",
		"hilippines":"Philippines",
		"nited Republic of Tanzania":"United Republic of Tanzania",
		"of Great Britain and Northern Ireland":"INVALID",
		"(Islamic Republic of)":"INVALID",
				}

nonnations = [	"European Community",
				"Palestine", 
				"Holy See",
				"International Federation of Red Cross and Red Crescent Societies",
				"General Assembly Affairs Branch",
				"Deputy Secretary-General", 
				"Conference of Non-Governmental Organizations in Consultative Relationship with the United Nations", 
			 ]


nationswithoutspaces = {}
for nation in nationdates:
	if re.search(" ", nation):
		nationswithoutspaces[re.sub(" ", "", nation)] = nation


# deals with problem that sometimes the spaces between characters are added
def FixNationName(lnation, sdate):
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
		print lnation, dr
		assert False
	return lnation

def GenerateNationsVoteList(vlfavour, vlagainst, vlabstain, sdate):
	nationvotes = { }
	for nation, dr in nationdates.iteritems():
		if dr[0] <= sdate < dr[1]:
			nationvotes[nation] = "absent"
	#print "\n\n\n"
	for vn in vlfavour:
		if nationvotes[vn] != "absent":
			print vn
			assert False
		nationvotes[vn] = "favour"
	for vn in vlagainst:
		assert nationvotes[vn] == "absent"
		nationvotes[vn] = "against"
	for vn in vlabstain:
		assert nationvotes[vn] == "absent"
		nationvotes[vn] = "abstain"
	return nationvotes, sorted([nation  for nation, vote in nationvotes.iteritems()  if vote == "absent"])



