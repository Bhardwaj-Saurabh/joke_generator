# Module 3: Cloud-Native Deployment & DevOps ☸️

This is the advanced class. We move from "Running Docker" to "Orchestrating a Fleet" using **Kubernetes (K8s)**.

---

## 1. Kubernetes Concepts
Docker runs one container. Kubernetes manages **Thousands**.

*   **Pod**: The smallest unit. A wrapper around your container.
*   **Deployment**: Manages Pods.
    *   "Make sure 3 copies of Backend are always running."
    *   If one crashes, the Deployment starts a new one immediately (Self-healing).
*   **Service**: The stable "Phone Number".
    *   Pods come and go (get new IPs). The Service gives a static IP to reach them.
*   **Secret**: An encrypted vault for passwords (`OPENAI_API_KEY`). K8s injects them into Pods as environment variables safely.

## 2. Helm: The Package Manager
Writing K8s YAML files manually is tedious. **Helm** is like `pip` or `npm` for Kubernetes.
*   **Charts**: A folder containing templates (`deployment.yaml`, `service.yaml`).
*   **Values**: A `values.yaml` file where you configure settings.
    ```yaml
    # values.yaml
    backend:
      replicaCount: 5  # Change this to scale up!
    ```
*   **Templating**:
    Helm replaces `{{ .Values.backend.replicaCount }}` with `5` and generates the final YAML. This lets you reuse the same code for Dev, Staging, and Production.

## 3. Observability: Prometheus & Grafana
How do you know if your app is healthy?
*   **Prometheus**: The "Scraper". It visits `/metrics` on your backend every 15 seconds and records data (e.g., "Request count = 50").
*   **Grafana**: The "Dashboard". It reads Prometheus data and draws beautiful graphs.
*   **Instrumentation**: The code we added to `main.py` is what exposes the data for Prometheus to find.

## 4. CI/CD: The Automation Pipeline
We used **GitHub Actions** to automate the workflow.
See `.github/workflows/ci-cd.yaml`:

1.  **Checkout**: Git clone the code.
2.  **Test**: Run `pytest`. If tests fail, **STOP**. Do not deploy broken code.
3.  **Login**: Authenticate with Docker Hub.
4.  **Build**: Run `docker build`.
5.  **Push**: Upload the image to the Registry.

**The "Cloud Native" Flow:**
1.  You push code to GitHub.
2.  GitHub Actions builds a new Image (e.g., `v2`).
3.  You run `helm upgrade`.
4.  Kubernetes notices the new image `v2`.
5.  It starts new Pods with `v2` and gracefully shuts down `v1` Pods (Zero Downtime Deployment).

---
## 🎓 Final Exam
1.  Commit a change to the code (e.g., change the frontend title).
2.  Watch the GitHub Action turn Green.
3.  Pull the new image locally: `docker pull aryansaurabhbhardwaj/joke-frontend:latest`.
4.  Upgrade your local cluster:
    ```bash
    helm upgrade joke-app ./charts/joke-creator \
      --set secrets.openaiApiKey="..." \
      --set secrets.opikApiKey="..."
    ```
5.  Refresh your browser. You should see the change immediately!
