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
class JeuxVideoApi {
  /**
   * Charge les statistiques d'accueil.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Donnees du tableau de bord.
   */
  static async fetchHomeStats() {
    return this.fetchJson("/collections/JeuxVideo/home", "Impossible de recuperer l'accueil.");
  }

  /**
   * Charge la liste des plateformes.
   *
   * @param {void} Aucun - Appelle l'API backend.
   * @returns {Promise<Object>} Objet contenant `platforms`.
   */
  static async fetchPlatforms() {
    return this.fetchJson(
      "/collections/JeuxVideo/platforms",
      "Impossible de recuperer les plateformes."
    );
  }

  /**
   * Charge les jeux d'une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS a lire.
   * @returns {Promise<Array>} Liste des jeux de la plateforme.
   */
  static async fetchGames(platform) {
    return this.fetchJson(
      `/collections/JeuxVideo/search?platform=${encodeURIComponent(platform)}`,
      "Impossible de recuperer les jeux video."
    );
  }

  /**
   * Charge les valeurs distinctes de colonnes pour une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS a analyser.
   * @returns {Promise<Object>} Objet contenant `values_by_column`.
   */
  static async fetchColumnValues(platform) {
    return this.fetchJson(
      `/collections/JeuxVideo/column-values?platform=${encodeURIComponent(platform)}`,
      "Impossible de recuperer les valeurs de colonnes."
    );
  }

  /**
   * Ajoute un jeu au fichier ODS.
   *
   * @param {Object} gameForm - Donnees du formulaire d'ajout.
   * @returns {Promise<Object>} Objet contenant le jeu ajoute.
   */
  static async addGame(gameForm) {
    return this.fetchJson("/collections/JeuxVideo/games", "Impossible d'ajouter le jeu.", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(gameForm),
    });
  }

  /**
   * Recherche un jeu par nom dans toutes les plateformes.
   *
   * @param {string} query - Texte recherche dans le nom du jeu.
   * @returns {Promise<Object>} Objet contenant les resultats.
   */
  static async searchGamesByName(query) {
    return this.fetchJson(
      `/collections/JeuxVideo/game-search?q=${encodeURIComponent(query)}`,
      "Impossible de rechercher les jeux."
    );
  }

  /**
   * Reinitialise le cache backend du fichier ODS.
   *
   * @param {void} Aucun - Appelle l'endpoint de reset.
   * @returns {Promise<Object>} Resultat de reinitialisation du cache.
   */
  static async resetCache() {
    return this.fetchJson("/collections/JeuxVideo/cache/reset", "Impossible de reinitialiser le cache.", {
      method: "POST",
    });
  }

  /**
   * Execute une requete JSON et normalise les erreurs.
   *
   * @param {string} url - URL appelee.
   * @param {string} fallbackMessage - Message utilise si l'API ne detaille pas l'erreur.
   * @param {RequestInit} options - Options transmises a `fetch`.
   * @returns {Promise<any>} Corps JSON retourne par l'API.
   */
  static async fetchJson(url, fallbackMessage, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || fallbackMessage);
    }
    return data;
  }
}

export default JeuxVideoApi;
