#!/usr/bin/python

# Member states and former member states taken from 
# http://en.wikipedia.org/wiki/United_Nations_member_states
unstates = {
    "Afghanistan" : ["1946-11-19","9999-12-31"],
    "Albania" : ["1955-12-14","9999-12-31"],
    "Algeria" : ["1962-10-08","9999-12-31"],
    "Andorra" : ["1993-07-28","9999-12-31"],
    "Angola" : ["1976-12-01","9999-12-31"],
    "Antigua and Barbuda" : ["1981-11-11","9999-12-31"],
    "Argentina" : ["1945-10-24","9999-12-31"],
    "Armenia" : ["1992-03-02","9999-12-31"],
    "Australia" : ["1945-11-01","9999-12-31"],
    "Austria" : ["1955-12-14","9999-12-31"],
    "Azerbaijan" : ["1992-03-02","9999-12-31"],
    "Bahamas" : ["1973-09-18","9999-12-31"],
    "Bahrain" : ["1971-09-21","9999-12-31"],
    "Bangladesh" : ["1974-09-17","9999-12-31"],
    "Barbados" : ["1966-12-09","9999-12-31"],
    "Belarus" : ["1945-10-24","9999-12-31"],
    "Belgium" : ["1945-12-27","9999-12-31"],
    "Belize" : ["1981-09-25","9999-12-31"],
    "Benin" : ["1960-09-20","9999-12-31"],
    "Bhutan" : ["1971-09-21","9999-12-31"],
    "Bolivia" : ["1945-11-14","9999-12-31"],
    "Bosnia and Herzegovina" : ["1992-05-22","9999-12-31"],
    "Botswana" : ["1966-10-17","9999-12-31"],
    "Brazil" : ["1945-10-24","9999-12-31"],
    "Brunei" : ["1984-09-21","9999-12-31"],
    "Bulgaria" : ["1955-12-14","9999-12-31"],
    "Burkina Faso" : ["1960-09-20","9999-12-31"],
    "Burundi" : ["1962-09-18","9999-12-31"],
    "Cambodia" : ["1955-12-14","9999-12-31"],
    "Cameroon" : ["1960-09-20","9999-12-31"],
    "Canada" : ["1945-11-09","9999-12-31"],
    "Cape Verde" : ["1975-09-16","9999-12-31"],
    "Central African Republic" : ["1960-09-20","9999-12-31"],
    "Chad" : ["1960-09-20","9999-12-31"],
    "Chile" : ["1945-10-24","9999-12-31"],
    "China" : ["1945-10-24","9999-12-31"],
    "Colombia" : ["1945-11-05","9999-12-31"],
    "Comoros" : ["1975-11-12","9999-12-31"],
    "Congo" : ["1960-09-20","9999-12-31"],
    "Costa Rica" : ["1945-11-02","9999-12-31"],
    "Cote d'Ivoire" : ["1960-09-20","9999-12-31"],
    "Croatia" : ["1992-05-22","9999-12-31"],
    "Cuba" : ["1945-10-24","9999-12-31"],
    "Cyprus" : ["1960-09-20","9999-12-31"],
    "Czech Republic" : ["1993-01-19","9999-12-31"],
    "Democratic People's Republic of Korea" : ["1991-09-17","9999-12-31"],
    "Democratic Republic of the Congo" : ["1997-05-17","9999-12-31"],
    "Denmark" : ["1945-10-24","9999-12-31"],
    "Djibouti" : ["1977-09-20","9999-12-31"],
    "Dominica" : ["1978-12-18","9999-12-31"],
    "Dominican Republic" : ["1945-10-24","9999-12-31"],
    "Ecuador" : ["1945-12-21","9999-12-31"],
    "Egypt" : ["1945-10-24","9999-12-31"],
    "El Salvador" : ["1945-10-24","9999-12-31"],
    "Equatorial Guinea" : ["1968-11-12","9999-12-31"],
    "Eritrea" : ["1993-05-28","9999-12-31"],
    "Estonia" : ["1991-09-17","9999-12-31"],
    "Ethiopia" : ["1945-11-13","9999-12-31"],
    "Fiji" : ["1970-10-13","9999-12-31"],
    "Finland" : ["1955-12-14","9999-12-31"],
    "France" : ["1945-10-24","9999-12-31"],
    "Gabon" : ["1960-09-20","9999-12-31"],
    "Gambia" : ["1965-09-21","9999-12-31"],
    "Georgia" : ["1992-07-31","9999-12-31"],
    "Germany" : ["1973-09-18","9999-12-31"],
    "Ghana" : ["1957-03-08","9999-12-31"],
    "Greece" : ["1945-10-25","9999-12-31"],
    "Grenada" : ["1974-09-17","9999-12-31"],
    "Guatemala" : ["1945-11-21","9999-12-31"],
    "Guinea" : ["1958-12-12","9999-12-31"],
    "Guinea-Bissau" : ["1974-09-17","9999-12-31"],
    "Guyana" : ["1966-09-20","9999-12-31"],
    "Haiti" : ["1945-10-24","9999-12-31"],
    "Honduras" : ["1945-12-17","9999-12-31"],
    "Hungary" : ["1955-12-14","9999-12-31"],
    "Iceland" : ["1946-11-19","9999-12-31"],
    "India" : ["1945-10-30","9999-12-31"],
    "Indonesia" : ["1950-09-28","9999-12-31"],
    "Iran" : ["1945-10-24","9999-12-31"],
    "Iraq" : ["1945-12-21","9999-12-31"],
    "Ireland" : ["1955-12-14","9999-12-31"],
    "Israel" : ["1949-05-11","9999-12-31"],
    "Italy" : ["1955-12-14","9999-12-31"],
    "Jamaica" : ["1962-09-18","9999-12-31"],
    "Japan" : ["1956-12-18","9999-12-31"],
    "Jordan" : ["1955-12-14","9999-12-31"],
    "Kazakhstan" : ["1992-03-02","9999-12-31"],
    "Kenya" : ["1963-12-16","9999-12-31"],
    "Kiribati" : ["1999-09-14","9999-12-31"],
    "Kuwait" : ["1963-05-14","9999-12-31"],
    "Kyrgyzstan" : ["1992-03-02","9999-12-31"],
    "Laos" : ["1955-12-14","9999-12-31"],
    "Latvia" : ["1991-09-17","9999-12-31"],
    "Lebanon" : ["1945-10-24","9999-12-31"],
    "Lesotho" : ["1966-10-17","9999-12-31"],
    "Liberia" : ["1945-11-02","9999-12-31"],
    "Libya" : ["1955-12-14","9999-12-31"],
    "Liechtenstein" : ["1990-09-18","9999-12-31"],
    "Lithuania" : ["1991-09-17","9999-12-31"],
    "Luxembourg" : ["1945-10-24","9999-12-31"],
    "Madagascar" : ["1960-09-20","9999-12-31"],
    "Malawi" : ["1964-12-01","9999-12-31"],
    "Malaysia" : ["1957-09-17","9999-12-31"],
    "Maldives" : ["1965-09-21","9999-12-31"],
    "Mali" : ["1960-09-28","9999-12-31"],
    "Malta" : ["1964-12-01","9999-12-31"],
    "Marshall Islands" : ["1991-09-17","9999-12-31"],
    "Mauritania" : ["1961-10-27","9999-12-31"],
    "Mauritius" : ["1968-04-24","9999-12-31"],
    "Mexico" : ["1945-11-07","9999-12-31"],
    "Micronesia" : ["1991-09-17","9999-12-31"],
    "Moldova" : ["1992-03-02","9999-12-31"],
    "Monaco" : ["1993-05-28","9999-12-31"],
    "Mongolia" : ["1961-10-27","9999-12-31"],
    "Montenegro" : ["2006-06-28","9999-12-31"],
    "Morocco" : ["1956-11-12","9999-12-31"],
    "Mozambique" : ["1975-09-16","9999-12-31"],
    "Myanmar" : ["1948-04-19","9999-12-31"],
    "Namibia" : ["1990-04-23","9999-12-31"],
    "Nauru" : ["1999-09-14","9999-12-31"],
    "Nepal" : ["1955-12-14","9999-12-31"],
    "Netherlands" : ["1945-12-10","9999-12-31"],
    "New Zealand" : ["1945-10-24","9999-12-31"],
    "Nicaragua" : ["1945-10-24","9999-12-31"],
    "Niger" : ["1960-09-20","9999-12-31"],
    "Nigeria" : ["1960-10-07","9999-12-31"],
    "Norway" : ["1945-11-27","9999-12-31"],
    "Oman" : ["1971-10-07","9999-12-31"],
    "Pakistan" : ["1947-09-30","9999-12-31"],
    "Palau" : ["1994-12-15","9999-12-31"],
    "Panama" : ["1945-11-13","9999-12-31"],
    "Papua New Guinea" : ["1975-10-10","9999-12-31"],
    "Paraguay" : ["1945-10-24","9999-12-31"],
    "Peru" : ["1945-10-31","9999-12-31"],
    "Philippines" : ["1945-10-24","9999-12-31"],
    "Poland" : ["1945-10-24","9999-12-31"],
    "Portugal" : ["1955-12-14","9999-12-31"],
    "Qatar" : ["1971-09-21","9999-12-31"],
    "Republic of Korea" : ["1991-09-17","9999-12-31"],
    "Romania" : ["1955-12-14","9999-12-31"],
    "Russia" : ["1945-10-24","9999-12-31"],
    "Rwanda" : ["1962-09-18","9999-12-31"],
    "Saint Kitts and Nevis" : ["1983-09-23","9999-12-31"],
    "Saint Lucia" : ["1979-09-18","9999-12-31"],
    "Saint Vincent and the Grenadines" : ["1980-09-16","9999-12-31"],
    "Samoa" : ["1976-12-15","9999-12-31"],
    "San Marino" : ["1992-03-02","9999-12-31"],
    "Sao Tome and Principe" : ["1975-09-16","9999-12-31"],
    "Saudi Arabia" : ["1945-10-24","9999-12-31"],
    "Senegal" : ["1960-09-28","9999-12-31"],
    "Serbia" : ["2000-11-01","9999-12-31"],
    "Seychelles" : ["1976-09-21","9999-12-31"],
    "Sierra Leone" : ["1961-09-27","9999-12-31"],
    "Singapore" : ["1965-09-21","9999-12-31"],
    "Slovakia" : ["1993-01-19","9999-12-31"],
    "Slovenia" : ["1992-05-22","9999-12-31"],
    "Solomon Islands" : ["1978-09-19","9999-12-31"],
    "Somalia" : ["1960-09-20","9999-12-31"],
    "South Africa" : ["1945-11-07","9999-12-31"],
    "Spain" : ["1955-12-14","9999-12-31"],
    "Sri Lanka" : ["1955-12-14","9999-12-31"],
    "Sudan" : ["1956-11-12","9999-12-31"],
    "Suriname" : ["1975-12-04","9999-12-31"],
    "Swaziland" : ["1968-09-24","9999-12-31"],
    "Sweden" : ["1946-11-19","9999-12-31"],
    "Switzerland" : ["2002-09-10","9999-12-31"],
    "Syria" : ["1945-10-24","9999-12-31"],
    "Tajikistan" : ["1992-03-02","9999-12-31"],
    "Tanzania" : ["1961-12-14","9999-12-31"],
    "Thailand" : ["1946-12-16","9999-12-31"],
    "The former Yugoslav Republic of Macedonia" : ["1993-04-08","9999-12-31"],
    "Timor-Leste" : ["2002-09-27","9999-12-31"],
    "Togo" : ["1960-09-20","9999-12-31"],
    "Tonga" : ["1999-09-14","9999-12-31"],
    "Trinidad and Tobago" : ["1962-09-18","9999-12-31"],
    "Tunisia" : ["1956-11-12","9999-12-31"],
    "Turkey" : ["1945-10-24","9999-12-31"],
    "Turkmenistan" : ["1992-03-02","9999-12-31"],
    "Tuvalu" : ["2000-09-05","9999-12-31"],
    "Uganda" : ["1962-10-25","9999-12-31"],
    "Ukraine" : ["1945-10-24","9999-12-31"],
    "United Arab Emirates" : ["1971-12-09","9999-12-31"],
    "United Kingdom" : ["1945-10-24","9999-12-31"],
    "United States" : ["1945-10-24","9999-12-31"],
    "Uruguay" : ["1945-12-18","9999-12-31"],
    "Uzbekistan" : ["1992-03-02","9999-12-31"],
    "Vanuatu" : ["1981-09-15","9999-12-31"],
    "Venezuela" : ["1945-11-15","9999-12-31"],
    "Viet Nam" : ["1977-09-20","9999-12-31"],
    "Yemen" : ["1947-09-30","9999-12-31"],
    "Yugoslavia" : ["1945-10-24","2002-12-21"],
    "Zaire" : ["1960-09-20","1997-05-17"],
    "Zambia" : ["1964-12-01","9999-12-31"],
    "Zimbabwe" : ["1980-08-25","9999-12-31"],
}

