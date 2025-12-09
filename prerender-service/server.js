/**
 * Service de Pre-rendering SEO
 * Intercepte les requêtes des bots et sert du HTML pré-rendu
 */

const express = require('express');
const puppeteer = require('puppeteer');
const { createClient } = require('redis');

const app = express();
const PORT = process.env.PORT || 3000;

// Configuration Redis pour le cache
const redis = createClient({
  url: process.env.REDIS_URL || 'redis://localhost:6379'
});

redis.on('error', err => console.log('Redis Error:', err));
redis.connect();

// Liste des User-Agents de bots SEO
const BOT_AGENTS = [
  'googlebot',
  'bingbot',
  'slurp',          // Yahoo
  'duckduckbot',
  'baiduspider',
  'yandexbot',
  'facebot',        // Facebook
  'twitterbot',
  'linkedinbot',
  'whatsapp',
  'telegrambot',
  'slackbot',
  'discordbot',
  'google-structured-data-testing-tool'
];

/**
 * Détecte si la requête vient d'un bot
 */
function isBot(userAgent) {
  if (!userAgent) return false;
  const ua = userAgent.toLowerCase();
  return BOT_AGENTS.some(bot => ua.includes(bot));
}

/**
 * Pre-render une page avec Puppeteer
 */
async function prerenderPage(url) {
  console.log('[PRERENDER] Starting for:', url);

  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu'
    ]
  });

  try {
    const page = await browser.newPage();

    // Configuration de la page
    await page.setViewport({ width: 1920, height: 1080 });
    await page.setUserAgent('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)');

    // Naviguer vers la page
    await page.goto(url, {
      waitUntil: ['networkidle0', 'domcontentloaded'],
      timeout: 30000
    });

    // Attendre que le JavaScript soit exécuté (i18n, etc.)
    await page.waitForTimeout(2000);

    // Extraire le HTML final
    const html = await page.content();

    console.log('[PRERENDER] Success:', url, '- HTML size:', html.length);

    return html;
  } finally {
    await browser.close();
  }
}

/**
 * Obtenir le TTL du cache selon le type de page
 */
function getCacheTTL(path) {
  if (path === '/') return 3600;           // 1 heure
  if (path.includes('blog')) return 86400; // 24 heures
  return 43200;                            // 12 heures par défaut
}

/**
 * Middleware principal
 */
app.use(async (req, res, next) => {
  const userAgent = req.headers['user-agent'] || '';
  const targetUrl = process.env.TARGET_DOMAIN || 'https://ethanthePhoenix38.github.io/phoenixproject-website';
  const fullUrl = `${targetUrl}${req.path}`;

  // Log de la requête
  console.log('[REQUEST]', {
    path: req.path,
    isBot: isBot(userAgent),
    userAgent: userAgent.substring(0, 50)
  });

  // Si ce n'est pas un bot, rediriger vers le site original
  if (!isBot(userAgent)) {
    console.log('[HUMAN] Redirecting to:', fullUrl);
    return res.redirect(fullUrl);
  }

  // C'est un bot : pre-rendering
  const cacheKey = `prerender:${req.path}`;

  try {
    // Vérifier le cache
    const cached = await redis.get(cacheKey);
    if (cached) {
      console.log('[CACHE HIT]', req.path);
      res.setHeader('X-Prerender-Cache', 'HIT');
      return res.send(cached);
    }

    // Cache miss : pre-render
    console.log('[CACHE MISS]', req.path);
    const html = await prerenderPage(fullUrl);

    // Mettre en cache
    const ttl = getCacheTTL(req.path);
    await redis.setEx(cacheKey, ttl, html);

    res.setHeader('X-Prerender-Cache', 'MISS');
    res.send(html);

  } catch (error) {
    console.error('[ERROR]', error);

    // Fallback : rediriger vers le site original
    res.redirect(fullUrl);
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    uptime: process.uptime(),
    redis: redis.isOpen ? 'connected' : 'disconnected'
  });
});

// Statistiques
app.get('/stats', async (req, res) => {
  try {
    const keys = await redis.keys('prerender:*');
    res.json({
      cached_pages: keys.length,
      pages: keys.map(k => k.replace('prerender:', ''))
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Invalidation du cache (webhook)
app.post('/invalidate', express.json(), async (req, res) => {
  const { api_key, urls } = req.body;

  // Vérifier l'API key
  if (api_key !== process.env.API_KEY) {
    return res.status(401).json({ error: 'Invalid API key' });
  }

  try {
    if (urls && Array.isArray(urls)) {
      for (const url of urls) {
        await redis.del(`prerender:${url}`);
      }
      res.json({ success: true, invalidated: urls });
    } else {
      res.status(400).json({ error: 'urls array required' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════╗
║   SEO Pre-rendering Service Running      ║
║   Port: ${PORT}                              ║
║   Target: ${process.env.TARGET_DOMAIN || 'https://ethanthePhoenix38.github.io/phoenixproject-website'}
╚═══════════════════════════════════════════╝
  `);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing server...');
  await redis.quit();
  process.exit(0);
});
