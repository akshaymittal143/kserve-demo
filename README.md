# KServe ML Model Deployment Demo

This repository demonstrates deploying ML models on Kubernetes using KServe and Kubeflow Lite components.

For a step-by-step walkthrough, check out [demo.md](demo.md) which provides detailed instructions and examples.

## Workshop Goals

- Deploy and scale ML models with KServe
- Implement canary deployments and A/B testing
- Monitor model performance and health
- Secure model endpoints

## Prerequisites

- macOS with Homebrew 
- Docker Desktop
- Python 3.9+
- kubectl

## Quick Setup

1. Install dependencies:
```bash
./setup/install-dependencies.sh
```

2. Create cluster and install components:
```bash
./scripts/setup_cluster.sh
```

3. Train models:
```bash
pip install -r requirements.txt
python models/train_model_v1.py
python models/train_model_v2.py
```

4. Deploy model:
```bash
kubectl apply -f kubernetes/kserve_deployment.yaml
export SERVICE_URL=$(kubectl get inferenceservice sentiment-classifier -o jsonpath='{.status.url}')
```

5. Test deployment:
```bash
python scripts/test_model.py --url $SERVICE_URL
```

## Key Features

- Model deployment and serving
- Automatic scaling based on traffic
- Canary deployments
- Authentication and security
- Metrics and monitoring

## Advanced Usage

See the [docs/](docs/) folder for detailed guides on:
- Autoscaling configuration
- Canary deployment strategies  
- Authentication setup
- Monitoring and observability

## Project Structure
```
├── kubernetes/     # K8s deployment files
├── models/        # ML model code
├── scripts/       # Utility scripts
└── docs/          # Detailed documentation
```

## Cleanup
```bash
kind delete cluster --name kserve-demo
```

## Troubleshooting

Check the [troubleshooting guide](docs/troubleshooting.md) or open an issue.
