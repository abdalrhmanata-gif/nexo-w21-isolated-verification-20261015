export type SameOriginRequestInput = {
  method: string;
  origin?: string | null;
  secFetchSite?: string | null;
  requestOrigin?: string | null;
  siteUrl?: string | null;
};

export function isSameOriginRequest(input: SameOriginRequestInput): boolean;
