import test from "node:test";
import assert from "node:assert/strict";
import { postgrestRpc } from "../lib/postgrest-rpc.mjs";

test("server RPC uses the public API without exposing a bearer credential", async () => {
  let received;
  const result = await postgrestRpc(
    "https://database.example",
    "server-only-test-key",
    "reserve_anonymous_ai_generation",
    { p_request_id: "test-request" },
    async (url, options) => {
      received = { url: String(url), options };
      return Response.json([{ allowed: true }]);
    },
  );

  assert.equal(received.url, "https://database.example/rest/v1/rpc/reserve_anonymous_ai_generation");
  assert.equal(received.options.method, "POST");
  assert.equal(received.options.headers.apikey, "server-only-test-key");
  assert.equal(received.options.headers["Content-Profile"], undefined);
  assert.equal(received.options.headers.Authorization, undefined);
  assert.equal(received.options.cache, "no-store");
  assert.deepEqual(JSON.parse(received.options.body), { p_request_id: "test-request" });
  assert.deepEqual(result, [{ allowed: true }]);
});

test("RPC configuration, function names, and HTTP failures fail closed", async () => {
  let calls = 0;
  const unusedFetch = async () => {
    calls += 1;
    return Response.json({ secret: "must not be reflected" }, { status: 403 });
  };

  for (const args of [
    ["", "key", "safe_rpc"],
    ["https://database.example", "", "safe_rpc"],
    ["https://database.example", "key", "bad/name"],
  ]) {
    await assert.rejects(
      postgrestRpc(...args, {}, unusedFetch),
      { message: "ANONYMOUS_AI_GUARD_UNAVAILABLE" },
    );
  }
  assert.equal(calls, 0);

  await assert.rejects(
    postgrestRpc("https://database.example", "key", "safe_rpc", {}, unusedFetch),
    { message: "ANONYMOUS_AI_GUARD_UNAVAILABLE" },
  );
  assert.equal(calls, 1);
});
