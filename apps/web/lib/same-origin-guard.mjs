const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);
const WEB_PROTOCOLS = new Set(["http:", "https:"]);

function parseOrigin(value, { allowPath = false } = {}) {
  if (typeof value !== "string" || value.length === 0 || value.trim() !== value) return null;

  let url;
  try {
    url = new URL(value);
  } catch {
    return null;
  }

  if (!WEB_PROTOCOLS.has(url.protocol) || url.origin === "null" || url.username || url.password) return null;
  if (!allowPath && (url.pathname !== "/" || url.search || url.hash)) return null;
  return url.origin;
}

/**
 * Check browser origin metadata for state-changing API requests.
 * Requests without Origin are accepted only when Fetch Metadata identifies a
 * same-origin request, or for safe methods without cross-origin metadata.
 */
export function isSameOriginRequest({ method, origin, secFetchSite, requestOrigin, siteUrl }) {
  const fetchSite = String(secFetchSite || "").trim().toLowerCase();
  const allowedOrigins = new Set([
    parseOrigin(requestOrigin),
    parseOrigin(siteUrl, { allowPath: true }),
  ].filter(Boolean));

  if (origin !== null && origin !== undefined) {
    const parsedOrigin = parseOrigin(origin);
    if (parsedOrigin === null) return false;
    // Some deployment adapters report a canonical URL that differs from the
    // browser-visible request origin. Fetch Metadata is browser-controlled;
    // honor its same-origin signal when the Origin itself is valid.
    return allowedOrigins.has(parsedOrigin) || fetchSite === "same-origin";
  }

  // Fetch Metadata also protects safe-verb API endpoints that can still cause
  // upstream egress (for example, the authenticated AI diagnostics GET).
  // Same-site requests may still come from a different, potentially hostile,
  // sibling origin, so only same-origin or user-initiated navigation is
  // allowed when Origin is absent.
  if (fetchSite === "cross-site" || fetchSite === "same-site") return false;
  if (fetchSite === "same-origin") return true;

  if (SAFE_METHODS.has(String(method || "").toUpperCase())) return true;

  return false;
}
