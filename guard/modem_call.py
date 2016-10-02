#!/usr/bin/env python2

import serial
import time
import ConfigParser
import subprocess

cp = ConfigParser.ConfigParser()
cp.read('/home/pi/RaspberryKiosk/telegram_bot/settings.cfg');

def connect():
   try:
      sp = serial.Serial(port = '/dev/ttyUSB0',
                   baudrate=115200,
                   bytesize=serial.EIGHTBITS,
                   parity=serial.PARITY_NONE,
                   stopbits=serial.STOPBITS_ONE,
                   timeout = 1)
      return sp
   except:
      print('cant open')
      return 0
def call(sp):
   count = 0
   sp.write('ATD+79139492078;\r\n')
   time.sleep(1)
   while(True):
       try:
          sp.write('AT+CLCC\r\n')
          ans = sp.readline()
          if(len(ans) > 20):
              count = 0
              if(ans[11] == '0'):
                  time.sleep(0.1)
                  sp.write('AT+CHUP\r\n')
                  return 1
          else:
             count = count + 1
             if(count > 40):
                print('error')
                return 0
       except KeyboardInterrupt:  
          sp.close()
       except:
           sp.close()
           return 0

def send_sms(sp, text):
   sp.write('AT+CMGF=1\r\n')
   time.sleep(0.1)
   sp.write('AT+CMGS="+79139492078"\r\n')
   time.sleep(0.1)
   sp.write(text)
   time.sleep(0.1)
   sp.write(chr(26))
   time.sleep(0.1)
   sp.write('AT+CMGF=0\r\n')

if __name__ == "__main__":
    args = ['/home/pi/3g/sakis3g', '--sudo', '--console', 'disconnect']
    result = 0
    sp = 0
    while(sp == 0):
       subprocess.call(args)
       sp = connect()
    while(result == 0):
       result = call(sp)
    addr = cp.get('ADDR', 'TRANSLATION1_ADDR')
    send_sms(sp, addr)
    sp.close()
    
