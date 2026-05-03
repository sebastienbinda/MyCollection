/*
 *  __  __ __   __       ____ ___  _     _     _____ ____ _____ __   _____ ___ ___  _   _
 * |  \/  |\ \ / /      / ___/ _ \| |   | |   | ____/ ___|_   _|\ \ / /_ _/ _ \| \ | |
 * | |\/| | \ V /_____ | |  | | | | |   | |   |  _|| |     | |   \ V / | | | | |  \| |
 * | |  | |  | |_____| | |__| |_| | |___| |___| |__| |___  | |    | |  | | |_| | |\  |
 * |_|  |_|  |_|       \____\___/|_____|_____|_____\____| |_|    |_| |___\___/|_| \_|
 * Projet : MY-COLLECTYION
 * Date de creation : 2026-05-03
 * Auteurs : Codex et Binda Sébastien
 */
class AppRouting {
  /**
   * Cree l'etat initial du formulaire d'ajout de jeu.
   *
   * @param {void} Aucun - Les valeurs par defaut sont statiques.
   * @returns {Object} Formulaire vide pret a etre stocke dans React.
   */
  static createInitialGameForm() {
    return {
      platform: "",
      "Nom du jeu": "",
      Studio: "",
      "Date de sortie": "",
      "Date d'achat": "",
      "Lieu d'achat": "",
      Note: "",
      "Prix d'achat": "",
      Version: "",
    };
  }

  /**
   * Lit la plateforme presente dans l'URL courante.
   *
   * @param {void} Aucun - Utilise `window.location.search`.
   * @returns {string} Nom de plateforme issu du parametre `platform`, ou chaine vide.
   */
  static getPlatformFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("platform") || "";
  }

  /**
   * Deduit la vue active depuis le chemin et les parametres d'URL.
   *
   * @param {void} Aucun - Utilise `window.location`.
   * @returns {"home"|"games"|"addGame"} Identifiant de vue a afficher.
   */
  static getViewFromUrl() {
    if (window.location.pathname === "/add-game") {
      return "addGame";
    }
    return AppRouting.getPlatformFromUrl() ? "games" : "home";
  }
}

export default AppRouting;
