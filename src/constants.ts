// ======================
// Site Configuration
// ======================
// Edit these values to customize your site

export const SITE_NAME = "SkyScript";
export const SITE_TITLE = "The Sky Script Blog";
export const SITE_DESCRIPTION =
  "Dive into Sky Script product updates, company news, and educational content on how developers and startups can leverage the cloud.";
export const SITE_URL = "https://skyscript.com"; // Your site's base URL (no trailing slash)
export const SITE_LANGUAGE = "en";

// ======================
// SEO & Meta Tags
// ======================
export const META_TITLE_TEMPLATE = "%s | SkyScript"; // %s will be replaced with page title
export const META_DESCRIPTION = SITE_DESCRIPTION; // Default meta description
export const META_AUTHOR = "SkyScript Team";
export const META_KEYWORDS = [
  "cloud",
  "developers",
  "startups",
  "technology",
  "blog",
];

// ======================
// Open Graph / Social
// ======================
export const OG_TYPE = "website"; // Default OG type for pages
export const OG_IMAGE = "/og-image.png"; // Default OG image (relative to public folder)
export const OG_IMAGE_ALT = "SkyScript - Cloud for Developers";
export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 630;

// ======================
// Twitter Card
// ======================
export const TWITTER_CARD = "summary_large_image"; // 'summary' or 'summary_large_image'
export const TWITTER_SITE = "@skyscript"; // Your Twitter handle (optional)
export const TWITTER_CREATOR = "@skyscript"; // Content creator Twitter handle (optional)

// ======================
// Footer Configuration
// ======================
export const FOOTER_COPYRIGHT_NAME = "SkyScript, Inc.";
export const FOOTER_COPYRIGHT_TEXT = "All rights reserved.";

// Navigation Links
export const FOOTER_NAV_LINKS = [
  { label: "About", href: "/about" },
  { label: "Blog", href: "#" },
  { label: "Team", href: "#" },
  { label: "Pricing", href: "#" },
  { label: "Contact", href: "#" },
  { label: "Terms", href: "#" },
];

// Social Media Links (set to empty string or remove property to hide)
export const SOCIAL_LINKS = {
  facebook: "#",
  instagram: "#",
  twitter: "#",
  github: "#",
  dribbble: "#",
};

// ======================
// Type Definitions
// ======================
export interface SEOProps {
  title?: string;
  description?: string;
  image?: string;
  imageAlt?: string;
  type?: "website" | "article";
  publishedTime?: string;
  modifiedTime?: string;
  author?: string;
  tags?: string[];
  noindex?: boolean;
}
