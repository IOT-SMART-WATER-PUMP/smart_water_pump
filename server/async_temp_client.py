import aiohttp
import asyncio
from datetime import datetime

# Define server details
SERVER_IP = "127.0.0.1"
SERVER_PORT = 3000

async def send_data_to_server(distance):
    url = f"http://{SERVER_IP}:{SERVER_PORT}/store_data"
    data = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "water_level": distance
    }

    try:
        # Use aiohttp to send the POST request asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    print("Data successfully sent!")
                    print("Server Response:", await response.json())
                else:
                    print(f"Failed to send data. Status code: {response.status}")
                    print("Error:", await response.json())
    except aiohttp.ClientError as e:
        print(f"Error: {e}")

# Example usage
# To test the async function, you need to run it within an asyncio event loop
async def main():
    distance = 45.6  # Example distance value
    send_data_to_server(distance)

# Run the async function
if __name__ == "__main__":
    asyncio.run(main())
