# Service de Pre-rendering SEO

Service autonome de pre-rendering pour optimiser le SEO en servant du HTML pré-rendu aux bots.

## Installation

```bash
cd prerender-service
npm install
```

## Configuration

Créer un fichier `.env` :

```bash
cp .env.example .env
```

Modifier les valeurs :
- `PORT` : Port du serveur (défaut: 3000)
- `REDIS_URL` : URL de connexion Redis
- `TARGET_DOMAIN` : Votre site à pre-render
- `API_KEY` : Clé API pour l'invalidation du cache

## Lancement en développement

```bash
npm run dev
```

## Lancement en production

```bash
npm start
```

## Docker

### Build
```bash
npm run docker:build
```

### Run
```bash
docker run -d \
  -p 3000:3000 \
  -e REDIS_URL=redis://redis:6379 \
  -e TARGET_DOMAIN=https://votre-site.com \
  -e API_KEY=votre-cle-securisee \
  --name phoenix-prerender \
  phoenix-prerender
```

## Utilisation

### 1. Configuration DNS

Pointer votre domaine vers le serveur de pre-rendering :

```
A   seo.votredomaine.com   → IP_DU_SERVEUR
```

### 2. Configuration Cloudflare (Recommandé)

Créer un Worker qui redirige les bots :

```javascript
addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const BOT_AGENTS = ['googlebot', 'bingbot', 'slurp', 'duckduckbot'];

async function handleRequest(request) {
  const userAgent = request.headers.get('user-agent') || '';
  const isBot = BOT_AGENTS.some(bot =>
    userAgent.toLowerCase().includes(bot)
  );

  if (isBot) {
    // Rediriger vers le service de pre-rendering
    const url = new URL(request.url);
    const prerenderUrl = `https://seo.votredomaine.com${url.pathname}`;
    return fetch(prerenderUrl);
  }

  // Utilisateur normal
  return fetch(request);
}
```

### 3. Invalidation du cache

```bash
curl -X POST https://seo.votredomaine.com/invalidate \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "votre-cle-api",
    "urls": ["/", "/about", "/services"]
  }'
```

### 4. Statistiques

```bash
curl https://seo.votredomaine.com/stats
```

## Architecture

```
Client (Bot)
     ↓
Cloudflare Worker (détection)
     ↓
Service Pre-rendering (Node.js + Puppeteer)
     ↓
Redis Cache (24h TTL)
     ↓
Site cible (GitHub Pages)
```

## Monitoring

Health check :
```bash
curl https://seo.votredomaine.com/health
```

Réponse :
```json
{
  "status": "OK",
  "uptime": 123456,
  "redis": "connected"
}
```

## Déploiement

### Option 1: VPS (Digital Ocean, Linode)

```bash
# Installation Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installation Redis
docker run -d --name redis -p 6379:6379 redis:alpine

# Lancement du service
docker run -d \
  -p 3000:3000 \
  --link redis:redis \
  -e REDIS_URL=redis://redis:6379 \
  -e TARGET_DOMAIN=https://votre-site.com \
  --restart unless-stopped \
  phoenix-prerender
```

### Option 2: Google Cloud Run

```bash
# Build et push
gcloud builds submit --tag gcr.io/PROJECT_ID/phoenix-prerender

# Deploy
gcloud run deploy phoenix-prerender \
  --image gcr.io/PROJECT_ID/phoenix-prerender \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --set-env-vars REDIS_URL=$REDIS_URL,TARGET_DOMAIN=$TARGET_DOMAIN
```

## Coûts estimés

- VPS 2GB RAM : ~10€/mois (Linode, Digital Ocean)
- Redis Cloud : ~0€ (plan gratuit 30MB) ou ~30€/mois (250MB)
- **Total : ~10-40€/mois**

## Service Commercial

Vous pouvez vendre ce service :

**Plan Pro : 99€/mois**
- 100,000 pre-renders/mois
- Cache 24h
- Support prioritaire

**Marge : 99€ - 40€ = 59€/client**

## Support

Pour toute question : contact@thephoenixagency.com
