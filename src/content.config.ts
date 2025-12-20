import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

// 로컬 Markdown 파일 기반 콘텐츠 설정
// 글은 src/content/posts/ 폴더에 .md 파일로 작성

const posts = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/posts" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    publishedAt: z.coerce.date(),
    updatedAt: z.coerce.date().optional(),
    coverImage: z.string().optional(),
    category: z.string().default("blog"),
    tags: z.array(z.string()).default([]),
    author: z.string().default("Admin"),
    featured: z.boolean().default(false),
    draft: z.boolean().default(false),
  }),
});

const page = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/pages" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
  }),
});

export const collections = { posts, page };
