import { defineConfig } from "astro/config";

import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import partytown from "@astrojs/partytown";

// https://astro.build/config
export default defineConfig({
  site: "https://narse.github.io",
  integrations: [
    sitemap({
      entryLimit: 45000,  // 한 파일에 모든 URL 포함
    }),
    partytown({
      config: {
        forward: ["dataLayer.push"],
      },
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  output: "static",  // GitHub Pages용 정적 빌드
});
