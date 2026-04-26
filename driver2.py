from escpos.printer import Serial
import os, random
import threading
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from luma.core.legacy import text
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import time
from RPLCD.i2c import CharLCD
from escpos.printer import Usb
import usb.core

# ── Button pins ───────────────────────────────────────────────────────────────
BUTTON_1_PIN = 11   # decrease CMC
BUTTON_2_PIN = 13   # increase CMC
BUTTON_3_PIN = 15   # print

# ── LCD config ────────────────────────────────────────────────────────────────
I2C_ADDR    = 0x27
I2C_NUM_ROWS = 4
I2C_NUM_COLS = 20

# ── Valid image extensions ────────────────────────────────────────────────────
VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

# ── LCD init ──────────────────────────────────────────────────────────────────
lcd = CharLCD(
    i2c_expander='PCF8574',
    address=0x27,
    port=1,
    cols=I2C_NUM_COLS,
    rows=I2C_NUM_ROWS
)

# ── GPIO init ─────────────────────────────────────────────────────────────────
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(BUTTON_1_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_2_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_3_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ── Printer init ──────────────────────────────────────────────────────────────
# Detach usblp kernel driver so escpos can claim the device directly.
# This runs every startup to handle cases where usblp reloaded.
dev = usb.core.find(idVendor=0x28e9, idProduct=0x0289)
if dev is not None and dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

# profile="ZJ-5870" tells escpos this is a 58mm (384px wide) thermal printer
p = Usb(
    idVendor=0x28e9,
    idProduct=0x0289,
    out_ep=0x03,
    in_ep=0x81,
    profile="ZJ-5870"
)

# ── State ─────────────────────────────────────────────────────────────────────
cmc            = 0
spaces         = " " * I2C_NUM_COLS
debounce_delay = 0.2
print_time     = 2
is_printing    = False  # flag so button spam doesn't queue multiple prints

# ── LCD helpers ───────────────────────────────────────────────────────────────
def display_cmc(cmc):
    lcd.cursor_pos = (0, 0)
    lcd.write_string("Current CMC: %d   " % cmc)

def display_print_message(cmc):
    lcd.cursor_pos = (2, 0)
    lcd.write_string("Printing Card With")
    lcd.cursor_pos = (3, 0)
    lcd.write_string("CMC = %d   " % cmc)

def clear_print_message():
    lcd.cursor_pos = (3, 0)
    lcd.write_string(spaces)
    lcd.cursor_pos = (2, 0)
    lcd.write_string(spaces)

# ── Print function (runs in its own thread) ───────────────────────────────────
def print_random_image(cmc):
    """
    Picks a random valid image from the cmc folder and prints it.
    Runs in a background thread so it never blocks the button loop.
    """
    global is_printing
    path = '/home/lazarus/mormir_proj/' + str(cmc) + '/'
    try:
        # Filter out macOS metadata files (._*), hidden files, and non-images
        valid_files = [
            f for f in os.listdir(path)
            if not f.startswith('.')
            and f.lower().endswith(VALID_EXTENSIONS)
            and os.path.isfile(os.path.join(path, f))
        ]

        if not valid_files:
            print("No valid images found in", path)
            return

        image_path = os.path.join(path, random.choice(valid_files))
        print("Printing:", image_path)

        img = Image.open(image_path)
        img = img.convert('RGB')
        # Resize to 384px wide (58mm printer). Change to 576 for 80mm.
        img = img.resize((384, int(img.height * 384 / img.width)))

        p.image(img, center=False)  # center=False avoids the media.width.pixel warning
        p.textln("")
        p.textln("")
        p.cut()

    except Exception as e:
        print("Print error:", e)
    finally:
        # Always clear the print message and release the lock when done
        clear_print_message()
        is_printing = False

# ── Startup ───────────────────────────────────────────────────────────────────
lcd.clear()
display_cmc(cmc)

# ── Main loop ─────────────────────────────────────────────────────────────────
while True:

    if GPIO.input(BUTTON_2_PIN) == GPIO.LOW:    # increase CMC
        if cmc < 16:
            cmc += 1
            display_cmc(cmc)
            time.sleep(debounce_delay)

    if GPIO.input(BUTTON_1_PIN) == GPIO.LOW:    # decrease CMC
        if cmc > 0:
            cmc -= 1
            display_cmc(cmc)
            time.sleep(debounce_delay)

    if GPIO.input(BUTTON_3_PIN) == GPIO.LOW:    # print
        if not is_printing:                     # ignore if already printing
            is_printing = True
            display_print_message(cmc)
            # Run print in background so buttons stay responsive
            t = threading.Thread(target=print_random_image, args=(cmc,), daemon=True)
            t.start()
        time.sleep(debounce_delay)
