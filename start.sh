#!/bin/bash
#  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
# |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
# | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
# | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
# |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
# Projet : MY-COLLECTYION
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
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