# Configuration des services

## Services requis (tous gratuits)

### Cloudflare Workers
- Site: https://cloudflare.com/
- Gratuit: 100,000 requêtes/jour
- Pas de carte bancaire requise

**Configuration:**
1. Créer un compte
2. Récupérer Account ID (dashboard)
3. Créer API Token (My Profile → API Tokens → Edit Cloudflare Workers)
4. Ajouter dans GitHub Secrets:
   - `CLOUDFLARE_API_TOKEN`
   - `CLOUDFLARE_ACCOUNT_ID`

### Supabase
- Site: https://supabase.com/
- Gratuit: 500MB base de données
- Pas de carte bancaire requise

**Configuration:**
1. Créer un compte
2. Créer un projet
3. Copier Project URL et anon key
4. Exécuter `database/schema.sql` dans SQL Editor
5. Ajouter dans GitHub Secrets:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`

### Upstash Redis
- Site: https://upstash.com/
- Gratuit: 10,000 commandes/jour
- Pas de carte bancaire requise

**Configuration:**
1. Créer un compte
2. Créer une database Redis (Regional)
3. Copier REST API URL et Token
4. Ajouter dans GitHub Secrets:
   - `UPSTASH_REDIS_REST_URL`
   - `UPSTASH_REDIS_REST_TOKEN`

## GitHub Secrets

**Où ajouter:**
1. Repo GitHub → Settings
2. Secrets and variables → Actions
3. New repository secret
4. Ajouter chaque secret avec son nom exact

**Liste complète:**
- CLOUDFLARE_API_TOKEN
- CLOUDFLARE_ACCOUNT_ID
- SUPABASE_URL
- SUPABASE_ANON_KEY
- UPSTASH_REDIS_REST_URL
- UPSTASH_REDIS_REST_TOKEN

Une fois ajoutés, le déploiement est automatique sur chaque push.
