#!/bin/bash
set -e

# Get PostgreSQL pod name
PG_POD=$(kubectl get pods -n postgres -l app.kubernetes.io/name=postgresql -o jsonpath='{.items[0].metadata.name}')

if [ -z "$PG_POD" ]; then
  echo "✗ PostgreSQL pod not found — run deploy.sh first"
  exit 1
fi

# Create tables
kubectl exec -n postgres "$PG_POD" -- psql -U learnflow -d learnflow -c "
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  role VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS progress (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  module INTEGER NOT NULL,
  topic VARCHAR(255),
  mastery_score FLOAT DEFAULT 0,
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS submissions (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  code TEXT,
  result VARCHAR(50),
  submitted_at TIMESTAMP DEFAULT NOW()
);
" > /dev/null 2>&1

echo "✓ Migrations applied"
