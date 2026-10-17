# ZENO OS 2026 — AI Media Buyer Operating System

## Product goal
Turn the existing Streamlit Meta analytics tool into an end-to-end, agency-grade operating system for Egyptian e-commerce and real-estate media buyers. Retain ZENO brand and existing analytics until replacement modules pass acceptance tests.

## Workflow
1. **Brand onboarding**: business model, product catalog, pricing, gross margin, AOV, fulfillment, COD return rate, goals, legal claims, brand voice, Meta category restrictions, access.
2. **Research**: first-party customer data, objections, reviews, competitors, audience hypotheses; label inferred findings vs verified sources.
3. **Measurement audit**: Pixel, CAPI, event mapping, deduplication, UTMs, attribution settings, lead quality, CRM/COD delivered orders, consent.
4. **Strategy**: targets (allowable CAC, MER, ROAS, contribution margin), budget, offer, customer journey, experiment backlog.
5. **Creative OS**: funnel/awareness stage, angle, hook, storyboard, UGC brief, script, copy, CTA, proof, policy preflight, human approvals.
6. **Campaign planning**: objective, conversion location, budget type, creative testing plan, placements, audience configuration, exclusions, Advantage+ eligibility based on current API/account capabilities; drafts only.
7. **Launch**: verify permissions, assets, policy risk, tracking, URLs, spend caps; require explicit human confirmation before any write operation.
8. **Insights**: Meta Insights plus Shopify/CRM where connected, trends, funnel leaks, spend pacing, quality signals, actionable diagnostics with confidence and evidence.
9. **Optimization**: hypotheses, prioritized actions, projected impact ranges, human-approved execution, rollback and audit logs.
10. **Learning loop**: connect each creative version to ad IDs, spend, outcomes and learning; avoid causal claims from observational data.

## Meta 2026 compatibility
- Maintain versioned Meta capability matrix, refreshed from official docs and live API validation; never hardcode one universal Advantage+ structure.
- Marketing API access tier naming changed in May 2026; permissions (ads_read, ads_management) and API tier are separate.
- Use supported campaign creation paths for the API version; legacy Advantage+ Shopping/App campaign creation deprecated in v25.0 / May 2026 rollout.
- Handle Meta API pagination, async insights jobs, rate limits, retries, partial responses and attribution windows.
- Policy preflight is advisory, not a guarantee of approval; no policy-evasion functionality.
- Special Ad Categories, financial/health-sensitive claims, housing and employment require category-specific compliance checks.
- Never upload customer PII or hashed identifiers without lawful basis, appropriate consent and platform terms.
- No fully autonomous spending changes or ad publication by default.

## Architecture
- Frontend: Next.js, responsive Arabic/English workspace.
- Backend: FastAPI Python (reuse and isolate existing Meta analytics).
- Storage: PostgreSQL (Railway) with organization/brand scoped row-level access enforced server-side.
- Workers: background sync queue for Meta Insights, research, AI generations, scheduled reporting.
- AI: server-side model calls with structured JSON schema, versioned prompts, cited evidence, budget caps, prompt-injection protections.
- Auth: secure identity provider or managed auth; RBAC roles owner/admin/strategist/media_buyer/creator/designer/client_viewer.
- Audit: immutable event log for approvals, ad changes, costs, policy flags, and access.

## Main entities
organizations, users, memberships, brands, products, offers, customer_insights, competitors, research_sources, measurement_checks, funnel_stages, strategies, creative_concepts, hooks, scripts, assets, creative_versions, approvals, experiments, ad_accounts, campaigns, adsets, ads, performance_snapshots, recommendations, action_requests, audit_events, ai_runs.

## First implementation milestone (MVP)
A. Organization/brand workspace + secure auth.
B. Brand onboarding form + AI-generated strategy brief (requires review).
C. Creative brief generator with 5 awareness stages and Meta policy checklist.
D. Meta account read-only analytics by selected brand; historical data persisted in PostgreSQL.
E. Performance recommendations grounded in fetched metrics.
F. Approval queue; no direct Meta writes until separately authorized.

## Acceptance tests
- No cross-brand or cross-user data leakage.
- Client viewer cannot sync/write or see other clients.
- Invalid/missing Meta credentials fail safely.
- Each AI claim about performance links to actual measured data or is explicitly a hypothesis.
- Unsupported API capability returns a safe explanatory message, not a guessed campaign payload.
- Every proposed spend change requires approval and creates an audit record.
- Sync of one account/window never destroys another account/window's snapshots.

## Current state
The existing codebase is Streamlit and does not yet implement this architecture. Railway production deployment and Meta API access must be verified separately. Continue changes on feature branch; do not merge without tests.
