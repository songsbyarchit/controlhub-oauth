import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

def fetch_spaces():
    url = "https://webexapis.com/v1/rooms"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        spaces = response.json().get("items", [])
        for space in spaces:
            print(f"Space Name: {space['title']}, Space ID: {space['id']}")
    else:
        print(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    fetch_spaces()