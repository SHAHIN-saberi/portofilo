# Deployment Guide — Universal Architecture (Northflank, Koyeb, Render & VPS)

## Overview

This project is architected around standard, long-lived web services and containers:
- **Frontend:** Next.js 14 App Router
- **Backend:** FastAPI with continuous `uvicorn` server (eliminating 10-second serverless execution limits)
- **Database:** PostgreSQL with `pgvector` extension (768-dim vectors for Google Gemini)
- **AI Provider:** Google Gemini API (`gemini-2.5-flash` + `text-embedding-004`)

---

## Option 1: Northflank Cloud + Neon Postgres (Recommended Developer Sandbox)

**Northflank (`app.northflank.com`)** provides a powerful Developer Sandbox where you can run Dockerfiles cleanly directly from GitHub.

### Step 1: Create Free Postgres + pgvector Database (Neon or Supabase)

1. Sign up at [Neon.tech](https://neon.tech) or [Supabase.com](https://supabase.com) using GitHub.
2. Create a new free database project.
3. If using Supabase, run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor.
4. Copy the PostgreSQL connection string (`postgresql+asyncpg://user:pass@host/db`).

### Step 2: Deploy Backend on Northflank

1. Sign into [Northflank](https://app.northflank.com).
2. Click **Create Service** → **Combined / Deployment Service**.
3. Connect your GitHub repository (`SHAHIN-saberi/portofilo`).
4. In **Build Settings**:
   - Build Type: **Dockerfile**
   - Dockerfile path: `backend/Dockerfile`
   - Build context: `backend`
5. Under **Ports & Networking**:
   - Port: `8000` | Protocol: `HTTP` | Public: **Checked (Yes)** (Northflank will generate a public domain for your backend).
6. Under **Environment Variables**, add:
   - `DATABASE_URL`: Your Neon/Supabase connection string.
   - `AI_PROVIDER`: `gemini`
   - `GEMINI_API_KEY`: Your free Gemini API key from [aistudio.google.com](https://aistudio.google.com).
   - `AUTH_SECRET`: A 64-character secure string.
   - `ADMIN_EMAIL`: Your admin login email.
   - `ADMIN_PASSWORD_HASH`: Hashed password from `python3 scripts/gen_password_hash.py <password>`.
7. Click **Create Service**. Northflank will build your Docker container, run migrations, and launch FastAPI!

### Step 3: Deploy Frontend on Vercel or Netlify

1. In Vercel or Netlify, import the same repository (`SHAHIN-saberi/portofilo`).
2. Set **Root Directory** strictly to `frontend`.
3. Under Environment Variables, add:
   - `NEXT_PUBLIC_API_URL`: Your Northflank backend URL (e.g. `https://portfolio-backend--project.nf.app/api/v1`).
4. Click **Deploy**.

---

## Option 2: Koyeb Cloud + Neon Postgres

**Koyeb.com** runs Docker containers continuously on their Free Eco Tier without requiring a credit card when signing up via GitHub.

### Step 1: Create Free Postgres + pgvector Database (Neon or Supabase)

1. Sign up at [Neon.tech](https://neon.tech) or [Supabase.com](https://supabase.com) using GitHub (No credit card required).
2. Create a new free database project.
3. If using Supabase, run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor.
4. Copy the PostgreSQL connection string (`postgresql+asyncpg://user:pass@host/db`).

### Step 2: Deploy Backend on Koyeb

1. Sign into [Koyeb.com](https://www.koyeb.com) via GitHub.
2. Click **Create Web Service** → **GitHub** and select your repository (`SHAHIN-saberi/portofilo`).
3. In **Builder**: Choose **Dockerfile** and set **Dockerfile path** to `backend/Dockerfile`.
4. In **Ports**: Set port to `8000` and path to `/`.
5. Under **Environment Variables**, add:
   - `DATABASE_URL`: Your Neon/Supabase connection string.
   - `AI_PROVIDER`: `gemini`
   - `GEMINI_API_KEY`: Your free Gemini API key from [aistudio.google.com](https://aistudio.google.com).
   - `AUTH_SECRET`: A 64-character secure string.
   - `ADMIN_EMAIL`: Your admin login email.
   - `ADMIN_PASSWORD_HASH`: Hashed password from `python3 scripts/gen_password_hash.py <password>`.
6. Click **Deploy**. Koyeb will automatically build `backend/Dockerfile`, execute Alembic migrations, and launch FastAPI!

### Step 3: Deploy Frontend on Vercel or Netlify

1. In Vercel or Netlify, import the same repository (`SHAHIN-saberi/portofilo`).
2. Set **Root Directory** strictly to `frontend`.
3. Under Environment Variables, add:
   - `NEXT_PUBLIC_API_URL`: Your Koyeb backend URL (e.g. `https://your-backend.koyeb.app/api/v1`).
4. Click **Deploy**.

---

## Option 2: Render Cloud + Neon Postgres

Unlike serverless platforms with strict 10-second timeouts, **Render.com** runs your FastAPI application as a long-lived ASGI process (`uvicorn`), making it another great free platform for multi-stage RAG pipelines.

### Step 1: Create Free Postgres + pgvector Database (Neon or Supabase)

1. Sign up at [Neon.tech](https://neon.tech) or [Supabase.com](https://supabase.com).
2. Create a new free database project.
3. If using Supabase, run `CREATE EXTENSION IF NOT EXISTS vector;` in SQL Editor.
4. Copy the PostgreSQL connection string (`postgresql+asyncpg://user:pass@host/db`).

### Step 2: Deploy Backend & Frontend via Render Blueprint

1. Sign up / Log into [Render.com](https://render.com).
2. Click **New** → **Blueprint** and connect your GitHub repository (`SHAHIN-saberi/portofilo`).
3. Render will detect `render.yaml` and configure both `portfolio-backend` and `portfolio-frontend` web services automatically.
4. In the Render environment variable prompt, enter:
   - `DATABASE_URL`: Your Neon/Supabase connection string.
   - `GEMINI_API_KEY`: Your free Gemini API key from [aistudio.google.com](https://aistudio.google.com).
   - `AUTH_SECRET`: A 64-character secure string (e.g. generated via `secrets.token_urlsafe(48)`).
   - `ADMIN_EMAIL`: Your admin login email.
   - `ADMIN_PASSWORD_HASH`: Hashed password from `python3 scripts/gen_password_hash.py <password>`.
   - `CORS_ORIGINS`: Your frontend URL once generated.
5. Click **Apply**.

---

## Option 2: Docker Compose on VPS (Locked Original Spec Architecture)

If deploying on a modest Linux VPS (2-4 vCPU, 4-8 GB RAM), Docker Compose is the single source of truth for self-hosted production orchestration.

### Step 1: Configure Environment

```bash
cp .env.example .env
# Edit .env with your secrets and Gemini API key
```

### Step 2: Launch Stack

```bash
docker compose up -d --build
```

This launches:
- `postgres` (with `pgvector:pg16`, port 5432 internal)
- `backend` (FastAPI with Alembic auto-migrations, port 8000 internal)
- `frontend` (Next.js standalone runner, port 3000 internal)
- `nginx` (Reverse proxy on port 80 routing `/api` to backend and static/pages to frontend)

---

## Post-Deployment Step: Reindex RAG Knowledge Base (Mandatory)

Because the vector dimension is configured to **768** for Google Gemini (`text-embedding-004`), you must build the initial vector index after deploying:

1. Visit your admin login page (`/adshs/login`).
2. Log in with your `ADMIN_EMAIL` and password.
3. Go to **AI Knowledge / Dashboard** and click **Reindex Chatbot Knowledge**.
4. The backend will parse all your profile content, batch-embed via Gemini, and populate `knowledge_chunks`.

---

## Verification & Monitoring

- **Public API Health:** `GET /api/v1/health`
- **Chatbot Test:** Send a test message via `/chat` interface.
- **Logs:** Check container logs (`docker compose logs -f backend`) or Render service logs dashboard.
