# Synthèse Menu Principal

## À retenir

- Le menu principal est porté par `frontend/src/components/MainMenu.jsx`.
- Il doit rester utilisable à la souris, au clavier et sur écran tactile.
- Le menu se ferme au clic extérieur, à la touche `Escape`, après une action et
  quand le curseur souris sort du menu.
- La fermeture à la sortie du menu ne doit pas casser les usages tactiles.
- Les entrées indisponibles doivent être désactivées plutôt que masquées.

## Objectif

Le menu principal donne accès aux vues applicatives transverses depuis les pages
About et Accueil. Il ne doit pas contenir de logique métier: il déclenche les
callbacks fournis par `App.jsx` et reflète uniquement l'état de session reçu en
props.

## Comportement Attendu

- Le bouton principal ouvre et ferme le menu.
- Un clic ou pointer event en dehors du menu ferme le menu.
- La touche `Escape` ferme le menu lorsqu'il est ouvert.
- Un clic sur une action ferme le menu avant de déclencher la navigation.
- Sur desktop, la sortie du pointeur souris ferme le menu.
- Une zone de transition entre le bouton et le panneau peut rester active pour
  éviter une fermeture involontaire lors du déplacement de la souris.
- Sur mobile et tactile, la sortie de pointeur ne doit pas provoquer de fermeture
  accidentelle; filtrer les événements par `pointerType`.
- Le menu doit conserver `aria-expanded` et `aria-haspopup` sur le bouton
  déclencheur.

## Contraintes d'Accès

- `About` reste toujours accessible.
- `Accueil` nécessite une session locale active.
- `Liste de souhaits` nécessite une session locale active.
- `Voir les jeux` nécessite une session locale active et une plateforme cible.
- Les entrées non accessibles doivent utiliser `disabled`.
- Le menu de session reste géré par `AuthStatusMenu`.

## Responsivité

- Le libellé `Menu` peut être masqué sur mobile, mais l'icône doit rester visible.
- La cible tactile doit garder une taille minimale confortable.
- Ne pas dépendre uniquement du hover: le menu doit fonctionner au clic/tap.
- Le panneau doit rester positionné sous le bouton et ne pas chevaucher le bouton
  d'authentification.

## Règles de Développement

- Ne pas réintroduire un `<details>` non contrôlé si le comportement de fermeture
  doit rester précis.
- Ne pas ajouter de dépendance externe pour ce menu.
- Garder la logique du menu dans `MainMenu.jsx`; les pages ne doivent pas gérer
  son état ouvert/fermé.
- Les routes et navigations restent centralisées dans `App.jsx` et
  `AppRouting`.
- Après toute modification du menu, lancer au minimum `npm run build`.
- Pour une modification visuelle importante, vérifier les états desktop et mobile.
