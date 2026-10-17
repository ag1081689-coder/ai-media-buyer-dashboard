# JustAds AI Creative OS — implementation roadmap

## Existing application audit
- Python Streamlit dashboard, Meta Marketing API fetcher, pandas/plotly analytics.
- Current login compares passwords from `config.auth_access.USERS`; **not suitable for multi-user production**.
- Preserve the existing dashboard and fetcher until a replacement passes regression tests.
- Existing branding says ZENO OS; rebrand only after checking assets and user requirements.

## Architecture decision
Target: Next.js web frontend, FastAPI Python service reusing Meta analytics, PostgreSQL on Railway, OpenAI server-side, role-based authorization and tenant-scoped data. The existing Streamlit app is retained as a legacy analytics service during migration. Do not expose it publicly with its current login.

## Roles
owner, admin, strategist, creator, designer, media_buyer, client_viewer. Enforce permissions server-side and by organization/brand membership; never trust role fields supplied by the browser.

## Database entities
organizations, users, memberships, brands, brand_memberships, products, brand_documents, customer_insights, funnel_stages, angles, concepts, hooks, creatives, creative_versions, approval_events, production_tasks, ad_accounts, ad_creative_links, performance_snapshots, ai_generations, audit_events.

## Creative workflow
DRAFT -> STRATEGY_REVIEW -> APPROVED -> IN_PRODUCTION -> QA -> READY_TO_TEST -> LIVE -> VALIDATED / REVISE / ARCHIVED. Record actor and timestamp for every transition.

## AI workflow
Product + brand brief + verified customer insights -> structured concept JSON (funnel, angle, persona, claim sources, hook, script, CTA) -> human review -> production brief -> results import -> performance analysis -> proposed iterations. Never invent discounts, stock levels, reviews, or guarantees. Keep API keys server-side. Do not feed sensitive customer data without appropriate minimization and permission.

## Delivery milestones
1. Railway staging for legacy dashboard (private access only) and environment configuration.
2. PostgreSQL schema and migrations; secure login, tenant isolation and roles.
3. Next.js dashboard and brand/product CRUD.
4. Content generator with JSON schema, approval workflow and version history.
5. Meta account mapping and creative-level analytics.
6. n8n workflows, observability, tests and production deployment.

## Railway staging
Connect this repository to a Railway service, select the feature branch, and provide PORT automatically. For Meta data set META_ACCESS_TOKEN, META_AD_ACCOUNT_ID and optionally META_BUSINESS_ID in Railway Variables. Do not commit `.env` files or credentials. Note: Railway deploy configuration here launches the **legacy Streamlit dashboard**, not the future Next.js app. Restrict staging access until login is replaced.
