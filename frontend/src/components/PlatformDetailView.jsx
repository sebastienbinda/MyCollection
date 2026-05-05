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
import {
  formatCurrency,
  formatNumber,
} from "../collectionUtils";
import GameTable from "./GameTable";

/**
 * Page de detail d'une plateforme avec statistiques, filtres et tableau de jeux.
 *
 * @param {Object} props - Donnees de plateforme, tableau filtre/trie et callbacks.
 * @returns {import("react").JSX.Element} Vue detail plateforme.
 */
function PlatformDetailView({
  selectedPlatform,
  selectedPlatformStats,
  studioCount,
  platforms,
  games,
  columns,
  valuesByColumn,
  columnFilters,
  sortConfig,
  sortedGames,
  filteredGames,
  deleteGameMessage,
  deleteGameError,
  error,
  isLoadingPlatforms,
  isLoadingGames,
  canDeleteGame,
  onBack,
  onOpenPlatform,
  onToggleSort,
  onColumnFiltersChange,
  onDeleteGame,
}) {
  /**
   * Indique si une note de jeu merite une mise en avant.
   *
   * @param {unknown} value - Valeur brute de la colonne `Note`.
   * @returns {boolean} `true` si la note est egale ou superieure a 9/10.
   */
  const isTopRatedGame = (value) => {
    const textValue = String(value || "").trim().replace(",", ".");
    if (!textValue) {
      return false;
    }

    const [scoreText, maxText] = textValue.split("/");
    const score = Number.parseFloat(scoreText);
    const max = Number.parseFloat(maxText || "10");
    if (Number.isNaN(score) || Number.isNaN(max) || max === 0) {
      return false;
    }

    return (score / max) * 10 >= 9;
  };

  return (
    <main className="container">
      <button className="backButton" type="button" onClick={onBack}>
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
          <h1>{selectedPlatformStats?.name || selectedPlatform || "CloudCollectionApp"}</h1>
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
      {deleteGameError ? <p className="error">{deleteGameError}</p> : null}
      {deleteGameMessage ? <p className="success">{deleteGameMessage}</p> : null}

      <div className="controls">
        <label htmlFor="platform">Plateforme :</label>
        <select
          id="platform"
          value={selectedPlatform}
          onChange={(event) => onOpenPlatform(event.target.value)}
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
        <GameTable
          games={games}
          columns={columns}
          valuesByColumn={valuesByColumn}
          columnFilters={columnFilters}
          sortConfig={sortConfig}
          sortedGames={sortedGames}
          onToggleSort={onToggleSort}
          onColumnFiltersChange={onColumnFiltersChange}
          getRowClassName={(game) =>
            isTopRatedGame(game.Note) ? "topRatedGameRow" : ""
          }
          renderRowActions={
            canDeleteGame
              ? (game) => (
                  <button
                    className="wishlistIconButton dangerIconButton"
                    type="button"
                    aria-label={`Supprimer ${game["Nom du jeu"] || "ce jeu"} de la plateforme`}
                    title="Supprimer de la plateforme"
                    onClick={() => onDeleteGame(game)}
                  >
                    <svg aria-hidden="true" className="wishlistActionIcon" viewBox="0 0 24 24">
                      <path d="M9 3h6l1 2h4v2H4V5h4l1-2Z" />
                      <path d="M6 9h12l-1 12H7L6 9Zm4 2v8h2v-8h-2Zm4 0v8h2v-8h-2Z" />
                    </svg>
                  </button>
                )
              : null
          }
        />
      ) : null}

      {!isLoadingGames && games.length > 0 && filteredGames.length === 0 ? (
        <p>Aucun jeu ne correspond aux filtres de colonnes.</p>
      ) : null}
    </main>
  );
}

export default PlatformDetailView;
