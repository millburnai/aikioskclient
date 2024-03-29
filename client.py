import RPi.GPIO as GPIO
import Adafruit_CharLCD as LCDLib
import math
import time
import random
#import connection
from aldenC import *
from subprocess import call	

kioskNumber = 1
lcd = LCDLib.Adafruit_CharLCDBackpack()
print("Initalized lcd library")
lcd.set_backlight(0)
max_len = 4
row_pins = [16,6,12,13]
col_pins = [19,20,5]
color_pins = [18,23]
txt = ""
#server_ip = "96.225.21.203"
#server_port = 25565
#server_connection = Connection(server_ip, server_port)
#server_connections.connect()

import csv

ids={}

with open('/home/pi/aikioskclient/ids.csv', mode='r') as f:
    reader=csv.reader(f)
    x = 0
    for row in reader:
        name, id = row[1], row[0]
        x = x + 1
        if x == 1: continue
        separated_name = name.lower().split(",")
        first = separated_name[1]
        last = separated_name[0]
        combined = first + "_" + last
        ids[combined[1:]] = id




color_dict = {
    "white": 0,
    "hotpink": 1,
    "yellow": 2,
    "red": 3,
    "babyblue": 4,
    "darkblue": 5,
    "green": 6,
    "null": 7
}

def set_color(color):
    port1 = color & 0b1
    port0 = (color >> 1) & 0b1
    back = (color >> 2) & 0b1
    GPIO.output(color_pins[1], port1)
    GPIO.output(color_pins[0], port0)
    lcd.set_backlight(back)

def send_to_server(id=None):
	#replaces bottom text with Checking and waits for a response from the server
	lcd.set_cursor(0,1)
	lcd.message("Checking...  ")

	if id is None:
		rObj = makeRec(txt)
	else:
		rObj = makeRec(id)
	name = rObj.names
	if (rObj.failed):
                set_color(color_dict['red'])
                lcd.set_cursor(0,0)
                lcd.message("Server Error")
                lcd.set_cursor(0,1)
                lcd.message("Contact Office")
                time.sleep(2)
	else:
		if (rObj.works):
			set_color(color_dict['green'])
			lcd.set_cursor(0,0)
			welcStr = "ID Accepted \n" + rObj.names + ""
			lcd.message(welcStr)
		else:
			set_color(color_dict['red'])
			if (rObj.withInfo):
				lcd.set_cursor(0,0)
				lcd.message("No Senior Priv\n" + rObj.names + "")
			else:
				lcd.set_cursor(0,0)
				lcd.message("ID not found")     
		GPIO.output(row_pins[0], GPIO.HIGH)
		GPIO.output(row_pins[1], GPIO.HIGH)
		GPIO.output(row_pins[2], GPIO.HIGH)
		GPIO.output(row_pins[3], GPIO.HIGH)
		start_time = time.time()
		while time.time() - start_time < 2:
			for col in col_pins:
				if (GPIO.input(col)):
					GPIO.output(row_pins[0], GPIO.LOW)
					GPIO.output(row_pins[1], GPIO.LOW)
					GPIO.output(row_pins[2], GPIO.LOW)
					GPIO.output(row_pins[3], GPIO.LOW)
					return
			time.sleep(0.021)
	
	set_color(color_dict['null'])
	return name

def reset(message="Look into camera"):
	#resets all variables and the LCD display for the next user
	global txt
	txt = ""
	print("RESETTING")
	lcd.set_cursor(0,1)
	lcd.clear()
	lcd.message("               ")
	lcd.home()
	set_color(0)
	lcd.message(message)
	print(message)
	lcd.set_cursor(4, 0)
	#set_color(color_dict['white'])
	return


def submit():
    lcd.set_cursor(0,1)
    lcd.message("Are you sure?")
    GPIO.output(row_pins[3], GPIO.HIGH)

    #waits for a second enter or delete press
    time.sleep(0.25)	
    while True:
    #if delete is pressed get rid of the message on line 2 and return to id input
        if(GPIO.input(col_pins[0])):
            lcd.set_cursor(0, 1)
            lcd.message("             ")
            lcd.set_cursor(4+len(txt), 0)

            #waits until delete is released to return to id input so that no number is deleted
            while True:
                if(not GPIO.input(col_pins[0])):
                    return
        #if enter is pressed send to the server and reset
        elif(GPIO.input(col_pins[2])):
            name = send_to_server()
            reset()
            return True
        time.sleep(0.021)
		
