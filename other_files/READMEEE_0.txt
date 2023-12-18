
FILE LOCATIONS:

1.  move the full Timer folder to the desktop

2.  copy the pi4_pi5_timer.sh file to the desktop

3.  make sure the bash file is pointing to the correct folder for the python file



AUTOSTART:

1.  create a file called timer.desktop in the other_files folder

2.  contents of timer.desktop file :

[Desktop Entry]
Name=PiTimer
Exec=/home/timer3/Desktop/pi4_pi5_timer.sh

MAKE SURE THE FULL PATH INCLUDING THE COMPUTER'S NAME IS IN THE Exec= path

3.  copy the timer.desktop file that you just created to the autostart directory:

sudo cp ~/Desktop/other_files/timer.desktop /etc/xdg/autostart/



LOCATION:

1.  create a sunrise sunset file like Tucson-Sunrise-Sunset.yml or SF-Sunrise-Sunset.yml

2.  put the full name of the file in a file called location.txt



