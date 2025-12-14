# Guide de configuration des services

## Upstash Redis - C'est quoi et pourquoi?

**Upstash** est un service de cache Redis serverless **100% GRATUIT** (jusqu'à 10,000 commandes/jour).

### Pourquoi on l'utilise?
- **Cache rapide** pour éviter de surcharger la base de données
- **Compteur de requêtes** en temps réel pour le rate limiting
- **Gratuit** et sans carte de crédit nécessaire
- **Serverless** = pas de serveur à gérer

### Configuration (5 minutes):

1. **Créer un compte gratuit:**
   - Aller sur https://upstash.com/
   - Cliquer "Sign up" → Utiliser GitHub ou Email
   - **Aucune carte de crédit requise**

2. **Créer une database Redis:**
   - Dashboard → "Create Database"
   - Name: `phoenix-cache`
   - Type: **Regional** (gratuit)
   - Region: Choisir le plus proche (ex: Europe)
   - Cliquer "Create"

3. **Copier les tokens:**
   - Cliquer sur la database créée
   - Section "REST API"
   - Copier `UPSTASH_REDIS_REST_URL` → GitHub Secrets
   - Copier `UPSTASH_REDIS_REST_TOKEN` → GitHub Secrets

**Free tier inclut:**
- ✅ 10,000 commandes/jour
- ✅ 256MB de stockage
- ✅ TLS encryption
- ✅ Pas de carte de crédit

---

## Cloudflare Workers - Configuration

**Cloudflare Workers** permet de déployer du code serverless **100% GRATUIT** (100,000 requêtes/jour).

### Pourquoi on l'utilise?
- **100,000 requêtes/jour GRATUIT**
- **Zéro cold start** (instantané)
- **Global CDN** (50+ datacenters)
- **Pas de serveur à gérer**

### Configuration (10 minutes):

1. **Créer un compte gratuit:**
   - Aller sur https://cloudflare.com/
   - Cliquer "Sign up"
   - **Aucune carte de crédit requise pour le free tier**

2. **Récupérer Account ID:**
   - Dashboard Cloudflare
   - Cliquer sur n'importe quel domaine (ou "Workers & Pages")
   - Sidebar droite → **Account ID** (copier)
   - Stocker dans GitHub Secrets: `CLOUDFLARE_ACCOUNT_ID`

3. **Créer API Token:**
   - Dashboard → Cliquer sur votre profil (coin haut droite)
   - "My Profile" → "API Tokens"
   - "Create Token"
   - Template: **"Edit Cloudflare Workers"**
   - Permissions:
     - Account → Cloudflare Workers Scripts → Edit
   - Cliquer "Continue to summary" → "Create Token"
   - **Copier le token immédiatement** (montré une seule fois!)
   - Stocker dans GitHub Secrets: `CLOUDFLARE_API_TOKEN`

**Free tier inclut:**
- ✅ 100,000 requêtes/jour
- ✅ 10ms CPU par requête
- ✅ Unlimited domains
- ✅ SSL gratuit

---

## Supabase - Configuration

**Supabase** est une alternative open-source à Firebase avec PostgreSQL.

### Configuration (5 minutes):

1. **Créer un compte:**
   - https://supabase.com/
   - Sign up avec GitHub

2. **Créer un projet:**
   - "New Project"
   - Name: `phoenix-api`
   - Database Password: **Générer et sauvegarder!**
   - Region: Choisir le plus proche
   - Free plan → "Create new project"

3. **Copier les clés:**
   - Project Settings → API
   - Project URL → Copier vers GitHub Secrets: `SUPABASE_URL`
   - `anon` `public` key → Copier vers GitHub Secrets: `SUPABASE_ANON_KEY`

4. **Exécuter le schema SQL:**
   - SQL Editor → New query
   - Copier le contenu de `cloudflare-workers/database/schema.sql`
   - Run

**Free tier inclut:**
- ✅ 500MB database
- ✅ 2GB bandwidth/mois
- ✅ 50,000 requêtes/mois
- ✅ Authentification incluse

---

## Resend - Emails (Optionnel)

**Resend** permet d'envoyer des emails de notification.

### Configuration (3 minutes):

1. **Créer un compte:**
   - https://resend.com/
   - Sign up (gratuit)

2. **Créer API Key:**
   - Dashboard → API Keys
   - "Create API Key"
   - Name: `phoenix-alerts`
   - Permission: **Sending access**
   - Create → **Copier immédiatement**
   - Stocker dans GitHub Secrets: `RESEND_API_KEY`

**Free tier:**
- ✅ 100 emails/jour
- ✅ 3,000 emails/mois

---

## Résumé des coûts

| Service | Free Tier | Coût mensuel |
|---------|-----------|--------------|
| Upstash Redis | 10k req/jour | **0€** |
| Cloudflare Workers | 100k req/jour | **0€** |
| Supabase | 500MB DB | **0€** |
| Resend | 100 emails/jour | **0€** |
| **TOTAL** | - | **0€** |

**Aucune carte de crédit requise!**

---

## GitHub Secrets - Comment ajouter?

1. Aller sur votre repo GitHub
2. Settings → Secrets and variables → Actions
3. "New repository secret"
4. Ajouter chaque secret:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`
   - `RESEND_API_KEY`

5. Une fois ajoutés, pusher sur la branche → déploiement automatique!
