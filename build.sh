#!/usr/bin/env bash
# Build Script for Render.com

# exit on error
set -o errexit

echo "Installing Node.js dependencies for frontend..."
cd web-player
npm install

echo "Building Vite frontend..."
npm run build
cd ..

echo "Installing Python dependencies for backend..."
pip install --upgrade pip
pip install -r python_iptv/requirements.txt
pip install gunicorn

echo "Build complete."
