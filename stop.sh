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

echo "Stopping backend (port ${BACKEND_PORT})..."
BACKEND_PIDS=$(lsof -ti :"$BACKEND_PORT")
if [ -n "$BACKEND_PIDS" ]; then
  echo "$BACKEND_PIDS" | xargs kill
  echo "Backend stopped."
else
  echo "No backend process found on port ${BACKEND_PORT}."
fi

echo "Stopping frontend (port ${FRONTEND_PORT})..."
FRONTEND_PIDS=$(lsof -ti :"$FRONTEND_PORT")
if [ -n "$FRONTEND_PIDS" ]; then
  echo "$FRONTEND_PIDS" | xargs kill
  echo "Frontend stopped."
else
  echo "No frontend process found on port ${FRONTEND_PORT}."
fi
