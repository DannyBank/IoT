from machine import Pin
from time import sleep

pir = Pin(14, Pin.IN)

while True:
    if pir.value() == 1:
        print("Motion detected")
    else:
        print("No motion")
        
    sleep(0.5)