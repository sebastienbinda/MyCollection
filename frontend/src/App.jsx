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
import { useEffect, useState } from "react";
import {
  filterGames,
  getStudioCount,
  sortGames,
} from "./collectionUtils";
import AppRouting from "./appRouting";
import AppFrame from "./components/AppFrame";
import AppViewSwitch from "./components/AppViewSwitch";
import JeuxVideoApi from "./services/JeuxVideoApi";
const initialGameForm = AppRouting.createInitialGameForm();
/**
 * Composant racine de l'application React.
 *
 * @param {void} Aucun - Aucun prop n'est attendu.
 * @returns {import("react").JSX.Element} Interface complete de l'application.
 */
function App() {
  const [currentView, setCurrentView] = useState(AppRouting.getViewFromUrl);
  const [homeStats, setHomeStats] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState(() =>
    AppRouting.getViewFromUrl() === "wishlist"
      ? AppRouting.wishlistSheetName
      : AppRouting.getPlatformFromUrl()
  );
  const [games, setGames] = useState([]);
  const [valuesByColumn, setValuesByColumn] = useState({});
  const [columnFilters, setColumnFilters] = useState({});
  const [sortConfig, setSortConfig] = useState({ column: "Nom du jeu", direction: "asc" });
  const [homeSearchQuery, setHomeSearchQuery] = useState("");
  const [homeSearchResults, setHomeSearchResults] = useState([]);
  const [homeSearchError, setHomeSearchError] = useState("");
  const [hasSearchedGames, setHasSearchedGames] = useState(false);
  const [gameForm, setGameForm] = useState(initialGameForm);
  const [addGameMessage, setAddGameMessage] = useState("");
  const [addGameError, setAddGameError] = useState("");
  const [addGameColumnValues, setAddGameColumnValues] = useState({});
  const [deleteGameMessage, setDeleteGameMessage] = useState("");
  const [deleteGameError, setDeleteGameError] = useState("");
  const [cacheResetMessage, setCacheResetMessage] = useState("");
  const [cacheResetError, setCacheResetError] = useState("");
  const [isLoadingHome, setIsLoadingHome] = useState(true);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [isLoadingGames, setIsLoadingGames] = useState(false);
  const [isSearchingGames, setIsSearchingGames] = useState(false);
  const [isAddingGame, setIsAddingGame] = useState(false);
  const [isResettingCache, setIsResettingCache] = useState(false);
  const [odsReloadKey, setOdsReloadKey] = useState(0);
  const [gamesReloadKey, setGamesReloadKey] = useState(0);
  const [error, setError] = useState("");

  const namedGames = games.filter((game) => String(game["Nom du jeu"] || "").trim() !== "");
  const columns = namedGames.length > 0
    ? ["Nom du jeu", ...Object.keys(namedGames[0]).filter((column) => column !== "Nom du jeu")]
    : [];
  const filteredGames = filterGames(namedGames, columns, columnFilters);
  const sortedGames = sortGames(filteredGames, sortConfig);
  const selectedPlatformStats = homeStats?.platforms?.find(
    (platform) => platform.sheet_name === selectedPlatform
  );
  /**
   * Synchronise l'URL avec la plateforme selectionnee.
   *
   * @param {string} platform - Nom de plateforme a placer dans `?platform=`.
   * @returns {void} Modifie l'historique navigateur sans recharger la page.
   */
  const updatePlatformUrl = (platform) => {
    const url = new URL(window.location.href);
    url.pathname = "/";
    if (platform) {
      url.searchParams.set("platform", platform);
    } else {
      url.searchParams.delete("platform");
    }
    window.history.pushState({}, "", `${url.pathname}${url.search}${url.hash}`);
  };

  /**
   * Efface les messages lies a la suppression d'un jeu de plateforme.
   *
   * @param {void} Aucun - Utilise les setters React de feedback.
   * @returns {void} Vide le succes et l'erreur de suppression.
   */
  const clearDeleteGameFeedback = () => {
    setDeleteGameMessage("");
    setDeleteGameError("");
  };

  /**
   * Revient a la page d'accueil.
   *
   * @param {void} Aucun - Utilise l'etat React et l'historique navigateur.
   * @returns {void} Met `currentView` a `home` et remplace l'URL par `/`.
   */
  const goHome = () => {
    clearDeleteGameFeedback();
    setCurrentView("home");
    window.history.pushState({}, "", "/");
  };

  /**
   * Ouvre la page d'ajout de jeu et initialise la plateforme du formulaire.
   *
   * @param {void} Aucun - Utilise la plateforme courante et la liste chargee.
   * @returns {void} Affiche la vue `addGame` et pousse `/add-game` dans l'historique.
   */
  const openAddGamePage = () => {
    clearDeleteGameFeedback();
    setCurrentView("addGame");
    setAddGameMessage("");
    setAddGameError("");
    setGameForm((previous) => ({
      ...previous,
      platform: previous.platform || selectedPlatform || platforms[0] || "",
    }));
    window.history.pushState({}, "", "/add-game");
  };
  /**
   * Ouvre la vue detail d'une plateforme.
   *
   * @param {string} platform - Nom d'onglet ODS de la plateforme.
   * @returns {void} Met a jour l'etat React et l'URL.
   */
  const openPlatform = (platform) => {
    clearDeleteGameFeedback();
    setSelectedPlatform(platform);
    setCurrentView("games");
    updatePlatformUrl(platform);
  };

  /**
   * Ouvre la vue dediee a l'onglet `Liste de souhaits`.
   *
   * @param {void} Aucun - Utilise le nom d'onglet configure dans `AppRouting`.
   * @returns {void} Met a jour l'etat React et l'URL.
   */
  const openWishlist = () => {
    clearDeleteGameFeedback();
    setSelectedPlatform(AppRouting.wishlistSheetName);
    setCurrentView("wishlist");
    window.history.pushState({}, "", "/wishlist");
  };

  /**
   * Met a jour un champ du formulaire d'ajout de jeu.
   *
   * @param {string} field - Nom du champ du formulaire.
   * @param {string} value - Nouvelle valeur saisie.
   * @returns {void} Met a jour `gameForm`.
   */
  const updateGameFormValue = (field, value) => {
    setGameForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  /**
   * Ferme et reinitialise le panneau de resultats de recherche de l'accueil.
   *
   * @param {void} Aucun - Utilise les setters React de recherche.
   * @returns {void} Vide la recherche et masque les resultats.
   */
  const closeHomeSearch = () => {
    setHomeSearchResults([]);
    setHomeSearchError("");
    setHasSearchedGames(false);
    setHomeSearchQuery("");
  };

  /**
   * Alterne le tri ascendant/descendant sur une colonne.
   *
   * @param {string} column - Nom de colonne a trier.
   * @returns {void} Met a jour `sortConfig`.
   */
  const toggleSort = (column) => {
    setSortConfig((previous) => ({
      column,
      direction: previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };

  useEffect(() => {
    const fetchHomeStats = async () => {
      try {
        setIsLoadingHome(true);
        setError("");
        const data = await JeuxVideoApi.fetchHomeStats();
        setHomeStats(data);
      } catch (e) {
        setError("Impossible de charger les statistiques de l'accueil.");
      } finally {
        setIsLoadingHome(false);
      }
    };

    fetchHomeStats();
  }, [odsReloadKey]);

  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        setIsLoadingPlatforms(true);
        setError("");
        const data = await JeuxVideoApi.fetchPlatforms();
        const loadedPlatforms = (data.platforms || [])
          .filter((platform) => !["Accueil", "Liste de souhaits"].includes(platform));
        setPlatforms(loadedPlatforms);

        const platformFromUrl = AppRouting.getPlatformFromUrl();
        if (currentView === "wishlist") {
          setSelectedPlatform(AppRouting.wishlistSheetName);
        } else if (platformFromUrl) {
          setSelectedPlatform(platformFromUrl);
          setCurrentView("games");
        } else if (loadedPlatforms.length > 0) {
          setSelectedPlatform(loadedPlatforms[0]);
          setGameForm((previous) => ({
            ...previous,
            platform: previous.platform || loadedPlatforms[0],
          }));
        }
      } catch (e) {
        setError("Impossible de charger les plateformes depuis le backend.");
      } finally {
        setIsLoadingPlatforms(false);
      }
    };

    fetchPlatforms();
  }, [currentView, odsReloadKey]);

  useEffect(() => {
    const handlePopState = () => {
      clearDeleteGameFeedback();
      if (window.location.pathname === "/add-game") {
        setCurrentView("addGame");
        return;
      }
      if (window.location.pathname === "/wishlist") {
        setSelectedPlatform(AppRouting.wishlistSheetName);
        setCurrentView("wishlist");
        return;
      }

      const platformFromUrl = AppRouting.getPlatformFromUrl();
      if (platformFromUrl) {
        setSelectedPlatform(platformFromUrl);
        setCurrentView("games");
      } else {
        setCurrentView("home");
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  useEffect(() => {
    const fetchGames = async () => {
      if (!selectedPlatform) {
        setGames([]);
        return;
      }

      try {
        setIsLoadingGames(true);
        setError("");
        const data = await JeuxVideoApi.fetchGames(selectedPlatform);
        setGames(Array.isArray(data) ? data : []);
        setColumnFilters({});
      } catch (e) {
        setError("Impossible de charger les jeux video pour cette plateforme.");
        setGames([]);
      } finally {
        setIsLoadingGames(false);
      }
    };

    fetchGames();
  }, [selectedPlatform, gamesReloadKey]);

  useEffect(() => {
    const fetchColumnValues = async () => {
      if (!selectedPlatform) {
        setValuesByColumn({});
        return;
      }

      try {
        const data = await JeuxVideoApi.fetchColumnValues(selectedPlatform);
        setValuesByColumn(data.values_by_column || {});
      } catch (e) {
        setValuesByColumn({});
      }
    };

    fetchColumnValues();
  }, [selectedPlatform, gamesReloadKey]);

  useEffect(() => {
    /**
     * Charge les valeurs existantes pour alimenter les suggestions du formulaire.
     *
     * @param {void} Aucun - Utilise `gameForm.platform` et la vue courante.
     * @returns {Promise<void>} Met a jour `addGameColumnValues`.
     */
    const fetchAddGameColumnValues = async () => {
      if (currentView !== "addGame" || !gameForm.platform) {
        setAddGameColumnValues({});
        return;
      }

      try {
        const data = await JeuxVideoApi.fetchColumnValues(gameForm.platform);
        setAddGameColumnValues(data.values_by_column || {});
      } catch (e) {
        setAddGameColumnValues({});
      }
    };

    fetchAddGameColumnValues();
  }, [currentView, gameForm.platform, odsReloadKey]);

  /**
   * Soumet un nouveau jeu au backend.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission du formulaire.
   * @returns {Promise<void>} Ajoute le jeu, recharge la liste et ouvre sa plateforme.
   */
  const submitNewGame = async (event) => {
    event.preventDefault();
    setAddGameMessage("");
    setAddGameError("");

    try {
      setIsAddingGame(true);
      const data = await JeuxVideoApi.addGame(gameForm);

      setAddGameMessage("Jeu ajoute avec succes.");
      setGameForm({
        ...initialGameForm,
        platform: gameForm.platform,
      });
      setOdsReloadKey((previous) => previous + 1);
      setGamesReloadKey((previous) => previous + 1);
      openPlatform(data.item.Plateforme);
    } catch (e) {
      setAddGameError(e.message || "Impossible d'ajouter le jeu.");
    } finally {
      setIsAddingGame(false);
    }
  };

  /**
   * Ajoute un jeu de la wishlist dans l'onglet de sa plateforme cible.
   *
   * @param {Object} gamePayload - Donnees nettoyees a envoyer au backend.
   * @returns {Promise<Object>} Donnees retournees par l'API d'ajout.
   */
  const addWishlistGameToPlatform = async (gamePayload) => {
    const data = await JeuxVideoApi.addGame(gamePayload);
    setOdsReloadKey((previous) => previous + 1);
    setGamesReloadKey((previous) => previous + 1);
    return data;
  };

  /**
   * Supprime un jeu de la liste de souhaits puis recharge la vue courante.
   *
   * @param {Object} game - Jeu wishlist a supprimer.
   * @returns {Promise<Object>} Donnees retournees par l'API de suppression.
   */
  const deleteWishlistGame = async (game) => {
    const data = await JeuxVideoApi.deleteWishlistGame(game);
    setOdsReloadKey((previous) => previous + 1);
    setGamesReloadKey((previous) => previous + 1);
    return data;
  };

  /**
   * Supprime un jeu de la plateforme courante puis recharge les donnees.
   *
   * @param {Object} game - Jeu de plateforme a supprimer.
   * @returns {Promise<void>} Vide les cellules du jeu et actualise l'interface.
   */
  const deletePlatformGame = async (game) => {
    const gameName = game["Nom du jeu"] || "ce jeu";
    const confirmed = window.confirm(`Confirmer la suppression de "${gameName}" ?`);
    if (!confirmed) {
      return;
    }

    setDeleteGameMessage("");
    setDeleteGameError("");
    try {
      await JeuxVideoApi.deleteGame({
        platform: selectedPlatform,
        ...game,
      });
      setDeleteGameMessage(`${gameName} a ete supprime de ${selectedPlatform}.`);
      setOdsReloadKey((previous) => previous + 1);
      setGamesReloadKey((previous) => previous + 1);
    } catch (e) {
      const message = e.message || "Impossible de supprimer le jeu.";
      setDeleteGameError(message);
      window.alert(message);
    }
  };

  /**
   * Reinitialise le cache ODS backend puis recharge les donnees de l'interface.
   *
   * @param {void} Aucun - Appelle l'endpoint de reset du cache.
   * @returns {Promise<void>} Met a jour les messages, les compteurs de rechargement et les erreurs.
   */
  const resetOdsCache = async () => {
    setCacheResetMessage("");
    setCacheResetError("");

    try {
      setIsResettingCache(true);
      await JeuxVideoApi.resetCache();

      setCacheResetMessage("Cache reinitialise. Donnees rechargees.");
      setOdsReloadKey((previous) => previous + 1);
      setGamesReloadKey((previous) => previous + 1);
    } catch (e) {
      setCacheResetError(e.message || "Impossible de reinitialiser le cache.");
    } finally {
      setIsResettingCache(false);
    }
  };

  /**
   * Recherche un jeu par nom depuis la page d'accueil.
   *
   * @param {React.FormEvent<HTMLFormElement>} event - Evenement de soumission du formulaire.
   * @returns {Promise<void>} Met a jour les resultats et erreurs de recherche.
   */
  const searchGamesByName = async (event) => {
    event.preventDefault();
    const query = homeSearchQuery.trim();
    setHasSearchedGames(true);

    if (!query) {
      setHomeSearchResults([]);
      setHomeSearchError("");
      return;
    }

    try {
      setIsSearchingGames(true);
      setHomeSearchError("");
      const data = await JeuxVideoApi.searchGamesByName(query);
      setHomeSearchResults(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setHomeSearchError("Impossible de rechercher dans la collection.");
      setHomeSearchResults([]);
    } finally {
      setIsSearchingGames(false);
    }
  };

  return (
    <AppFrame>
      {AppViewSwitch.render({
        currentView, homeStats, platforms, selectedPlatform, error,
        isLoadingHome, isSearchingGames, hasSearchedGames,
        homeSearchQuery, homeSearchResults, homeSearchError,
        cacheResetMessage, cacheResetError, isResettingCache,
        gameForm, addGameColumnValues, addGameError, addGameMessage, isAddingGame,
        namedGames, columns, valuesByColumn, columnFilters, sortConfig,
        sortedGames, filteredGames, isLoadingGames,
        selectedPlatformStats,
        studioCount: getStudioCount(namedGames),
        deleteGameMessage, deleteGameError, isLoadingPlatforms,
        openAddGamePage, openWishlist, openPlatform, setHomeSearchQuery,
        searchGamesByName, closeHomeSearch, resetOdsCache, goHome,
        submitNewGame, updateGameFormValue, addWishlistGameToPlatform,
        deleteWishlistGame, toggleSort, setColumnFilters, deletePlatformGame,
      })}
    </AppFrame>
  );
}

export default App;
