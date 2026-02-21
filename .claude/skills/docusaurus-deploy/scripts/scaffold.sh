#!/bin/bash
set -e

DOCS_DIR=$1

if [ -z "$DOCS_DIR" ]; then
  echo "✗ Usage: scaffold.sh <docs-dir>"
  exit 1
fi

# Create docs directory
mkdir -p "$DOCS_DIR"
cd "$DOCS_DIR"

# Initialize Docusaurus (if not already initialized)
if [ ! -f "package.json" ]; then
  npx create-docusaurus@latest . classic --skip-install > /dev/null 2>&1
  npm install > /dev/null 2>&1
fi

# Create Dockerfile
cat > Dockerfile <<'EOF'
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

echo "✓ Docusaurus site scaffolded"
