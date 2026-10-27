export function postgrestRpc(
  supabaseUrl: string,
  apiKey: string,
  name: string,
  body: Record<string, unknown>,
): Promise<unknown>;
