#!/bin/bash
set -e

echo "Setting up KServe demo environment..."

# Install Homebrew if not installed
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed"
fi

# Install kind
if ! command -v kind &> /dev/null; then
    echo "Installing kind..."
    brew install kind
else
    echo "kind already installed"
fi

# Install kubectl if needed
if ! command -v kubectl &> /dev/null; then
    echo "Installing kubectl..."
    brew install kubectl
else
    echo "kubectl already installed"
fi

# Create a kind cluster
echo "Creating Kubernetes cluster with kind..."
cat <<EOF | kind create cluster --name kserve-demo --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
EOF

# Install Istio
echo "Installing Istio..."
brew install istioctl
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled

# Install KServe
echo "Installing KServe..."
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve.yaml

# Install Knative Serving
echo "Installing Knative Serving..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.0/serving-core.yaml

# Install Prometheus for monitoring
echo "Installing Prometheus..."
kubectl create namespace monitoring
kubectl apply -f https://raw.githubusercontent.com/kserve/kserve/master/hack/quick_install/prometheus/prometheus-operator/ -n monitoring
kubectl apply -f https://raw.githubusercontent.com/kserve/kserve/master/hack/quick_install/prometheus/prometheus-instance/ -n monitoring

echo "Waiting for KServe to be ready..."
kubectl wait --for=condition=ready pod -l app=kserve -n kserve --timeout=300s

echo "Setup complete! KServe is now ready to use."
echo "Use 'kubectl config use-context kind-kserve-demo' to switch to this cluster."