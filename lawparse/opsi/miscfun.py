import os

# starting point for directories
actdir = "acts"
actdirhtml = os.path.join(actdir, "html")

if not os.path.isdir(actdirhtml):
	os.mkdir(actdirhtml)



