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
 * Description : service objet de tri et coloration des jeux de la liste de souhaits.
 */

class WishlistSortService {
  /**
   * Trie les jeux par plateforme puis par nom.
   *
   * @param {Record<string, unknown>[]} games - Jeux wishlist a trier.
   * @returns {Record<string, unknown>[]} Jeux tries par console puis nom.
   */
  sortByPlatformAndName(games) {
    return [...games].sort((leftGame, rightGame) => {
      const platformCompare = this.getGamePlatform(leftGame).localeCompare(
        this.getGamePlatform(rightGame),
        "fr",
        { sensitivity: "base" }
      );
      if (platformCompare !== 0) return platformCompare;
      return String(leftGame["Nom du jeu"] || "").localeCompare(
        String(rightGame["Nom du jeu"] || ""),
        "fr",
        { sensitivity: "base" }
      );
    });
  }

  /**
   * Retourne la plateforme d'un jeu wishlist.
   *
   * @param {Record<string, unknown>} game - Jeu wishlist.
   * @returns {string} Console ou plateforme du jeu.
   */
  getGamePlatform(game) {
    return String(game.Console || game.Plateforme || "").trim();
  }

  /**
   * Retourne l'index couleur stable d'une plateforme.
   *
   * @param {Record<string, unknown>} game - Jeu wishlist.
   * @returns {number} Index CSS entre 0 et 5.
   */
  getPlatformColorIndex(game) {
    const platform = this.getGamePlatform(game).toLowerCase();
    let hash = 0;
    for (let index = 0; index < platform.length; index += 1) {
      hash += platform.charCodeAt(index);
    }
    return hash % 6;
  }
}

export default WishlistSortService;
