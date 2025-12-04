import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  root: ".",
  plugins: [react()],

  resolve: {
    alias: {
      "@components": "./src/components",
      "@services": "./src/services",
      "@styles": "./src/styles",
    },
  },

  server: {
    port: 5173,
    strictPort: false,
    open: true,

    // Proxy API to FastAPI backend
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
