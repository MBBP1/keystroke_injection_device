import os
import json
import time
import subprocess
import RPi.GPIO as GPIO

CONFIG_FILE = "/home/pi/badusb_config.json"
LOG_FILE = "/home/pi/badusb.log" 

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

def log_message(message):
    """Logger beskeder til fil"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"LOG: {message}")

def load_config():
    """Loader konfiguration"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"current_script": "none"}

def save_config(script_name):
    """Gemmer konfiguration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"current_script": script_name}, f, indent=2)
        log_message(f"Script ændret til: {script_name}")
    except Exception as e:
        log_message(f"Fejl ved gemning: {e}")

def get_service_status():
    """Tjekker om badusb.service kører"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'badusb.service'],
                              capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "unknown"

def restart_service():
    """Genstarter badusb service"""
    try:
        subprocess.run(['sudo', 'systemctl', 'restart', 'badusb.service'], check=True)
        log_message("Service genstartet")
        return True
    except Exception as e:
        log_message(f"Fejl: {e}")
        return False

def show_status():
    """Viser system status"""
    config = load_config()
    service_status = get_service_status()

    print(f"\n=== SYSTEM STATUS ===")
    print(f"Valgt script: {config['current_script']}")
    print(f"Service status: {service_status}")
    print(f"Log fil: {LOG_FILE}")


    # Vis sidste log entries
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()[-5:]
            print("\nSidste log entries:")
            for line in lines:
                print(f"  {line.strip()}")
    except:
        print("\nIngen log data endnu")

    input("\nTryk Enter for at fortsætte...")

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

        elif btn == "SELECT":
            selected_item = menu_items[selected_index]

            if selected_item == "Afslut":
                oled_clear()
                time.sleep(3)
                cleanup_buttons()
                break

            elif selected_item == "Genstart Service":
                oled_clear()
                oled_text(1, 0, "Genstarter...")
                success = restart_service()
                oled_clear()
                if success:
                    oled_text(1, 0, "Service genstartet")
                else:
                    oled_text(1, 0, "Fejl ved genstart")
                time.sleep(2)

            elif selected_item == "Vis System Status":
                status = get_service_status()
                oled_clear()
                oled_text(1, 0, f"Service status:")
                oled_text(1, 1, status)
                time.sleep(3)

            # Additional menu item actions can be added here

        draw_menu(selected_index, scroll_offset)

if __name__ == "__main__":
    open(LOG_FILE, 'a').close()
    main()
