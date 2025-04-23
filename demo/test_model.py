import requests
import json
import time
import subprocess
import os

print("Testing the deployed model...")

# Get the InferenceService URL
try:
    result = subprocess.run(
        ['kubectl', 'get', 'inferenceservice', 'sentiment-classifier', '-o', 'jsonpath={.status.url}'],
        capture_output=True, text=True, check=True
    )
    
    service_url = result.stdout.strip()
    if not service_url:
        print("Error: Could not get service URL. Is the model deployed?")
        print("Run: kubectl get inferenceservices")
        exit(1)
        
    service_host = service_url.split("//")[1]
    
except subprocess.CalledProcessError as e:
    print(f"Error running kubectl: {e}")
    print("Make sure the model is deployed and kubectl is configured correctly.")
    exit(1)

print(f"Found service at: {service_url}")

# Test payload
data = {
    "instances": [
        {"text": "This product is amazing!"},
        {"text": "I'm disappointed with the quality."},
        {"text": "Great service, would buy again."}
    ]
}

# Endpoint for prediction
prediction_url = f"http://{service_host}/v1/models/sentiment-classifier:predict"

print(f"Sending prediction request to: {prediction_url}")
print(f"Payload: {json.dumps(data, indent=2)}")

# Send prediction request
headers = {"Content-Type": "application/json"}

try:
    response = requests.post(prediction_url, headers=headers, data=json.dumps(data), timeout=30)
    
    # Print results
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Predictions:")
        print(json.dumps(result, indent=2))
        
        # Display in a more readable format
        print("\nReadable Results:")
        for i, (text, pred) in enumerate(zip(data["instances"], result["predictions"])):
            sentiment = "positive" if pred.get("prediction") == 1 else "negative"
            confidence = pred.get("confidence", 0) * 100
            print(f"Text {i+1}: \"{text['text']}\"")
            print(f"Sentiment: {sentiment} (Confidence: {confidence:.1f}%)")
            print()
    else:
        print(f"Error: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if pods are running: kubectl get pods")
    print("2. Check pod logs: kubectl logs -l serving.kserve.io/inferenceservice=sentiment-classifier")
    print("3. Is the model ready? kubectl get inferenceservice")