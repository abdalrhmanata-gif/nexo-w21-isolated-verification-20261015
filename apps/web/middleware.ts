import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { isSameOriginRequest } from "./lib/same-origin-guard.mjs";

type RuntimeGlobal = typeof globalThis & {
  Netlify?: {
    env?: {
      get(name: string): string | undefined;
    };
  };
  process?: {
    env?: Record<string, string | undefined>;
  };
};

function getRuntimeEnv(name: string) {
  const runtimeGlobal = globalThis as RuntimeGlobal;
  return runtimeGlobal.Netlify?.env?.get(name) ?? runtimeGlobal.process?.env?.[name];
}

export async function middleware(request: NextRequest) {
  const pathname = request.nextUrl.pathname;
  const isApiRequest = pathname === "/api" || pathname.startsWith("/api/");
  const isInternalApiRequest = pathname === "/api/internal" || pathname.startsWith("/api/internal/");

  // The worker endpoint has its own fail-closed bearer-token boundary.
  if (isApiRequest && isInternalApiRequest) return NextResponse.next();

  if (isApiRequest) {
    // This authenticated GET can make an outbound provider request, so it
    // requires explicit browser same-origin provenance even though GET is safe
    // with respect to application state.
    const requiresBrowserProvenance = pathname.replace(/\/+$/, "") === "/api/ai/diagnostics";
    if (!isInternalApiRequest && !isSameOriginRequest({
      method: request.method,
      origin: request.headers.get("origin"),
      secFetchSite: request.headers.get("sec-fetch-site"),
      requestOrigin: request.nextUrl.origin,
      siteUrl: getRuntimeEnv("NEXT_PUBLIC_SITE_URL"),
      requireSameOriginSignalForSafeMethods: requiresBrowserProvenance,
    })) {
      return NextResponse.json({ error: "Cross-origin request blocked." }, { status: 403 });
    }
    // API route handlers own their session checks; do not duplicate Supabase
    // auth lookups here. The internal worker route separately checks its token.
    return NextResponse.next({ request });
  }

  // Read the public Supabase values at runtime. This prevents Next.js from
  // embedding the publishable key into the generated Netlify middleware bundle.
  const supabaseUrl = getRuntimeEnv("NEXT_PUBLIC_SUPABASE_URL");
  const supabasePublishableKey = getRuntimeEnv("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY");

  if (!supabaseUrl || !supabasePublishableKey) return NextResponse.next();

  let response = NextResponse.next({ request });
  const supabase = createServerClient(supabaseUrl, supabasePublishableKey, {
    cookies: {
      getAll: () => request.cookies.getAll(),
      setAll(cookiesToSet) {
        cookiesToSet.forEach(({ name, value }) => request.cookies.set(name, value));
        response = NextResponse.next({ request });
        cookiesToSet.forEach(({ name, value, options }) => response.cookies.set(name, value, options));
      },
    },
  });

  const { data: { user } } = await supabase.auth.getUser();
  if (request.nextUrl.pathname === "/auth/reset-password") {
    response.headers.set("Referrer-Policy", "no-referrer");
    response.headers.set("Cache-Control", "no-store");
  }
  if (request.nextUrl.pathname.startsWith("/app") && !user) {
    const url = request.nextUrl.clone();
    url.pathname = "/auth/sign-in";
    url.searchParams.set("next", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }
  const isConfirmationEndpoint = request.nextUrl.pathname === "/auth/callback"
    || request.nextUrl.pathname === "/auth/confirm"
    || request.nextUrl.pathname === "/auth/reset-password";
  if (request.nextUrl.pathname.startsWith("/auth/") && user && !isConfirmationEndpoint) {
    return NextResponse.redirect(new URL("/app", request.url));
  }
  return response;
}

export const config = {
  matcher: ["/app/:path*", "/auth/:path*", "/api/:path*"],
};
