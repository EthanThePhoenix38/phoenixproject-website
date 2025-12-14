# Guide complet - Génération des secrets

## 📍 Où ajouter les secrets dans GitHub?

1. Aller sur votre repo: https://github.com/EthanThePhoenix38/phoenixproject-website
2. Cliquer sur **Settings** (en haut)
3. Dans le menu gauche: **Secrets and variables** → **Actions**
4. Cliquer **New repository secret**
5. Entrer le nom exact + la valeur
6. Cliquer **Add secret**

**IMPORTANT:** Vous n'avez PAS besoin de me donner les secrets! Vous les ajoutez directement dans GitHub.

---

## 1️⃣ CLOUDFLARE_API_TOKEN

### Où le trouver:
1. Aller sur https://dash.cloudflare.com/
2. Se connecter (créer un compte gratuit si besoin)
3. Cliquer sur votre profil (coin haut droit) → **My Profile**
4. Menu gauche: **API Tokens**
5. Cliquer **Create Token**
6. Sélectionner le template **"Edit Cloudflare Workers"**
7. Cliquer **Continue to summary** → **Create Token**
8. **COPIER le token immédiatement** (montré une seule fois!)

### Dans GitHub Secrets:
- **Nom:** `CLOUDFLARE_API_TOKEN`
- **Valeur:** Le token copié (commence par "...")

---

## 2️⃣ CLOUDFLARE_ACCOUNT_ID

### Où le trouver:
1. Dashboard Cloudflare: https://dash.cloudflare.com/
2. Cliquer sur **Workers & Pages** (menu gauche)
3. Sidebar droite → Section **Account details**
4. **Account ID** est affiché → Cliquer pour copier

### Dans GitHub Secrets:
- **Nom:** `CLOUDFLARE_ACCOUNT_ID`
- **Valeur:** L'ID copié (32 caractères)

---

## 3️⃣ SUPABASE_URL

### Où le trouver:
1. Aller sur https://supabase.com/
2. Se connecter (créer un compte gratuit si besoin)
3. Cliquer **New Project** (si premier projet)
   - Organization: Choisir ou créer
   - Name: `phoenix-api`
   - Database Password: **Générer un mot de passe fort et le sauvegarder!**
   - Region: Choisir le plus proche
   - Plan: **Free**
   - Cliquer **Create new project** (prend 1-2 minutes)
4. Une fois créé, aller dans **Project Settings** (icône engrenage)
5. Menu gauche: **API**
6. Section **Project URL** → Copier l'URL

### Dans GitHub Secrets:
- **Nom:** `SUPABASE_URL`
- **Valeur:** L'URL copiée (format: `https://xxxxx.supabase.co`)

---

## 4️⃣ SUPABASE_ANON_KEY

### Où le trouver:
1. Même page que ci-dessus (Project Settings → API)
2. Section **Project API keys**
3. Trouver la clé `anon` `public`
4. Cliquer sur l'icône 👁️ pour afficher
5. Cliquer sur l'icône 📋 pour copier

### Dans GitHub Secrets:
- **Nom:** `SUPABASE_ANON_KEY`
- **Valeur:** La clé copiée (longue chaîne)

### Important - Exécuter le SQL:
1. Dans Supabase, aller à **SQL Editor**
2. Cliquer **New query**
3. Copier tout le contenu de `cloudflare-workers/database/schema.sql`
4. Coller dans l'éditeur
5. Cliquer **Run** (en bas à droite)
6. Vérifier qu'il n'y a pas d'erreurs

---

## 5️⃣ UPSTASH_REDIS_REST_URL

### Où le trouver:
1. Aller sur https://upstash.com/
2. Se connecter (créer un compte gratuit si besoin)
3. Cliquer **Create Database**
   - Name: `phoenix-cache`
   - Type: **Regional** (gratuit)
   - Region: Choisir le plus proche
   - Cliquer **Create**
4. Cliquer sur la database créée
5. Section **REST API**
6. Copier **UPSTASH_REDIS_REST_URL**

### Dans GitHub Secrets:
- **Nom:** `UPSTASH_REDIS_REST_URL`
- **Valeur:** L'URL copiée (format: `https://xxx.upstash.io`)

---

## 6️⃣ UPSTASH_REDIS_REST_TOKEN

### Où le trouver:
1. Même page que ci-dessus (Database → REST API)
2. Copier **UPSTASH_REDIS_REST_TOKEN**

### Dans GitHub Secrets:
- **Nom:** `UPSTASH_REDIS_REST_TOKEN`
- **Valeur:** Le token copié

---

## ✅ Vérification finale

Une fois TOUS les secrets ajoutés dans GitHub:

1. Aller dans **Actions** (onglet en haut du repo)
2. Si vous voyez "Secrets not configured" → Un secret manque
3. Si vous voyez "All secrets configured" → C'est bon! ✅
4. Faire un push sur la branche → Déploiement automatique!

---

## 🎯 Récapitulatif des 6 secrets:

| Secret | Service | Où le trouver |
|--------|---------|---------------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare | Profile → API Tokens → Create |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare | Workers & Pages → Account ID |
| `SUPABASE_URL` | Supabase | Project Settings → API |
| `SUPABASE_ANON_KEY` | Supabase | Project Settings → API → anon key |
| `UPSTASH_REDIS_REST_URL` | Upstash | Database → REST API |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash | Database → REST API |

---

## ❓ Questions fréquentes:

**Q: Dois-je donner les secrets à Claude?**
→ NON! Vous les ajoutez directement dans GitHub Secrets. Claude n'a pas accès.

**Q: C'est vraiment gratuit?**
→ OUI! Tous les services ont un free tier généreux sans carte bancaire.

**Q: Que faire si un secret est incorrect?**
→ GitHub Secrets → Trouver le secret → Update → Coller la nouvelle valeur.

**Q: Le déploiement est automatique?**
→ OUI! Dès que les 6 secrets sont ajoutés, chaque push déclenche le déploiement.
