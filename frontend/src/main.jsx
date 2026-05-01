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
