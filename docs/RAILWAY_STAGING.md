# JustAds AI Creative OS — staging

Existing Streamlit Meta analytics app, optimized on this feature branch. **This is not yet the new multi-user Creative OS.**

## Railway
- Deploy branch `feature/justads-ai-creative-os` as a staging service. `railway.json` starts the Streamlit server on `$PORT`.
- Add `ADMIN_PASSWORD`, `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`, optionally `META_BUSINESS_ID`. Add `MEMMAR_DEGLA_PASSWORD` only if the client account needs access.
- Never publish `.env` or tokens. Strong unique passwords required; the legacy password system is temporary.
- `meta_ads_report.csv` is ephemeral on Railway unless persistent storage is configured; new deploys can clear it.
- This app's CSV is **shared per service**; isolate clients or postpone external access until tenant-scoped PostgreSQL storage is implemented.

## Current reductions
- Requests to Meta are limited to the selected report window, by default 7 days.
- Cached ad account lookup and cached report reads.
- Smaller navigation focused on overview, campaign, creative and recommendations.
- Login rejects missing password environment values.

## Safety
This staging app must not be exposed as a production multi-tenant platform. Do not connect customer logins until DB-scoped authorization, persistent storage, session management and audit logs are built and tested.
