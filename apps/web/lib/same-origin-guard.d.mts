export type SameOriginRequestInput = {
  method: string;
  origin?: string | null;
  secFetchSite?: string | null;
  requestOrigin?: string | null;
  siteUrl?: string | null;
  requireSameOriginSignalForSafeMethods?: boolean;
};

export function isSameOriginRequest(input: SameOriginRequestInput): boolean;