# Data from GeoIP, taken from the source code for Debian package libgeoip1 1.3.17

GeoIP_country_code = [
"--","AP","EU","AD","AE","AF","AG","AI","AL","AM","AN","AO","AQ","AR","AS","AT","AU","AW","AZ","BA","BB","BD","BE","BF","BG","BH","BI","BJ","BM","BN","BO","BR","BS","BT","BV","BW","BY","BZ","CA","CC","CD","CF","CG","CH","CI","CK","CL","CM","CN","CO","CR","CU","CV","CX","CY","CZ","DE","DJ","DK","DM","DO","DZ","EC","EE","EG","EH","ER","ES","ET","FI","FJ","FK","FM","FO","FR","FX","GA","GB","GD","GE","GF","GH","GI","GL","GM","GN","GP","GQ","GR","GS","GT","GU","GW","GY","HK","HM","HN","HR","HT","HU","ID","IE","IL","IN","IO","IQ","IR","IS","IT","JM","JO","JP","KE","KG","KH","KI","KM","KN","KP","KR","KW","KY","KZ","LA","LB","LC","LI","LK","LR","LS","LT","LU","LV","LY","MA","MC","MD","MG","MH","MK","ML","MM","MN","MO","MP","MQ","MR","MS","MT","MU","MV","MW","MX","MY","MZ","NA","NC","NE","NF","NG","NI","NL","NO","NP","NR","NU","NZ","OM","PA","PE","PF","PG","PH","PK","PL","PM","PN","PR","PS","PT","PW","PY","QA","RE","RO","RU","RW","SA","SB","SC","SD","SE","SG","SH","SI","SJ","SK","SL","SM","SN","SO","SR","ST","SV","SY","SZ","TC","TD","TF","TG","TH","TJ","TK","TM","TN","TO","TP","TR","TT","TV","TW","TZ","UA","UG","UM","US","UY","UZ","VA","VC","VE","VG","VI","VN","VU","WF","WS","YE","YT","CS","ZA","ZM","ZR","ZW","A1","A2","O1"
]

