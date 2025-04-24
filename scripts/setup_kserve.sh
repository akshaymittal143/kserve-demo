#!/bin/bash
set -e

echo "Setting up KServe demo environment..."

# Helper function to check cluster connection
check_kubernetes_connection() {
    if ! kubectl cluster-info &> /dev/null; then
        echo "No Kubernetes cluster found or connection failed"
        echo "Creating new cluster..."
        return 1
    fi
    return 0
}

# Delete existing cluster if it exists
delete_existing_cluster() {
    if kind get clusters | grep -q "kserve-demo"; then
        echo "Deleting existing kserve-demo cluster..."
        kind delete cluster --name kserve-demo
        sleep 5  # Wait for cleanup
    fi
}

# Install required tools first
for tool in brew kind kubectl istioctl helm; do
    if ! command -v $tool &> /dev/null; then
        echo "Installing $tool..."
        case $tool in
            "brew")
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
                ;;
            "kind"|"kubectl"|"istioctl")
                brew install $tool
                ;;
            "helm")
                brew install helm
                ;;
        esac
    else
        echo "$tool already installed"
    fi
done

# Create new cluster
delete_existing_cluster

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

# Verify cluster is running
echo "Verifying cluster connection..."
if ! check_kubernetes_connection; then
    echo "Failed to create cluster. Exiting."
    exit 1
fi

echo "Cluster is ready. Continuing with installation..."

# Install Istio
echo "Installing Istio..."
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.17.2 sh -
cd istio-1.17.2
export PATH=$PWD/bin:$PATH
istioctl install -y --set profile=demo
kubectl label namespace default istio-injection=enabled
cd ..

# Install Knative Serving
echo "Installing Knative Serving..."
kubectl create namespace knative-serving
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.1/serving-crds.yaml
sleep 10
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.1/serving-core.yaml
sleep 10
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.10.1/net-istio.yaml
sleep 10

# Install Cert Manager
echo "Installing Cert Manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml
echo "Waiting for Cert Manager to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

# Install KServe
echo "Installing KServe..."
kubectl create namespace kserve
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.10.1/kserve.yaml
sleep 20
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.10.1/kserve-runtimes.yaml

# Install Prometheus for monitoring
echo "Installing Prometheus..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
kubectl create namespace monitoring
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring

# Wait for all components to be ready
echo "Waiting for all components to be ready..."
kubectl wait --for=condition=ready pod -l control-plane=kserve-controller-manager -n kserve --timeout=300s
kubectl wait --for=condition=ready pod --all -n knative-serving --timeout=300s

# Verify installation
echo "Verifying installation..."
for ns in knative-serving kserve monitoring; do
    echo "Checking pods in $ns namespace:"
    kubectl get pods -n $ns
done

echo "Checking KServe CRDs..."
kubectl get crd | grep kserve

echo "Setup complete! KServe is now ready to use."
echo "Use 'kubectl config use-context kind-kserve-demo' to switch to this cluster."