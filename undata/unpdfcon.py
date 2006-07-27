import os
import shutil
import re
import sys

for pl in os.listdir("."):
	if re.match("plenary", pl) and os.path.isdir(pl):
		for sd in os.listdir(pl):
			pdf = os.path.join(pl, sd)
			pdfdest = os.path.join("pdfxml", sd)
			shutil.copyfile(pdf, pdfdest)
			print pdfdest
			os.spawnl(os.P_WAIT, 'pdftohtml', 'pdftohtml', '-xml', pdfdest)
			os.remove(pdfdest)
print "done"

