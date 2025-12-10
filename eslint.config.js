import tailwind from "eslint-plugin-tailwindcss";
import eslintPluginAstro from "eslint-plugin-astro";

export default [
  ...tailwind.configs["flat/recommended"],
  ...eslintPluginAstro.configs["flat/recommended"],
];