GeoIP_country_code3 = [
"--","AP","EU","AND","ARE","AFG","ATG","AIA","ALB","ARM","ANT","AGO","AQ","ARG","ASM","AUT","AUS","ABW","AZE","BIH","BRB","BGD","BEL","BFA","BGR","BHR","BDI","BEN","BMU","BRN","BOL","BRA","BHS","BTN","BV","BWA","BLR","BLZ","CAN","CC","COD","CAF","COG","CHE","CIV","COK","CHL","CMR","CHN","COL","CRI","CUB","CPV","CX","CYP","CZE","DEU","DJI","DNK","DMA","DOM","DZA","ECU","EST","EGY","ESH","ERI","ESP","ETH","FIN","FJI","FLK","FSM","FRO","FRA","FX","GAB","GBR","GRD","GEO","GUF","GHA","GIB","GRL","GMB","GIN","GLP","GNQ","GRC","GS","GTM","GUM","GNB","GUY","HKG","HM","HND","HRV","HTI","HUN","IDN","IRL","ISR","IND","IO","IRQ","IRN","ISL","ITA","JAM","JOR","JPN","KEN","KGZ","KHM","KIR","COM","KNA","PRK","KOR","KWT","CYM","KAZ","LAO","LBN","LCA","LIE","LKA","LBR","LSO","LTU","LUX","LVA","LBY","MAR","MCO","MDA","MDG","MHL","MKD","MLI","MMR","MNG","MAC","MNP","MTQ","MRT","MSR","MLT","MUS","MDV","MWI","MEX","MYS","MOZ","NAM","NCL","NER","NFK","NGA","NIC","NLD","NOR","NPL","NRU","NIU","NZL","OMN","PAN","PER","PYF","PNG","PHL","PAK","POL","SPM","PCN","PRI","PSE","PRT","PLW","PRY","QAT","REU","ROU","RUS","RWA","SAU","SLB","SYC","SDN","SWE","SGP","SHN","SVN","SJM","SVK","SLE","SMR","SEN","SOM","SUR","STP","SLV","SYR","SWZ","TCA","TCD","TF","TGO","THA","TJK","TKL","TLS","TKM","TUN","TON","TUR","TTO","TUV","TWN","TZA","UKR","UGA","UM","USA","URY","UZB","VAT","VCT","VEN","VGB","VIR","VNM","VUT","WLF","WSM","YEM","YT","SCG","ZAF","ZMB","ZR","ZWE","A1","A2","O1"
]

