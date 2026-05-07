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
import ProjectIcon from "./ProjectIcon";

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
      <div className="appFooterBrand">
        <ProjectIcon className="appFooterIcon" />
        <strong>{metadata.name}</strong>
      </div>
      <div className="appFooterMeta">
        <a href={metadata.githubUrl} target="_blank" rel="noreferrer">
          <svg aria-hidden="true" className="githubFooterIcon" viewBox="0 0 24 24">
            <path d="M12 .5A12 12 0 0 0 8.2 23.9c.6.1.8-.3.8-.6v-2.1c-3.3.7-4-1.4-4-1.4-.5-1.3-1.2-1.7-1.2-1.7-1-.7.1-.7.1-.7 1.1.1 1.7 1.2 1.7 1.2 1 .1.9 2.1 3.4 1.5.1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.9 0-1.3.5-2.4 1.2-3.2-.1-.3-.5-1.6.1-3.2 0 0 1-.3 3.3 1.2a11.4 11.4 0 0 1 6 0C17.3 5.9 18.3 6.2 18.3 6.2c.6 1.6.2 2.9.1 3.2.8.8 1.2 1.9 1.2 3.2 0 4.6-2.8 5.6-5.4 5.9.4.4.8 1.1.8 2.2v2.6c0 .3.2.7.8.6A12 12 0 0 0 12 .5Z" />
          </svg>
          GitHub
        </a>
        <span>{metadata.releaseDate}</span>
        <span>v{metadata.version}</span>
      </div>
    </footer>
  );
}

export default AppFooter;
