import { defineConfig } from "astro/config";

import alpinejs from "@astrojs/alpinejs";
import vercel from "@astrojs/vercel";
import partytown from "@astrojs/partytown";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";

import { rehypePrettyCode } from "rehype-pretty-code";
import { transformerCopyButton } from "@rehype-pretty/transformers";
import moonlightTheme from "./public/theme/moonlight-ii.json";

// https://astro.build/config
export default defineConfig({
  markdown: {
    syntaxHighlight: false,
    rehypePlugins: [
      [
        rehypePrettyCode,
        {
          theme: moonlightTheme,
          transformers: [
            transformerCopyButton({
              visibility: "hover",
              feedbackDuration: 2_500,
            }),
          ],
        },
      ],
    ],
  },
  integrations: [
    alpinejs(),
    partytown(),
    sitemap({
      site: "https://skyscript.vercel.app",
    }),
  ],
  vite: {
    plugins: [tailwindcss()],
  },
  output: "server",
  adapter: vercel(),
});
