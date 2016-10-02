# coding: utf-8
import requests
import time
import subprocess
import os
import logging
import urllib
import configparser
import fileinput



# Создание фильтра, чтобы избавиться от множественных HTTP запросов в логах
class RequestFilter(logging.Filter):
   def filter(self, record):
      return not "HTTPS" in record.getMessage()
   
# Создание парсера файла конфигурации бота  
cp = configparser.ConfigParser()
cp.read('settings.cfg')

# Создание логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('log.log')# Логи записываются в указанный файл
formatter = logging.Formatter(u'%(levelname)- 8s[%(asctime)s] %(message)s')
fh.setFormatter(formatter)
fh.addFilter(RequestFilter())
logger.addHandler(fh)

requests.packages.urllib3.disable_warnings()  # Подавление InsecureRequestWarning 

ADMIN_ID = int(cp.get('BotAPI', 'ADMIN_ID'))  # ID супер-юзера. Только он может запрашивать выполнение команд в любое время суток без авторизации
URL = cp.get('BotAPI', 'URL')  # Адрес HTTP Bot API
TOKEN = cp.get('BotAPI', 'TOKEN')  # Токен бота
offset = 0  # ID последнего обновления
stream1_status = False # флаг для проверки статуса стрима
stream2_status = False

"""Метод проверяет наличие новых команд для бота и вызывает метод, обрабатывающий команды,
но только после проверки прав отправителя"""
def check_updates():
    global offset
    data = {'offset': offset + 1, 'limit': 5, 'timeout': 0}  # Формирование параметров запроса

    try:
        request = requests.post(URL + TOKEN + '/getUpdates', data=data)  # Отправка запроса к Bot API
    except:
        logger.error(u'Error getting updates')
        return False  # 

    if not request.status_code == 200: return False  # Проверка ответа сервера
    if not request.json()['ok']: return False  # Проверка успешного ответа Bot API
    for update in request.json()['result']:  
        offset = update['update_id']  # Извлечение ID сообщения
        # Если сообщение пустое или не содержит текста, оно отбрасывается
        if not 'message' in update or not 'text' in update['message']:
            logger.error(u'Unknown update: %s' % update) 
            continue
        from_id = update['message']['chat']['id']  # Извлечение ID отправителя
        name = update['message']['chat']['first_name']  # Извлечение имени отправителя
        message = update['message']['text']  # Извлечение текста сообщения
        parameters = (offset, name, from_id, message)
        logger.info(u'Message (id%s) from %s (id%s): "%s"' % parameters)
        if(from_id == ADMIN_ID): # Если отправитель - супер-юзер, то его команда выполняется сразу же
           parameters = (offset, name, from_id, message, 'admin')
           run_command(*parameters)
        else: 
           rights = check_rights(from_id) # В противном случае вызывается метод, проверяющий права пользователя
           if(rights == 'error'):
              send_text(from_id, 'Извините, но во время запроса к серверу произошла непредвиденная ошибка. Попробуйте снова воспользоваться ботом через несколько секунд.')
           elif(rights == 'none'):
               send_text(from_id, 'Извините, но вы ввели неправильный пароль или же истекли 60 секунд ожидания вашего ответа. Попробуйте воспользоваться ботом еще раз.')
           else:
               parameters = (offset, name, from_id, message, rights)
               run_command(*parameters)

"""Метод проверяет, находится ли отправитель в списке авторизованных
пользователей и возвращает строку, описывающие его права, если отправитель в
списке, в противном случае высылается запрос пароля"""
def check_rights(user_id):
   auth_list = open('authorized.txt')
   for line in auth_list:
      if(line.startswith(str(user_id))):
         if(line.endswith('admin\n')):
            return 'admin'
         else:
            return 'user'
   rights = ask_password(user_id)
   return rights

