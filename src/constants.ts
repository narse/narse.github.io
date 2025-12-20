// ======================
// Site Configuration
// ======================
// Edit these values to customize your site

export const SITE_NAME = "지원금 25시";
export const SITE_TITLE = "지원금 25시 - 정부지원금 정보 허브";
export const SITE_DESCRIPTION =
  "정부지원금, 보조금, 복지혜택 정보를 한눈에! 최신 지원금 소식과 신청 방법을 빠르게 안내해드립니다.";
export const SITE_URL = "https://narse.github.io"; // Your site's base URL (no trailing slash)
export const SITE_LANGUAGE = "ko";

// ======================
// Analytics
// ======================
export const GA_MEASUREMENT_ID = ""; // Replace with your Google Analytics Measurement ID

// ======================
// SEO & Meta Tags
// ======================
export const META_TITLE_TEMPLATE = "%s | 지원금 25시"; // %s will be replaced with page title
export const META_DESCRIPTION = SITE_DESCRIPTION; // Default meta description
export const META_AUTHOR = "지원금 25시";
export const META_KEYWORDS = [
  "정부지원금",
  "보조금",
  "복지혜택",
  "지원금신청",
  "정부혜택",
  "생활지원",
];

// ======================
// Open Graph / Social
// ======================
export const OG_TYPE = "website"; // Default OG type for pages
export const OG_IMAGE = "/og-image.png"; // Default OG image (relative to public folder)
export const OG_IMAGE_ALT = "지원금 25시 - 정부지원금 정보 허브";
export const OG_IMAGE_WIDTH = 1200;
export const OG_IMAGE_HEIGHT = 630;

// ======================
// Twitter Card
// ======================
export const TWITTER_CARD = "summary_large_image"; // 'summary' or 'summary_large_image'
export const TWITTER_SITE = ""; // Your Twitter handle (optional)
export const TWITTER_CREATOR = ""; // Content creator Twitter handle (optional)

// ======================
// Footer Configuration
// ======================
export const FOOTER_COPYRIGHT_NAME = "지원금 25시";
export const FOOTER_COPYRIGHT_TEXT = "All rights reserved.";

// Navigation Links
export const FOOTER_NAV_LINKS = [
  { label: "소개", href: "/about" },
  { label: "블로그", href: "/" },
  { label: "문의", href: "#" },
];

// Social Media Links (set to empty string or remove property to hide)
export const SOCIAL_LINKS = {
  facebook: "",
  instagram: "",
  twitter: "",
  github: "",
  dribbble: "",
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
