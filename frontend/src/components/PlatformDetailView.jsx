import {
  formatCellValue,
  formatCurrency,
  formatNumber,
  getColumnClassName,
  getDateYearOptions,
  isDateColumn,
  isSelectFilterColumn,
} from "../collectionUtils";
import SortIcon from "./SortIcon";

/**
 * Rend des pictogrammes de region/version pour une cellule `Version`.
 *
 * @param {unknown} value - Valeur brute de version, par exemple `PAL FR`.
 * @returns {string|import("react").JSX.Element} Tiret si vide, sinon span avec les pictogrammes.
 */
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
  error,
  isLoadingPlatforms,
  isLoadingGames,
  onBack,
  onOpenPlatform,
  onToggleSort,
  onColumnFiltersChange,
}) {
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
        <div className="tableWrapper">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column} className={getColumnClassName(column)}>
                    <button
                      className="sortButton"
                      type="button"
                      onClick={() => onToggleSort(column)}
                      aria-label={`Trier ${column} en ${
                        sortConfig.column === column && sortConfig.direction === "asc"
                          ? "descendant"
                          : "ascendant"
                      }`}
                    >
                      <span>{column}</span>
                      <SortIcon column={column} sortConfig={sortConfig} />
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
                          onColumnFiltersChange((previous) => ({
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
                            onColumnFiltersChange((previous) => ({
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
                            onColumnFiltersChange((previous) => ({
                              ...previous,
                              [column]: {
                                operator: previous[column]?.operator || "=",
                                year: event.target.value,
                              },
                            }))
                          }
                        >
                          <option value="">Toutes</option>
                          {getDateYearOptions(valuesByColumn, column).map((year) => (
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
                          onColumnFiltersChange((previous) => ({
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

export default PlatformDetailView;
