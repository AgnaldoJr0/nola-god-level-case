import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  // serve the frontend folder itself when running from inside frontend/
  root: '.',
  plugins: [vue()],
  build: {
    rollupOptions: {
      // simple relative input path
      input: 'src/main.js',
    },
    outDir: '../dist',
  },
  server: {
    proxy: {
      "/api": {
        // backend runserver default
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
