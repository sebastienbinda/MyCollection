# Synthèse Page About

## À retenir

- La page About est la page publique non connectée de l'application.
- Elle est rendue par `frontend/src/components/AboutView.jsx`.
- Sa route est `/about`; l'accueil connecté reste `/accueil`.
- Elle ne doit pas appeler d'endpoint backend protégé sans token.
- Elle utilise l'image statique `/about-home-image.jpg`, extraite de l'onglet
  `Accueil` du fichier `collection.ods`.

## Objectif

La page About présente les fonctionnalités de CloudCollectionApp sans entrer
dans les détails techniques. Elle doit expliquer l'intérêt de l'application à un
visiteur non connecté, tout en laissant l'accès à la connexion et au menu
principal.

## Contraintes Fonctionnelles

- La page doit rester accessible sans authentification.
- Elle ne doit pas exposer de données de collection issues d'un appel backend.
- Le contenu doit rester descriptif et non technique.
- Le texte doit parler des usages: explorer la collection, suivre la liste de
  souhaits, consulter l'accueil connecté et maintenir les données.
- La navigation doit passer par `MainMenu`.
- Les actions réservées à une session connectée doivent rester désactivées via
  le menu lorsque l'utilisateur n'est pas connecté.

## Image

- L'image affichée est `frontend/public/about-home-image.jpg`.
- Cette image provient de l'onglet `Accueil` de `collection.ods`.
- Ne pas remplacer cette image par une URL externe.
- Si l'image de l'onglet `Accueil` change dans l'ODS, ré-extraire l'asset public
  et vérifier le rendu responsive.
- L'image doit garder un texte alternatif clair.

## UI et Responsivité

- Le composant doit rester distinct de `HomeView`.
- Les styles spécifiques utilisent les classes `aboutShell`, `aboutHeader`,
  `aboutContent`, `aboutHomeImage`, `aboutIntro` et `aboutFeatureGrid`.
- La grille des fonctionnalités doit rester lisible sur desktop et se replier
  proprement sur mobile.
- Éviter les détails techniques, les longues listes et les textes trop denses.
- Ne pas transformer cette page en landing page marketing complexe.

## Règles de Développement

- Lire aussi `documentation/menu.md` avant de modifier le menu de la page.
- Lire aussi `documentation/authentication.md` avant tout changement de route ou
  d'accès à la page.
- Après modification visuelle ou JSX, lancer au minimum `npm run build`.
- Si l'asset public change, reconstruire l'image Docker frontend lorsque Docker
  est disponible.
