import os

# starting point for directories
actdir = "acts"
actdirhtml = os.path.join(actdir, "html")
actdirxml= os.path.join(actdir, "xml")

if not os.path.isdir(actdirhtml):
	os.mkdir(actdirhtml)

if not os.path.isdir(actdirxml):
	os.mkdir(actdirxml)



