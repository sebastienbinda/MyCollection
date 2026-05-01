import { useEffect, useState } from "react";

function App() {
  const getPlatformFromUrl = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get("platform") || "";
  };
  const getViewFromUrl = () => {
    if (window.location.pathname === "/add-game") {
      return "addGame";
    }
    return getPlatformFromUrl() ? "games" : "home";
  };
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

  const goHome = () => {
    setCurrentView("home");
    window.history.pushState({}, "", "/");
  };

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

  useEffect(() => {
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

  const columns =
    games.length > 0
      ? ["Nom du jeu", ...Object.keys(games[0]).filter((column) => column !== "Nom du jeu")]
      : [];
  const dateFormatter = new Intl.DateTimeFormat("fr-FR");
  const isDateColumn = (column) => column.toLowerCase().includes("date");
  const isDeveloperColumn = (column) => {
    const normalized = column.toLowerCase();
    return normalized.includes("studio") || normalized.includes("develop");
  };
  const isSelectFilterColumn = (column) => isDeveloperColumn(column) || column === "Version";
  const renderSortIcon = (column) => {
    const isActive = sortConfig.column === column;
    const direction = isActive ? sortConfig.direction : "both";

    return (
      <svg
        className={`sortIcon sortIcon-${direction}`}
        viewBox="0 0 16 16"
        aria-hidden="true"
        focusable="false"
      >
        <path
          className="sortIconUp"
          d="M8 3.2 4.6 6.6h6.8L8 3.2Z"
        />
        <path
          className="sortIconDown"
          d="M8 12.8 11.4 9.4H4.6L8 12.8Z"
        />
      </svg>
    );
  };
  const getColumnClassName = (column) => {
    if (column === "Nom du jeu") {
      return "gameNameColumn";
    }
    if (isDateColumn(column)) {
      return "dateColumn";
    }
    if (["Note", "Version"].includes(column)) {
      return "compactColumn";
    }
    if (column === "Prix d'achat") {
      return "priceColumn";
    }
    return "";
  };
  const toggleSort = (column) => {
    setSortConfig((previous) => ({
      column,
      direction:
        previous.column === column && previous.direction === "asc" ? "desc" : "asc",
    }));
  };

  const formatCellValue = (column, value) => {
    if (value === null || value === undefined || value === "") {
      return "-";
    }

    if (isDateColumn(column)) {
      const parsed = new Date(value);
      if (!Number.isNaN(parsed.getTime())) {
        return dateFormatter.format(parsed);
      }
    }

    return String(value);
  };

  const extractYear = (value) => {
    if (value === null || value === undefined || value === "") {
      return null;
    }

    const parsedDate = new Date(value);
    if (!Number.isNaN(parsedDate.getTime())) {
      return parsedDate.getFullYear();
    }

    const text = String(value).trim();
    const fourDigitYearMatch = text.match(/(19|20)\d{2}/);
    if (fourDigitYearMatch) {
      return Number.parseInt(fourDigitYearMatch[0], 10);
    }

    const shortDateMatch = text.match(/^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{2})$/);
    if (shortDateMatch) {
      const year = Number.parseInt(shortDateMatch[3], 10);
      return year >= 70 ? 1900 + year : 2000 + year;
    }

    return null;
  };

  const renderVersionValue = (value) => {
    if (value === null || value === undefined || value === "") {
      return "-";
    }

    const versionText = String(value);
    const normalized = versionText.toLowerCase();
    const icons = [];

    if (normalized.includes("pal")) {
      icons.push("🌍");
    }
    if (normalized.includes("ntsc")) {
      icons.push("📺");
    }
    if (normalized.includes("jap")) {
      icons.push("🇯🇵");
    }
    if (normalized.includes("us")) {
      icons.push("🇺🇸");
    }
    if (normalized.includes("fr")) {
      icons.push("🇫🇷");
    }

    if (icons.length === 0) {
      return "-";
    }

    return <span className="versionIcons">{icons.join(" ")}</span>;
  };

  const getDateYearOptions = (column) => {
    const years = new Set();

    (valuesByColumn[column] || []).forEach((value) => {
      const year = extractYear(value);
      if (year !== null) {
        years.add(year);
      }
    });

    return Array.from(years).sort((a, b) => b - a);
  };

  const filteredGames = games.filter((game) =>
    columns.every((column) => {
      if (isDateColumn(column)) {
        const dateFilter = columnFilters[column];
        if (!dateFilter || !dateFilter.year) {
          return true;
        }

        const gameYear = extractYear(game[column]);
        if (gameYear === null) {
          return false;
        }

        const selectedYear = Number.parseInt(dateFilter.year, 10);

        if (Number.isNaN(selectedYear)) {
          return true;
        }

        if (dateFilter.operator === ">") {
          return gameYear > selectedYear;
        }

        if (dateFilter.operator === "=") {
          return gameYear === selectedYear;
        }

        return gameYear < selectedYear;
      }

      const filterValue = (columnFilters[column] || "").trim().toLowerCase();
      if (!filterValue) {
        return true;
      }
      const cellValue = game[column] === null ? "" : String(game[column]).toLowerCase();
      return cellValue.includes(filterValue);
    })
  );
  const sortedGames = [...filteredGames].sort((firstGame, secondGame) => {
    const directionMultiplier = sortConfig.direction === "asc" ? 1 : -1;
    const firstValue = firstGame[sortConfig.column];
    const secondValue = secondGame[sortConfig.column];

    if (
      firstValue === null ||
      firstValue === undefined ||
      firstValue === ""
    ) {
      return secondValue === null || secondValue === undefined || secondValue === ""
        ? 0
        : 1;
    }
    if (
      secondValue === null ||
      secondValue === undefined ||
      secondValue === ""
    ) {
      return -1;
    }

    if (isDateColumn(sortConfig.column)) {
      const firstDate = new Date(firstValue);
      const secondDate = new Date(secondValue);
      if (!Number.isNaN(firstDate.getTime()) && !Number.isNaN(secondDate.getTime())) {
        return (firstDate.getTime() - secondDate.getTime()) * directionMultiplier;
      }
    }

    const firstNumber = Number.parseFloat(String(firstValue).replace(",", "."));
    const secondNumber = Number.parseFloat(String(secondValue).replace(",", "."));
    if (!Number.isNaN(firstNumber) && !Number.isNaN(secondNumber)) {
      return (firstNumber - secondNumber) * directionMultiplier;
    }

    return (
      String(firstValue).localeCompare(String(secondValue), "fr", {
        numeric: true,
        sensitivity: "base",
      }) * directionMultiplier
    );
  });

  const formatNumber = (value) => {
    if (value === null || value === undefined || value === "") {
      return "-";
    }
    return new Intl.NumberFormat("fr-FR").format(value);
  };

  const formatCurrency = (value) => {
    if (value === null || value === undefined || value === "") {
      return "-";
    }
    return new Intl.NumberFormat("fr-FR", {
      style: "currency",
      currency: "EUR",
      maximumFractionDigits: 0,
    }).format(value);
  };

  const openPlatform = (platform) => {
    setSelectedPlatform(platform);
    setCurrentView("games");
    updatePlatformUrl(platform);
  };

  const updateGameFormValue = (field, value) => {
    setGameForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

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

  const topPlatform = homeStats?.platforms?.reduce((top, platform) => {
    if (!top || (platform.games_count || 0) > (top.games_count || 0)) {
      return platform;
    }
    return top;
  }, null);
  const selectedPlatformStats = homeStats?.platforms?.find(
    (platform) => platform.sheet_name === selectedPlatform
  );
  const studioCount = new Set(
    games
      .map((game) => game.Studio)
      .filter((studio) => studio !== null && studio !== undefined && String(studio).trim() !== "")
      .map((studio) => String(studio).trim().toLowerCase())
  ).size;

  const totalGames = homeStats?.totals?.games_count;
  const totalPrice = homeStats?.totals?.total_price;
  const averagePrice = homeStats?.totals?.average_price;

  if (currentView === "home") {
    return (
      <main className="appShell">
        <header className="hero">
          <div>
            <p className="eyebrow">Tableau de bord</p>
            <h1>{homeStats?.title || "Collection Jeux Video"}</h1>
            <p className="subtitle">
              Une vue d'ensemble de la collection, alimentee par l'onglet Accueil du
              fichier ODS.
            </p>
          </div>
          <div className="heroActions">
            <button
              type="button"
              onClick={openAddGamePage}
              disabled={platforms.length === 0}
            >
              Ajouter un jeu
            </button>
            <button
              className="secondaryButton"
              type="button"
              onClick={() => openPlatform(selectedPlatform || platforms[0] || "")}
              disabled={platforms.length === 0}
            >
              Voir les jeux
            </button>
          </div>
        </header>

        {error ? <p className="error">{error}</p> : null}
        {isLoadingHome ? <p>Chargement des statistiques...</p> : null}

        {!isLoadingHome && homeStats ? (
          <>
            <section className="homeSearchSection" aria-label="Recherche de jeux">
              {(hasSearchedGames || homeSearchResults.length > 0) && !isSearchingGames ? (
                <button
                  className="closeSearchButton"
                  type="button"
                  aria-label="Fermer les resultats de recherche"
                  onClick={() => {
                    setHomeSearchResults([]);
                    setHomeSearchError("");
                    setHasSearchedGames(false);
                    setHomeSearchQuery("");
                  }}
                >
                  x
                </button>
              ) : null}
              <form className="homeSearchForm" onSubmit={searchGamesByName}>
                <label htmlFor="home-search">Rechercher un jeu</label>
                <div>
                  <input
                    id="home-search"
                    type="search"
                    value={homeSearchQuery}
                    onChange={(event) => setHomeSearchQuery(event.target.value)}
                    placeholder="Nom du jeu..."
                  />
                  <button type="submit" disabled={isSearchingGames}>
                    Rechercher
                  </button>
                </div>
              </form>

              {isSearchingGames ? (
                <div className="searchLoadingBar" aria-label="Recherche en cours" role="status">
                  <span />
                </div>
              ) : null}
              {homeSearchError ? <p className="error">{homeSearchError}</p> : null}
              {hasSearchedGames && !isSearchingGames && homeSearchResults.length === 0 ? (
                <p>Aucun jeu trouve pour cette recherche.</p>
              ) : null}

              {homeSearchResults.length > 0 ? (
                <div className="searchResults">
                  {homeSearchResults.map((game, index) => (
                    <article
                      className="searchResultCard"
                      key={`${game.Plateforme}-${game["Nom du jeu"]}-${index}`}
                    >
                      <div>
                        <span>{game.Plateforme}</span>
                        <h3>{game["Nom du jeu"]}</h3>
                      </div>
                      <dl>
                        <div>
                          <dt>Studio</dt>
                          <dd>{formatCellValue("Studio", game.Studio)}</dd>
                        </div>
                        <div>
                          <dt>Sortie</dt>
                          <dd>{formatCellValue("Date", game["Date de sortie"])}</dd>
                        </div>
                        <div>
                          <dt>Achat</dt>
                          <dd>{formatCellValue("Date", game["Date d'achat"])}</dd>
                        </div>
                        <div>
                          <dt>Note</dt>
                          <dd>{formatCellValue("Note", game.Note)}</dd>
                        </div>
                        <div>
                          <dt>Prix</dt>
                          <dd>{formatCurrency(game["Prix d'achat"])}</dd>
                        </div>
                        <div>
                          <dt>Version</dt>
                          <dd>{formatCellValue("Version", game.Version)}</dd>
                        </div>
                      </dl>
                      <button type="button" onClick={() => openPlatform(game.Plateforme)}>
                        Voir la plateforme
                      </button>
                    </article>
                  ))}
                </div>
              ) : null}
            </section>

            <section className="statsGrid" aria-label="Statistiques principales">
              <article className="statCard">
                <span>Total jeux</span>
                <strong>{formatNumber(totalGames)}</strong>
              </article>
              <article className="statCard">
                <span>Valeur totale</span>
                <strong>{formatCurrency(totalPrice)}</strong>
              </article>
              <article className="statCard">
                <span>Prix moyen</span>
                <strong>{formatCurrency(averagePrice)}</strong>
              </article>
              <article className="statCard">
                <span>Plateforme la plus fournie</span>
                <strong>{topPlatform ? topPlatform.name : "-"}</strong>
              </article>
            </section>

            <section className="dateBand" aria-label="Periode de la collection">
              <div>
                <span>Premier jeu</span>
                <strong>{formatCellValue("Date", homeStats.first_game_date)}</strong>
              </div>
              <div>
                <span>Dernier jeu</span>
                <strong>{formatCellValue("Date", homeStats.last_game_date)}</strong>
              </div>
            </section>

            <section className="platformSection">
              <div className="sectionHeader">
                <h2>Plateformes</h2>
                <span>{formatNumber(homeStats.platforms?.length || 0)} onglets</span>
              </div>
              <div className="platformGrid">
                {(homeStats.platforms || []).map((platform) => (
                  <article
                    className={`platformCard${platform.has_image ? " platformCardWithImage" : ""}`}
                    key={platform.name}
                    style={
                      platform.image_url
                        ? { backgroundImage: `url("${encodeURI(platform.image_url)}")` }
                        : undefined
                    }
                  >
                    <div>
                      <h3>{platform.name}</h3>
                      <p>{formatNumber(platform.games_count)} jeux</p>
                    </div>
                    <dl>
                      <div>
                        <dt>Prix</dt>
                        <dd>{formatCurrency(platform.total_price)}</dd>
                      </div>
                      <div>
                        <dt>Moyen</dt>
                        <dd>{formatCurrency(platform.average_price)}</dd>
                      </div>
                    </dl>
                    <button
                      type="button"
                      onClick={() => openPlatform(platform.sheet_name)}
                    >
                      Ouvrir
                    </button>
                  </article>
                ))}
              </div>
            </section>
          </>
        ) : null}
      </main>
    );
  }

  if (currentView === "addGame") {
    return (
      <main className="container">
        <button className="backButton" type="button" onClick={goHome}>
          Accueil
        </button>
        <section className="addGameHeader">
          <p className="eyebrow">Nouveau jeu</p>
          <h1>Ajouter un jeu</h1>
          <p className="subtitle">
            Le jeu sera ajoute dans l'onglet de la plateforme selectionnee, en
            conservant le style du fichier ODS.
          </p>
        </section>

        {addGameError ? <p className="error">{addGameError}</p> : null}
        {addGameMessage ? <p className="success">{addGameMessage}</p> : null}

        <form className="addGameForm" onSubmit={submitNewGame}>
          <label>
            Plateforme
            <select
              value={gameForm.platform}
              onChange={(event) => updateGameFormValue("platform", event.target.value)}
              required
            >
              <option value="">Choisir une plateforme</option>
              {platforms.map((platform) => (
                <option key={platform} value={platform}>
                  {platform}
                </option>
              ))}
            </select>
          </label>

          <label>
            Nom du jeu
            <input
              type="text"
              value={gameForm["Nom du jeu"]}
              onChange={(event) => updateGameFormValue("Nom du jeu", event.target.value)}
              required
            />
          </label>

          <label>
            Studio
            <input
              list="studio-options"
              type="text"
              value={gameForm.Studio}
              onChange={(event) => updateGameFormValue("Studio", event.target.value)}
            />
            <datalist id="studio-options">
              {(addGameColumnValues.Studio || []).map((studio) => (
                <option key={studio} value={studio} />
              ))}
            </datalist>
          </label>

          <label>
            Date de sortie
            <input
              type="date"
              value={gameForm["Date de sortie"]}
              onChange={(event) => updateGameFormValue("Date de sortie", event.target.value)}
            />
          </label>

          <label>
            Date d'achat
            <input
              type="date"
              value={gameForm["Date d'achat"]}
              onChange={(event) => updateGameFormValue("Date d'achat", event.target.value)}
            />
          </label>

          <label>
            Lieu d'achat
            <input
              type="text"
              value={gameForm["Lieu d'achat"]}
              onChange={(event) => updateGameFormValue("Lieu d'achat", event.target.value)}
            />
          </label>

          <label>
            Note
            <input
              type="text"
              value={gameForm.Note}
              onChange={(event) => updateGameFormValue("Note", event.target.value)}
              placeholder="8/10"
            />
          </label>

          <label>
            Prix d'achat
            <input
              type="number"
              min="0"
              step="0.01"
              value={gameForm["Prix d'achat"]}
              onChange={(event) => updateGameFormValue("Prix d'achat", event.target.value)}
            />
          </label>

          <label>
            Version
            <input
              list="version-options"
              type="text"
              value={gameForm.Version}
              onChange={(event) => updateGameFormValue("Version", event.target.value)}
              placeholder="FR, PAL, NTSC..."
            />
            <datalist id="version-options">
              {(addGameColumnValues.Version || []).map((version) => (
                <option key={version} value={version} />
              ))}
            </datalist>
          </label>

          <div className="formActions">
            <button type="button" className="secondaryButton" onClick={goHome}>
              Annuler
            </button>
            <button type="submit" disabled={isAddingGame}>
              {isAddingGame ? "Ajout en cours..." : "Ajouter le jeu"}
            </button>
          </div>
        </form>
      </main>
    );
  }

  return (
    <main className="container">
      <button className="backButton" type="button" onClick={goHome}>
        Accueil
      </button>
      <section
        className={`platformDetailHero${
          selectedPlatformStats?.has_image ? " platformDetailHeroWithImage" : ""
        }`}
        style={
          selectedPlatformStats?.image_url
            ? { backgroundImage: `url("${encodeURI(selectedPlatformStats.image_url)}")` }
            : undefined
        }
      >
        <div className="platformDetailContent">
          <p className="eyebrow">Plateforme</p>
          <h1>{selectedPlatformStats?.name || selectedPlatform || "Collection Jeux Video"}</h1>
          <p className="subtitle">Filtrer la liste par plateforme (onglet ODS)</p>
        </div>
        <div className="platformDetailStats" aria-label="Statistiques de la plateforme">
          <article>
            <span>Jeux</span>
            <strong>{formatNumber(selectedPlatformStats?.games_count ?? games.length)}</strong>
          </article>
          <article>
            <span>Valeur</span>
            <strong>{formatCurrency(selectedPlatformStats?.total_price)}</strong>
          </article>
          <article>
            <span>Prix moyen</span>
            <strong>{formatCurrency(selectedPlatformStats?.average_price)}</strong>
          </article>
          <article>
            <span>Studios</span>
            <strong>{formatNumber(studioCount)}</strong>
          </article>
        </div>
      </section>
      {error ? <p className="error">{error}</p> : null}

      <div className="controls">
        <label htmlFor="platform">Plateforme :</label>
        <select
          id="platform"
          value={selectedPlatform}
          onChange={(event) => openPlatform(event.target.value)}
          disabled={isLoadingPlatforms || platforms.length === 0}
        >
          {platforms.map((platform) => (
            <option key={platform} value={platform}>
              {platform}
            </option>
          ))}
        </select>
      </div>

      {isLoadingPlatforms ? <p>Chargement des plateformes...</p> : null}
      {isLoadingGames ? <p>Chargement des jeux...</p> : null}

      {!isLoadingGames && games.length === 0 ? (
        <p>Aucun jeu a afficher pour cette plateforme.</p>
      ) : null}

      {!isLoadingGames && games.length > 0 ? (
        <div className="tableWrapper">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column} className={getColumnClassName(column)}>
                    <button
                      className="sortButton"
                      type="button"
                      onClick={() => toggleSort(column)}
                      aria-label={`Trier ${column} en ${
                        sortConfig.column === column && sortConfig.direction === "asc"
                          ? "descendant"
                          : "ascendant"
                      }`}
                    >
                      <span>{column}</span>
                      {renderSortIcon(column)}
                    </button>
                  </th>
                ))}
              </tr>
              <tr>
                {columns.map((column) => (
                  <th
                    key={`${column}-filter`}
                    className={`filterCell ${getColumnClassName(column)}`}
                  >
                    {isSelectFilterColumn(column) ? (
                      <select
                        value={columnFilters[column] || ""}
                        onChange={(event) =>
                          setColumnFilters((previous) => ({
                            ...previous,
                            [column]: event.target.value,
                          }))
                        }
                      >
                        <option value="">Tous</option>
                        {(valuesByColumn[column] || []).map((value) => (
                          <option key={value} value={value}>
                            {value}
                          </option>
                        ))}
                      </select>
                    ) : isDateColumn(column) ? (
                      <div className="dateFilterGroup">
                        <select
                          value={columnFilters[column]?.operator || "="}
                          onChange={(event) =>
                            setColumnFilters((previous) => ({
                              ...previous,
                              [column]: {
                                operator: event.target.value,
                                year: previous[column]?.year || "",
                              },
                            }))
                          }
                        >
                          <option value="=">{"="}</option>
                          <option value=">">{">"}</option>
                          <option value="<">{"<"}</option>
                        </select>
                        <select
                          value={columnFilters[column]?.year || ""}
                          onChange={(event) =>
                            setColumnFilters((previous) => ({
                              ...previous,
                              [column]: {
                                operator: previous[column]?.operator || "=",
                                year: event.target.value,
                              },
                            }))
                          }
                        >
                          <option value="">Toutes</option>
                          {getDateYearOptions(column).map((year) => (
                            <option key={`${column}-${year}`} value={String(year)}>
                              {year}
                            </option>
                          ))}
                        </select>
                      </div>
                    ) : (
                      <input
                        type="text"
                        value={columnFilters[column] || ""}
                        onChange={(event) =>
                          setColumnFilters((previous) => ({
                            ...previous,
                            [column]: event.target.value,
                          }))
                        }
                        placeholder="Filtrer..."
                      />
                    )}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedGames.map((game, index) => (
                <tr key={`${game["Nom du jeu"] || "game"}-${index}`}>
                  {columns.map((column) => (
                    <td key={`${column}-${index}`} className={getColumnClassName(column)}>
                      {column === "Version"
                        ? renderVersionValue(game[column])
                        : formatCellValue(column, game[column])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}

      {!isLoadingGames && games.length > 0 && filteredGames.length === 0 ? (
        <p>Aucun jeu ne correspond aux filtres de colonnes.</p>
      ) : null}
    </main>
  );
}

export default App;
