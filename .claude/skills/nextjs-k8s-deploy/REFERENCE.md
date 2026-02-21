# nextjs-k8s-deploy Reference

## Purpose
Builds a Next.js app into a Docker image and deploys it to Kubernetes on Minikube.

## How It Works

### build.sh <app-dir>
- Takes app directory as argument
- Runs: docker build -t learnflow-frontend:latest <app-dir>
- Expects Dockerfile in app directory
- Prints "✓ Image built: learnflow-frontend:latest"

### load_image.sh
- Loads Docker image into Minikube's internal registry
- Runs: minikube image load learnflow-frontend:latest
- Required because Minikube doesn't use Docker's registry
- Prints "✓ Image loaded into Minikube"

### deploy.sh
- Creates learnflow namespace (idempotent)
- Applies inline YAML with:
  - **Deployment**: learnflow-frontend, 1 replica, imagePullPolicy: Never
  - **Service**: NodePort on port 80 → 3000
- Prints "✓ Frontend deployed"

### get_url.py
- Runs: minikube service learnflow-frontend -n learnflow --url
- Extracts URL from output
- Prints "✓ Frontend live at <url>"

## Configuration
- Namespace: learnflow
- Image: learnflow-frontend:latest
- Container port: 3000
- Service port: 80 (NodePort)
- Image pull policy: Never (uses Minikube local images)

## Token Efficiency
- build.sh: docker output hidden, prints only "✓ Image built..." (5 tokens)
- load_image.sh: prints only "✓ Image loaded..." (4 tokens)
- deploy.sh: kubectl output hidden, prints only "✓ Frontend deployed" (3 tokens)
- get_url.py: prints only "✓ Frontend live at <url>" (6 tokens)

## Usage
```bash
# Full deployment pipeline
bash .claude/skills/nextjs-k8s-deploy/scripts/build.sh ./frontend
bash .claude/skills/nextjs-k8s-deploy/scripts/load_image.sh
bash .claude/skills/nextjs-k8s-deploy/scripts/deploy.sh
python .claude/skills/nextjs-k8s-deploy/scripts/get_url.py
```

## Expected Dockerfile
The Next.js app directory should contain a Dockerfile like:
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting
- If build fails: check Dockerfile exists in app-dir
- If pod stuck: check image was loaded with `minikube image ls`
- If service not accessible: check NodePort with `kubectl get svc -n learnflow`
- To rebuild: delete deployment, rebuild image, redeploy

## Dependencies
- Docker installed
- Minikube running
- kubectl configured
- Next.js app with Dockerfile
