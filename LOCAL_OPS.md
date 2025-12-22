# Local Cloud-Native Development Guide

This guide details how to run the **Joke Creator** application in a "Cloud-Native" way on your local machine, using **Minikube**, **Docker Registry**, and **Helm**. This simulates a production environment (like AKS/EKS) without the cost.

## 🛠️ Prerequisites

Ensure you have the following installed:
1.  **Docker Desktop** (or Docker Engine)
2.  **Minikube**: `brew install minikube`
3.  **Helm**: `brew install helm`
4.  **Kubectl**: `brew install kubernetes-cli`

---

## 🚀 1. Start the Environment

### Start Local Registry
We need a place to push our Docker images. We'll run a registry on port **5000**.
```bash
docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

### Start Minikube (Multi-Node & Insecure Registry)
We start a 2-node cluster and tell it to trust our local registry (HTTP).
```bash
minikube start --nodes 2 -p joke-cluster --insecure-registry "host.minikube.internal:5000"
```

---

## 📦 2. Build & Publish Images

We need to build our images and push them to `localhost:5000`. Minikube will read them from `host.minikube.internal:5000`.

**Backend**:
```bash
docker build -t localhost:5000/joke-backend ./backend
docker push localhost:5000/joke-backend
```

**Frontend**:
```bash
docker build -t localhost:5000/joke-frontend ./frontend
docker push localhost:5000/joke-frontend
```

---

## ⚓ 3. Deploy with Helm

We use **Helm** to deploy our application stack (Backend + Frontend + Postgres).

### Install the Chart
We need to pass our API keys securely.
*(Replace values with your actual keys)*:

```bash
helm install joke-app ./charts/joke-creator \
  --set secrets.openaiApiKey="sk-..." \
  --set secrets.opikApiKey="..."
```

> **Note**: If you change code and rebuild images, upgrade the deployment:
> `kubectl rollout restart deployment joke-app-backend joke-app-frontend`

---

## 🌐 4. Access the Application

Since we are in Minikube, we can't just access `localhost`. We need a tunnel or proxy.

**Method 1: Minikube Service (Easiest)**
This opens the frontend service in your default browser.
```bash
minikube service joke-app-frontend -p joke-cluster
```

**Method 2: Port Forwarding (Manual)**
Forward the frontend service to your localhost:3000.
```bash
kubectl port-forward svc/joke-app-frontend 3000:80
```
Then visit: [http://localhost:3000](http://localhost:3000)

---

## 🔍 5. Debugging & Observability

**Check Pods**:
```bash
kubectl get pods
```

**View Logs**:
```bash
kubectl logs -f label=app=backend
```

**Describe Deployment (Errors)**:
```bash
kubectl describe pod -l app=backend
```

---

## 🧹 Cleanup

Stop the cluster to save resources:
```bash
minikube stop -p joke-cluster
```

Delete the cluster (resets everything):
```bash
minikube delete -p joke-cluster
```
