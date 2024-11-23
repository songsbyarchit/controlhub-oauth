import json
import requests

def send_to_splunk(event_name, data, splunk_url, splunk_token):
    headers = {
        "Authorization": f"Splunk {splunk_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "event": event_name,
        "fields": data,
    }
    try:
        response = requests.post(splunk_url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            print(f"Data sent to Splunk successfully for event: {event_name}")
        else:
            print(f"Failed to send data to Splunk. Status Code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Splunk: {e}")
