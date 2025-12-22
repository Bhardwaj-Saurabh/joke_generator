# Azure Deployment Guide: Joke Creator

This guide explains how to deploy the **Joke Creator** application to **Azure Kubernetes Service (AKS)** using **Azure Container Registry (ACR)**.

## Prerequisites

1.  **Azure CLI**: [Install Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
2.  **Kubectl**: [Install Kubectl](https://kubernetes.io/docs/tasks/tools/)
3.  **Docker**: Installed and running.

---

## Step 1: Azure Setup

Login to Azure:
```bash
az login
```

Create a Resource Group:
```bash
az group create --name JokeAppGroup --location eastus
```

Create an Azure Container Registry (ACR):
```bash
# Choose a unique name (alphanumeric only)
ACR_NAME=jokecreatorreg$RANDOM
az acr create --resource-group JokeAppGroup --name $ACR_NAME --sku Basic
```

Login to ACR locally:
```bash
az acr login --name $ACR_NAME
```

Get the ACR Login Server name:
```bash
ACR_SERVER=$(az acr list --resource-group JokeAppGroup --query "[0].loginServer" --output tsv)
echo "Your ACR Server is: $ACR_SERVER"
```

---

## Step 2: Build & Push Images

Build and tag images for ACR:

**Backend**:
```bash
docker build -t $ACR_SERVER/joke-backend:latest ./backend
docker push $ACR_SERVER/joke-backend:latest
```

**Frontend**:
```bash
docker build -t $ACR_SERVER/joke-frontend:latest ./frontend
docker push $ACR_SERVER/joke-frontend:latest
```

---

## Step 3: Create Kubernetes Cluster (AKS)

Create the AKS cluster (this takes a few minutes):
```bash
az aks create \
    --resource-group JokeAppGroup \
    --name JokeCluster \
    --node-count 1 \
    --enable-addons monitoring \
    --generate-ssh-keys \
    --attach-acr $ACR_NAME
```

Connect `kubectl` to your new cluster:
```bash
az aks get-credentials --resource-group JokeAppGroup --name JokeCluster
```

---

## Step 4: Deploy to Kubernetes

1.  **Update Manifests**:
    Open `kubernetes/backend.yaml` and `kubernetes/frontend.yaml`.
    Replace `<YOUR_ACR_NAME>.azurecr.io` with your actual login server (e.g., `jokecreatorreg123.azurecr.io`).

2.  **Configure Secrets**:
    Open `kubernetes/secrets.yaml` and paste your real API keys.
    *Note: Do not commit this file to Git!*

3.  **Apply Manifests**:
    ```bash
    kubectl apply -f kubernetes/secrets.yaml
    kubectl apply -f kubernetes/postgres.yaml
    kubectl apply -f kubernetes/backend.yaml
    kubectl apply -f kubernetes/frontend.yaml
    ```

---

## Step 5: Verify & Access

Check the status of your pods:
```bash
kubectl get pods
```

Get the public IP of your Frontend LoadBalancer:
```bash
kubectl get service frontend-service --watch
```
*Wait until the `EXTERNAL-IP` changes from `<pending>` to an actual IP address.*

**Visit the IP in your browser!**

---

## Cleanup (Save Costs)

When you are done, delete the entire resource group to avoid charges:
```bash
az group delete --name JokeAppGroup --yes --no-wait
```