GeoIP_country_name = [ "N/A","Asia/Pacific Region","Europe","Andorra","United Arab Emirates","Afghanistan","Antigua and Barbuda","Anguilla","Albania","Armenia","Netherlands Antilles","Angola","Antarctica","Argentina","American Samoa","Austria","Australia","Aruba","Azerbaijan","Bosnia and Herzegovina","Barbados","Bangladesh","Belgium","Burkina Faso","Bulgaria","Bahrain","Burundi","Benin","Bermuda","Brunei Darussalam","Bolivia","Brazil","Bahamas","Bhutan","Bouvet Island","Botswana","Belarus","Belize","Canada","Cocos (Keeling) Islands","Congo, The Democratic Republic of the","Central African Republic","Congo","Switzerland","Cote D'Ivoire","Cook Islands","Chile","Cameroon","China","Colombia","Costa Rica","Cuba","Cape Verde","Christmas Island","Cyprus","Czech Republic","Germany","Djibouti","Denmark","Dominica","Dominican Republic","Algeria","Ecuador","Estonia","Egypt","Western Sahara","Eritrea","Spain","Ethiopia","Finland","Fiji","Falkland Islands (Malvinas)","Micronesia, Federated States of","Faroe Islands","France","France, Metropolitan","Gabon","United Kingdom","Grenada","Georgia","French Guiana","Ghana","Gibraltar","Greenland","Gambia","Guinea","Guadeloupe","Equatorial Guinea","Greece","South Georgia and the South Sandwich Islands","Guatemala","Guam","Guinea-Bissau","Guyana","Hong Kong","Heard Island and McDonald Islands","Honduras","Croatia","Haiti","Hungary","Indonesia","Ireland","Israel","India","British Indian Ocean Territory","Iraq","Iran, Islamic Republic of","Iceland","Italy","Jamaica","Jordan","Japan","Kenya","Kyrgyzstan","Cambodia","Kiribati","Comoros","Saint Kitts and Nevis",
"Korea, Democratic People's Republic of","Korea, Republic of","Kuwait","Cayman Islands","Kazakhstan","Lao People's Democratic Republic","Lebanon","Saint Lucia","Liechtenstein","Sri Lanka","Liberia","Lesotho","Lithuania","Luxembourg","Latvia","Libyan Arab Jamahiriya","Morocco","Monaco","Moldova, Republic of","Madagascar","Marshall Islands","Macedonia","Mali","Myanmar","Mongolia","Macau","Northern Mariana Islands","Martinique","Mauritania","Montserrat","Malta","Mauritius","Maldives","Malawi","Mexico","Malaysia","Mozambique","Namibia","New Caledonia","Niger","Norfolk Island","Nigeria","Nicaragua","Netherlands","Norway","Nepal","Nauru","Niue","New Zealand","Oman","Panama","Peru","French Polynesia","Papua New Guinea","Philippines","Pakistan","Poland","Saint Pierre and Miquelon","Pitcairn Islands","Puerto Rico","Palestinian Territory","Portugal","Palau","Paraguay","Qatar","Reunion","Romania","Russian Federation","Rwanda","Saudi Arabia","Solomon Islands","Seychelles","Sudan","Sweden","Singapore","Saint Helena","Slovenia","Svalbard and Jan Mayen","Slovakia","Sierra Leone","San Marino","Senegal","Somalia","Suriname","Sao Tome and Principe","El Salvador","Syrian Arab Republic","Swaziland","Turks and Caicos Islands","Chad","French Southern Territories","Togo","Thailand","Tajikistan","Tokelau","Turkmenistan","Tunisia","Tonga","East Timor","Turkey","Trinidad and Tobago","Tuvalu","Taiwan","Tanzania, United Republic of","Ukraine","Uganda","United States Minor Outlying Islands","United States","Uruguay","Uzbekistan","Holy See (Vatican City State)","Saint Vincent and the Grenadines","Venezuela","Virgin Islands, British","Virgin Islands, U.S.","Vietnam","Vanuatu","Wallis and Futuna","Samoa","Yemen","Mayotte","Serbia and Montenegro","South Africa","Zambia","Zaire","Zimbabwe",
"Anonymous Proxy","Satellite Provider","Other"]

