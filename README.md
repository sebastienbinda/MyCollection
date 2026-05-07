<!--
    ____ _                 _  ____      _ _           _   _             ___
   / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
  | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
  | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
   \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
                                                                             |_|   |_|
  Projet : CloudCollectionApp
  Date de creation : 2026-05-03
  Auteurs : Codex et Binda Sébastien
-->
# CloudCollectionApp

> **Note IA**  
> Le code de ce projet a ete genere et modifie avec l'aide de **Codex**, l'agent de developpement d'**OpenAI** base sur **GPT-5**.

Application web personnelle pour consulter, rechercher et maintenir une collection de jeux video stockee dans un fichier LibreOffice Calc `.ods`.

Le projet transforme un fichier ODS existant en interface web : tableau de bord, statistiques par plateforme, recherche globale de jeux, consultation par onglet plateforme et formulaire d'ajout de nouveaux jeux.

## Objectif

L'objectif est de garder le fichier ODS comme source de verite tout en offrant une interface plus confortable pour :

- visualiser les statistiques de l'onglet `Accueil`
- naviguer dans la collection par plateforme
- filtrer les jeux par colonnes
- rechercher un jeu par nom sur toutes les plateformes
- ajouter un jeu dans le bon onglet du fichier ODS en conservant le style existant

## Fonctionnalites

- Page d'accueil avec statistiques globales issues de l'onglet `Accueil`
- Cartes plateformes avec image de fond extraite depuis chaque onglet ODS
- Recherche globale par nom de jeu, toutes plateformes confondues
- Page plateforme accessible directement par URL, par exemple `/?platform=Switch`
- Tableau filtrable par colonne, avec filtres specifiques pour les dates et studios
- Bandeau plateforme avec image, nombre de jeux, valeur, prix moyen et nombre de studios
- Page `/add-game` avec formulaire d'ajout
- Suggestions de valeurs existantes pour `Studio` et `Version`
- Ecriture backend dans le fichier ODS avec sauvegarde automatique avant modification

## Architecture Technique

Le projet est separe en deux applications :

- `backend/` : API Python Flask
- `frontend/` : application React construite avec Vite

Le frontend communique avec le backend via les routes `/collections/...`. En developpement, Vite proxifie ces routes vers Flask grace a `frontend/vite.config.js`.

### Backend

Technologies :

- Python
- Flask
- Flask-Cors
- pandas
- odfpy
- `zipfile` et `xml.etree.ElementTree` pour lire et modifier le contenu ODS

Fichiers principaux :

- `backend/app.py` : routes HTTP Flask
- `backend/services/jeu_video_service.py` : lecture, recherche, extraction d'images et ecriture du fichier ODS
- `backend/models/jeu_video.py` : normalisation des lignes de jeux video
- `backend/models/collection_types.py` : types de collections supportes

Le service `JeuVideoService` lit les donnees dans le fichier ODS. Pour les onglets de plateformes, les colonnes de jeux sont lues dans la plage logique `F:M`, avec la ligne d'en-tete a l'index 5.

Pour l'ajout d'un jeu, le backend :

- cree une sauvegarde du fichier ODS original
- ouvre le fichier ODS comme archive ZIP
- modifie `content.xml`
- trouve l'onglet de la plateforme selectionnee
- clone une ligne de jeu existante pour conserver le style
- remplit les cellules du nouveau jeu
- reecrit le fichier ODS

### Frontend

Technologies :

- React
- Vite
- CSS classique dans `frontend/src/styles.css`

Fichiers principaux :

- `frontend/src/App.jsx` : application React, navigation, pages et appels API
- `frontend/src/styles.css` : styles de l'interface
- `frontend/vite.config.js` : configuration Vite et proxy backend

L'application gere trois vues principales :

- accueil
- detail d'une plateforme
- ajout d'un jeu

La navigation reste volontairement simple et utilise l'URL :

- `/` : accueil
- `/?platform=Playstation%204` : vue d'une plateforme
- `/add-game` : formulaire d'ajout

## Fichier ODS

Par defaut, le backend cherche le fichier :

- `collection.ods` a la racine du projet

Il est aussi possible de forcer le chemin avec la variable :

```bash
export JEUXVIDEO_ODS_PATH=/chemin/vers/collection.ods
```

Structure attendue :

- onglet `Accueil` : statistiques par plateforme
- onglet `Liste de souhaits` : ignore dans la navigation principale
- un onglet par plateforme : `Playstation`, `Playstation 4`, `Switch`, etc.

Les images affichees dans l'interface sont extraites directement des images embarquees dans les onglets du fichier ODS.

## API Principale

### Authentification

Les endpoints qui modifient les donnees exigent un token Bearer OAuth2 :

```http
POST /auth/token
Content-Type: application/json
```

Exemple :

```json
{
  "username": "admin",
  "password": "change-me"
}
```

Configurer les valeurs avec `AUTH_USERNAME`, `AUTH_PASSWORD_ENCRYPTED`,
`AUTH_SECRET_KEY_ENCRYPTED`, `AUTH_ENV_ENCRYPTION_KEY` et `AUTH_TOKEN_TTL_SECONDS`.
Les anciennes variables `AUTH_PASSWORD` et `AUTH_SECRET_KEY` restent acceptees
en secours local, mais le fichier `.env` doit utiliser les valeurs chiffrees.

