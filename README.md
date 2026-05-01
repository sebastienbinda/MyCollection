# Projet Hello World - Python + React

Ce projet contient:

- Un backend Python (Flask) qui expose une API `/api/time`.
- Un frontend React (Vite) qui affiche "Hello World" et l'heure recuperee depuis le serveur Python.

## Variables d'environnement (ports)

- `BACKEND_PORT` : port du serveur Python (defaut: `7777`)
- `FRONTEND_PORT` : port du serveur React/Vite (defaut: `7778`)
- `JEUXVIDEO_ODS_PATH` : chemin vers le fichier ODS (defaut: `~/Documents/JeuxVideo-v2.ods`)

Exemple:

```bash
export BACKEND_PORT=5000
export FRONTEND_PORT=5173
export JEUXVIDEO_ODS_PATH=~/Documents/JeuxVideo-v2.ods
```

## Structure

- `backend/` : API Python
- `frontend/` : application React

## 1) Lancer le backend Python

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_PORT=7777 python app.py
```

Le serveur tourne sur `http://localhost:7777` (ou la valeur de `BACKEND_PORT`).

## 2) Lancer le frontend React

Dans un autre terminal:

```bash
cd frontend
npm install
BACKEND_PORT=7777 FRONTEND_PORT=7778 npm run dev
```

Le frontend tourne sur `http://localhost:7778` (ou la valeur de `FRONTEND_PORT`).

## 3) Resultat attendu

Sur la page, tu verras:

- "Hello World"
- un message du backend Python
- l'heure actuelle renvoyee par l'API Python

## Endpoint collections

Le backend expose:

- `GET /collections/JeuxVideo/search`
- `GET /collections/Films/search`

Pour `JeuxVideo`, les donnees sont lues depuis l'onglet `Playstation` du fichier ODS.
Chaque ligne est retournee comme objet JSON avec les colonnes de la feuille.

Exemples:

```bash
curl "http://localhost:7777/collections/JeuxVideo/platforms"
curl "http://localhost:7777/collections/JeuxVideo/column-values?platform=Playstation"
curl "http://localhost:7777/collections/JeuxVideo/search?platform=Playstation"
curl "http://localhost:7777/collections/JeuxVideo/search?platform=Playstation&q=sony"
curl "http://localhost:7777/collections/Films/search?q=inter"
```

## Scripts utilitaires

Depuis la racine:

```bash
./start.sh
./stop.sh
```

Avec ports personnalises:

```bash
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./start.sh
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./stop.sh
```
