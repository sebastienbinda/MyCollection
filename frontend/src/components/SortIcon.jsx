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
/**
 * Icone SVG indiquant l'etat du tri d'une colonne.
 *
 * @param {{column: string, sortConfig: {column: string, direction: "asc"|"desc"}}} props - Colonne et tri courant.
 * @returns {import("react").JSX.Element} Icone de tri ascendante, descendante ou inactive.
 */
function SortIcon({ column, sortConfig }) {
  const isActive = sortConfig.column === column;
  const direction = isActive ? sortConfig.direction : "both";

  return (
    <svg
      className={`sortIcon sortIcon-${direction}`}
      viewBox="0 0 16 16"
      aria-hidden="true"
      focusable="false"
    >
      <path className="sortIconUp" d="M8 3.2 4.6 6.6h6.8L8 3.2Z" />
      <path className="sortIconDown" d="M8 12.8 11.4 9.4H4.6L8 12.8Z" />
    </svg>
  );
}

export default SortIcon;
