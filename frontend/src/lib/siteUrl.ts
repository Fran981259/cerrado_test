const PRODUCTION_SITE_URL = "https://www.portalcerrado.com.br";

/** Returns the only URL allowed in public SEO metadata. */
export function getPublicSiteUrl(): string {
  const configured = process.env.NEXT_PUBLIC_SITE_URL?.trim();
  if (!configured) return PRODUCTION_SITE_URL;

  try {
    const url = new URL(configured);
    const isHttp = url.protocol === "http:" || url.protocol === "https:";
    const isLocalHost = url.hostname === "localhost" || url.hostname === "127.0.0.1" || url.hostname === "::1";
    const isPrivateIpv4 = /^(10\.|127\.|192\.168\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(url.hostname);
    if (isHttp && !isLocalHost && !isPrivateIpv4) return url.origin;
  } catch {
    // Invalid build-time input must not become public metadata.
  }

  return PRODUCTION_SITE_URL;
}
