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
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./styles.css";

/**
 * Monte l'application React dans le noeud HTML racine.
 *
 * @param {void} Aucun - Le noeud racine est lu directement dans le DOM.
 * @returns {void} Rend le composant `App` dans le DOM via React.
 */
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
