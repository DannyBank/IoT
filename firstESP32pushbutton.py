from machine import Pin
import time

# Configure GPIO 13 as input with an internal pull-up resistor
BUTTON_PIN = 26
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

print(f"Testing button on GPIO {BUTTON_PIN}...")
print("Press the red button to test functionality (Ctrl+C to stop).\n")

# Track previous state to avoid flooding the terminal
last_state = button.value()

while True:
    current_state = button.value()
    
    # Check if state has changed
    if current_state != last_state:
        if current_state == 0:
            print("🔴 Button PRESSED! (Pin read: 0)")
        else:
            print("⚪ Button RELEASED (Pin read: 1)")
            
        last_state = current_state
        
    time.sleep(0.1)  # Small delay for debouncing