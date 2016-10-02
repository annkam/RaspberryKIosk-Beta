#!/usr/bin/env python3
#! coding: utf-8

import subprocess
import re
import os
from bs4 import BeautifulSoup, Tag

uptime = subprocess.check_output('uptime -p', shell = True).decode("utf-8")
uptime = re.sub(r'up ', r'', uptime)
mem = re.split(r' ', subprocess.check_output('free -o -h', shell = True).decode("utf-8"))
ds = re.split(r' ', subprocess.check_output('df -h', shell = True).decode("utf-8"))
memCached  = re.sub(r'M\nSwap:', r'', mem[87])
memTotal = re.sub(r'M', r'', mem[51])
memUsed = re.sub(r'M', r'', mem[58])
memUsed = int(memUsed) - int(memCached)
if(os.path.exists('/tmp/telegram.pid')):
    tbot = "online"
else:
    tbot = "offline"
if(os.path.exists('/tmp/PID.pid')):
    sensors = "online"
else:
    sensors = "offline"
with open('/home/www/index.html','r+') as html_file:
   soup = BeautifulSoup(html_file, 'html5lib')
   tag = soup.find("span", { "class" : "uptime" })
   tag.string = uptime
   tag = soup.find("span", { "class" : "tbot" })
   tag.string = tbot
   tag = soup.find("span", { "class" : "sensors" })
   tag.string = sensors
   tag = soup.find("span", { "class" : "mem-used" })
   tag.string = str(memUsed)
   tag = soup.find("span", { "class" : "mem-total" })
   tag.string = memTotal
   tag = soup.find("span", { "class" : "ds-available" })
   tag.string = ds[24]
   tag = soup.find("span", { "class" : "ds-total" })
   tag.string = ds[20]
   html_file.seek(0,0)
   html_file.write(soup.prettify())