"""Метод высылает пользователю сообщение с запросом пароля и ждёт ответа в течение 60 секунд"""
def ask_password(user_id):
   global offset
   data = {'offset': offset + 1, 'limit': 5, 'timeout': 0}  
   send_text(user_id, 'Вы не авторизованы. Пожалуйста, введите пароль в течение 60 секунд.')
   #time.sleep(int(cp.get('VAR','INTERVAL'))*12) # Ожидание в течение 20 секунд
   # Далее процедура, аналогичная функции check_updates()
   for i in range(0, 12):
      time.sleep(int(cp.get('VAR', 'interval')))
      try:
         request = requests.post(URL + TOKEN + '/getUpdates', data=data)
      except:
         logger.error(u'Error getting updates for password')
         return 'error'
      if not request.status_code == 200:
         return 'error'
      if not request.json()['ok']:
         return 'error'
      for update in request.json()['result']:  
              offset = update['update_id']  
           
              if not 'message' in update or not 'text' in update['message']:
                  logger.error(u'Unknown update: %s' % update)  
                  continue
              from_id = update['message']['chat']['id']  
              name = update['message']['chat']['first_name']  
              message = update['message']['text']  
              parameters = (offset, name, from_id, message)
              logger.info(u'Message (id%s) from %s (id%s): "%s"' % parameters)
              if(from_id != user_id): # Если ID отправителя принадлежит не пользователю, от которого ожидается введение пароля, его просят подождать
                  send_text(from_id, 'В данный момент бот занят. Пожалуйста, попробуйте позже')
                  continue # Продолжение проверки поступивших сообщений
              else: # Далее проверяется, какой пароль был введен юзером
                  if(message == cp.get('AUTH', 'adm_passwd')): # Присвоение прав администратора
                     auth = open('authorized.txt', 'a')
                     auth.write('%s=admin\n' % user_id)
                     auth.close()
                     send_text(user_id, 'Вы авторизованы как администратор на один час.')
                     return 'admin'
                  elif(message == cp.get('AUTH', 'usr_passwd')): #Присвоение прав пользователя
                     auth = open('authorized.txt', 'a')
                     auth.write('%s=user\n' % user_id)
                     auth.close()
                     send_text(user_id, 'Вы авторизованы как пользователь на один час.')
                     return 'user'
                  else: return 'none' # Если пароль неправильный, то пользователю не присваивается никаких прав
   return 'none'; # Если пользователь ничего не отправил в течение 20 секунд, ему присваиваеется никаких прав
    
