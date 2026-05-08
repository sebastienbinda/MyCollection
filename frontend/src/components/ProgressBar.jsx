/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-08
 * Auteurs : OpenAI ChatGPT, Codex, Binda Sébastien
 * License : Apache 2.0
 *
 * Description : composant objet d'affichage d'une barre de progression indeterminee.
 */

/**
 * Affiche une barre de progression indeterminee.
 *
 * @param {Object} props - Proprietes d'accessibilite et de style.
 * @param {string} props.label - Libelle accessible de l'operation en cours.
 * @param {string} props.className - Classe CSS additionnelle.
 * @returns {import("react").JSX.Element} Barre de progression animee.
 */
function ProgressBar({ label = "Chargement en cours", className = "" }) {
  return (
    <div
      className={`progressBar${className ? ` ${className}` : ""}`}
      aria-label={label}
      role="status"
    >
      <span />
    </div>
  );
}

export default ProgressBar;
