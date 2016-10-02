import RPi.GPIO as GPIO
import time
import subprocess
import os

# Инициализация GPIO
GPIO_PIR = 21
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIR, GPIO.IN)

calibration_time = 10 # Время на калибровку датчика
lockLow = True # Флаг, который необходим для первоначального фиксирования состояния
# "движения нет", а также для дальнейшей проверки, что обнаружено новое движение
pause = 3
lowIn = 0
takeLowTime = False
is_guard_on = False
timer = 0

for i in range(calibration_time):
    print("Calibration")
    time.sleep(1)
print("Calibration OK")
time.sleep(0.05)

pid = str(os.getpid())
pidfile = "/tmp/PIR.pid"
with open(pidfile, 'w') as file:
    file.write(pid)
    file.close()
try:
  while(True):
    if(GPIO.input(GPIO_PIR) == True):
            if(lockLow):
                lockLow = False
                print("Motion detected")
                time.sleep(0.05)
            takeLowTime = True
    if(GPIO.input(GPIO_PIR) == False):
           if(takeLowTime):
              lowIn = time.time()
              takeLowTime = False
           if(not lockLow and time.time() - lowIn > pause):
                 lockLow = True
                 print("Motion finished")
                 time.sleep(0.05)
finally:
    os.unlink(pidfile)
 
    


"""while(True):
    try:
        if(is_guard_on):
                if(time.time() - timer < 300):
                    print(time.time() - timer)
                    continue
                else:
                    is_guard_on = False
                    print("Reset")
        if(GPIO.input(GPIO_PIR) == False): continue
        if(GPIO.input(GPIO_PIR) == True):
            print("Motion")
            if(not is_guard_on):
               print("Motion detected")
               #subprocess.Popen('python3 ./stream-and-snapshot.py', shell = True)
               timer = time.time()
               is_guard_on = True
        time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted")
        GPIO.cleanup()  """


"""if(GPIO.input(GPIO_PIR) == True):
            if(lockLow):
                lockLow = False
                print("Motion detected")
                #time.sleep(0.05)
            takeLowTime = True
    if(GPIO.input(GPIO_PIR) == False):
           if(takeLowTime):
              lowIn = time.time()
              takeLowTime = False
           if(not lockLow and time.time() - lowIn > pause):
                 lockLow = True
                 print("Motion finished")
                 #time.sleep(0.05)"""
""" try:
        print(GPIO.input(GPIO_PIR))
        #time.sleep(0.1)
    except KeyboardInterrupt:
        print("Interrupted")
        GPIO.cleanup()"""
