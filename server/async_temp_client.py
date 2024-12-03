import time
from datetime import datetime
import requests
import threading

# Define server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = 3000

# Send data to the server
def send_data_to_server(distance):
    url = f"http://{SERVER_IP}:{SERVER_PORT}/api/water-level/store"
    data = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "water_level": distance
    }

    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Data successfully sent! Distance: {distance}")
        else:
            print(f"Failed to send data. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending distance {distance}: {e}")

# Send data asynchronously
def send_data_to_server_async(distance):
    """Runs the send_data_to_server function in a separate thread."""
    thread = threading.Thread(target=send_data_to_server, args=(distance,))
    thread.start()

# Simulate generating and sending multiple distance data points
def simulate_data_sending():
    distances = list(range(100, 300))  # Simulated distance values
    for distance in distances:
        send_data_to_server_async(distance)
        time.sleep(0.001)  # Simulate interval between data points

# Perform some other work in parallel
def perform_other_tasks():
    for i in range(200):
        print(f"Performing another task {i + 1}...")
        time.sleep(0.0001)  # Simulate time taken by other tasks

def main():
    # Start sending data and performing other tasks in parallel
    print("Starting data sending and other tasks...")
    
    # Create threads for data sending and other tasks
    data_thread = threading.Thread(target=simulate_data_sending)
    task_thread = threading.Thread(target=perform_other_tasks)
    
    # Start both threads
    data_thread.start()
    task_thread.start()
    
    # Wait for both threads to finish
    # data_thread.join()
    # task_thread.join()
    
    print("All tasks completed.")

if __name__ == "__main__":
    main()