GeoIP_country_continent = ["--","AS","EU","EU","AS","AS","SA","SA","EU","AS","SA","AF","AN","SA","OC","EU","OC","SA","AS","EU","SA","AS","EU","AF","EU","AS","AF","AF","SA","AS","SA","SA","SA","AS","AF","AF","EU","SA","NA","AS","AF","AF","AF","EU","AF","OC","SA","AF","AS","SA","SA","SA","AF","AS","AS","EU","EU","AF","EU","SA","SA","AF","SA","EU","AF","AF","AF","EU","AF","EU","OC","SA","OC","EU","EU","EU","AF","EU","SA","AS","SA","AF","EU","SA","AF","AF","SA","AF","EU","SA","SA","OC","AF","SA","AS","AF","SA","EU","SA","EU","AS","EU","AS","AS","AS","AS","AS","EU","EU","SA","AS","AS","AF","AS","AS","OC","AF","SA","AS","AS","AS","SA","AS","AS","AS","SA","EU","AS","AF","AF","EU","EU","EU","AF","AF","EU","EU","AF","OC","EU","AF","AS","AS","AS","OC","SA","AF","SA","EU","AF","AS","AF","NA","AS","AF","AF","OC","AF","OC","AF","SA","EU","EU","AS","OC","OC","OC","AS","SA","SA","OC","OC","AS","AS","EU","SA","OC","SA","AS","EU","OC","SA","AS","AF","EU","AS","AF","AS","OC","AF","AF","EU","AS","AF","EU","EU","EU","AF","EU","AF","AF","SA","AF","SA","AS","AF","SA","AF","AF","AF","AS","AS","OC","AS","AF","OC","AS","AS","SA","OC","AS","AF","EU","AF","OC","NA","SA","AS","EU","SA","SA","SA","SA","AS","OC","OC","OC","AS","AF","EU","AF","AF","AF","AF"]

