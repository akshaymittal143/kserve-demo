#!/bin/bash
# Script to install necessary dependencies for KServe demo on macOS

echo "Installing dependencies for KServe demo..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install kubectl
if ! command -v kubectl &> /dev/null; then
    echo "Installing kubectl..."
    brew install kubectl
else
    echo "kubectl already installed."
fi

# Install kind (Kubernetes in Docker)
if ! command -v kind &> /dev/null; then
    echo "Installing kind..."
    brew install kind
else
    echo "kind already installed."
fi

# Install istioctl
if ! command -v istioctl &> /dev/null; then
    echo "Installing istioctl..."
    brew install istioctl
else
    echo "istioctl already installed."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r ../model/requirements.txt

echo "All dependencies installed successfully."
echo "Make sure Docker Desktop is running before proceeding with setup-cluster.sh."