import RPi.GPIO as GPIO
import time

# GPIO Pin Definitions
TRIG = 23         # Define PIN for Trigger (GPIO 23)
ECHO = 24         # Define PIN for Echo (GPIO 24)
RELAY_PIN = 13    # Define PIN for Relay
GREEN_LED = 15    # Define PIN for Green LED
RED_LED = 16      # Define PIN for Red LED

# Thresholds
UPPER_LEVEL_THRESHOLD = 5  # Distance threshold in cm (adjustable)
LOWER_LEVEL_THRESHOLD = 30 # 
TIMEOUT = 0.03  # Timeout for ultrasonic sensor (30ms)
MEASUREMENT_INTERVAL = 0.5  # Time between measurements in seconds
GLOBAL_STATE = 0
def setup():
    GPIO.setmode(GPIO.BCM)     # Use BCM GPIO numbering
    GPIO.setwarnings(False)    # Disable GPIO warnings
    GPIO.setup(ECHO, GPIO.IN)  # Echo pin as input
    GPIO.setup(TRIG, GPIO.OUT) # Trigger pin as output
    GPIO.setup(RELAY_PIN, GPIO.OUT)  # Relay pin as output
    GPIO.setup(GREEN_LED, GPIO.OUT)  # Green LED pin as output
    GPIO.setup(RED_LED, GPIO.OUT)    # Red LED pin as output
   
    # Initialize all outputs to False (off)
    GPIO.output(TRIG, False)
    GPIO.output(RELAY_PIN, False)  # Motor off
    GPIO.output(GREEN_LED, False)  # Green LED off
    GPIO.output(RED_LED, False)    # Red LED off
   
    print("System Initializing... Waiting for sensor to settle")
    time.sleep(1)  # Wait for the sensor to settle

def measure_distance():
    """Measures the distance using the ultrasonic sensor."""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)  # 10 µs pulse
    GPIO.output(TRIG, False)
   
    pulse_start = pulse_end = time.time()
    timeout_start = time.time()
   
    # Wait for echo to start (go high)
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
        if pulse_start - timeout_start > TIMEOUT:
            return None  # Timeout, no valid measurement
   
    # Wait for echo to end (go low)
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
        if pulse_end - pulse_start > TIMEOUT:
            return None  # Timeout, no valid measurement
   
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound is 34300 cm/s, divided by 2 for round-trip
    return round(distance, 2)

def control_motor_and_leds(distance):
    global GLOBAL_STATE
    """Controls the motor and LEDs based on the distance measured."""
    if distance is None:
        print("Error: Timeout occurred. No valid reading.")
        return
   
    print(f"Water Level: {distance} cm")
    


    if distance < UPPER_LEVEL_THRESHOLD:
        GLOBAL_STATE = 0
        GPIO.output(RELAY_PIN, False)  # Motor OFF
        GPIO.output(GREEN_LED, True)   # Green LED ON
        GPIO.output(RED_LED, False)    # Red LED OFF
        print("Water level OK. Motor OFF")
    elif distance > UPPER_LEVEL_THRESHOLD and distance < LOWER_LEVEL_THRESHOLD and GLOBAL_STATE == 0:
        GLOBAL_STATE = 0
        GPIO.output(RELAY_PIN, False)  # Motor OFF
        GPIO.output(GREEN_LED, True)   # Green LED ON
        GPIO.output(RED_LED, False)    # Red LED OFF
        print("Water level OK. Motor OFF")
    elif distance > UPPER_LEVEL_THRESHOLD and distance < LOWER_LEVEL_THRESHOLD and GLOBAL_STATE == 1:
        GLOBAL_STATE = 1
        GPIO.output(RELAY_PIN, True)   # Motor ON
        GPIO.output(GREEN_LED, False)  # Green LED OFF
        GPIO.output(RED_LED, True)     # Red LED ON
        print("Water level LOW. Motor ON")
    elif distance > LOWER_LEVEL_THRESHOLD:
        GLOBAL_STATE = 1
        GPIO.output(RELAY_PIN, True)   # Motor ON
        GPIO.output(GREEN_LED, False)  # Green LED OFF
        GPIO.output(RED_LED, True)     # Red LED ON
        print("Water level LOW. Motor ON")
def main():
    setup()
    try:
        while True:
            distance = measure_distance()
            control_motor_and_leds(distance)
            time.sleep(MEASUREMENT_INTERVAL)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    finally:
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()

if __name__ == "__main__":
    main()