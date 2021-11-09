#!/bin/bash

cd  
cd /home/tit/AI/Qrcode

# while true
# do
# 	wget -q --tries=10 --timeout=20 --spider http://google.com
# 	if [[ $? -eq 0 ]]; then
# 				# notify-send "You connect  successful!" -t 3000
# 			echo "Online"
# 		break
# 	else
# 		echo "Offline"
# 		notify-send "Khong co internet " -t 1
# 	fi
# done
# sleep 1
while true
do
	if [ -c /dev/video0 ]; then
		echo  "webcam video 0 connected"
		break
	elif [ -c /dev/video1 ]; then
		echo  "webcam video 1 connected"
		break
	else
		echo "No camera"
		notify-send "No Camera" -t 1
		sleep 1
	fi
done
sleep 1

# while true
# do
# 	if [ -c /dev/ttyUSB0 ];
# 	then
# 		echo  "Arduino  connected"
# 		break
# 	elif [ -c /dev/ttyUSB1 ]; 
# 	then
# 		echo  "Arduino  connect"
# 		break
# 	elif [ -c /dev/ttyACM0 ]; 
# 	then
# 		echo  "Arduino connect"
# 		break
# 	elif [ -c /dev/ttyACM1 ]; 
# 	then
# 		echo  "Arduino connect"
# 		break
# 	else
# 		echo "No arduino"
# 		notify-send "No arduino" -t 1
# 		sleep 1
# 	fi
# done
# sleep 1

# sudo -S <<< 2020 apt-get update
cd /home/tit/AI/Qrcode/
python3 1_Ur.py
