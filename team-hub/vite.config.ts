import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
  plugins: [react()],
  base: "/ddthon/",
  build: { chunkSizeWarningLimit: 1600 },
});