continent_names = {
    "AF" : "Africa",
    "AS" : "Asia / Middle East", 
    "EU" : "Europe",
    "NA" : "North America", 
    "OC" : "Oceana",
    "SA" : "South America",
}

# Process it

import sys
import csv
writer = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)

print "# THIS FILE IS AUTOGENERATED BY ./nationdatasucker.py EDIT THAT TO ALTER IT"
writer.writerow(["Name", "Date entered UN", "Date left UN", "Country code", "Country code (3 letter)", "Continent (GeoIP)" ])
for unname in unstates:
    # Get basic data
    date_from = unstates[unname][0]
    date_to = unstates[unname][1]

    # Look up more info in GeoIP list of countries
    iso2 = None
    iso3 = None
    continent = None
    geoip_name = unname

    if geoip_name == 'Tanzania':
        geoip_name = 'Tanzania, United Republic of'
    if geoip_name == 'Viet Nam':
        geoip_name = 'Vietnam'
    if geoip_name == 'Laos':
        geoip_name = "Lao People's Democratic Republic"
    if geoip_name == "Cote d'Ivoire":
        geoip_name = "Cote D'Ivoire"
    if geoip_name == "Republic of Korea":
        geoip_name = "Korea, Republic of"
    if geoip_name == "Democratic People's Republic of Korea":
        geoip_name = "Korea, Democratic People's Republic of"
    if geoip_name == "The former Yugoslav Republic of Macedonia":
        geoip_name = "Macedonia"
    if geoip_name == "Syria":
        geoip_name = "Syrian Arab Republic"
    if geoip_name == "Brunei":
        geoip_name = "Brunei Darussalam"
    if geoip_name == "Russia":
        geoip_name = "Russian Federation"
    if geoip_name == 'Libya':
        geoip_name = "Libyan Arab Jamahiriya"
    if geoip_name == 'Iran':
        geoip_name = "Iran, Islamic Republic of"
    if geoip_name == 'Moldova':
        geoip_name = "Moldova, Republic of"
    if geoip_name == 'Micronesia':
        geoip_name = "Micronesia, Federated States of"
    if geoip_name == 'Timor-Leste':
        geoip_name = "East Timor"
    if geoip_name == 'Timor-Leste':
        geoip_name = "East Timor"
    if geoip_name == 'Democratic Republic of the Congo':
        geoip_name = 'Congo, The Democratic Republic of the'

    if geoip_name in GeoIP_country_name:
        geoip_id = GeoIP_country_name.index(geoip_name)
        iso2 = GeoIP_country_code[geoip_id]
        iso3 = GeoIP_country_code3[geoip_id]
        continent = GeoIP_country_continent[geoip_id]
        continent_name = continent_names[continent]
    else:
        print >>sys.stderr, "country %s not in GeoIP" % geoip_name
    
    # Write out data
    writer.writerow([unname, date_from, date_to, iso2, iso3, continent_name])


