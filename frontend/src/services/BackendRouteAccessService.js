/*
 *   ____ _                 _  ____      _ _           _   _             ___
 *  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
 * | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
 * | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
 *  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
 *                                                                            |_|   |_|
 * Projet : CloudCollectionApp
 * Date de creation : 2026-05-05
 * Auteurs : Codex et Binda Sébastien
 * Licence : Apache 2.0
 *
 * Description : service objet evaluant les actions frontend autorisees par les routes backend.
 */

class BackendRouteAccessService {
  /**
   * Retourne les permissions par defaut avant chargement du backend.
   *
   * @param {void} Aucun - Ne depend pas de l'etat applicatif.
   * @returns {Object} Permissions refusees par defaut.
   */
  static getDefaultActionPermissions() {
    return {
      canAddGame: false,
      canDeleteGame: false,
      canEditWishlistGame: false,
      canDeleteWishlistGame: false,
      canResetCache: false,
      isAuthenticated: false,
    };
  }

  /**
   * Charge les routes backend et calcule les permissions du frontend.
   *
   * @param {Object} apiClient - Client API exposant `fetchRoutes` et `getAccessToken`.
   * @returns {Promise<Object>} Permissions applicatives calculees.
   */
  static async loadActionPermissions(apiClient) {
    const data = await apiClient.fetchRoutes();
    const service = new BackendRouteAccessService(
      data.routes || [],
      apiClient.getAccessToken()
    );
    return service.getActionPermissions();
  }

  /**
   * Initialise le service avec les routes et le token courant.
   *
   * @param {Array<Object>} routes - Routes retournees par `/api/routes`.
   * @param {string} accessToken - Token Bearer disponible cote frontend.
   * @returns {void} Le constructeur ne retourne aucune valeur.
   */
  constructor(routes = [], accessToken = "") {
    this.routes = Array.isArray(routes) ? routes : [];
    this.accessToken = accessToken || "";
  }

  /**
   * Indique si une route backend peut etre appelee.
   *
   * @param {string} method - Methode HTTP de l'action.
   * @param {string} path - Chemin exact expose par le backend.
   * @returns {boolean} `true` si la route est publique ou si un token est present.
   */
  canAccess(method, path) {
    const route = this.findRoute(method, path);
    if (!route) {
      return false;
    }
    return !route.requires_auth || this.hasToken();
  }

  /**
   * Cherche une route par methode et chemin.
   *
   * @param {string} method - Methode HTTP recherchee.
   * @param {string} path - Chemin exact recherche.
   * @returns {Object|null} Route trouvee ou `null`.
   */
  findRoute(method, path) {
    const normalizedMethod = String(method || "").toUpperCase();
    return (
      this.routes.find(
        (route) =>
          route.path === path &&
          Array.isArray(route.methods) &&
          route.methods.includes(normalizedMethod)
      ) || null
    );
  }

  /**
   * Indique si le frontend dispose d'un token Bearer.
   *
   * @param {void} Aucun - Utilise le token fourni au constructeur.
   * @returns {boolean} `true` si un token non vide est disponible.
   */
  hasToken() {
    return this.accessToken.trim().length > 0;
  }

  /**
   * Retourne les permissions utiles aux vues React.
   *
   * @param {void} Aucun - Utilise le catalogue de routes charge.
   * @returns {Object} Drapeaux booleens par action applicative.
   */
  getActionPermissions() {
    return {
      ...BackendRouteAccessService.getDefaultActionPermissions(),
      canAddGame: this.canAccess("POST", "/collections/JeuxVideo/games"),
      canEditGame: this.canAccess("PUT", "/collections/JeuxVideo/games"),
      canDeleteGame: this.canAccess("DELETE", "/collections/JeuxVideo/games"),
      canEditWishlistGame: this.canAccess("PUT", "/collections/JeuxVideo/wishlist/games"),
      canDeleteWishlistGame: this.canAccess("DELETE", "/collections/JeuxVideo/wishlist/games"),
      canResetCache: this.canAccess("POST", "/collections/JeuxVideo/cache/reset"),
      isAuthenticated: this.hasToken(),
    };
  }
}

export default BackendRouteAccessService;
