import RPi.GPIO as GPIO
import time
from datetime import datetime
import requests


# GPIO Pin Definitions
TRIG = 23  # Define PIN for Trigger (GPIO 23)
ECHO = 24  # Define PIN for Echo (GPIO 24)
RELAY_PIN = 13  # Define PIN for Relay
GREEN_LED = 15  # Define PIN for Green LED
RED_LED = 16  # Define PIN for Red LED

# Thresholds
UPPER_LEVEL_THRESHOLD = 5  # Distance threshold in cm (adjustable)
LOWER_LEVEL_THRESHOLD = 30  #
TIMEOUT = 0.03  # Timeout for ultrasonic sensor (30ms)
MEASUREMENT_INTERVAL = 0.5  # Time between measurements in seconds
PUMP_IS_ON = False

# Server details
SERVER_PORT = 3000
SERVER_IP = "127.0.0.1"


def setup():
    GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbering
    GPIO.setwarnings(False)  # Disable GPIO warnings
    GPIO.setup(ECHO, GPIO.IN)  # Echo pin as input
    GPIO.setup(TRIG, GPIO.OUT)  # Trigger pin as output
    GPIO.setup(RELAY_PIN, GPIO.OUT)  # Relay pin as output
    GPIO.setup(GREEN_LED, GPIO.OUT)  # Green LED pin as output
    GPIO.setup(RED_LED, GPIO.OUT)  # Red LED pin as output

    # Initialize all outputs to False (off)
    GPIO.output(TRIG, False)
    GPIO.output(RELAY_PIN, False)  # Motor off
    GPIO.output(GREEN_LED, False)  # Green LED off
    GPIO.output(RED_LED, False)  # Red LED off

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
    distance = (
        pulse_duration * 17150
    )  # Speed of sound is 34300 cm/s, divided by 2 for round-trip
    return round(distance, 2)


# Set motor and LED states
def set_motor_and_leds(motor_state, green_led_state, red_led_state):
    """Sets the motor and LED states."""
    GPIO.output(RELAY_PIN, motor_state)
    GPIO.output(GREEN_LED, green_led_state)
    GPIO.output(RED_LED, red_led_state)


# Send data to the server
def send_data_to_server(distance):
    url = f"http://{SERVER_IP}:{SERVER_PORT}/store_data"
    data = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "water_level": distance
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("Data successfully sent!")
            print("Server Response:", response.json())
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
            print("Error:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

def control_motor_and_leds(distance):
    global PUMP_IS_ON
    """Controls the motor and LEDs based on the distance measured."""
    if distance is None:
        print("Error: Timeout occurred. No valid reading.")
        return

    print(f"Water Level: {distance} cm")

    if distance < UPPER_LEVEL_THRESHOLD:
        set_motor_and_leds(False, True, False)  # Motor OFF, Green LED ON, Red LED OFF
        PUMP_IS_ON = False
        print("Water level OK. Motor OFF")

    elif ( distance > UPPER_LEVEL_THRESHOLD and distance < LOWER_LEVEL_THRESHOLD ):  
        if PUMP_IS_ON == True:
            set_motor_and_leds(True, False, True)  # Motor ON, Green LED OFF, Red LED ON
            PUMP_IS_ON = True
            print("Water level LOW. Motor ON")
        else:
            set_motor_and_leds(False, True, False)  # Motor OFF, Green LED ON, Red LED OFF
            PUMP_IS_ON = False
            print("Water level OK. Motor OFF")

    elif distance > LOWER_LEVEL_THRESHOLD:
        set_motor_and_leds(True, False, True)  # Motor ON, Green LED OFF, Red LED ON
        PUMP_IS_ON = True
        print("Water level LOW. Motor ON")

    send_data_to_server(distance)


def main():
    setup()
    try:
        while True:
            distance = measure_distance()
            control_motor_and_leds(distance)
            time.sleep(MEASUREMENT_INTERVAL)
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"\nSystem error: {str(e)}")
    finally:
        print("Cleaning up GPIO pins...")
        GPIO.cleanup()


if __name__ == "__main__":
    main()
