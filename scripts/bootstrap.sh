#!/bin/sh
# Resolve all dependencies that the application requires to run.

# Stop on errors
set -e

cd "$(realpath "$(dirname "$0")/..")"

if [ ! -n "$VIRTUAL_ENV" ]; then
  . .venv/bin/activate
fi

echo "Installing development dependencies..."
uv sync --locked --group dev