def press(id):
    global txt
    #if enter is pressed and submit the id
    if id == 12 and len(txt) == 5:
        if submit(): return True
        return
    #if delete is pressed remove one number from input and txt
    if len(txt) > 0 and id == 10:
        txt = txt[:-1]
        lcd.set_cursor(4 + len(txt), 0)
        lcd.message(" ")
        lcd.set_cursor(4 + len(txt), 0)
    #only allow input if there are less than 5 numbers in the input field    
    if len(txt) <= max_len:
    	#if any of the number keys save 0 are pressed add them to the text and display them
        if id < 10:
            txt += str(id)
            lcd.message(str(id))
        #if zero is pressed add zero to the input field and txt
        elif id == 11:
            txt += "0"
            lcd.message("0")

GPIO.setmode(GPIO.BCM)
GPIO.setup(row_pins, GPIO.OUT)
GPIO.setup(color_pins, GPIO.OUT)
GPIO.setup(col_pins, GPIO.IN, pull_up_down=GPIO.PUD_DOWN    )
GPIO.output(row_pins, GPIO.LOW)

buttons_pressed = [False] * 12
pressing = False
current = -1
#comment
#Set up LCD
lcd.show_cursor(True)
lcd.home()

import websocket
import json
try:
	import thread
except ImportError:
	import _thread as thread
import time
def on_message(ws, message):
    lcd.clear()
    name = json.loads(message)
    lcd.message(name+"\nYes-ENT,No-CLR")
    print(name)
    ws.send(json.dumps({"signal":False}))
    confirmed = True
    while confirmed:
        button_id = 0
        for rp in row_pins:
            GPIO.output(rp,GPIO.HIGH)
            for cp in col_pins:
                button_id += 1
                current = GPIO.input(cp)
                if current and not buttons_pressed[button_id - 1]:
                    buttons_pressed[button_id - 1] = True
                    print (button_id)
                    if button_id == 12:
                        ws.send(json.dumps({"signal":True}))
                        send_to_server(ids[name])
                        reset()
                        return
                    elif button_id == 10:
                        confirmed = False
                elif not current and buttons_pressed[button_id - 1]:
                    buttons_pressed[button_id - 1] = False
            GPIO.output(rp, GPIO.LOW)
    lcd.clear()
    lcd.message("ID: ")
    set_color(0)
    while True:
        button_id = 0
        for rp in row_pins:
            GPIO.output(rp, GPIO.HIGH)
            for cp in col_pins:
                button_id += 1
                current = GPIO.input(cp)
                if current and not buttons_pressed[button_id - 1]:
                    buttons_pressed[button_id - 1] = True
                    press(button_id)
                    print(button_id)
                    if button_id == 12:
                        ws.send(json.dumps({"signal":True}))
                        return
                elif not current and buttons_pressed[button_id - 1]:
                    buttons_pressed[button_id - 1] = False
            GPIO.output(rp, GPIO.LOW)

def on_error(ws, error):
    print(error)

def on_open(ws):
    def run(*args):
        ws.send(json.dumps({"id":"1"}))
        reset()
    thread.start_new_thread(run, ())


from errno import ENETUNREACH
successful = False
lcd.message("Waiting for Wifi")
set_color(color_dict["red"])
while not successful:
	try:
		websocket.enableTrace(True)
		ws = websocket.WebSocketApp("ws://10.56.9.186:8000/v1/pi", on_message = lambda ws,msg: on_message(ws,msg), on_error = lambda ws,error: on_error(ws, error))
		ws.on_open = on_open
		ws.run_forever()
		succcesful = True
	except IOError as e:
                if e.errno == ENETUNREACH:
			print("Network reach fail") 
		else: 
			raise
