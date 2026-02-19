#!/bin/bash

# Load .env if it exists, skipping read-only variables
if [ -f .env ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    [[ "$line" =~ ^#.*$ ]] && continue
    [[ "$line" =~ ^[[:space:]]*$ ]] && continue
    key=$(echo "$line" | cut -d '=' -f 1)
    # Check if variable is read-only in bash
    if ! readonly -p | grep -qE "declare -[a-z]*r[a-z]* $key="; then
      export "$line"
    fi
  done < .env
else
  echo "Error: .env file not found. Please copy .env.example to .env and configure it."
  exit 1
fi

# Validate PORTAFOLIO_PATH
if [ -z "$PORTAFOLIO_PATH" ]; then
  echo "Error: PORTAFOLIO_PATH is not set in .env"
  exit 1
fi

if [ ! -d "$PORTAFOLIO_PATH" ]; then
  echo "Creating portfolio directory at $PORTAFOLIO_PATH..."
  mkdir -p "$PORTAFOLIO_PATH"
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
  echo "Error: docker-compose (or docker compose) is not installed."
  exit 1
fi

# Optional: Check connectivity to external services (fail silently but warn)
echo "Checking external services..."
curl -s --connect-timeout 2 $COMFYUI_HOST > /dev/null || echo "Warning: ComfyUI ($COMFYUI_HOST) not reachable."
curl -s --connect-timeout 2 $OLLAMA_HOST > /dev/null || echo "Warning: Ollama ($OLLAMA_HOST) not reachable."

echo "Starting Tlacuilo environment..."
docker compose up -d --build

echo "Services started in detached mode."
echo "Use 'docker compose logs -f' to view output."