#Метод обрабатывает команды пользователя и вызывает соответствующие им методы
def run_command(offset, name, from_id, cmd, rights):
    global led_status
    global stream1_status
    global stream2_status
    if cmd == '/start':
        if(rights == 'admin'):
            send_text(from_id, 'Привет, я RaspiCam Bot. Вы авторизованы как администратор. Чтобы получить список доступных команд, введите /help')
        else:
            send_text(from_id, 'Привет, я RaspiCam Bot. Вы авторизованы как администратор. Чтобы получить список доступных команд, введите /help')

    elif cmd == '/help':
        if(rights == 'admin'):
            send_text(from_id,
"""/photo - получить фото с обеих камер\n
/photo1 или /photo2 - получить фото с одной из камер\n
/stream - запустить трансляцию с обеих камер\n
/stream1 or /stream2 - запустить трансляцию видео с одной из камер\n
/stop_stream - остановить трансляцию видео с камер\n
/password - получить текущий пароль пользователя\n
/logout - завершение сессии(отмена авторизации)\n
Вы также можете получать снимки с любой из камер даже во время трансляции видео""")
        else:
            send_text(from_id,
 """/photo - получить фото с обеих камер\n
/photo1 или /photo2 - получить фото с одной из камер\n
/logout - завершение сессии(отмена авторизации)""")

    elif cmd == '/photo':
        # Иногда камера не доступна с первой попытки,
        # поэтому для каждой камеры предоставляется две попытки сделать фото
       if (make_photo(offset, 0) or make_photo(offset, 0)) and (make_photo(offset, 1) or make_photo(offset, 1)):
            # Пользователь уведомляется о загрузке фото
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_photo(from_id, offset, 0)  
            send_photo(from_id, offset, 1)
            # Проверка, не запущена ли трансляция с какой-либо камеры.
            # В зависимости от результата, высылается либо фото, либо снэпшот с трансляции.
       elif stream1_status and stream2_status:
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_snapshot(cp.get('ADDR', 'TRANSLATION1_ADDR') + '/?action=snapshot.jpg',from_id)
            send_snapshot(cp.get('ADDR', 'TRANSLATION2_ADDR')+ '/?action=snapshot.jpg',from_id)
       elif stream1_status:
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_snapshot(cp.get('ADDR', 'TRANSLATION1_ADDR')+ '/?action=snapshot.jpg', from_id)
            make_photo(offset, 1)
            send_photo(from_id, offset, 1)
       elif stream2_status:
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_snapshot(cp.get('ADDR', 'TRANSLATION2_ADDR')+ '/?action=snapshot.jpg', from_id)
            make_photo(offset, 0)
            send_photo(from_id, offset, 0)
       else: # Если что-то не получилось
            send_text(from_id, 'Произошла ошибка')  # Уведомление пользователя о том, что произошла ошибка
            logger.error(u'Error sending a photo to %s - id%s' % (name, from_id))
    elif cmd == '/photo1':
        if make_photo(offset, 0):
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_photo(from_id, offset, 0)
        elif stream1_status:
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_snapshot(cp.get('ADDR', 'TRANSLATION1_ADDR') + '/?action=snapshot.jpg', from_id)
        else:
            send_text(from_id, 'Произошла ошибка')
            logger.error(u'Error sending a photo to %s - id %s' % (name, from_id))
    elif cmd == '/photo2':
        if make_photo(offset, 1):
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_photo(from_id, offset, 1)
        elif stream2_status:
            requests.post(URL + TOKEN + '/sendChatAction', data={'chat_id': from_id, 'action': 'upload_photo'})
            send_snapshot(cp.get('ADDR', 'TRANSLATION2_ADDR') + '/?action=snapshot.jpg', from_id)
        else:
            send_text(from_id, 'Произошла ошибка')
            logger.error(u'Error sending a photo to %s - id %s' % (name, from_id))
    elif cmd == '/logout':
        for line in fileinput.input('authorized.txt', inplace=True):
           if(line.startswith(str(from_id))):
              print(line.replace(line, ''))
           else: print(line)
        send_text(from_id, 'Вы больше не авторизованы')
    elif cmd.startswith("/run_msg"):
       msg = ' Сообщение от %s' % name + ': ' + cmd[9:]
       file = open('/home/pi/RaspberryKiosk/mediaplayer/t.txt', 'a')
       file.write(msg)
       file.close()
    else:
       if( rights == 'user'): send_text(from_id, 'Такой команды нет. Чтобы посмотреть список доступных команд, введите /help')
       elif(rights == 'admin'): # Если пользователь владеет правами администратора, ему доступны все команды
         if cmd == ('/stream'):
             os.popen('mjpg_streamer -i "/usr/lib/input_uvc.so -d /dev/video0 -y -r 640x480 -q 95 -f 15" -o "/usr/lib/output_http.so -p 3496"')
             os.popen('mjpg_streamer -i "/usr/lib/input_uvc.so -d /dev/video1 -y -r 640x480 -q 95 -f 15" -o "/usr/lib/output_http.so -p 3497"')
             stream1_status = True
             stream2_status = True
             send_text(from_id, 'Запущена трансляция видео с обеих камер')
         elif cmd == ('/stream1'):
             if(os.path.exists('/dev/video0')):
                os.popen('mjpg_streamer -i "/usr/lib/input_uvc.so -d /dev/video0 -y -r 640x480 -q 95 -f 15" -o "/usr/lib/output_http.so -p 3496"')
                stream1_status = True
                send_text(from_id, 'Запущена трансляция видео с камеры 1')
             else:
                logger.error(u'Camera 1 was not found')
                send_text(from_id, 'Ошибка: камера 1 не найдена.')
         elif cmd == ('/stream2'):
             if(os.path.exists('/dev/video1')):
                os.popen('mjpg_streamer -i "/usr/lib/input_uvc.so -d /dev/video1 -y -r 640x480 -q 95 -f 15" -o "/usr/lib/output_http.so -p 3497"')
                stream2_status = True
                send_text(from_id, 'Запущена трансляция видео с камеры 2')
             else:
                logger.error(u'Camera 2 was not found')
                send_text(from_id, 'Ошибка: камера 2 не найдена.')
         elif cmd == '/stop_stream':
             subprocess.call('killall mjpg_streamer', shell=True)
             stream1_status = False
             stream2_status = False
             send_text(from_id, 'Трансляция остановлена')
         elif cmd == '/password':
            cp.read('settings.cfg')
            send_text(from_id, cp.get('AUTH', 'usr_passwd'))
         else:
             send_text(from_id, 'Такой команды нет. Чтобы посмотреть список доступных команд, введите /help')
    
