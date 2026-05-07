/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __| (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-07
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : composant objet affichant l'icone publique du projet.
 */

/**
 * Affiche l'icone officielle de l'application.
 *
 * @param {Object} props - Classe CSS optionnelle et libelle accessible.
 * @returns {import("react").JSX.Element} Image de l'icone projet.
 */
function ProjectIcon({ className = "projectIcon", label = "CloudCollectionApp" }) {
  return <img className={className} src="/favicon.svg" alt={label} />;
}

export default ProjectIcon;
