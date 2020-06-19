import socket
import time
import pycom
import machine
import binascii
import struct
import ubinascii
from machine import Pin
from network import LoRa

GREEN = 0x007f00
RED = 0x7f0000
YELLOW = 0x7f7f00
OFF = 0x000000


lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

THE_APP_EUI = '70B3D57ED00307B8'
THE_APP_KEY = '2A931242F9C54966445410B1E867D81D'
app_eui = ubinascii.unhexlify('70B3D57ED00307B8')
app_key = ubinascii.unhexlify('2A931242F9C54966445410B1E867D81D')

lora = LoRa(mode=LoRa.LORAWAN)


adc = machine.ADC()
apin = adc.channel(pin="P16")
val = 0
dac = machine.DAC("P22")

def set_led_to(color=GREEN):
    pycom.heartbeat(False)
    pycom.rgbled(color)

def flash_led_to(color=GREEN, t1=1):
    set_led_to(color)
    time.sleep(t1)
    set_led_to(OFF)

def join_lora(force_join = False):
    print("Connecting to TTN")

    if not force_join:
        print("restoring state")
        lora.nvram_restore()

    if not lora.has_joined() or force_join == True:

        # Join netowkr using OTAA
        lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

        # Wait for module to join network
        while not lora.has_joined():
            print("Not joined yet...")
            time.sleep(2.5)

        lora.nvram_save()

        # returning whether the join was successful
        if lora.has_joined():
            flash_led_to(GREEN)
            print('LoRa Joined')
            return True
        else:
            flash_led_to(RED)
            print('LoRa Not Joined')
            return False

    else:
        return True

print("Device LoRa MAC:", binascii.hexlify(lora.mac()))

pycom.heartbeat(False)

flash_led_to(YELLOW)
# Join LoRa
join_lora(True)

while True:
    # LoRa Socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
    s.setblocking(True)

    val = apin()
    dac.write((val/100))

    payload = struct.pack(">fff", val)

    # s.send(payload)
    s.setblocking(False)
    flash_led_to(GREEN)
    print("iterated")
    time.sleep(2)

    