# Метод отправляет сообщение с текстом text пользователю
def send_text(chat_id, text):
    logger.info(u'Sending to %s: %s' % (chat_id, text))
    data = {'chat_id': chat_id, 'text': text}  
    request = requests.post(URL + TOKEN + '/sendMessage', data=data)  
    if not request.status_code == 200:  
        return False  
    return request.json()['ok']  

"""Метод получает фото с одной из камер в зависимости от переданного id камеры
и сохраняет его под именем id полученного от пользователя сообщения. Таким образом,
запросивший фото пользователь всегда будет получать свежее фото, а старые фото не будут
перезаписываться. Возвращается true or false в зависимости от успешности получения фото"""
def make_photo(photo_id, camera_id):
    photo_name = '/home/pi/RaspberryKiosk/telegram_bot/photo/cam%s/%s.jpg' % (camera_id, photo_id)  
    subprocess.call('fswebcam -q -r 1280x720 -d /dev/video%s %s' % (camera_id, photo_name), shell=True)  
    return os.path.exists(photo_name)  

"""Метод отправляет свежее фото пользователю"""
def send_photo(chat_id, photo_id, camera_id):
    data = {'chat_id': chat_id}  
    photo_name = '/home/pi/RaspberryKiosk//telegram_bot/photo/cam%s/%s.jpg' % (camera_id, photo_id)             
    if not os.path.exists(photo_name):
        logger.error(u'Photo %s by camera %s not found' % (photo_id, camera_id))  
        send_text(chat_id, 'Фото не найдено')
        return False
    files = {'photo': open(photo_name, 'rb')}
    request = requests.post(URL + TOKEN + '/sendPhoto', data=data, files=files)  
    return request.json()['ok']
   
"""Метод сохраняет и отправляет пользователю снэпшот с транслирующей видео камеры. Запрос формируется
с указанием логина и пароля, необходимых для прохождения авторизации"""
def send_snapshot(url, chat_id):
    data = {'chat_id': chat_id}
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(realm='MJPG-Streamer',
                          uri=url,
                          user='nicelight',
                          passwd='extraterrestrial')
    opener = urllib.request.build_opener(auth_handler)
    urllib.request.install_opener(opener)
    file = urllib.request.urlopen(url)
    contents = file.read()
    photo = open('photo/photo.jpg', 'wb')
    photo.write(contents)
    photo.close()
    files = {'photo': open('photo/photo.jpg', 'rb')}
    request = requests.post(URL + TOKEN + '/sendPhoto', data=data, files=files)
    return request.json()['ok']

if __name__ == "__main__":
    pid = str(os.getpid())
    pidfile = "/tmp/telegram.pid"
    with open(pidfile, 'w') as file:
      file.write(pid)
      file.close()
    try:
       while True:
            check_updates()
            time.sleep(int(cp.get('VAR','INTERVAL')))
    except KeyboardInterrupt:
       subprocess.call('killall mjpg_streamer', shell=True)
       logger.critical(u'Keyboard interrupt!')
    finally:
       os.unlink(pidfile)
            
