import { createClient } from '@supabase/supabase-js';
import { MCPRouter } from './mcp-router.js';
import { UsageTracker } from './usage-tracker.js';
import { AlertService } from './alert-service.js';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    };

    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // Initialize services
      const supabase = createClient(env.SUPABASE_URL, env.SUPABASE_ANON_KEY);
      const usageTracker = new UsageTracker(supabase, env);
      const alertService = new AlertService(env);
      const mcpRouter = new MCPRouter(env);

      // Track request
      const apiKey = request.headers.get('X-API-Key') || 'anonymous';
      await usageTracker.trackRequest(apiKey, url.pathname);

      // Check usage limits
      const usage = await usageTracker.getUsage(apiKey);
      const limits = {
        free: 100,
        pro: 1000,
        business: Infinity
      };

      const userTier = usage.tier || 'free';
      const dailyLimit = limits[userTier];

      if (usage.dailyCount >= dailyLimit) {
        await alertService.sendLimitAlert(apiKey, usage);
        return new Response(JSON.stringify({
          error: 'Daily limit exceeded',
          usage: usage.dailyCount,
          limit: dailyLimit,
          tier: userTier
        }), {
          status: 429,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Route to appropriate handler
      if (url.pathname.startsWith('/api/mcp')) {
        return await mcpRouter.route(request, env);
      }

      if (url.pathname === '/api/catalog') {
        return await handleCatalog(request, env, supabase);
      }

      if (url.pathname === '/api/usage') {
        return new Response(JSON.stringify(usage), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      if (url.pathname === '/api/health') {
        return new Response(JSON.stringify({ status: 'ok', timestamp: Date.now() }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      return new Response(JSON.stringify({ error: 'Not found' }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }
};

async function handleCatalog(request, env, supabase) {
  const { data, error } = await supabase
    .from('api_catalog')
    .select('*')
    .order('category', { ascending: true });

  if (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify(data), {
    headers: { 'Content-Type': 'application/json' }
  });
}
