import { defineCollection } from "astro:content";
import { postsLoader, authorsLoader, tagsLoader } from "@astracms/astro-loader";

const config = {
  apiKey: import.meta.env.ASTRACMS_API_KEY,
};

const posts = defineCollection({
  loader: postsLoader({
    ...config,
    format: "markdown",
    categories: ["blog"],
  }),
});

const page = defineCollection({
  loader: postsLoader({
    ...config,
    format: "markdown",
    categories: ["page"],
  }),
});

const authors = defineCollection({
  loader: authorsLoader(config),
});

const tags = defineCollection({
  loader: tagsLoader(config),
});

export const collections = { posts, page, authors, tags };
