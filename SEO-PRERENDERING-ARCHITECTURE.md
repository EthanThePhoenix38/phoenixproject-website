# Architecture de Pre-rendering SEO

## Concept

Le pre-rendering SEO permet de servir du HTML pré-rendu aux bots (Google, Bing, etc.) tout en gardant une SPA dynamique pour les utilisateurs humains.

## Algorithme de Base

```
1. Requête arrive sur le serveur
2. Analyser le User-Agent
3. SI c'est un bot SEO:
   a. Vérifier le cache
   b. SI pas en cache:
      - Lancer headless browser (Puppeteer/Playwright)
      - Attendre le rendu complet du JavaScript
      - Extraire le HTML final
      - Mettre en cache
   c. Retourner le HTML pré-rendu
4. SINON (utilisateur humain):
   - Retourner le HTML normal (SPA)
```

## Détection des Bots

### User-Agents Courants
```javascript
const BOT_USER_AGENTS = [
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
  'telegrambot'
];

function isBot(userAgent) {
  const ua = userAgent.toLowerCase();
  return BOT_USER_AGENTS.some(bot => ua.includes(bot));
}
```

## Architecture Technique

### Option 1: Service Cloud (Recommandé pour vendre)
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Middleware Proxy   │ ◄── Détecte bot vs humain
│  (Node.js/Express)  │
└──────┬──────┬───────┘
       │      │
Bot ───┘      └─── Humain
       │              │
       ▼              ▼
┌──────────────┐  ┌──────────────┐
│  Puppeteer   │  │  HTML normal │
│  Renderer    │  │  (SPA)       │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│  Redis Cache │ ◄── TTL: 24h
└──────────────┘
```

### Option 2: GitHub Pages + Service Externe
```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  Cloudflare Workers  │ ◄── Edge computing
│  (ou Vercel Edge)    │
└──────┬───────────────┘
       │
       ├─── Bot ──────► Service de Pre-rendering
       │
       └─── Humain ───► GitHub Pages (HTML normal)
```

## Implémentation avec Node.js + Puppeteer

### 1. Serveur de Pre-rendering

```javascript
// server.js
const express = require('express');
const puppeteer = require('puppeteer');
const redis = require('redis');

const app = express();
const cache = redis.createClient();

const BOT_AGENTS = ['googlebot', 'bingbot', 'slurp', 'duckduckbot'];

function isBot(userAgent) {
  if (!userAgent) return false;
  const ua = userAgent.toLowerCase();
  return BOT_AGENTS.some(bot => ua.includes(bot));
}

async function prerenderPage(url) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // Attendre que le JS soit exécuté
  await page.goto(url, {
    waitUntil: ['networkidle0', 'domcontentloaded'],
    timeout: 30000
  });

  // Attendre que le contenu i18n soit chargé
  await page.waitForSelector('[data-i18n]', { timeout: 5000 });

  // Extraire le HTML final
  const html = await page.content();

  await browser.close();

  return html;
}

app.get('*', async (req, res) => {
  const userAgent = req.headers['user-agent'];
  const url = `https://yourdomain.com${req.path}`;

  if (!isBot(userAgent)) {
    // Humain : proxy vers GitHub Pages
    return res.redirect(url);
  }

  // Bot : pre-render
  const cacheKey = `prerender:${url}`;

  try {
    // Vérifier le cache
    const cached = await cache.get(cacheKey);
    if (cached) {
      console.log('Cache hit:', url);
      return res.send(cached);
    }

    // Pre-render
    console.log('Pre-rendering:', url);
    const html = await prerenderPage(url);

    // Mettre en cache (24h)
    await cache.setEx(cacheKey, 86400, html);

    res.send(html);
  } catch (error) {
    console.error('Pre-render error:', error);
    res.redirect(url); // Fallback
  }
});

app.listen(3000, () => {
  console.log('SEO Pre-rendering service running on port 3000');
});
```

### 2. Configuration Cloudflare Workers (Edge)

```javascript
// cloudflare-worker.js
const BOT_AGENTS = ['googlebot', 'bingbot', 'slurp', 'duckduckbot'];

