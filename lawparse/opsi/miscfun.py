import os

# starting point for directories
actdir = "acts"
actdirhtml = os.path.join(actdir, "html")
actdirxml = os.path.join(actdir, "xml")
sidir = "si"
sidirhtml = os.path.join(sidir, "html")
sidirxml = os.path.join(sidir, "xml") 

if not os.path.isdir(actdir):
	os.mkdir(actdir)

if not os.path.isdir(sidir):
	os.mkdir(sidir)

if not os.path.isdir(actdirhtml):
	os.mkdir(actdirhtml)

if not os.path.isdir(actdirxml):
	os.mkdir(actdirxml)

if not os.path.isdir(sidirhtml):
	os.mkdir(sidirhtml)

if not os.path.isdir(sidirxml):
	os.mkdir(sidirxml)



