import test from "node:test";
import assert from "node:assert/strict";
import { isSameOriginRequest } from "../lib/same-origin-guard.mjs";

const sameOrigin = {
  method: "POST",
  requestOrigin: "https://app.example.com",
  siteUrl: "https://app.example.com",
};

test("safe methods do not require Origin metadata", () => {
  for (const method of ["GET", "HEAD", "OPTIONS"]) {
    assert.equal(isSameOriginRequest({ method, requestOrigin: sameOrigin.requestOrigin }), true);
  }
});

test("sensitive safe methods require explicit same-origin browser provenance when configured", () => {
  const required = {
    method: "GET",
    requestOrigin: "https://app.example.com",
    requireSameOriginSignalForSafeMethods: true,
  };

  assert.equal(isSameOriginRequest(required), false);
  assert.equal(isSameOriginRequest({ ...required, secFetchSite: "same-origin" }), true);
  assert.equal(isSameOriginRequest({ ...required, origin: "https://app.example.com" }), true);
  assert.equal(isSameOriginRequest({ ...required, secFetchSite: "cross-site" }), false);
});

test("blocks cross-site Fetch Metadata on safe verbs that can still cause upstream egress", () => {
  assert.equal(isSameOriginRequest({
    method: "GET",
    requestOrigin: "https://app.example.com",
    secFetchSite: "cross-site",
  }), false);
  assert.equal(isSameOriginRequest({
    method: "GET",
    requestOrigin: "https://app.example.com",
    secFetchSite: "same-site",
  }), false);
});

test("accepts the exact request origin and canonical default ports", () => {
  assert.equal(isSameOriginRequest({ ...sameOrigin, origin: "https://app.example.com" }), true);
  assert.equal(isSameOriginRequest({ ...sameOrigin, origin: "https://app.example.com:443" }), true);
});

test("accepts browser same-origin metadata when an adapter reports a different canonical origin", () => {
  assert.equal(isSameOriginRequest({
    ...sameOrigin,
    origin: "https://app.example.com",
    requestOrigin: "http://internal-proxy:3000",
    secFetchSite: "same-origin",
  }), true);
  assert.equal(isSameOriginRequest({
    ...sameOrigin,
    origin: "https://attacker.example",
    requestOrigin: "http://internal-proxy:3000",
    secFetchSite: "cross-site",
  }), false);
});

test("accepts an explicitly configured site origin for preview runtimes", () => {
  assert.equal(isSameOriginRequest({
    method: "POST",
    origin: "https://zavqera.example",
    secFetchSite: "cross-site",
    requestOrigin: "https://deploy-preview-3--zavqera.netlify.app",
    siteUrl: "https://zavqera.example/app",
  }), true);
});

test("rejects cross-origin hosts, schemes, and non-default ports", () => {
  for (const origin of [
    "https://evil.example",
    "http://app.example.com",
    "https://app.example.com:8443",
    "https://app.example.com.evil.example",
    "https://evilapp.example.com",
  ]) {
    assert.equal(isSameOriginRequest({ ...sameOrigin, origin }), false, origin);
  }
});

test("rejects opaque, non-web, malformed, path-bearing, and credential-bearing origins", () => {
  for (const origin of [
    "null",
    "ftp://app.example.com",
    "not a url",
    "https://app.example.com/path",
    "https://user@app.example.com",
    " https://app.example.com",
  ]) {
    assert.equal(isSameOriginRequest({ ...sameOrigin, origin }), false, origin);
  }
});

test("rejects malformed request origins instead of deriving trust from a host header", () => {
  assert.equal(isSameOriginRequest({
    method: "POST",
    origin: "https://attacker.example",
    requestOrigin: "not a url",
  }), false);
});

test("blocks unsafe requests without Origin or same-origin Fetch Metadata", () => {
  assert.equal(isSameOriginRequest({ ...sameOrigin, secFetchSite: "cross-site" }), false);
  assert.equal(isSameOriginRequest({ ...sameOrigin, secFetchSite: "same-site" }), false);
  assert.equal(isSameOriginRequest({ ...sameOrigin }), false);
  assert.equal(isSameOriginRequest({ ...sameOrigin, secFetchSite: "same-origin" }), true);
});

test("a preview request may use its own request origin", () => {
  assert.equal(isSameOriginRequest({
    method: "POST",
    origin: "https://deploy-preview-3--zavqera.netlify.app",
    requestOrigin: "https://deploy-preview-3--zavqera.netlify.app",
  }), true);
});
