from escpos.printer import Serial
import os, random
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306 #imports of different modules
from luma.core.legacy import text
#from fonts.ttf import FredokaOne
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time

from RPLCD.i2c import CharLCD

#from machine import Pin, SoftI2C
#import machine
#from pico_i2c_lcd import I2cLcd
#from time import sleep
#import utime
#import _thread

#for the new printer beta
from escpos.printer import Usb
#Button pins
BUTTON_1_PIN = 11  
BUTTON_2_PIN = 13
BUTTON_3_PIN = 15

# Define the LCD I2C address and dimensions
I2C_ADDR = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20


#lock 
#lock = _thread.allocate_lock()

# Initialize I2C and LCD objects
#i2c = SoftI2C(sda=Pin(3), scl=Pin(5), freq=400000)
#lcd = I2cLcd(i2c, I2C_ADDR, I2C_NUM_ROWS, I2C_NUM_COLS)

lcd = CharLCD(
    i2c_expander='PCF8574', 
    address=0x27,            
    port=1,
    cols=I2C_NUM_COLS,                
    rows=I2C_NUM_ROWS                  
)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

#Buttons TODO, adapt this to raspi3b+

GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

cmc = 0 #cmc variable for tracking cmc

#p = Serial(devfile='/dev/serial0', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=1.00, dsrdtr=True) #initilize thermal printer serial 
import usb.core
dev = usb.core.find(idVendor=0x28e9, idProduct=0x0289)
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

#p = Usb(idVendor=0x28e9, idProduct=0x0289, out_ep=0x03, in_ep=0x81)#initilize OLED screen serial ports, set communication and set font/size
p = Usb(idVendor=0x28e9, idProduct=0x0289, out_ep=0x03, in_ep=0x81, profile="ZJ-5870)
p.image(img, center=False)
spaces = "                  "
debounce_delay = 0.2  # Adjust this value as needed for your buttons
print_time = 2
#p.text("test\n")
#p.text("test\n")
#p.text("test\n")
#p.cut()
def display_cmc(cmc):
    """
    Function to display cmc on screen
    """
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Current CMC: %d   " % cmc)

        
#display initial cmc = 0
lcd.clear()
display_cmc(cmc) 

def display_print_message(cmc):
    """
    Function to display print message
    """
    lcd.cursor_pos = (2, 0)
    lcd.write_string("Printing Card With")
    lcd.cursor_pos = (3, 0)
    lcd.write_string("CMC = %d   " % cmc)
    time.sleep(print_time)
    lcd.cursor_pos = (3, 0)
    lcd.write_string(spaces)
    lcd.cursor_pos = (2, 0)
    lcd.write_string(spaces)

#ignore button warnings and set numbering mode to BOARD
#GPIO.setwarnings(False) 
#GPIO.setmode(GPIO.BOARD)

def print_random_image(cmc):
    path = '/home/lazarus/mormir_proj/' + str(cmc) + '/'
    try:
        image_path = path + random.choice(os.listdir(path))
        print(image_path)
        
        # Resize image to fit printer width (384px for 58mm, 576px for 80mm)
        img = Image.open(image_path)
        img = img.convert('RGB')
        img = img.resize((384, int(img.height * 384 / img.width)))  # change 384 to 576 if 80mm printer
        
        p.image(img)
        p.textln("")
        p.textln("")
        p.cut()  # THIS is likely why nothing comes out — paper needs to feed/cut
    except Exception as e:
        print("An error occurred:", e)

def print_random_image(cmc):
    path = '/home/lazarus/mormir_proj/' + str(cmc) + '/'
    valid = [f for f in os.listdir(path) 
             if not f.startswith('.') 
             and f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not valid:
        print("No images found")
        return
    image_path = path + random.choice(valid)


#print_random_image(0)


while True: # Run forever

    if GPIO.input(BUTTON_2_PIN) == GPIO.LOW: #increase CMC button
        if cmc < 16: #highest cmc is 16, so we don't want to go over that
            cmc = cmc + 1
            display_cmc(cmc)
            time.sleep(debounce_delay)  # Debounce delay
        else:
            pass
    if GPIO.input(BUTTON_1_PIN) == GPIO.LOW: #decrese CMC button
        if cmc > 0: #lowest cmc is 0 so we don't want to go negative
            cmc = cmc - 1
            display_cmc(cmc)
            time.sleep(debounce_delay)  # Debounce delay
        else:
            pass
    if GPIO.input(BUTTON_3_PIN) == GPIO.LOW: #printing button
        print("print")
        display_print_message(cmc)
        print_random_image(cmc)
        time.sleep(debounce_delay)  # Debounce delay
