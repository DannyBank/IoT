import machine
import time

PIR_PIN = 32  # Updated to GPIO 32
LED_PIN = 2   # Built-in LED

pir = machine.Pin(PIR_PIN, machine.Pin.IN)
led = machine.Pin(LED_PIN, machine.Pin.OUT)

print("Warming up PIR sensor...")
time.sleep(15)
print("PIR Ready!")

while True:
    if pir.value() == 1:
        led.value(1)
        print("Motion detected!")
        time.sleep(2)
    else:
        led.value(0)
        
    time.sleep(0.1)