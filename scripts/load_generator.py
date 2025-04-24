import requests
import json
import time
import threading
import random
import argparse

# Command line arguments
parser = argparse.ArgumentParser(description='Generate load for KServe model')
parser.add_argument('--hostname', type=str, required=True, help='Service hostname')
parser.add_argument('--requests', type=int, default=500, help='Number of requests to send')
parser.add_argument('--concurrency', type=int, default=10, help='Number of concurrent requests')
parser.add_argument('--delay', type=float, default=0.1, help='Delay between requests in seconds')
parser.add_argument('--port', type=int, default=8080, help='Service port')
args = parser.parse_args()

# Configuration
SERVICE_HOST = args.hostname
SERVICE_URL = f"http://{SERVICE_HOST}:{args.port}/v1/models/sentiment-classifier:predict"
TOTAL_REQUESTS = args.requests
CONCURRENT_REQUESTS = args.concurrency
REQUEST_DELAY = args.delay

# Sample texts for prediction
sample_texts = [
    "I love this product, it's amazing",
    "Great service and fast delivery",
    "This is terrible, doesn't work at all",
    "Awful experience, never buying again",
    "Fantastic customer support",
    "Disappointed with the quality",
    "Best purchase I've made this year",
    "Would recommend to everyone",
    "Complete waste of money",
    "Exceeded all my expectations"
]

# Stats tracking
successful_requests = 0
failed_requests = 0
response_times = []

def send_request():
    global successful_requests, failed_requests
    
    # Create random payload
    num_instances = random.randint(1, 5)
    instances = [{"text": random.choice(sample_texts)} for _ in range(num_instances)]
    data = {"instances": instances}
    
    headers = {"Content-Type": "application/json"}
    
    try:
        start_time = time.time()
        response = requests.post(SERVICE_URL, headers=headers, data=json.dumps(data), timeout=10)
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            successful_requests += 1
            response_times.append(elapsed_time)
            print(f"Request successful, latency: {elapsed_time:.4f}s")
        else:
            failed_requests += 1
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        failed_requests += 1
        print(f"Request failed with error: {str(e)}")

def worker():
    requests_sent = 0
    while requests_sent < (TOTAL_REQUESTS // CONCURRENT_REQUESTS):
        send_request()
        requests_sent += 1
        time.sleep(REQUEST_DELAY)

def main():
    print(f"Starting load test against {SERVICE_URL}")
    print(f"Sending {TOTAL_REQUESTS} requests with {CONCURRENT_REQUESTS} concurrent workers")
    
    start_time = time.time()
    
    threads = []
    for _ in range(CONCURRENT_REQUESTS):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    total_time = time.time() - start_time
    
    print("\nLoad Test Results:")
    print(f"Total requests sent: {successful_requests + failed_requests}")
    print(f"Successful requests: {successful_requests}")
    print(f"Failed requests: {failed_requests}")
    print(f"Total time: {total_time:.2f} seconds")
    
    if response_times:
        avg_latency = sum(response_times) / len(response_times)
        print(f"Average latency: {avg_latency:.4f} seconds")
        print(f"Min latency: {min(response_times):.4f} seconds")
        print(f"Max latency: {max(response_times):.4f} seconds")
    
    print(f"Throughput: {successful_requests / total_time:.2f} requests/second")

if __name__ == "__main__":
    main()