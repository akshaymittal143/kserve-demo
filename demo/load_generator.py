import requests
import json
import time
import threading
import random
import argparse
import sys
import os

# Command line arguments
parser = argparse.ArgumentParser(description='Generate load for KServe model to test autoscaling')
parser.add_argument('--hostname', type=str, help='Service hostname (if not provided, will try to get from kubectl)')
parser.add_argument('--requests', type=int, default=500, help='Number of requests to send')
parser.add_argument('--concurrency', type=int, default=10, help='Number of concurrent requests')
parser.add_argument('--delay', type=float, default=0.1, help='Delay between requests in seconds')
args = parser.parse_args()

# Get hostname if not provided
if not args.hostname:
    try:
        import subprocess
        result = subprocess.run(
            ['kubectl', 'get', 'inferenceservice', 'sentiment-classifier', '-o', 'jsonpath={.status.url}'],
            capture_output=True, text=True, check=True
        )
        service_url = result.stdout.strip()
        args.hostname = service_url.split("//")[1]
        print(f"Found service hostname: {args.hostname}")
        
    except (subprocess.CalledProcessError, ImportError) as e:
        print(f"Error getting service hostname: {e}")
        print("Please provide the hostname with --hostname parameter")
        sys.exit(1)

# Configuration
SERVICE_HOST = args.hostname
SERVICE_URL = f"http://{SERVICE_HOST}/v1/models/sentiment-classifier:predict"
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
lock = threading.Lock()  # For thread-safe updates to counters

def send_request():
    global successful_requests, failed_requests
    
    # Create random payload
    num_instances = random.randint(1, 5)  # Random number of instances per request
    instances = [{"text": random.choice(sample_texts)} for _ in range(num_instances)]
    data = {"instances": instances}
    
    headers = {"Content-Type": "application/json"}
    
    try:
        start_time = time.time()
        response = requests.post(SERVICE_URL, headers=headers, data=json.dumps(data), timeout=10)
        elapsed_time = time.time() - start_time
        
        with lock:
            if response.status_code == 200:
                successful_requests += 1
                response_times.append(elapsed_time)
                if successful_requests % 20 == 0:  # Print less frequently
                    print(f"Request successful, latency: {elapsed_time:.4f}s (Success: {successful_requests}, Fail: {failed_requests})")
            else:
                failed_requests += 1
                print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
        with lock:
            failed_requests += 1
            print(f"Request failed with error: {str(e)}")

def worker():
    requests_sent = 0
    requests_per_worker = TOTAL_REQUESTS // CONCURRENT_REQUESTS
    
    while requests_sent < requests_per_worker:
        send_request()
        requests_sent += 1
        time.sleep(REQUEST_DELAY)

def display_progress():
    """Display progress bar during the load test"""
    start_time = time.time()
    expected_duration = (TOTAL_REQUESTS / CONCURRENT_REQUESTS) * REQUEST_DELAY
    
    while True:
        elapsed = time.time() - start_time
        with lock:
            total_completed = successful_requests + failed_requests
        
        if total_completed >= TOTAL_REQUESTS or elapsed > expected_duration * 2:
            break
            
        progress = total_completed / TOTAL_REQUESTS
        bar_length = 30
        filled_length = int(bar_length * progress)
        
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        percent = progress * 100
        
        print(f'\rProgress: |{bar}| {percent:.1f}% Complete ({total_completed}/{TOTAL_REQUESTS})', end='')
        
        time.sleep(1)

def main():
    print(f"Starting load test against {SERVICE_URL}")
    print(f"Sending {TOTAL_REQUESTS} requests with {CONCURRENT_REQUESTS} concurrent workers")
    print(f"Delay between requests: {REQUEST_DELAY}s")
    print("\nThis test will help demonstrate KServe's autoscaling capabilities.")
    print("You can monitor pod count with: kubectl get pods -w\n")
    
    start_time = time.time()
    
    # Start progress display thread
    progress_thread = threading.Thread(target=display_progress)
    progress_thread.daemon = True
    progress_thread.start()
    
    # Start worker threads
    threads = []
    for _ in range(CONCURRENT_REQUESTS):
        t = threading.Thread(target=worker)
        threads.append(t)
        t.start()
    
    # Wait for all threads to complete
    for t in threads:
        t.join()
    
    total_time = time.time() - start_time
    
    print("\n\nLoad Test Results:")
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
    
    print("\nCheck the Kubernetes dashboard or run 'kubectl get pods' to see if autoscaling occurred.")

if __name__ == "__main__":
    main()