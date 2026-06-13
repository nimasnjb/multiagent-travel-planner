import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/multiagent-travel-planner/",
  plugins: [react()],
});
