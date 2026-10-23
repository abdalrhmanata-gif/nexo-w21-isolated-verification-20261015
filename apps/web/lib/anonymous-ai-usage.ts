import { supabaseUrl } from "./supabase/config";
import { postgrestRpc } from "./postgrest-rpc.mjs";

function getServerDbConfig() {
  const url = supabaseUrl;
  const key = process.env.ZAVQERA_SERVER_DB_KEY;
  if (!url || !key) throw new Error("ANONYMOUS_AI_GUARD_UNAVAILABLE");
  return { url, key };
}

async function callRpc<T>(name: string, body: Record<string, unknown>) {
  const { url, key } = getServerDbConfig();
  return await postgrestRpc(url, key, name, body) as T;
}

export async function reserveAnonymousAiGeneration(
  visitorHash: string,
  ipHash: string,
  requestId: string,
) {
  const data = await callRpc<Array<{
    allowed: boolean;
    reservation_id: string | null;
    remaining: number;
    reason: string | null;
  }>>("reserve_anonymous_ai_generation", {
    p_visitor_hash: visitorHash,
    p_ip_hash: ipHash,
    p_request_id: requestId,
  });
  if (!data?.[0]) throw new Error("ANONYMOUS_AI_GUARD_UNAVAILABLE");
  return data[0];
}

export async function consumeAnonymousAiGeneration(reservationId: string) {
  const data = await callRpc<boolean>("consume_anonymous_ai_generation", {
    p_reservation_id: reservationId,
  });
  if (data !== true) throw new Error("ANONYMOUS_AI_GUARD_UNAVAILABLE");
}

export async function releaseAnonymousAiGeneration(reservationId: string) {
  await callRpc<boolean>("release_anonymous_ai_generation", {
    p_reservation_id: reservationId,
  });
}
