#!/bin/bash

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
