#!/usr/bin/env python3
# coding: utf-8
import subprocess
import urllib
import requests
import configparser
import time

cp = configparser.ConfigParser() # Адрес стрима извлекается из конфиг-файла бота
cp.read('/home/pi/RaspberryKiosk/telegram_bot/settings.cfg')
url = cp.get('ADDR', 'TRANSLATION1_ADDR')+ '/?action=snapshot.jpg' # Формируется ссылка из адреса стрима и пути к захвату снэпшота

auth_handler = urllib.request.HTTPBasicAuthHandler() # Хэндлер для окна авторизации стрима
auth_handler.add_password(realm='MJPG-Streamer',
                          uri=url,
                          user='nicelight',
                          passwd='extraterrestrial')
opener = urllib.request.build_opener(auth_handler)
urllib.request.install_opener(opener)

if __name__ == "__main__":
    # Сначала запускаем стрим
    subprocess.Popen('mjpg_streamer -i "/usr/lib/input_uvc.so -d /dev/video0 -y -r 640x480 -q 95 -f 10" -o "/usr/lib/output_http.so -p 3496 -w /home/pi/telegram_bot/stream/templates -c nicelight:extraterrestrial"', shell=True)
    #subprocess.Popen('python modem_call.py', shell=True) # Пора позвонить хозяину с модема и скинуть ссылку на стрим
    time.sleep(1) # Контрольная пауза (чтобы стрим наверняка успел начаться)
    current_time = time.strftime("%d-%m-%Y-%H-%M-%S")
    folder = '/home/pi/RaspberryKiosk/telegram_bot/photo/' + current_time  # Путь к новой директории, имя папки = текущие время и дата
    subprocess.call('mkdir %s' % folder, shell=True) # Создается новая директория, туда будут сохраняться снэпшоты
    start = time.time() # Фиксируется время начала выполнения следующей части кода
    i = 0 # Счетчик для формирования имени каждого следующего снэпшота в папке
    while(time.time() - start < 300): # Цикл на ~5 минут
        file = urllib.request.urlopen(url) # Получаем файл по ссылке
        contents = file.read() # Считываем содержимое
        photo = open('/home/pi/RaspberryKiosk/telegram_bot/photo/%s/photo%s.jpg' % (current_time, i), 'wb') # Создание нового файла
        photo.write(contents) # Содержимое файла по ссылке записывается в созданный файл
        photo.close()
        i = i + 1
        time.sleep(0.5) # Пауза, снэпшоты берутся 2 раза в секунду
    subprocess.call('killall mjpg_streamer', shell=True) # Выключение трансляции
    subprocess.Popen('python3 /home/pi/RaspberryKiosk/guard/timelapse/timelapse_launcher.py %s %s' % (folder, current_time), shell=True)
    
