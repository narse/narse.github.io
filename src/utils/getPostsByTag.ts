import type { CollectionEntry } from "astro:content";
import { slugifyAll } from "./slugify";
import getSortedPosts from "./getSortedPosts";

const getPostsByTag = (posts: CollectionEntry<"posts">[], tag: string) =>
  getSortedPosts(
    posts.filter((post) => slugifyAll(post.data.tags).includes(tag)),
  );

export default getPostsByTag;
