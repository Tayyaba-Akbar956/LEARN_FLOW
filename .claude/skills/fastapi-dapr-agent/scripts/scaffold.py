#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def scaffold_service(service_name):
    """Scaffold a FastAPI + Dapr microservice"""

    # Create service directory
    service_dir = f"services/{service_name}"
    os.makedirs(service_dir, exist_ok=True)

    # main.py
    main_py = f"""from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/health")
def health():
    return {{"status": "ok", "service": "{service_name}"}}

from typing import Any
from fastapi import Request

@app.post("/invoke")
async def invoke(request: Request):
    data = await request.json()
    return {{"message": "Received", "data": data}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    # requirements.txt
    requirements = """fastapi==0.109.0
uvicorn==0.27.0
dapr==1.12.0
openai==1.12.0
"""

    # Dockerfile
    dockerfile = f"""FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

CMD ["python", "main.py"]
"""

    # k8s-deployment.yaml
    k8s_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: learnflow
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {service_name}
  template:
    metadata:
      labels:
        app: {service_name}
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "{service_name}"
        dapr.io/app-port: "8000"
    spec:
      containers:
      - name: {service_name}
        image: {service_name}:latest
        imagePullPolicy: Never
        ports:
        - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: learnflow
spec:
  selector:
    app: {service_name}
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
"""

    # Write files
    with open(f"{service_dir}/main.py", 'w') as f:
        f.write(main_py)

    with open(f"{service_dir}/requirements.txt", 'w') as f:
        f.write(requirements)

    with open(f"{service_dir}/Dockerfile", 'w') as f:
        f.write(dockerfile)

    with open(f"{service_dir}/k8s-deployment.yaml", 'w') as f:
        f.write(k8s_yaml)

    print(f"✓ Service {service_name} scaffolded")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("✗ Usage: scaffold.py <service-name>")
        sys.exit(1)

    sys.exit(scaffold_service(sys.argv[1]))
