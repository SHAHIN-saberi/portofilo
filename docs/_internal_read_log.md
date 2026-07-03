# Internal Read Log (Phase 0)

## Repository Audit & Full Read
- **Cloned location**: `/home/user/My-portofilo`
- **Total audited files**: 105 code files (Python, TypeScript, TSX, Markdown, Configuration)
- **Total LOC**: ~12,598 lines

### Root Documentation & Architecture Files
1. `README.md`: Defines project overview, stack (Next.js App Router, FastAPI, PostgreSQL + pgvector, swappable AI provider).
2. `spec.md` (910 LOC): Source of truth specification. Defines hybrid architecture, bilingual domains (EN/FA), strict scope filter, RAG flow (cosine similarity + BM25 hybrid), 1024-dim embedding lock (for DeepSeek), and locked constraints.
3. `agent_state.json`: Tracked up to Phase 1 Production Readiness (73% complete). 69 tests baseline passing.
4. `PROJECT_HANDOFF.md`: Comprehensive handoff documenting Package 1-4 implementations, database schemas, API routers, and existing gaps.
5. `NEXT_AGENT.md`: Strict operating instructions locking stack and architecture.
6. `SYSTEM_CONTRACTS.md`, `FRONTEND_CONTRACTS.md`, `SYSTEM_RUNTIME_FREEZE.md`: Behavior and runtime freeze documentation defining exact consumption rules and fallback policies (`identity.ts`).
7. `AUDIT_REPORT.md` (1,257 LOC): Thorough staff engineering audit detailing 6 P0 blockers and 14 P1 high priority issues.
8. `FIX_TRACKING.md`: Production readiness checklist tracking fixes applied (e.g. P0-1 fake embedding removal, P0-3 duplicate admin route cleanup in previous steps).

### Backend Analysis (`backend/`)
- **App Structure**: FastAPI app entrypoint `main.py`, routers (`public.py`, `admin.py`, `chatbot.py`), core configs (`config.py`, `security.py`, `limiter.py`).
- **Database Layer**: Models defined in `db/models.py` (translation tables, content domains, `knowledge_chunks` with `vector(1024)` and tsvectors for BM25). Three migrations in `alembic/versions/`: `0001_initial.py`, `0002_add_bm25_search_vector.py`, `0003_fix_education_translations.py`.
- **Services Layer**: `content.py` (public queries with language fallbacks), `admin_service.py` (full CRUD for all 9 domains), `rag.py` (complete RAG pipeline with query planner, hybrid retrieval, RRF fusion, scope gate, citation validation), `reindex.py` (chunking and DB ingestion).
- **AI Provider Layer**: `base.py` (`AIProvider` ABC), `deepseek.py` (DeepSeek implementation), `factory.py` (dynamic DI factory), `gemini.py` (initial draft using `google.genai` SDK with `gemini-2.5-flash` and `text-embedding-004`).

### Frontend Analysis (`frontend/`)
- **App Router Layout**: Next.js 14 App Router structure.
- **Admin Routing**: Notice in repo check that `frontend/app/(admin)/admin` still exists or let's verify if `admin` vs `adshs` duplication exists! Let's check `frontend/app/(admin)` contents.
- **Adapter Firewall**: Clean layer (`lib/adapters/*.ts`) mapping raw API envelopes to deterministic front-end UI types.
- **Service Layer**: Single source of truth for API calls (`services/*.ts`).
