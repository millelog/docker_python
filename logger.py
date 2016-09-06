from datetime import datetime

def log(string):
        with open("/var/docker/log.txt", "a") as log:
                log.write(str(datetime.now())+"  :  "+string+"\n")
