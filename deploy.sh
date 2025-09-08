#!/bin/bash
# =========================================
# deploy.sh - Deploy FastAPI API from subfolder on Azure
# =========================================

# Exit immediately if a command fails
set -e

# Navigate to the subfolder containing your FastAPI app
cd food101_api_starterModel || { echo "Subfolder 'food101_api' not found!"; exit 1; }

# Optional: create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies from requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Start FastAPI app using Gunicorn + Uvicorn workers
# Azure dynamically assigns the port using $PORT
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
