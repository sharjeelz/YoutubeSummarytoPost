import os
import dotenv
import requests

# Load environment variables from.env file
dotenv.load_dotenv(override=True)
pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url="https://api.pushover.net/1/messages.json"
print(f"Pushover user: {pushover_user}"
      f"\nPushover token: {pushover_token}")
def send_pushover_notification(message: str):
    payload = {
        "token": pushover_token,
        "user": pushover_user,
        "message": message}
    response = requests.post(pushover_url, data=payload)
    print(f"Pushover notification sent: {response.text}")

send_pushover_notification('he bussy now!')