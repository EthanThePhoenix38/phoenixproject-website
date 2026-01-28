# Required Tokens

Store these in GitHub Secrets (Settings → Secrets and variables → Actions → New repository secret)

## Service Configuration

### 1. CLOUDFLARE_API_TOKEN
**Name for TrueKey:** `CF_API_TOKEN`
**Where to get:**
1. Login to Cloudflare Dashboard
2. My Profile → API Tokens
3. Create Token → Edit Cloudflare Workers
4. Permissions: Account.Cloudflare Workers Scripts (Edit)
5. Copy token immediately (shown once)

**Scope:** Deploy workers to Cloudflare

---

### 2. CLOUDFLARE_ACCOUNT_ID
**Name for TrueKey:** `CF_ACCOUNT_ID`
**Where to get:**
1. Cloudflare Dashboard
2. Select any site
3. Right sidebar → Account ID (copy)

**Scope:** Identify your Cloudflare account

---

### 3. SUPABASE_URL
**Name for TrueKey:** `SB_URL`
**Where to get:**
1. Supabase Dashboard → Project Settings
2. API → Project URL
3. Copy URL (format: https://xxx.supabase.co)

**Scope:** Database connection

---

### 4. SUPABASE_ANON_KEY
**Name for TrueKey:** `SB_KEY`
**Where to get:**
1. Supabase Dashboard → Project Settings
2. API → Project API keys
3. Copy `anon` `public` key

**Scope:** Database authentication

---

### 5. UPSTASH_REDIS_REST_URL
**Name for TrueKey:** `REDIS_URL`
**Where to get:**
1. Upstash Dashboard → Create Database
2. Select region → Create
3. REST API → UPSTASH_REDIS_REST_URL
4. Copy URL

**Scope:** Cache service

---

### 6. UPSTASH_REDIS_REST_TOKEN
**Name for TrueKey:** `REDIS_TOKEN`
**Where to get:**
1. Same Upstash Database
2. REST API → UPSTASH_REDIS_REST_TOKEN
3. Copy token

**Scope:** Cache authentication

---

### 7. RESEND_API_KEY
**Name for TrueKey:** `EMAIL_KEY`
**Where to get:**
1. Resend Dashboard → API Keys
2. Create API Key
3. Copy key (shown once)

**Scope:** Email alerts

---

## Setup Order

1. Create Cloudflare account (free)
2. Create Supabase project (free)
3. Create Upstash Redis database (free)
4. Create Resend account (free)
5. Generate all tokens
6. Store in GitHub Secrets
7. Push code → auto-deploy

## Verification

After deployment, test:
```bash
curl https://api-service-production.workers.dev/api/health
```

Expected: `{"status":"ok","timestamp":1234567890}`
