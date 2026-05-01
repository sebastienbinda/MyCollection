#!/bin/bash
BACKEND_PORT="${BACKEND_PORT:-7777}"
FRONTEND_PORT="${FRONTEND_PORT:-7778}"

echo "Starting backend..."

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_PORT="$BACKEND_PORT" python app.py &

echo "Starting frontend..."
cd ../frontend
npm install
BACKEND_PORT="$BACKEND_PORT" FRONTEND_PORT="$FRONTEND_PORT" npm run dev &
cd ..