#!/bin/bash
set -e

echo "Cleaning up existing installations..."
kubectl delete namespace knative-serving --ignore-not-found=true
kubectl delete namespace istio-system --ignore-not-found=true
kubectl delete namespace kserve --ignore-not-found=true

# Wait for namespaces to be fully deleted
echo "Waiting for namespaces to be cleaned up..."
wait_for_namespace_deletion() {
    local namespace=$1
    while kubectl get namespace $namespace >/dev/null 2>&1; do
        echo "Waiting for namespace $namespace to be deleted..."
        sleep 5
    done
}

wait_for_namespace_deletion "knative-serving"
wait_for_namespace_deletion "istio-system"
wait_for_namespace_deletion "kserve"

echo "Installing Istio..."
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=1.17.2 sh -
cd istio-1.17.2
export PATH=$PWD/bin:$PATH
istioctl install -y --set profile=demo
cd ..

echo "Creating Knative Serving namespace..."
kubectl create namespace knative-serving

echo "Installing Knative Serving CRDs..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.1/serving-crds.yaml
sleep 10

echo "Installing Knative Serving core..."
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.10.1/serving-core.yaml
sleep 10

echo "Configuring Knative with Istio..."
kubectl apply -f https://github.com/knative/net-istio/releases/download/knative-v1.10.1/net-istio.yaml
sleep 10

echo "Installing Cert Manager..."
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.11.0/cert-manager.yaml

echo "Waiting for Cert Manager to be ready..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s

echo "Creating KServe namespace..."
kubectl create namespace kserve

echo "Installing KServe CRDs..."
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.10.1/kserve.yaml
sleep 20  # Increased wait time for CRDs to be established

echo "Installing KServe runtime..."
kubectl apply -f https://github.com/kserve/kserve/releases/download/v0.10.1/kserve-runtimes.yaml

echo "Waiting for KServe controller to be ready..."
kubectl wait --for=condition=ready pod -l control-plane=kserve-controller-manager -n kserve --timeout=300s

echo "Verifying installation..."
kubectl get pods -n knative-serving
kubectl get pods -n kserve
kubectl get crd | grep kserve

echo "Checking for any errors in kserve namespace..."
kubectl get events -n kserve --sort-by='.lastTimestamp'