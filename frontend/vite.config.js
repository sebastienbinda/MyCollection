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
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(() => {
  const frontendPort = Number(process.env.FRONTEND_PORT || 7778);
  const backendPort = Number(process.env.BACKEND_PORT || 7777);

  return {
    plugins: [react()],
    server: {
      port: frontendPort,
      proxy: {
        "/api": {
          target: `http://localhost:${backendPort}`,
          changeOrigin: true,
        },
      "/collections": {
        target: `http://localhost:${backendPort}`,
        changeOrigin: true,
      },
      },
    },
  };
});
