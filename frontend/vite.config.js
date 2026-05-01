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
