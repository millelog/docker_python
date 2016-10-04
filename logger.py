<<<<<<< HEAD
from datetime import datetime

def log(string):
	with open("/var/docker/log.txt", "a") as log:
		log.write(str(datetime.now())+"  :  "+string+"\n")
=======
from datetime import datetime

def log(string):
        with open("/var/docker/log.txt", "a") as log:
                log.write(str(datetime.now())+"  :  "+string+"\n")
>>>>>>> 083ac187920a7733c37f36ae876abec2c223698d
