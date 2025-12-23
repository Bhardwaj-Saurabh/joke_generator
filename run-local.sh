#!/bin/bash
set -e  # Exit on any error

echo "🚀 Joke Creator - Local Kubernetes Deployment Script"
echo "===================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${GREEN}▶ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check prerequisites
print_step "Checking prerequisites..."

if ! command -v minikube &> /dev/null; then
    print_error "minikube not found. Install it with: brew install minikube"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    print_error "helm not found. Install it with: brew install helm"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "docker not found. Please install Docker Desktop"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl not found. Install it with: brew install kubernetes-cli"
    exit 1
fi

echo "✓ All prerequisites installed"

# Check for .env file
if [ ! -f "backend/.env" ]; then
    print_error ".env file not found in backend/"
    echo "Please create backend/.env with your API keys:"
    echo "  cp backend/.env.example backend/.env"
    echo "  # Then edit backend/.env and add your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat backend/.env | grep -v '^#' | xargs)

if [ -z "$OPENAI_API_KEY" ]; then
    print_error "OPENAI_API_KEY not set in backend/.env"
    exit 1
fi

# Start local registry
print_step "Starting local Docker registry..."
if ! docker ps | grep -q "registry"; then
    docker run -d -p 5000:5000 --restart=always --name registry registry:2 2>/dev/null || true
    echo "✓ Registry started on localhost:5000"
else
    echo "✓ Registry already running"
fi

# Start Minikube
print_step "Starting Minikube cluster..."
if minikube status -p joke-cluster &>/dev/null; then
    echo "✓ Cluster already running"
else
    minikube start --nodes 2 -p joke-cluster --insecure-registry "host.minikube.internal:5000"
fi

# Set context
minikube profile joke-cluster

# Build and push images
print_step "Building Docker images..."
echo "  - Building backend..."
docker build -t localhost:5000/joke-backend ./backend

echo "  - Building frontend..."
docker build -t localhost:5000/joke-frontend ./frontend

print_step "Pushing images to local registry..."
docker push localhost:5000/joke-backend
docker push localhost:5000/joke-frontend

# Deploy with Helm
print_step "Deploying application with Helm..."
helm upgrade --install joke-app ./charts/joke-creator \
  --set secrets.openaiApiKey="$OPENAI_API_KEY" \
  --set secrets.opikApiKey="${OPIK_API_KEY:-dummy}" \
  --wait

# Wait for pods to be ready
print_step "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend --timeout=120s

# Get status
print_step "Deployment Status:"
kubectl get pods

echo ""
echo "===================================================="
echo -e "${GREEN}✓ Application deployed successfully!${NC}"
echo "===================================================="
echo ""
echo "To access the application, run:"
echo -e "${YELLOW}  minikube service joke-app-frontend -p joke-cluster${NC}"
echo ""
echo "Or use port-forward:"
echo -e "${YELLOW}  kubectl port-forward svc/joke-app-frontend 8080:80${NC}"
echo -e "  Then visit: ${GREEN}http://localhost:8080${NC}"
echo ""
echo "To view logs:"
echo "  kubectl logs -f -l app=backend"
echo ""
echo "To view Grafana (Observability):"
echo "  kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring"
echo "  Username: admin"
echo "  Password: $(kubectl get secret --namespace monitoring monitoring-grafana -o jsonpath="{.data.admin-password}" | base64 -d 2>/dev/null || echo 'Run the command above to get password')"
echo ""
