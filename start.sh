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
WEB_PORT="${WEB_PORT:-8080}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_COMPOSE_FILE="${SCRIPT_DIR}/docker/docker-compose.yml"

START_MODE="local"

while getopts "dh" option; do
  case "$option" in
    d)
      START_MODE="docker"
      ;;
    h)
      echo "Usage: ./start.sh [-d]"
      echo "  -d  Build et demarre la version Docker en recreant les conteneurs."
      exit 0
      ;;
    *)
      echo "Usage: ./start.sh [-d]"
      exit 1
      ;;
  esac
done

start_local() {
  # Description : demarre le backend Flask et le frontend Vite en local.
  # Parametres : aucun.
  # Retour : void, lance les processus en arriere-plan.
  echo "Starting backend..."

  cd "${SCRIPT_DIR}/backend"
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  BACKEND_PORT="$BACKEND_PORT" python app.py &

  echo "Starting frontend..."
  cd "${SCRIPT_DIR}/frontend"
  npm install
  BACKEND_PORT="$BACKEND_PORT" FRONTEND_PORT="$FRONTEND_PORT" npm run dev &
  cd "$SCRIPT_DIR"
}

start_docker() {
  # Description : reconstruit les images Docker et demarre les conteneurs recrees.
  # Parametres : aucun, utilise WEB_PORT et les variables Docker Compose existantes.
  # Retour : void, demarre la stack Docker Compose.
  echo "Building and starting Docker stack on web port ${WEB_PORT}..."
  WEB_PORT="$WEB_PORT" docker compose -f "$DOCKER_COMPOSE_FILE" up -d --build --force-recreate
}

if [ "$START_MODE" = "docker" ]; then
  start_docker
else
  start_local
fi
