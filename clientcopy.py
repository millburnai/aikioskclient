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
col_pins = [19,20,21]
color_pins = [18,23]
txt = ""
#server_ip = "96.225.21.203"
#server_port = 25565
#server_connection = Connection(server_ip, server_port)
#server_connections.connect()

#lcd.message("ID: ")
#server_ip = "96.225.21.203"
#server_port = 25565
#server_connection = connection.Connection(server_ip,server_port)
#server_connection.connect()

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

def send_to_server():
	#replaces bottom text with Checking and waits for a response from the server
	lcd.set_cursor(0,1)
	lcd.message("Checking...  ")
	
	#sends
	#print(myConnection.send(Message(MessageType.CONNECTION, 0, b'/00/00')))
	#response = myConnection.message_protocol(Message(MessageType.INPUT, 0, 12598))	
	
	#if(response.transactionID != -1):
#		set_color(color_dict['green'])
#		lcd.set_cursor(0,1)
#		name = response.messageValue[4:][1::2].decode('utf-8')
#		lcd.message('ID is invalid 	\n' + name)
#	else:
#		set_color(color_dict['red'])
#		lcd.set_cursor(0,1)
#		lcd.message("ID is invalid			")

	rObj = makeRec(txt)
	
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


	# if (rObj.works):
	# 	set_color(color_dict['green'])
	# 	lcd.set_cursor(0,0)
	# 	welcStr = ''
	# 	if (rObj.leaving):
	# 		welcStr = "Goodbye     \n" + rObj.names + ""
	# 	else:
	# 		welcStr = "Welcome back\n" + rObj.names + ""
	# 	lcd.message(welcStr)
	# 	time.sleep(1.5)
	# else:
	# 	set_color(color_dict['red'])
	# 	lcd.set_cursor(0,1)
	# 	lcd.message("              ")
	# 	lcd.set_cursor(0,0)
	# 	if (rObj.failed):
			
	# 	else:
	# 		lcd.message("ID not found")		
	# 	time.sleep(2.5)

	#sets the color back to normal	
	
	set_color(color_dict['null'])
	return

def reset():
	#resets all variables and the LCD display for the next user
	global txt
	txt = ""
	print("RESETTING")
	lcd.set_cursor(0,1)
	lcd.message("                ")
	lcd.home()
	lcd.message("ID:             ")
	lcd.set_cursor(4, 0)
	set_color(color_dict['white'])
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
            send_to_server()
            reset()
            return
        time.sleep(0.021)
		
def press(id):
    global txt
    #if enter is pressed and submit the id
    if id == 12 and len(txt) == 5:
        submit()
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
lcd.message("ID: ")

set_color(0)
import websocket
import json
try:
    import thread
except ImportError:
    import _thread as thread
import time

def on_message(ws, message):
    timeout= 3 
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        button_id = 0
        for rp in row_pins:
            GPIO.output(rp,GPIO.HIGH)
            for cp in col_pins:
                    button_id += 1
                    current = GPIO.input(cp)
                    if current and not buttons_pressed[button_id  - 1]:
                            buttons_pressed[button_id - 1] = True
                            press(button_id)
                    elif not current and buttons_pressed[button_id - 1]:
                            buttons_pressed[button_id - 1] = False 
            GPIO.output(rp, GPIO.LOW)
        time.sleep(0.021)
    GPIO.cleanup()

def on_message_test(ws,message): lcd.message(json.loads(message)) def on_error(ws,error): pass def on_close(ws): pass def on_open(ws):
    def run(*args):
        ws.send("1")

    thread.start_new_thread(run,())

websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://172.31.217.136:8000/v1/pi",on_message = lambda ws,msg: on_message(ws,msg),on_error = on_error, on_close = on_close)
ws.on_open = on_open
ws.run_forever()
