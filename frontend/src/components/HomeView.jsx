import { formatCellValue, formatCurrency, formatNumber } from "../collectionUtils";

/**
 * Page d'accueil avec statistiques, recherche globale et cartes plateformes.
 *
 * @param {Object} props - Donnees et callbacks necessaires a la page d'accueil.
 * @returns {import("react").JSX.Element} Vue d'accueil.
 */
function HomeView({
  homeStats,
  platforms,
  selectedPlatform,
  error,
  isLoadingHome,
  isSearchingGames,
  hasSearchedGames,
  homeSearchQuery,
  homeSearchResults,
  homeSearchError,
  cacheResetMessage,
  cacheResetError,
  isResettingCache,
  downloadError,
  isDownloadingOds,
  canAddGame,
  canResetCache,
  canDownloadOds,
  isAuthenticated,
  onAddGame,
  onLogout,
  onOpenWishlist,
  onOpenPlatform,
  onSearchQueryChange,
  onSearchSubmit,
  onCloseSearch,
  onResetCache,
  onDownloadOds,
}) {
  const topPlatform = homeStats?.platforms?.reduce((top, platform) => {
    if (!top || (platform.games_count || 0) > (top.games_count || 0)) {
      return platform;
    }
    return top;
  }, null);
  return (
    <main className="appShell">
      <header className="pageHeader">
        {isAuthenticated ? (
          <button
            className="authButtonLink pageHeaderAuthButton authButtonConnected"
            type="button"
            aria-label="Se deconnecter"
            title="Se deconnecter"
            onClick={onLogout}
          >
            <svg aria-hidden="true" className="authStatusIcon" viewBox="0 0 24 24">
              <path d="M12 2a5 5 0 0 1 5 5v3h1a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2h1V7a5 5 0 0 1 5-5Zm0 2a3 3 0 0 0-3 3v3h6V7a3 3 0 0 0-3-3Zm1 11.73A2 2 0 1 0 11 15.73V19h2v-3.27Z" />
            </svg>
          </button>
        ) : (
          <a
            className="authButtonLink pageHeaderAuthButton"
            href="/auth"
            aria-label="Connexion"
            title="Connexion"
          >
            <svg aria-hidden="true" className="authStatusIcon" viewBox="0 0 24 24">
              <path d="M12 2a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 12c4.42 0 8 2.24 8 5v2H4v-2c0-2.76 3.58-5 8-5Z" />
            </svg>
            <span>Connexion</span>
          </a>
        )}
        <div>
          <p className="eyebrow">Collection personnelle</p>
          <h1>{homeStats?.title || "Ma collection"}</h1>
          <p className="pageHeaderDateSummary">
            <span>Premier jeu : {formatCellValue("Date", homeStats?.first_game_date)}</span>
            <span>Dernier jeu : {formatCellValue("Date", homeStats?.last_game_date)}</span>
          </p>
          <p className="subtitle">Jeux, plateformes et statistiques essentielles.</p>
        </div>
        <div className="pageHeaderActionArea">
          <div className="pageHeaderActions">
            {canAddGame ? (
              <button type="button" onClick={onAddGame} disabled={platforms.length === 0}>
                Ajouter un jeu
              </button>
            ) : null}
            <button className="secondaryButton" type="button" onClick={onOpenWishlist}>
              Liste de souhaits
            </button>
            {canResetCache ? (
              <button
                className="secondaryButton"
                type="button"
                onClick={onResetCache}
                disabled={isResettingCache}
              >
                {isResettingCache ? "Reset..." : "Reset cache"}
              </button>
            ) : null}
            {canDownloadOds ? (
              <button
                className="downloadOdsButton"
                type="button"
                onClick={onDownloadOds}
                disabled={isDownloadingOds}
              >
                {isDownloadingOds ? "Telechargement..." : "Telecharger ODS"}
              </button>
            ) : null}
            <button
              className="secondaryButton"
              type="button"
              onClick={() => onOpenPlatform(selectedPlatform || platforms[0] || "")}
              disabled={platforms.length === 0}
            >
              Voir les jeux
            </button>
          </div>
        </div>
      </header>

      {error ? <p className="error">{error}</p> : null}
      {cacheResetError ? <p className="error">{cacheResetError}</p> : null}
      {downloadError ? <p className="error">{downloadError}</p> : null}
      {cacheResetMessage ? <p className="success">{cacheResetMessage}</p> : null}
      {isLoadingHome ? <p>Chargement des statistiques...</p> : null}

      {!isLoadingHome && homeStats ? (
        <>
          <section className="homeSearchSection" aria-label="Recherche de jeux">
            {(hasSearchedGames || homeSearchResults.length > 0) && !isSearchingGames ? (
              <button
                className="closeSearchButton"
                type="button"
                aria-label="Fermer les resultats de recherche"
                onClick={onCloseSearch}
              >
                x
              </button>
            ) : null}
            <form className="homeSearchForm" onSubmit={onSearchSubmit}>
              <label htmlFor="home-search">Rechercher un jeu</label>
              <div>
                <input
                  id="home-search"
                  type="search"
                  value={homeSearchQuery}
                  onChange={(event) => onSearchQueryChange(event.target.value)}
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
                    <button type="button" onClick={() => onOpenPlatform(game.Plateforme)}>
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
              <strong>{formatNumber(homeStats.totals?.games_count)}</strong>
            </article>
            <article className="statCard">
              <span>Valeur totale</span>
              <strong>{formatCurrency(homeStats.totals?.total_price)}</strong>
            </article>
            <article className="statCard">
              <span>Prix moyen</span>
              <strong>{formatCurrency(homeStats.totals?.average_price)}</strong>
            </article>
            <article className="statCard">
              <span>Plateforme la plus fournie</span>
              <strong>{topPlatform ? topPlatform.name : "-"}</strong>
            </article>
          </section>

          <section className="platformSection">
            <div className="sectionHeader">
              <div>
                <h2>Plateformes</h2>
                <span>{formatNumber(homeStats.platforms?.length || 0)} onglets</span>
              </div>
            </div>
            <div className="platformGrid">
              {(homeStats.platforms || []).map((platform) => (
                <article
                  className={[
                    "platformCard",
                    platform.has_image ? "platformCardWithImage" : "",
                    topPlatform?.sheet_name === platform.sheet_name ? "platformCardTopCount" : "",
                  ].join(" ")}
                  key={platform.name}
                  style={
                    platform.image_url
                      ? { backgroundImage: `url("${encodeURI(platform.image_url)}")` }
                      : undefined
                  }
                >
                  <div className="platformCardHeader">
                    <h3>{platform.name}</h3>
                    <p className="platformGameCount">
                      {formatNumber(platform.games_count)} jeux
                    </p>
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
                  <button type="button" onClick={() => onOpenPlatform(platform.sheet_name)}>
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

export default HomeView;
