import sys
import subprocess

if __name__ == "__main__":
    subprocess.call('avconv -r 5 -i %s/photo%%d.jpg -r 5 -vcodec mjpeg /home/pi/RaspberryKiosk/guard/timelapse/%s.avi' % (sys.argv[1], sys.argv[2]), shell = True)
    subprocess.call('rm -rf %s' % sys.argv[1], shell=True)
