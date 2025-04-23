#!/bin/bash
# Script to set up Kubernetes cluster with KServe

echo "Setting up Kubernetes cluster with KServe..."

# Create a KinD cluster
echo "Creating KinD cluster..."
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
istioctl install --set profile=demo -y

# Label the default namespace for Istio injection
kubectl label namespace default istio-injection=enabled

# Install Knative Serving
echo "Installing Knative Serving..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.0/serving-core.yaml

# Wait for Knative to be ready
echo "Waiting for Knative to be ready..."
kubectl wait --for=condition=ready pod -l app=controller -n knative-serving --timeout=300s
kubectl wait --for=condition=ready pod -l app=webhook -n knative-serving --timeout=300s

# Install KServe
echo "Installing KServe..."
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.11.0/kserve.yaml

# Wait for KServe to be ready
echo "Waiting for KServe controller to be ready..."
kubectl wait --for=condition=ready pod -l control-plane=kserve-controller-manager -n kserve --timeout=300s

# Install monitoring tools
echo "Installing Prometheus and Grafana..."
kubectl create namespace monitoring
kubectl apply -f https://raw.githubusercontent.com/kserve/kserve/master/hack/quick_install/prometheus/prometheus-operator/ -n monitoring
kubectl apply -f https://raw.githubusercontent.com/kserve/kserve/master/hack/quick_install/prometheus/prometheus-instance/ -n monitoring

echo "Cluster setup complete!"
echo "You can check the status with: kubectl get pods --all-namespaces"