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
DOCKER_COMPOSE_LOCAL_FILE="${SCRIPT_DIR}/docker/docker-compose.local.yml"
DOCKER_COMPOSE_ONLINE_FILE="${SCRIPT_DIR}/docker/docker-compose.online.yml"

START_MODE="local"
DEPLOY_ENV="local"
RECREATE_DOCKER_STACK=false

print_usage() {
  echo "Usage: ./start.sh [-d] [-p] [-r]"
  echo "  -d  Demarre la stack Docker locale."
  echo "  -p  Demarre la stack Docker de production online."
  echo "  -r  Reconstruit les images Docker et force la recreation des conteneurs."
}

while getopts "dprh" option; do
  case "$option" in
    d)
      START_MODE="docker"
      ;;
    p)
      START_MODE="docker"
      DEPLOY_ENV="online"
      ;;
    r)
      RECREATE_DOCKER_STACK=true
      ;;
    h)
      print_usage
      exit 0
      ;;
    *)
      print_usage
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
  # Description : demarre les conteneurs Docker Compose et supprime les orphelins.
  # Parametres : aucun, utilise WEB_PORT et les variables Docker Compose existantes.
  # Retour : void, demarre la stack Docker Compose.
  local docker_options=("--remove-orphans")

  if [ "$RECREATE_DOCKER_STACK" = true ]; then
    docker_options+=("--build" "--force-recreate")
  fi

  if [ "$DEPLOY_ENV" = "online" ]; then
    echo "Starting online Docker stack..."
    docker compose -f "$DOCKER_COMPOSE_ONLINE_FILE" up -d "${docker_options[@]}"
  else
    echo "Starting local Docker stack on web port ${WEB_PORT}..."
    WEB_PORT="$WEB_PORT" docker compose -f "$DOCKER_COMPOSE_LOCAL_FILE" up -d "${docker_options[@]}"
  fi
}

if [ "$START_MODE" = "docker" ]; then
  start_docker
else
  start_local
fi
