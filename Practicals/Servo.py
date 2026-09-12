from machine import Pin, PWM
from time import sleep

servo = PWM(Pin(26), freq=50)

def move(angle):
    duty = int(26 + (angle / 180) * 102)
    servo.duty(duty)
    
while True:
    move(0)
    sleep(1)
    
    move(90)
    sleep(1)
    
    move(180)
    sleep(1)
    
    move(90)
    sleep(1)