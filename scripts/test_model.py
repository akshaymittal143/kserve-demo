import requests
import json
import argparse
import base64

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test the deployed KServe model')
parser.add_argument('--hostname', type=str, required=True, help='Service hostname')
parser.add_argument('--auth', action='store_true', help='Use authentication')
parser.add_argument('--username', type=str, default='admin', help='Auth username')
parser.add_argument('--password', type=str, default='kserve-demo', help='Auth password')
args = parser.parse_args()

# Get the InferenceService URL
SERVICE_HOST = args.hostname
SERVICE_URL = f"http://{SERVICE_HOST}/v1/models/sentiment-classifier:predict"

# Test payload
data = {
    "instances": [
        {"text": "This product is amazing!"},
        {"text": "I'm disappointed with the quality."},
        {"text": "Great service, would buy again."}
    ]
}

# Prepare headers
headers = {"Content-Type": "application/json"}

# Add authentication if needed
if args.auth:
    auth_header = base64.b64encode(f"{args.username}:{args.password}".encode()).decode()
    headers["Authorization"] = f"Basic {auth_header}"

# Send prediction request
print(f"Sending request to {SERVICE_URL}")
print(f"Request payload: {json.dumps(data, indent=2)}")
response = requests.post(SERVICE_URL, headers=headers, data=json.dumps(data))

# Print results
print(f"\nStatus Code: {response.status_code}")
if response.status_code == 200:
    print(f"Response: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Error: {response.text}")