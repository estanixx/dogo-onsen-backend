#!/bin/sh
set -e

# Working directory is /usr/src/app (mounted project)
cd /usr/src/app || exit 1

# Install test deps if requirements-dev exists
if [ -f requirements-dev.txt ]; then
  pip install -r requirements-dev.txt || true
fi

# Run pytest in the mounted tests folder
pytest -q
