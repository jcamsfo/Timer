# import necessary packages
from tkinter import *
from time import strftime
import time
import threading
from threading import Thread
import platform
import requests
import re
import os

outpins = [18,24]


## doesnt work with mac yet but not needed
def machine_is_Pi() -> bool:
    machine_type = platform.machine()
    print(machine_type)
    if (('x86_64' == machine_type) or ('AMD64' == machine_type)):
        print("Big Computer")
        return False  # PC
    else:
        print("Pi Computer")
        return True  # raspberry pi only
   
## returns 4 or 5 or -1   
def get_pi_model_number() -> int:
    with open('/proc/device-tree/model') as f:
        model = f.read()
        m_sub = re.search(r"\d", model)
        if m_sub:
            m_num = int( model[m_sub.start():m_sub.start()+1] )
            if(m_num== 4 ):
                return 4  
            elif(m_num == 5 ):
                return 5  
            else:
                return -1
        else:
            return -1
 
    
    
def Init_GPIO(model_in):
    global GPIO
    global outpins
    global pin_Array
    
    if(model_in== 4 ):
        import RPi.GPIO as GPIO
        print("Raspberry Pi Model 4 Detected")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for i in outpins :
            GPIO.setup(i, GPIO.OUT)

    elif(model_in== 5 ):
        import gpiod
        print("Raspberry Pi Model 5 Detected")
        chip = gpiod.Chip('gpiochip4', gpiod.Chip.OPEN_BY_NAME)
        pin_Array = [chip.get_line(outpins[0])  ]
        pin_Array[0].request(consumer="blinktest", type=gpiod.LINE_REQ_DIR_OUT)
        for i in range(1,len(outpins) ) :
            pin_Array.append( chip.get_line(outpins[i]) )
            pin_Array[i].request(consumer="blinktest", type=gpiod.LINE_REQ_DIR_OUT)
            
    else:
        print("No Raspberry Pi Detected")
    

def GPIO_Out(Pin_Pointer,Val):
    global GPIO
    global pin_Array
    if(pi_model== 4 ):
        GPIO.output(outpins[Pin_Pointer], Val)
    elif(pi_model== 5 ):
            pin_Array[Pin_Pointer].set_value(Val)



    
    
global wifi_status_x
wifi_status_x = 5

def is_internet_on(timeout):
    global wifi_status_x
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        wifi_status_x = 1
        return True
    except requests.ConnectionError:
        wifi_status_x = 0
        return False    
    

# do this once  get the sunrise sunset times
def get_sunrise_sunset_list():
    global file_to_read
    location_file_exists = os.path.isfile('location.txt') 
    if( location_file_exists ):
        file2= open('location.txt', 'r')
        Lines2 = file2.readlines()
        for line in Lines2:
            if line[0].isalnum():
                print(line)
                file_to_read = line
    else :
        file_to_read = 'Sunrise-Sunset.yml'
        
    file1 = open(file_to_read, 'r')  
    Lines = file1.readlines()
    countt = 0
    month_offset_list = [1,32,61,  92,122,153,  183,214,245,  275,306,336]
    for line in Lines:
        s = ''.join(ch for ch in line if ch.isalnum())
        if (s[0:1].isdigit()):
          #  Offset2 = 15
          #  x1 = (float(s[0:2]) - 1) * 30.2 + (float(s[2:4]))

            x1 = month_offset_list[ (int(s[0:2]) - 1) ] + (int(s[2:4])) - 1
            x2 = (int(s[4:6])) * 60 + (int(s[6:8]))
            x3 = (int(s[8:10])) * 60 + (int(s[10:12]))
            date_time_list[countt] = [x1, x2, x3]   
            countt = countt + 1
    if(location_file_exists):
        file2.close()
    file1.close()




# put the graphics up
def timeX(day_or_night):
    string = strftime('%H:%M:%S')
    if day_or_night == 1:
        string  += "  day"
    else:
        string += "  night"
    mark.config(text= string  )
    return 60 * int(strftime('%H')) + int(strftime('%M'))


