/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
import AppMetadata from "../appMetadata";

/**
 * Affiche le pied de page applicatif.
 *
 * @param {void} Aucun - Les metadonnees sont lues depuis `AppMetadata`.
 * @returns {import("react").JSX.Element} Footer avec nom, GitHub, date et version.
 */
function AppFooter() {
  const metadata = AppMetadata.getFooterMetadata();

  return (
    <footer className="appFooter">
      <strong>{metadata.name}</strong>
      <div className="appFooterMeta">
        <a href={metadata.githubUrl} target="_blank" rel="noreferrer">
          GitHub
        </a>
        <span>{metadata.releaseDate}</span>
        <span>v{metadata.version}</span>
      </div>
    </footer>
  );
}

export default AppFooter;
