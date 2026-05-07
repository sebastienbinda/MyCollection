#!/bin/bash
#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#

BACKEND_PORT="${BACKEND_PORT:-7777}"
FRONTEND_PORT="${FRONTEND_PORT:-7778}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker/docker-compose.yml"

STOP_MODE="local"

while getopts "dh" option; do
  case "$option" in
    d)
      STOP_MODE="docker"
      ;;
    h)
      echo "Usage: ./stop.sh [-d]"
      echo "  -d  Arrete la version Docker avec Docker Compose."
      exit 0
      ;;
    *)
      echo "Usage: ./stop.sh [-d]"
      exit 1
      ;;
  esac
done

stop_local() {
  # Description : arrete les processus locaux ecouteurs des ports backend et frontend.
  # Parametres : aucun.
  # Retour : void, termine les processus detectes.
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
}

stop_docker() {
  # Description : arrete et supprime les conteneurs Docker Compose du projet.
  # Parametres : aucun.
  # Retour : void, arrete la stack Docker Compose.
  echo "Stopping Docker stack..."
  docker compose -f "$DOCKER_COMPOSE_FILE" down
}

if [ "$STOP_MODE" = "docker" ]; then
  stop_docker
else
  stop_local
fi
