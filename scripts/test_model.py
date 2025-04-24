import requests
import json
import argparse
import base64
import time

def wait_for_model_ready(url, auth_header=None, timeout=60):
    print(f"Waiting for model to be ready at {url}")
    headers = {"Content-Type": "application/json"}
    if auth_header:
        headers["Authorization"] = auth_header
        
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url.replace(':predict', '/ready'), 
                                 headers=headers,
                                 timeout=5)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        print(".", end="", flush=True)
        time.sleep(2)
    return False

# Parse arguments
parser = argparse.ArgumentParser(description='Test the deployed KServe model')
parser.add_argument('--hostname', type=str, default='localhost')
parser.add_argument('--port', type=int, default=8080)
parser.add_argument('--auth', action='store_true')
parser.add_argument('--username', type=str, default='admin')
parser.add_argument('--password', type=str, default='kserve-demo')
args = parser.parse_args()

# Setup URL and headers
SERVICE_URL = f"http://{args.hostname}:{args.port}/v1/models/sentiment-classifier-auth:predict"
headers = {"Content-Type": "application/json"}

# Add authentication if needed
auth_header = None
if args.auth:
    auth_string = base64.b64encode(
        f"{args.username}:{args.password}".encode()
    ).decode()
    auth_header = f"Basic {auth_string}"
    headers["Authorization"] = auth_header

# Test data
data = {
    "instances": [
        {"text": "This product is amazing!"},
        {"text": "I'm disappointed with the quality."},
        {"text": "Great service, would buy again."}
    ]
}

# Wait for model to be ready
if not wait_for_model_ready(SERVICE_URL, auth_header):
    print("\nError: Model not ready after timeout")
    exit(1)

# Send request
print(f"\nSending request to {SERVICE_URL}")
print(f"Request payload: {json.dumps(data, indent=2)}")

try:
    response = requests.post(
        SERVICE_URL,
        headers=headers,
        json=data,
        timeout=30
    )
    response.raise_for_status()
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except requests.exceptions.RequestException as e:
    print(f"\nError: {str(e)}")
    exit(1)