async function handleRequest(request) {
  const url = new URL(request.url);
  const userAgent = request.headers.get('user-agent') || '';

  const isBot = BOT_AGENTS.some(bot =>
    userAgent.toLowerCase().includes(bot)
  );

  if (!isBot) {
    // Utilisateur humain : GitHub Pages normal
    return fetch(request);
  }

  // Bot : pre-rendering service
  const prerenderUrl = `https://your-prerender-service.com${url.pathname}`;
  return fetch(prerenderUrl);
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
```

## Optimisations

### 1. Cache Intelligent
```javascript
const CACHE_TIMES = {
  homepage: 3600,      // 1 heure
  services: 86400,     // 24 heures
  contact: 604800      // 7 jours
};

function getCacheTTL(path) {
  if (path === '/') return CACHE_TIMES.homepage;
  if (path.startsWith('/services')) return CACHE_TIMES.services;
  return CACHE_TIMES.contact;
}
```

### 2. Queue System
```javascript
// Pour éviter de surcharger avec trop de renders en parallèle
const Queue = require('bull');
const renderQueue = new Queue('prerender');

renderQueue.process(async (job) => {
  const { url } = job.data;
  return await prerenderPage(url);
});

// Ajouter à la queue
renderQueue.add({ url: 'https://example.com' });
```

### 3. Monitoring
```javascript
// Logs pour analytics
app.use((req, res, next) => {
  const isBot = isBotRequest(req);

  console.log({
    timestamp: new Date(),
    path: req.path,
    userAgent: req.headers['user-agent'],
    isBot: isBot,
    cached: req.cached || false
  });

  next();
});
```

## Service Commercial

### Pricing Model
```
Plan Basique: 29€/mois
- 10,000 pre-renders/mois
- Cache 24h
- Support email

Plan Pro: 99€/mois
- 100,000 pre-renders/mois
- Cache personnalisé
- Support prioritaire
- Analytics détaillés

Plan Enterprise: Sur devis
- Illimité
- SLA 99.9%
- Support 24/7
- White label
```

### API pour les Clients
```javascript
// Client API
POST /api/v1/register
{
  "domain": "example.com",
  "plan": "pro",
  "email": "contact@example.com"
}

// Webhook pour invalidation cache
POST /api/v1/invalidate
{
  "api_key": "xxx",
  "urls": ["/", "/about", "/services"]
}
```

## Infrastructure Recommandée

### Stack Technique
```
- Frontend: Cloudflare Workers (Edge)
- Pre-rendering: Node.js + Puppeteer (Docker)
- Cache: Redis Cloud
- Queue: Bull + Redis
- Monitoring: Datadog ou Sentry
- Hosting: AWS ECS ou Google Cloud Run
```

### Coûts Estimés (pour 100k pre-renders/mois)
```
- Cloud Run (2 instances): ~$50/mois
- Redis Cloud: ~$30/mois
- Cloudflare Workers: ~$5/mois
- Total: ~$85/mois
```

**Marge**: 99€ (plan Pro) - 85€ (coûts) = **14€/client**

### Scalabilité
```
1-10 clients: 1 instance ($50/mois)
10-100 clients: 3-5 instances ($150-250/mois)
100+ clients: Auto-scaling + Load balancer
```

## Avantages Compétitifs

1. **Pre-rendering à la demande** (pas de stockage permanent)
2. **Cache intelligent** (économie de resources)
3. **Detection multi-bots** (Google, Bing, social media)
4. **Analytics inclus** (trafic bot vs humain)
5. **API simple** (intégration en 5 min)

## Next Steps

1. Créer un MVP avec Express + Puppeteer
2. Tester sur votre propre site
3. Déployer sur Cloud Run ou Heroku
4. Créer une landing page de vente
5. Automatiser la facturation (Stripe)

---

**Note**: Ce service est légal et éthique car il ne change pas le contenu, il optimise juste la livraison pour les bots SEO.
