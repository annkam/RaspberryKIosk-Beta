# Usage:
# ${scroll [length] /path/to/script/rss-ticker.sh}
#
# Usage Example
# $scroll 100{${execi 300 /home/youruser/scripts/rss-ticker.sh}}

 

#RSS Setup
URI=https://lenta.ru/rss #URI of RSS Feed
LINE=1 #Number of headline

#Environment Setup
EXEC="curl -s" 

#Loading Feeds
feed1=$($EXEC $URI | grep title | head -n $(($LINE + 2)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed2=$($EXEC $URI | grep title | head -n $(($LINE + 3)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed3=$($EXEC $URI | grep title | head -n $(($LINE + 4)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed4=$($EXEC $URI | grep title | head -n $(($LINE + 5)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed5=$($EXEC $URI | grep title | head -n $(($LINE + 6)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed6=$($EXEC $URI | grep title | head -n $(($LINE + 7)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed7=$($EXEC $URI | grep title | head -n $(($LINE + 8)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed8=$($EXEC $URI | grep title | head -n $(($LINE + 9)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed9=$($EXEC $URI | grep title | head -n $(($LINE + 10)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))
feed10=$($EXEC $URI | grep title | head -n $(($LINE + 11)) | sed 's/<[^>]*>//g' | tail -n $(($LINE)))

#Work Start
echo -n $feed1. $feed2. $feed3. $feed4. $feed5. $feed6. $feed7. $feed8. $feed9. $feed10. > /home/pi/RaspberryKiosk/mediaplayer/t.txt
