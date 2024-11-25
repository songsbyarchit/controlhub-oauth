import logging
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_to_splunk(event_name, data, splunk_url, splunk_token):
    headers = {
        "Authorization": f"Splunk {splunk_token}",
        "Content-Type": "application/json",
    }
    # Updated payload format: Move data to the "event" field
    payload = {
        "event": {
            "name": event_name,
            "data": data,  # Nest the actual data under "data"
        }
    }
    try:
        # Disable SSL verification for development
        response = requests.post(splunk_url, headers=headers, data=json.dumps(payload), verify=False)
        if response.status_code == 200:
            logger.info(f"Data sent to Splunk successfully for event: {event_name}")
        else:
            logger.error(f"Failed to send data to Splunk. Status Code: {response.status_code}, Response: {response.text}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error connecting to Splunk: {e}")