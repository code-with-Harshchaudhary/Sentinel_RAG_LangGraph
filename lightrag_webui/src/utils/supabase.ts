import { createClient, SupabaseClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseKey = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY || '';

export const isSupabaseConfigured = Boolean(
  supabaseUrl &&
  supabaseKey &&
  !supabaseUrl.includes('unconfigured')
);

export const supabase: SupabaseClient = createClient(
  supabaseUrl || 'https://unconfigured.supabase.co',
  supabaseKey || 'unconfigured-publishable-key',
  {
    auth: {
      persistSession: typeof window !== 'undefined',
      autoRefreshToken: true,
      detectSessionInUrl: true
    }
  }
);

export interface SupabaseTestResult {
  ok: boolean;
  message: string;
  latencyMs?: number;
  error?: string;
}

/**
 * Tests connection to the configured Supabase instance.
 */
export async function testSupabaseConnection(): Promise<SupabaseTestResult> {
  if (!isSupabaseConfigured) {
    return {
      ok: false,
      message: 'Supabase is not configured. Please set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY.'
    };
  }

  const start = performance.now();
  try {
    const { error } = await supabase.auth.getSession();
    const latencyMs = Math.round(performance.now() - start);

    if (error) {
      return {
        ok: false,
        message: `Supabase responded with an error: ${error.message}`,
        error: error.message,
        latencyMs
      };
    }

    return {
      ok: true,
      message: 'Supabase connection verified successfully.',
      latencyMs
    };
  } catch (err: unknown) {
    const errorMsg = err instanceof Error ? err.message : String(err);
    return {
      ok: false,
      message: `Failed to connect to Supabase: ${errorMsg}`,
      error: errorMsg,
      latencyMs: Math.round(performance.now() - start)
    };
  }
}