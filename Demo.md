# KServe Demo Guide

A step-by-step guide for deploying ML models using KServe on Kubernetes.

## Running the Demo

Follow these steps to run the demo after setting up all required files.

### Step 1: Environment Setup

1. Open Terminal and navigate to your project folder:
    ```bash
    cd path/to/kserve-demo
    ```

2. Run the setup script to create your Kubernetes environment:
    ```bash
    ./scripts/setup_cluster.sh
    ```
    This will take a few minutes to complete while installing Kubernetes components (kind, Istio, KServe, Knative).

3. Verify the installation:
    ```bash
    kubectl get pods -A
    ```
    You should see pods running in various namespaces including kserve and knative-serving.

### Step 2: Train the ML Models

1. Install Python dependencies:
    ```bash
    pip install scikit-learn pandas numpy joblib
    ```

2. Train both model versions:
    ```bash
    python models/train_model_v1.py
    python models/train_model_v2.py
    ```
    This creates two directories: `sentiment-model-v1` and `sentiment-model-v2`, each containing a trained model.

### Step 3: Build Docker Images

1. Set your Docker username:
    ```bash
    export DOCKER_USERNAME=your-username
    ```

2. Build the model Docker images:
    ```bash
    # Build v1
    docker build -t $DOCKER_USERNAME/sentiment-model:v1 -f docker/Dockerfile.v1 .
    
    # Build v2
    docker build -t $DOCKER_USERNAME/sentiment-model:v2 -f docker/Dockerfile.v2 .
    ```

3. Push images to Docker Hub:
    ```bash
    docker login
    docker push $DOCKER_USERNAME/sentiment-model:v1
    docker push $DOCKER_USERNAME/sentiment-model:v2
    ```

### Step 4: Deploy the Model with KServe

1. Update YAML with Docker username:
    ```bash
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_deployment.yaml
    ```

2. Apply deployment:
    ```bash
    kubectl apply -f kubernetes/kserve_deployment.yaml
    ```

3. Check deployment status:
    ```bash
    kubectl get inferenceservice
    ```

4. Test the model:
    ```bash
    export SERVICE_HOSTNAME=$(kubectl get inferenceservice sentiment-classifier -o jsonpath='{.status.url}' | cut -d "/" -f 3)
    python scripts/test_model.py --hostname $SERVICE_HOSTNAME
    ```

### Step 5: Demonstrate Autoscaling

1. Apply autoscaling config:
    ```bash
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_autoscaling.yaml
    kubectl apply -f kubernetes/kserve_autoscaling.yaml
    ```

2. Monitor pods in a new terminal:
    ```bash
    kubectl get pods -w
    ```

3. Run load test:
    ```bash
    python scripts/load_generator.py --hostname $SERVICE_HOSTNAME --requests 1000 --concurrency 20
    ```

### Step 6: Demonstrate Canary Deployment

1. Apply canary config:
    ```bash
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_canary.yaml
    kubectl apply -f kubernetes/kserve_canary.yaml
    ```

2. Test traffic splitting:
    ```bash
    python scripts/test_model.py --hostname $SERVICE_HOSTNAME
    ```

### Step 7: Demonstrate Authentication

1. Apply auth config:
    ```bash
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_auth.yaml
    kubectl apply -f kubernetes/kserve_auth.yaml
    ```

2. Test with and without auth:
    ```bash
    export AUTH_SERVICE_HOSTNAME=$(kubectl get inferenceservice sentiment-classifier-auth -o jsonpath='{.status.url}' | cut -d "/" -f 3)
    
    # With auth (should succeed)
    python scripts/test_model.py --hostname $AUTH_SERVICE_HOSTNAME --auth
    
    # Without auth (should fail)
    python scripts/test_model.py --hostname $AUTH_SERVICE_HOSTNAME
    ```

## Expected Outcomes

- Basic Deployment: Model deployment and prediction serving
- Autoscaling: Automatic pod scaling under load
- Canary Deployment: Traffic splitting between versions
- Authentication: Secured model endpoints

## Troubleshooting

- For ImagePullBackOff: Verify Docker images accessibility
- For InferenceService issues: Use `kubectl describe inferenceservice sentiment-classifier`
- For networking: Check Istio with `kubectl get gateway -A` and `kubectl get virtualservice -A`
- For pod issues: Use `kubectl logs <pod-name>`

## Cleanup

Remove all resources:
```bash
kind delete cluster --name kserve-demo
```