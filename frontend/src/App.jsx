import { useEffect, useState } from "react";
import {
  filterGames,
  getStudioCount,
  sortGames,
} from "./collectionUtils";
import AddGameView from "./components/AddGameView";
import HomeView from "./components/HomeView";
import PlatformDetailView from "./components/PlatformDetailView";

const initialGameForm = {
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

/**
 * Lit la plateforme presente dans l'URL courante.
 *
 * @param {void} Aucun - Utilise `window.location.search`.
 * @returns {string} Nom de plateforme issu du parametre `platform`, ou chaine vide.
 */
const getPlatformFromUrl = () => {
  const params = new URLSearchParams(window.location.search);
  return params.get("platform") || "";
};

/**
 * Deduit la vue active depuis le chemin et les parametres d'URL.
 *
 * @param {void} Aucun - Utilise `window.location`.
 * @returns {"home"|"games"|"addGame"} Identifiant de vue a afficher.
 */
const getViewFromUrl = () => {
  if (window.location.pathname === "/add-game") {
    return "addGame";
  }
  return getPlatformFromUrl() ? "games" : "home";
};

/**
 * Composant racine de l'application React.
 *
 * @param {void} Aucun - Aucun prop n'est attendu.
 * @returns {import("react").JSX.Element} Interface complete de l'application.
 */
function App() {
  const [currentView, setCurrentView] = useState(getViewFromUrl);
  const [homeStats, setHomeStats] = useState(null);
  const [platforms, setPlatforms] = useState([]);
  const [selectedPlatform, setSelectedPlatform] = useState(getPlatformFromUrl);
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
  const [isLoadingHome, setIsLoadingHome] = useState(true);
  const [isLoadingPlatforms, setIsLoadingPlatforms] = useState(true);
  const [isLoadingGames, setIsLoadingGames] = useState(false);
  const [isSearchingGames, setIsSearchingGames] = useState(false);
  const [isAddingGame, setIsAddingGame] = useState(false);
  const [gamesReloadKey, setGamesReloadKey] = useState(0);
  const [error, setError] = useState("");

  const columns =
    games.length > 0
      ? ["Nom du jeu", ...Object.keys(games[0]).filter((column) => column !== "Nom du jeu")]
      : [];
  const filteredGames = filterGames(games, columns, columnFilters);
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
   * Revient a la page d'accueil.
   *
   * @param {void} Aucun - Utilise l'etat React et l'historique navigateur.
   * @returns {void} Met `currentView` a `home` et remplace l'URL par `/`.
   */
  const goHome = () => {
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
    setSelectedPlatform(platform);
    setCurrentView("games");
    updatePlatformUrl(platform);
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
      direction:
        previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };

  useEffect(() => {
    /**
     * Charge les statistiques d'accueil depuis l'API backend.
     *
     * @param {void} Aucun - Appelle `/collections/JeuxVideo/home`.
     * @returns {Promise<void>} Met a jour `homeStats`, `error` et `isLoadingHome`.
     */
    const fetchHomeStats = async () => {
      try {
        setError("");
        const response = await fetch("/collections/JeuxVideo/home");
        if (!response.ok) {
          throw new Error("Impossible de recuperer l'accueil.");
        }
        const data = await response.json();
        setHomeStats(data);
      } catch (e) {
        setError("Impossible de charger les statistiques de l'accueil.");
      } finally {
        setIsLoadingHome(false);
      }
    };

    fetchHomeStats();
  }, []);

  useEffect(() => {
    /**
     * Charge la liste des plateformes exposees par le backend.
     *
     * @param {void} Aucun - Appelle `/collections/JeuxVideo/platforms`.
     * @returns {Promise<void>} Met a jour `platforms`, `selectedPlatform` et l'etat de chargement.
     */
    const fetchPlatforms = async () => {
      try {
        setError("");
        const response = await fetch("/collections/JeuxVideo/platforms");
        if (!response.ok) {
          throw new Error("Impossible de recuperer les plateformes.");
        }
        const data = await response.json();
        const loadedPlatforms = (data.platforms || []).filter(
          (platform) => !["Accueil", "Liste de souhaits"].includes(platform)
        );
        setPlatforms(loadedPlatforms);

        const platformFromUrl = getPlatformFromUrl();
        if (platformFromUrl) {
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
  }, []);

  useEffect(() => {
    /**
     * Reagit aux boutons precedent/suivant du navigateur.
     *
     * @param {void} Aucun - Utilise uniquement `window.location`.
     * @returns {void} Synchronise la vue React avec l'URL courante.
     */
    const handlePopState = () => {
      if (window.location.pathname === "/add-game") {
        setCurrentView("addGame");
        return;
      }

      const platformFromUrl = getPlatformFromUrl();
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
    /**
     * Charge les jeux de la plateforme selectionnee.
     *
     * @param {void} Aucun - Utilise `selectedPlatform`.
     * @returns {Promise<void>} Met a jour `games`, les filtres et l'etat de chargement.
     */
    const fetchGames = async () => {
      if (!selectedPlatform) {
        setGames([]);
        return;
      }

      try {
        setIsLoadingGames(true);
        setError("");
        const response = await fetch(
          `/collections/JeuxVideo/search?platform=${encodeURIComponent(selectedPlatform)}`
        );
        if (!response.ok) {
          throw new Error("Impossible de recuperer les jeux video.");
        }
        const data = await response.json();
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
    /**
     * Charge les valeurs distinctes de colonnes pour les filtres de tableau.
     *
     * @param {void} Aucun - Utilise `selectedPlatform`.
     * @returns {Promise<void>} Met a jour `valuesByColumn`.
     */
    const fetchColumnValues = async () => {
      if (!selectedPlatform) {
        setValuesByColumn({});
        return;
      }

      try {
        const response = await fetch(
          `/collections/JeuxVideo/column-values?platform=${encodeURIComponent(selectedPlatform)}`
        );
        if (!response.ok) {
          throw new Error("Impossible de recuperer les valeurs de colonnes.");
        }
        const data = await response.json();
        setValuesByColumn(data.values_by_column || {});
      } catch (e) {
        setValuesByColumn({});
      }
    };

    fetchColumnValues();
  }, [selectedPlatform]);

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
        const response = await fetch(
          `/collections/JeuxVideo/column-values?platform=${encodeURIComponent(gameForm.platform)}`
        );
        if (!response.ok) {
          throw new Error("Impossible de recuperer les valeurs existantes.");
        }
        const data = await response.json();
        setAddGameColumnValues(data.values_by_column || {});
      } catch (e) {
        setAddGameColumnValues({});
      }
    };

    fetchAddGameColumnValues();
  }, [currentView, gameForm.platform]);

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
      const response = await fetch("/collections/JeuxVideo/games", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(gameForm),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || "Impossible d'ajouter le jeu.");
      }

      setAddGameMessage("Jeu ajoute avec succes.");
      setGameForm({
        ...initialGameForm,
        platform: gameForm.platform,
      });
      setGamesReloadKey((previous) => previous + 1);
      openPlatform(data.item.Plateforme);
    } catch (e) {
      setAddGameError(e.message || "Impossible d'ajouter le jeu.");
    } finally {
      setIsAddingGame(false);
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
      const response = await fetch(
        `/collections/JeuxVideo/game-search?q=${encodeURIComponent(query)}`
      );
      if (!response.ok) {
        throw new Error("Impossible de rechercher les jeux.");
      }
      const data = await response.json();
      setHomeSearchResults(Array.isArray(data.items) ? data.items : []);
    } catch (e) {
      setHomeSearchError("Impossible de rechercher dans la collection.");
      setHomeSearchResults([]);
    } finally {
      setIsSearchingGames(false);
    }
  };

  if (currentView === "home") {
    return (
      <HomeView
        homeStats={homeStats}
        platforms={platforms}
        selectedPlatform={selectedPlatform}
        error={error}
        isLoadingHome={isLoadingHome}
        isSearchingGames={isSearchingGames}
        hasSearchedGames={hasSearchedGames}
        homeSearchQuery={homeSearchQuery}
        homeSearchResults={homeSearchResults}
        homeSearchError={homeSearchError}
        onAddGame={openAddGamePage}
        onOpenPlatform={openPlatform}
        onSearchQueryChange={setHomeSearchQuery}
        onSearchSubmit={searchGamesByName}
        onCloseSearch={closeHomeSearch}
      />
    );
  }

  if (currentView === "addGame") {
    return (
      <AddGameView
        platforms={platforms}
        gameForm={gameForm}
        addGameColumnValues={addGameColumnValues}
        addGameError={addGameError}
        addGameMessage={addGameMessage}
        isAddingGame={isAddingGame}
        onBack={goHome}
        onSubmit={submitNewGame}
        onFieldChange={updateGameFormValue}
      />
    );
  }

  return (
    <PlatformDetailView
      selectedPlatform={selectedPlatform}
      selectedPlatformStats={selectedPlatformStats}
      studioCount={getStudioCount(games)}
      platforms={platforms}
      games={games}
      columns={columns}
      valuesByColumn={valuesByColumn}
      columnFilters={columnFilters}
      sortConfig={sortConfig}
      sortedGames={sortedGames}
      filteredGames={filteredGames}
      error={error}
      isLoadingPlatforms={isLoadingPlatforms}
      isLoadingGames={isLoadingGames}
      onBack={goHome}
      onOpenPlatform={openPlatform}
      onToggleSort={toggleSort}
      onColumnFiltersChange={setColumnFilters}
    />
  );
}

export default App;
