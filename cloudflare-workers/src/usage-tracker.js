export class UsageTracker {
  constructor(supabase, env) {
    this.supabase = supabase;
    this.env = env;
    this.cache = new Map();
  }

  async trackRequest(apiKey, endpoint) {
    const today = new Date().toISOString().split('T')[0];
    const key = `${apiKey}:${today}`;

    try {
      // Try Redis cache first (if available)
      if (this.env.UPSTASH_REDIS_REST_URL) {
        await this.incrementRedis(key);
      }

      // Update database
      const { error } = await this.supabase
        .from('usage_stats')
        .upsert({
          api_key: apiKey,
          date: today,
          endpoint: endpoint,
          count: 1,
          updated_at: new Date().toISOString()
        }, {
          onConflict: 'api_key,date,endpoint',
          count: 'count + 1'
        });

      if (error) console.error('Usage tracking error:', error);
    } catch (err) {
      console.error('Usage tracking failed:', err);
    }
  }

  async getUsage(apiKey) {
    const today = new Date().toISOString().split('T')[0];
    const cacheKey = `usage:${apiKey}:${today}`;

    // Check memory cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 60000) { // 1 min cache
        return cached.data;
      }
    }

    try {
      // Try Redis cache
      if (this.env.UPSTASH_REDIS_REST_URL) {
        const redisCount = await this.getRedisCount(`${apiKey}:${today}`);
        if (redisCount !== null) {
          const usage = { dailyCount: redisCount, tier: 'free' };
          this.cache.set(cacheKey, { data: usage, timestamp: Date.now() });
          return usage;
        }
      }

      // Fallback to database
      const { data, error } = await this.supabase
        .from('usage_stats')
        .select('count')
        .eq('api_key', apiKey)
        .eq('date', today);

      if (error) throw error;

      const dailyCount = data.reduce((sum, row) => sum + (row.count || 0), 0);
      const usage = { dailyCount, tier: 'free' };

      this.cache.set(cacheKey, { data: usage, timestamp: Date.now() });
      return usage;

    } catch (err) {
      console.error('Get usage error:', err);
      return { dailyCount: 0, tier: 'free' };
    }
  }

  async incrementRedis(key) {
    try {
      const response = await fetch(`${this.env.UPSTASH_REDIS_REST_URL}/incr/${key}`, {
        headers: { 'Authorization': `Bearer ${this.env.UPSTASH_REDIS_REST_TOKEN}` }
      });
      const data = await response.json();

      // Set expiry to end of day
      const now = new Date();
      const endOfDay = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
      const ttl = Math.floor((endOfDay - now) / 1000);

      await fetch(`${this.env.UPSTASH_REDIS_REST_URL}/expire/${key}/${ttl}`, {
        headers: { 'Authorization': `Bearer ${this.env.UPSTASH_REDIS_REST_TOKEN}` }
      });

      return data.result;
    } catch (err) {
      console.error('Redis increment error:', err);
      return null;
    }
  }

  async getRedisCount(key) {
    try {
      const response = await fetch(`${this.env.UPSTASH_REDIS_REST_URL}/get/${key}`, {
        headers: { 'Authorization': `Bearer ${this.env.UPSTASH_REDIS_REST_TOKEN}` }
      });
      const data = await response.json();
      return data.result ? parseInt(data.result) : 0;
    } catch (err) {
      console.error('Redis get error:', err);
      return null;
    }
  }
}
