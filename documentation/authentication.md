# Synthèse Authentification

## À retenir

- Tout endpoint backend est protégé sauf `POST /auth/token`.
- Sans Bearer token: `403`; token invalide ou expiré: `401`.
- Le frontend ne fait qu'envoyer ou effacer le token, la sécurité reste backend.
- Tout appel protégé doit utiliser `Authorization: Bearer <access_token>`.
- Toute exception publique doit être documentée et testée.

Ce document décrit les contraintes fonctionnelles à respecter lors de toute
évolution touchant l'authentification, les routes backend ou les appels API
frontend.

## Objectif

L'application utilise une authentification Bearer simple pour protéger les
données de collection. Le backend reste l'autorité unique pour valider les
tokens et décider si une requête est autorisée.

Le frontend ne doit jamais contenir de logique de sécurité métier. Il peut
masquer des actions ou éviter des appels inutiles, mais toute protection réelle
doit rester côté backend.

## Contrat Backend

- Tous les endpoints backend applicatifs doivent exiger un token Bearer valide.
- La seule route applicative publique est `POST /auth/token`, utilisée pour
  obtenir un token.
- Les requêtes CORS `OPTIONS` restent exemptées pour permettre les preflights.
- Les routes doivent être protégées globalement avec `AuthGuard.protect_all_routes`.
- Ne pas ajouter de nouvelle route publique sans décision explicite et sans
  documenter l'exception dans ce fichier.
- Ne pas dupliquer la logique d'authentification dans les services métier.
- Ne pas lire ni valider directement le token dans les endpoints, sauf besoin
  très local et justifié.

## Obtention d'un Token

Endpoint:

```http
POST /auth/token
Content-Type: application/json
```

Corps JSON accepté:

```json
{
  "username": "admin",
  "password": "mot-de-passe"
}
```

Le backend accepte aussi les champs `client_id` et `client_secret` pour un flux
compatible client credentials.

Réponse attendue:

```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

Les identifiants invalides retournent `401` avec un challenge
`WWW-Authenticate: Bearer realm="CloudCollectionApp"`.

## Appels Protégés

Tous les appels aux endpoints protégés doivent envoyer:

```http
Authorization: Bearer <access_token>
```

Codes de réponse à préserver:

- `403` si aucun token Bearer n'est fourni.
- `401` si un token est fourni mais invalide ou expiré.
- `200`, `201`, `400`, `404` ou `500` selon le contrat métier de la route une
  fois le token validé.

Le message actuel pour absence de token est `Token Bearer manquant.`.

## Format et Validation des Tokens

- Les tokens sont créés par `AuthTokenService`.
- Le format interne est `payload.signature`.
- Le payload contient au minimum `sub`, `iat` et `exp`.
- La signature utilise HMAC SHA-256 avec le secret applicatif.
- La durée de vie par défaut est de 3600 secondes.
- La validation doit vérifier la structure, la signature et l'expiration.
- Ne jamais accepter un token non signé ou un token dont l'expiration est passée.

## Variables d'Environnement

Variables principales:

- `AUTH_USERNAME`: identifiant autorisé.
- `AUTH_PASSWORD_ENCRYPTED`: mot de passe applicatif chiffré.
- `AUTH_SECRET_KEY_ENCRYPTED`: secret de signature chiffré.
- `AUTH_ENV_ENCRYPTION_KEY`: clé Fernet utilisée pour déchiffrer les secrets.
- `AUTH_TOKEN_TTL_SECONDS`: durée de vie des tokens Bearer.

Les variables en clair `AUTH_PASSWORD` et `AUTH_SECRET_KEY` existent comme
fallback de développement, mais il ne faut pas introduire de secret en dur dans
le code, les tests, la documentation ou les scripts.

## Contrat Frontend

- Le token est stocké dans `localStorage` sous `cloudCollectionAccessToken`.
- L'expiration locale est stockée sous `cloudCollectionAccessTokenExpiresAt`.
- Tous les appels backend protégés doivent passer par `JeuxVideoApi` ou réutiliser
  `JeuxVideoApi.getAuthorizationHeaders()`.
- Le frontend doit éviter d'appeler les endpoints protégés lorsqu'aucun token
  n'est stocké.
- La page publique non connectée est `AboutView` sur `/about`.
- L'accueil authentifié est `HomeView` sur `/accueil`.
- La route `/` redirige fonctionnellement vers `/about` sans token et vers
  `/accueil` avec token.
- En cas de refus d'un token envoyé (`401` ou `403`), le frontend doit nettoyer
  la session locale et ouvrir le flux de reconnexion.

## Découverte des Routes

`GET /api/routes` est lui-même protégé. Il sert au frontend à calculer les
permissions d'action, mais il ne doit pas devenir une source de vérité de
sécurité. La sécurité reste assurée par le backend avant chaque requête.

Les routes retournées par ce catalogue doivent indiquer correctement:

- `requires_auth`
- `access`
- `auth_schemes`

Toute route protégée doit annoncer `requires_auth: true` et `auth_schemes:
["Bearer"]`.

## Tests à Maintenir

Toute modification de l'authentification doit mettre à jour ou ajouter des tests
backend couvrant au minimum:

- `POST /auth/token` avec identifiants valides.
- `POST /auth/token` avec identifiants invalides.
- Un endpoint protégé sans token qui retourne `403`.
- Un endpoint protégé avec token invalide qui retourne `401`.
- Un endpoint protégé avec token valide qui conserve son comportement métier.
- Le catalogue `/api/routes` et ses indicateurs d'authentification.

Après modification, lancer:

```bash
./test_backend.sh
```

Si le changement impacte le comportement runtime, reconstruire les images Docker
concernées lorsque le daemon Docker est disponible.

## Règles de Développement

- Ne jamais exposer une donnée de collection depuis le backend sans token.
- Ne jamais réintroduire un mode lecture publique pour masquer seulement certains
  champs côté backend.
- Ne jamais hardcoder de secret, token, mot de passe ou clé de signature.
- Ne pas ajouter de dépendance externe d'authentification sans justification
  forte.
- Préférer l'extension de `AuthGuard` et `AuthTokenService` aux vérifications
  dispersées.
- Toute exception publique doit être explicite, testée et mentionnée dans ce
  document.
