/** Call a server-only RPC while selecting the private PostgREST schema. */
export async function postgrestRpc(supabaseUrl, apiKey, name, body, fetchImpl = fetch) {
  if (!supabaseUrl || !apiKey || !/^[a-z][a-z0-9_]*$/.test(name)) {
    throw new Error("ANONYMOUS_AI_GUARD_UNAVAILABLE");
  }

  const response = await fetchImpl(`${supabaseUrl}/rest/v1/rpc/${name}`, {
    method: "POST",
    headers: {
      apikey: apiKey,
      "Content-Type": "application/json",
      "Content-Profile": "private",
    },
    body: JSON.stringify(body),
    cache: "no-store",
    redirect: "error",
  });
  if (!response.ok) throw new Error("ANONYMOUS_AI_GUARD_UNAVAILABLE");
  return await response.json();
}
