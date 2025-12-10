import type { CollectionEntry } from "astro:content";
import postFilter from "./postFilter";

const getSortedPosts = (posts: CollectionEntry<"posts">[]) => {
  return posts
    .filter(postFilter)
    .sort(
      (a, b) =>
        Math.floor(
          new Date(b.data.updatedAt ?? b.data.publishedAt).getTime() / 1000,
        ) -
        Math.floor(
          new Date(a.data.updatedAt ?? a.data.publishedAt).getTime() / 1000,
        ),
    );
};

export default getSortedPosts;
