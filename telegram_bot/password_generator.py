#!/usr/bin/env python3
import random
import string
import configparser

#Creating a config parser to change the contents of config file
cp = configparser.RawConfigParser()
cp.read('/home/pi/RaspberryKiosk/telegram_bot/settings.cfg')
adj = ['happy', 'pretty', 'funny', 'shiny', 'beautiful', 'wonderful', 'amazing', 'stupendous', 'frisky', 'jolly']
noun = ['sun', 'day', 'pizza', 'friend', 'cat', 'dog', 'life', 'future', 'world', 'game']
#Generating a string of 8 symbols consisting of upper and lowercase characters and digits to use as a password
#token = "".join(random.choice(string.ascii_lowercase + string.digits))
token = random.choice(adj) + random.choice(noun)
#Setting the newly generated password
cp.set('AUTH', 'USR_PASSWD', token)
#Writing the password into config file
with open('/home/pi/RaspberryKiosk/telegram_bot/settings.cfg', 'w') as configfile:
    cp.write(configfile);
    
