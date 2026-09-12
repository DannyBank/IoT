from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(26), freq=50)

def move(angle):
    duty = int(26 + (angle / 180) * 102)
    servo.duty(duty)
    
while True:
    for i in range(1,180):
        move(i)
        sleep(0.1)
        
    for i in range(180, 0, -1):
        move(i)
        sleep(0.1)