# KServe ML Model Deployment Demo

This repository demonstrates how to deploy, scale, and monitor machine learning models on Kubernetes using KServe and Kubeflow Lite components.

Workshop Goals:

- Understand KServe's role in the ML on Kubernetes stack.
- Deploy Scikit-learn and HuggingFace models using KServe.
- Demonstrate autoscaling based on traffic load.
- Perform a canary rollout to manage model versions.
- Discuss observability and security options.

## Prerequisites

- macOS with Homebrew installed
- Docker Desktop
- Python 3.9+
- pip

## Quick Start
### 1. Environment Setup
    1. Install dependencies:
    ```bash
    ./setup/install-dependencies.sh
    ```

    2. Set up the Kubernetes cluster with KServe:
    Run the setup script to create a local Kubernetes cluster and install required components:

        ```bash
        ./scripts/setup_cluster.sh
        ```
        #### Note:This script will:
        - Install kind (Kubernetes in Docker)
        - Create a Kubernetes cluster
        - Install Istio service mesh
        - Install KServe
        - Install Knative Serving
        - Install Prometheus for monitoring

### 2.  Train the sentiment analysis model:
Train the initial and improved models:
   ```bash
        # Install dependencies
        pip install scikit-learn pandas numpy joblib

        # Train models
        python models/train_model_v1.py
        python models/train_model_v2.py
   ```


### 3. Build and push the Docker image:

### 4. Deploy with KServe
Basic deployment:
```bash
# Replace ${DOCKER_USERNAME} in the YAML files with your Docker username
sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_deployment.yaml
kubectl apply -f kubernetes/kserve_deployment.yaml

# Get the service URL
SERVICE_HOSTNAME=$(kubectl get inferenceservice sentiment-classifier -o jsonpath='{.status.url}' | cut -d "/" -f 3)
echo $SERVICE_HOSTNAME
```

#### Test the deployed model:
`bashpython scripts/test_model.py --hostname $SERVICE_HOSTNAME`

### 5. Demo Autoscaling
```bash
    # Update the YAML file
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_autoscaling.yaml
    kubectl apply -f kubernetes/kserve_autoscaling.yaml

    # Generate load to trigger autoscaling
    python scripts/load_generator.py --hostname $SERVICE_HOSTNAME --requests 1000 --concurrency 20

    # Check the scaling
    kubectl get pods -w
```
### 6. Demo Canary Deployment
```bash
    # Update the YAML file
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_canary.yaml
    kubectl apply -f kubernetes/kserve_canary.yaml

    # Test the canary deployment
    python scripts/test_model.py --hostname $SERVICE_HOSTNAME
```
### 7. Demo Authentication
```bash
    # Update the YAML file
    sed -i '' "s/\${DOCKER_USERNAME}/$DOCKER_USERNAME/g" kubernetes/kserve_auth.yaml
    kubectl apply -f kubernetes/kserve_auth.yaml

    # Get the service URL
    AUTH_SERVICE_HOSTNAME=$(kubectl get inferenceservice sentiment-classifier-auth -o jsonpath='{.status.url}' | cut -d "/" -f 3)

    # Test with auth
    python scripts/test_model.py --hostname $AUTH_SERVICE_HOSTNAME --auth
```

#### Cleanup
Delete the Kubernetes cluster:

```
bashkind delete cluster --name kserve-demo
```
## Demo Features

- **Basic Model Deployment**: Deploy a scikit-learn sentiment analysis model
- **Autoscaling**: Observe how KServe scales pods based on traffic
- **Canary Deployment**: Test traffic splitting between model versions
- **Authentication**: Secure model endpoints with basic auth
- **Observability**: View metrics in Prometheus and Grafana

## Troubleshooting

If you encounter issues:

1. Check pod status:
   ```bash
   kubectl get pods
   kubectl describe pod <pod-name>
   ```

2. View logs:
   ```bash
   kubectl logs -l serving.kserve.io/inferenceservice=sentiment-classifier
   ```

3. Ensure no port conflicts:
   ```bash
   lsof -i :80
   ```

## Clean Up

To delete all resources:
```bash
kind delete cluster --name kserve-demo
```
Project Structure:

```bash
kserve-demo/
├── README.md                        # Project documentation
├── setup/
│   ├── install-dependencies.sh      # Script to install necessary tools  
│   └── setup-cluster.sh             # Script to set up K8s cluster with KServe
├── model/
│   ├── train_model.py               # Script to train the sentiment model
│   ├── model_server.py              # Flask server for model inference
│   └── requirements.txt             # Python dependencies
├── kubernetes/
│   ├── inference-service.yaml       # Basic KServe deployment
│   ├── inference-service-canary.yaml # Canary deployment config
│   ├── auth-secret.yaml             # Authentication secret
│   └── inference-service-auth.yaml  # Deployment with auth
└── demo/
    ├── test_model.py                # Basic test script
    └── load_generator.py            # Script to generate traffic
```