Generer un nouveau mot de passe, une nouvelle cle HMAC et leurs valeurs chiffrees :

```bash
backend/.venv/bin/python scripts/generate_auth_env.py
```

Reporter ensuite `AUTH_ENV_ENCRYPTION_KEY`, `AUTH_PASSWORD_ENCRYPTED` et
`AUTH_SECRET_KEY_ENCRYPTED` dans `docker/.env`. La sortie affiche aussi
`GENERATED_AUTH_PASSWORD`, qui est le mot de passe a saisir dans l'ecran
d'authentification.

La reponse contient `access_token`, `token_type` et `expires_in`. Les appels de
mise a jour doivent ensuite envoyer :

```http
Authorization: Bearer <access_token>
```

### Routes Disponibles

```http
GET /api/routes
```

Retourne les routes backend et indique si elles sont publiques ou protegees :

```json
{
  "routes": [
    {
      "path": "/collections/JeuxVideo/games",
      "endpoint": "add_jeux_video_game",
      "methods": ["POST"],
      "requires_auth": true,
      "access": "bearer_token",
      "auth_schemes": ["Bearer"]
    }
  ]
}
```

### Plateformes

```http
GET /collections/JeuxVideo/platforms
```

Retourne la liste des onglets de plateformes.

### Accueil

```http
GET /collections/JeuxVideo/home
```

Retourne les statistiques de l'onglet `Accueil`, avec les liens vers les images de plateformes.

### Jeux d'une plateforme

```http
GET /collections/JeuxVideo/search?platform=Switch
```

Retourne les jeux d'une plateforme. Le parametre `q` permet de filtrer les resultats.

### Recherche globale par nom

```http
GET /collections/JeuxVideo/game-search?q=mario
```

Recherche un jeu par son nom dans tous les onglets de plateformes.

### Valeurs de colonnes

```http
GET /collections/JeuxVideo/column-values?platform=Switch
```

Retourne les valeurs distinctes par colonne, utilisees notamment pour les filtres et les suggestions du formulaire.

### Image d'une plateforme

```http
GET /collections/JeuxVideo/platform-image/Switch
```

Retourne l'image embarquee dans l'onglet de la plateforme.

### Ajouter un jeu

```http
POST /collections/JeuxVideo/games
Content-Type: application/json
Authorization: Bearer <access_token>
```

Exemple :

```json
{
  "platform": "Switch",
  "Nom du jeu": "Exemple",
  "Studio": "Nintendo",
  "Date de sortie": "2026-05-01",
  "Date d'achat": "2026-05-01",
  "Lieu d'achat": "Fnac",
  "Note": "8/10",
  "Prix d'achat": "49.99",
  "Version": "FR"
}
```

Avant chaque ecriture, une sauvegarde est creee a cote du fichier ODS :

```text
collection.ods.backup-YYYYMMDDHHMMSS
```

## Lancement Local

### Avec Docker Compose

Le projet peut tourner avec deux conteneurs :

- `backend` : API Flask exposee uniquement au reseau Docker interne
- `web` : Nginx qui sert le frontend React compile et proxifie `/api` et `/collections` vers le backend

Seul le fichier `collection.ods` de la racine du projet est monte dans le conteneur backend, sans monter tout le dossier projet.

Copier le fichier d'exemple d'environnement :

```bash
cp docker/.env.example docker/.env
```

Adapter ensuite `docker/.env` si besoin :

```bash
WEB_PORT=8080
```

Demarrer l'application :

```bash
cd docker
docker compose up --build
```

L'application sera disponible sur :

```text
http://localhost:8080
```

Depuis un autre appareil du meme Wi-Fi, utiliser l'adresse IP locale du Mac :

```text
http://IP_DU_MAC:8080
```

Pour l'utiliser avec un nom local comme `cloud-collection-app.fr`, faire pointer ce nom vers l'IP locale du Mac dans le DNS local du reseau, puis acceder a :

```text
http://cloud-collection-app.fr:8080
```

Pour arreter :

```bash
cd docker
docker compose down
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
BACKEND_PORT=7777 python app.py
```

Le backend tourne sur `http://localhost:7777`.

### Frontend

Dans un autre terminal :

```bash
cd frontend
npm install
BACKEND_PORT=7777 FRONTEND_PORT=7778 npm run dev
```

Le frontend tourne sur `http://localhost:7778`.

### Scripts Utilitaires

Depuis la racine :

```bash
./start.sh
./stop.sh
```

Avec ports personnalises :

```bash
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./start.sh
BACKEND_PORT=5000 FRONTEND_PORT=5173 ./stop.sh
```

## Build Frontend

```bash
cd frontend
npm run build
```

Le build de production est genere dans `frontend/dist/`.

## Notes De Maintenance

- Le fichier ODS reste la source de verite.
- Les dossiers `node_modules/`, `dist/`, `.venv/` et les caches Python sont ignores par Git.
- L'ajout de jeu modifie le fichier ODS sur disque : verifier la sauvegarde si une modification doit etre annulee.
- Si la structure du fichier ODS change fortement, il faudra adapter `JeuVideoService`.
