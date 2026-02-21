# docusaurus-deploy Reference

## Purpose
Scaffolds a Docusaurus documentation site and deploys it to Kubernetes on Minikube.

## How It Works

### scaffold.sh <docs-dir>
- Creates docs directory
- Initializes Docusaurus with: npx create-docusaurus@latest . classic
- Installs dependencies
- Creates Dockerfile with:
  - Builder stage: Node.js 18, npm install, npm run build
  - Runtime stage: nginx:alpine, serves static build
  - Exposes port 80
- Prints "✓ Docusaurus site scaffolded"

### build.sh <docs-dir>
- Builds Docker image: learnflow-docs:latest
- Loads image into Minikube
- Prints "✓ Docs image built and loaded"

### deploy.sh
- Creates learnflow namespace (idempotent)
- Applies inline YAML with:
  - **Deployment**: learnflow-docs, 1 replica, imagePullPolicy: Never
  - **Service**: NodePort on port 80
- Prints "✓ Docs deployed"

### get_url.py
- Runs: minikube service learnflow-docs -n learnflow --url
- Extracts URL from output
- Prints "✓ Docs live at <url>"

## Configuration
- Namespace: learnflow
- Image: learnflow-docs:latest
- Container port: 80
- Service port: 80 (NodePort)
- Image pull policy: Never (uses Minikube local images)

## Token Efficiency
- scaffold.sh: all npm output hidden, prints only "✓ Docusaurus site scaffolded" (4 tokens)
- build.sh: docker output hidden, prints only "✓ Docs image built and loaded" (6 tokens)
- deploy.sh: kubectl output hidden, prints only "✓ Docs deployed" (3 tokens)
- get_url.py: prints only "✓ Docs live at <url>" (6 tokens)

## Usage
```bash
# Full deployment pipeline
bash .claude/skills/docusaurus-deploy/scripts/scaffold.sh ./docs
bash .claude/skills/docusaurus-deploy/scripts/build.sh ./docs
bash .claude/skills/docusaurus-deploy/scripts/deploy.sh
python .claude/skills/docusaurus-deploy/scripts/get_url.py
```

## Docusaurus Structure
After scaffolding, the docs directory contains:
```
docs/
├── docs/               # Markdown documentation files
├── blog/               # Blog posts
├── src/                # React components
├── static/             # Static assets
├── docusaurus.config.js  # Configuration
├── package.json
└── Dockerfile
```

## Customization
Edit `docusaurus.config.js` to:
- Change site title and tagline
- Add custom navbar items
- Configure plugins
- Set theme options

## Troubleshooting
- If scaffold fails: ensure Node.js 18+ and npm are installed
- If build fails: check Dockerfile was created
- If pod stuck: check image was loaded with `minikube image ls`
- If service not accessible: check NodePort with `kubectl get svc -n learnflow`
- To rebuild: delete deployment, rebuild image, redeploy

## Dependencies
- Node.js 18+ and npm
- Docker installed
- Minikube running
- kubectl configured