# check daynight by comparing time to chart
def check_day_night(time_in, year_day_in):
    global wifi_status_x
    n = 0
    while date_time_list[n][0] < year_day_in:
        n = n + 1

    # Daylight Savings Time
    if time.localtime().tm_isdst != 0 :
        Offset_Hours = 1
    else:
        Offset_Hours = 0

    # start 15 minutes before sunrise and sunset which has to match Xilinx fade time
    day_night = (time_in > (date_time_list[n][1] + (Offset_Hours * 60) - 15)) and (time_in < (date_time_list[n][2] + (Offset_Hours * 60) - 15))

    print("file:  dayin rise set", int(date_time_list[n][0]), date_time_list[n][1]+ Offset_Hours, date_time_list[n][2]+ Offset_Hours)

    sunrise_minutes = int(60 * ((date_time_list[n][1] / 60) - int(date_time_list[n][1] / 60)))  
    sunrise_hours = int(((date_time_list[n][1] / 60)))

    # make 7:9  7:09 for time display
    if sunrise_minutes < 10 :
        added_0 = ":0"
    else:
        added_0 = ":"

    rise = "sun rise/set   " + str(sunrise_hours + Offset_Hours) + added_0 + str(sunrise_minutes)

    sunset_minutes = int(60 * ((date_time_list[n][2] / 60) - int(date_time_list[n][2] / 60)))
    sunset_hours = int(((date_time_list[n][2] / 60)))
    if wifi_status_x == 1:
        wifi_status = "wifi:on"
    elif wifi_status_x == 0:
        wifi_status = "wifi:off"
    else:
        wifi_status = "wifi:???"        

    if sunset_minutes < 10 :
        added_0 = ":0"
    else:
        added_0 = ":"

    set = str(sunset_hours + Offset_Hours) + added_0 + str(sunset_minutes) + "  " + wifi_status

    mark4.config(text=rise + "  " + set)
    mark5.config(text=file_to_read)

    return (day_night)


modeX = 0


def det_button_p():
    global modeX
    modeX = modeX + 1
    if modeX == 3:
        modeX = 0
    print("button_press")
    if modeX == 0:
        btn1['text'] = 'Automatic'
    elif modeX == 1:
        btn1['text'] = 'Daytime'
    else:
        btn1['text'] = 'Nighttime'


date_time_list = [[0 for c in range(3)] for r in range(53)]

get_sunrise_sunset_list()

root = Tk()
root.geometry("500x200")
root.resizable(0, 0)
root.title('Sculpture')

mark3 = Label(root, text='SCULPTURE TIMER', font='arial 20 bold')
mark3.pack(side=TOP)

mark4 = Label(root, font='arial 16 bold')
mark4.pack(side=BOTTOM)

mark5 = Label(root, font='arial 12 bold')
mark5.pack(side=BOTTOM, pady = 3)

btn1 = Button(root, text='Automatic', command=det_button_p)
btn1.pack(side='bottom', pady = 3)
# btn1.grid(padx=10, pady=10)


mark = Label(root,
             font=('calibri', 40, 'bold'),
             pady=30,
             foreground='black')

mark.pack(anchor='center')


enable_GPIO = machine_is_Pi()  
if(enable_GPIO): 
    pi_model = get_pi_model_number()   
    if(pi_model > 0):
        Init_GPIO(pi_model)
        

loop = 7
toggle = True
day_night = 0


## test GPIO
# ~ while True: 
    # ~ GPIO_Out(1,1)   #  outpin array #  0,1,2 ... , value
    # ~ GPIO_Out(1,0)  #   outpin array #  0,1,2 ... , value
    # ~ GPIO_Out(0,1)   #  outpin array #  0,1,2 ... , value
    # ~ GPIO_Out(0,0)  #   outpin array #  0,1,2 ... , value   
    
    
while True:
    time.sleep(1)
    current_local = time.localtime()
    time_in_minutes = timeX(day_night)
    root.update()   

    ## need to thread this because it takes a long time and the clock stutters
    if (loop == 7):
        t = Thread(target=is_internet_on, args=(2,))
        t.start()
    
    if (loop == 10):
        day_night = check_day_night(time_in_minutes, current_local.tm_yday)
        print("computer: day-", current_local.tm_yday, " time-", time_in_minutes, " day_night-", day_night, " DST-", time.localtime().tm_isdst )
        loop = 0

    if enable_GPIO:
        if ((modeX == 1) or (day_night and (modeX == 0))):
            GPIO_Out(0,1)
            GPIO_Out(1,1)
        elif ((modeX == 2) or (not day_night and (modeX == 0))):
            GPIO_Out(0,0)
            GPIO_Out(1,0)
    loop += 1


mainloop()



