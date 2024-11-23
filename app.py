import os
from flask import Flask, redirect, request, jsonify
import requests
from dotenv import load_dotenv
from splunk_helpers import send_to_splunk

# Load environment variables from .env
load_dotenv()

# Environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = os.getenv("SCOPES")
PORT = os.getenv("PORT", 5151)  # Default to 5151 if not specified
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL")  # Splunk HEC URL
SPLUNK_TOKEN = os.getenv("SPLUNK_TOKEN")      # Splunk Token

# Flask app setup
app = Flask(__name__)

# Helper function to update .env file
def update_env_file(key, value):
    with open(".env", "r") as file:
        lines = file.readlines()

    with open(".env", "w") as file:
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
            else:
                file.write(line)

# Home route to start OAuth flow
@app.route("/")
def home():
    auth_url = (
        f"https://webexapis.com/v1/authorize"
        f"?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}&state=1234"
    )
    return f'<a href="{auth_url}">Authenticate with Webex Control Hub</a>'

# Callback route to handle OAuth redirect
@app.route("/callback")
def callback():
    global ACCESS_TOKEN, REFRESH_TOKEN
    code = request.args.get("code")
    if not code:
        return "Authorization failed. No code provided."

    # Exchange the code for an access token
    token_url = "https://webexapis.com/v1/access_token"
    token_payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(token_url, data=token_payload)

    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data.get("access_token")
        REFRESH_TOKEN = token_data.get("refresh_token")

        # Update .env file with the new tokens
        update_env_file("ACCESS_TOKEN", ACCESS_TOKEN)
        update_env_file("REFRESH_TOKEN", REFRESH_TOKEN)

        return jsonify({
            "Access Token": ACCESS_TOKEN,
            "Refresh Token": REFRESH_TOKEN,
            "Expires In": token_data.get("expires_in"),
        })
    else:
        return f"Failed to retrieve access token. Response: {response.text}"

# Function to refresh the access token
def refresh_access_token():
    global ACCESS_TOKEN, REFRESH_TOKEN
    token_url = "https://webexapis.com/v1/access_token"
    token_payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
    }
    response = requests.post(token_url, data=token_payload)

    if response.status_code == 200:
        token_data = response.json()
        ACCESS_TOKEN = token_data.get("access_token")
        REFRESH_TOKEN = token_data.get("refresh_token")

        # Update .env file with the new tokens
        update_env_file("ACCESS_TOKEN", ACCESS_TOKEN)
        update_env_file("REFRESH_TOKEN", REFRESH_TOKEN)

        print("Access token refreshed successfully!")
        return {
            "Access Token": ACCESS_TOKEN,
            "Refresh Token": REFRESH_TOKEN,
            "Expires In": token_data.get("expires_in"),
        }
    else:
        print(f"Error refreshing token: {response.status_code}, {response.text}")
        return None

# Route to manually refresh the access token
@app.route("/refresh_token")
def handle_token_refresh():
    token_data = refresh_access_token()
    if token_data:
        return jsonify(token_data)
    else:
        return "Failed to refresh token."

# Function to fetch data from Control Hub
def fetch_control_hub_data(endpoint):
    base_url = "https://webexapis.com/v1/"
    url = f"{base_url}{endpoint}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching {endpoint}: {response.status_code} - {response.text}")
        return {}

# Example: Fetch Rooms
@app.route("/fetch_rooms")
def fetch_rooms():
    data = fetch_control_hub_data("rooms")
    return jsonify(data)

# Example: Send Rooms to Splunk
@app.route("/send_rooms_to_splunk")
def send_rooms_to_splunk():
    rooms = fetch_control_hub_data("rooms")
    if rooms:
        send_to_splunk("webex_rooms", rooms, SPLUNK_HEC_URL, SPLUNK_TOKEN)
        return "Rooms data sent to Splunk successfully!"
    else:
        return "Failed to fetch or send rooms data to Splunk."

@app.route("/fetch_visible_rooms")
def fetch_visible_rooms():
    return fetch_control_hub_data("rooms")

# Run the Flask app
if __name__ == "__main__":
    app.run(port=int(PORT), debug=True)