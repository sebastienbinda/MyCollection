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
import packageMetadata from "../package.json";

class AppMetadata {
  /**
   * Retourne les informations publiques de l'application.
   *
   * @param {void} Aucun - Les informations sont statiques ou issues du package npm.
   * @returns {{name: string, githubUrl: string, releaseDate: string, version: string}} Metadonnees affichees.
   */
  static getFooterMetadata() {
    return {
      name: "CloudApplicationApp",
      githubUrl: "https://github.com/sebastienbinda/CloudCollectionApp",
      releaseDate: "2026-05-03",
      version: packageMetadata.version,
    };
  }
}

export default AppMetadata;
