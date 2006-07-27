import os
import re

countryvotes = { }

def SingleParaProcess(tlc):

	# glue together the words of the paragraph
	tlc.paratext = " ".join([txl.ltext  for txl in tlc.txls])
	tlc.paraembed = tlc.bindent and ("\t<blockquote>", "</blockquote>\n") or ("<p>", "</p>\n")

	tlc.recvote = ""
	for rvs in ["<i>In (fa)vour:</i>", "<i>(Ag)ainst:?</i>", "<i>(Ab)staining:</i>"]:
		m = re.match(rvs, tlc.paratext)
		if m:
			tlc.recvote = m.group(1)
			tlc.votelist = [ c.strip()  for c in re.split(",", tlc.paratext[m.end(0):])  if not re.match("\s*$|\s*None\s*$", c) ]
			break
	if tlc.recvote:
		for v in tlc.votelist:
			countryvotes.setdefault(v, {"fa":0, "Ag":0, "Ab":0})[tlc.recvote] += 1
		print tlc.recvote, len(tlc.votelist)
#	<blockquote><i>A recorded vote was taken.</i></blockquote>
#	<blockquote><i>In favour:</i> Algeria, Andorra, Argentina, Armenia, Australia, Austria, Azerbaijan, Bahrain, Bangladesh, Belarus, Belgium, Brazil, Brunei Darussalam, Bulgaria, Burkina Faso, Cameroon, Canada, Cape Verde, Chad, Chile, Colombia, Costa Rica, Côte d'Ivoire, Cuba, Cyprus, Czech Republic, Denmark, Djibouti, Dominican Republic, Ecuador, Egypt, El Salvador, Estonia, Ethiopia, Finland, France, Georgia, Germany, Ghana, Greece, Guinea, Guinea-Bissau, Guyana, Hungary, Indonesia, Iran (Islamic Republic of), Ireland, Israel, Italy, Jamaica, Japan, Kazakhstan, Kuwait, Latvia, Libyan Arab Jamahiriya, Liechtenstein, Lithuania, Luxembourg, Malaysia, Maldives, Mali, Malta, Mauritius, Mexico, Micronesia (Federated States of), Monaco, Mongolia, Morocco, Mozambique, Myanmar, Namibia, Netherlands, New Zealand, Nicaragua, Niger, Norway, Oman, Paraguay, Peru, Philippines, Poland, Portugal, Qatar, Republic of Korea, Republic of Moldova, Romania, San Marino, Saudi Arabia, Senegal, Singapore, Slovakia, Slovenia, South Africa, Spain, Sri Lanka, Sudan, Suriname, Swaziland, Sweden, Thailand, the former Yugoslav Republic of Macedonia, Togo, Tunisia, Turkey, Ukraine, United Arab Emirates, United Kingdom of Great Britain and Northern Ireland, United Republic of Tanzania, United States of America, Uruguay, Vanuatu, Venezuela, Yemen</blockquote>
#	<blockquote><i>Against:</i> Democratic People's Republic of Korea</blockquote>
#	<blockquote><i>Abstaining:</i> Bhutan, Botswana, China, India, Lao People's Democratic Republic, Pakistan, Syrian Arab Republic, Viet Nam</blockquote>

