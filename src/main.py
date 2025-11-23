import time
import subprocess
import RPi.GPIO as GPIO

# GPIO pins for buttons
BUTTON_UP = 22      
BUTTON_DOWN = 23    
BUTTON_SELECT = 24  

selected_index = 0
scroll_offset = 0
VISIBLE_LINES = 8


menu_items = [
    "System Information|",
    "Netvaerks Diagnos |",
    "Test Keyboard",
    "Vis System Status",
    "Genstart Service",
    "Ryd Log",
    "Inverter Screen",
    "test",
    "test2",
    "Afslut"
]

# OLED 
def oled_command(args):
    """Kører OLED kommando via C-programmet"""
    cmd = ["/home/pi/test/ssd1306_linux/ssd1306_bin", "-n", "1"] + args
    subprocess.run(cmd, capture_output=True)

def oled_clear():
    """Ryd OLED skærm"""
    oled_command(["-c"])

def oled_text(x, y, text):
    """Vis tekst på OLED skærm"""
    oled_command(["-x", str(x), "-y", str(y), "-l", text])

def oled_init():
    """Initialiser OLED skærm"""
    oled_command(["-I", "128x64"])
    oled_clear()

###############################################################

def setup_buttons():
    """Opsæt GPIO til knapper"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BUTTON_SELECT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def cleanup_buttons():
    GPIO.cleanup()

def wait_for_button():
    while True:
        if GPIO.input(BUTTON_UP) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BUTTON_UP) == GPIO.LOW:
                time.sleep(0.01)
            return "UP"
        elif GPIO.input(BUTTON_DOWN) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BUTTON_DOWN) == GPIO.LOW:
                time.sleep(0.01)
            return "DOWN"
        elif GPIO.input(BUTTON_SELECT) == GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BUTTON_SELECT) == GPIO.LOW:
                time.sleep(0.01)
            return "SELECT"
        time.sleep(0.01)

#####################################################################

def draw_menu(selected, offset):
    oled_clear()

    for display_line in range(VISIBLE_LINES):
        item_index = display_line + offset

        if item_index >= len(menu_items):
            break  # no more items to display

        prefix = "> " if item_index == selected else " "
        oled_text(1, display_line, prefix + menu_items[item_index])



#####################################################################

def main():
    global selected_index, scroll_offset
    setup_buttons()
    oled_init()
    time.sleep(0.1)

    draw_menu(selected_index, scroll_offset)

    while True:
        btn = wait_for_button()

        if btn == "DOWN":
            selected_index = min(selected_index + 1, len(menu_items) - 1)
            if selected_index >= scroll_offset + VISIBLE_LINES:
                scroll_offset += 1

        elif btn == "UP":
            selected_index = max(selected_index - 1, 0)
            if selected_index < scroll_offset:
                scroll_offset -= 1

        draw_menu(selected_index, scroll_offset)

if __name__ == "__main__":
    main()
