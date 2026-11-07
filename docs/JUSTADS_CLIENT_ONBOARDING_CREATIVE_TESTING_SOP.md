# JustAds / ZENO OS — Client Onboarding & Creative Testing SOP
Version: 1.0 | 2026-11-07
Status: user-defined operating logic, for training and future product implementation. Documentation only; no automatic campaign actions.

## 1. Tracking first
- Connect Meta Pixel and validate domain, Events Manager, and website events.
- Verify ViewContent, AddToCart, InitiateCheckout, Purchase, values/currency, and test events.
- Check CAPI, event_id deduplication, and UTMs where applicable.
- Do not launch before tracking QA and account access checks.

## 2. Account / catalogue analysis
- Audit product categories, SKU/product pricing, best sellers, availability, margins and verified offers.
- Map category priorities and possible acquisition products.
- Record missing business facts instead of guessing.

## 3. Creative audit
- Review historical paid creatives and organic Facebook/Instagram posts.
- Classify by concept (UGC, Product Demo, Offer, Lifestyle, Problem/Solution, Comparison), then by angle, hook, format, body, CTA, and variation.
- Record creative-level spend, impressions, reach, frequency, CTR, CPC, CPM, ATC, purchases, CPA, ROAS where reliable.
- Compare like-for-like; avoid declaring winners on engagement alone.

## 4. Initial concept testing
- Working example: one creative testing campaign with three ad sets, each testing one distinct concept; each ad set has multiple ads varying hooks and executions.
- Example: Ad Set A UGC (3 hooks), Ad Set B Demo (3 hooks), Ad Set C Offer (3 hooks).
- Use ABO when controlled budget per concept is important and feasible; no universal claim that this is Meta's best structure.
- Control audience, placement, conversion event, offer, and budget conditions as much as practical.
- Watch fragmentation and learning volume; consolidate if budget or conversion signal is too low.

## 5. Winner isolation and iterative testing
- Identify candidate winning concept from business outcome and sufficiently meaningful evidence.
- Example: if UGC performs best, run dedicated UGC hook tests (separate campaign only if justified by spend and signal).
- Keep concept stable while testing hooks; create variants of winning hooks and retest.
- Move validated winners to a scaling setup only when KPI, tracking, sample size, stability and account constraints justify it.
- Continue testing new concepts alongside scaling.

## 6. Organic UGC due diligence
- Analyze Facebook page and Instagram posts for views, engagement, saves, shares, and comment quality.
- Read and classify comments: buying intent, price/product questions, genuine feedback, generic praise, model friends/personal network, irrelevant or suspicious activity.
- A UGC video with many comments from the model's friends is NOT automatically a winner.
- Organic performance generates testing hypotheses, not proof of paid purchase performance.

## 7. Decision gates
- Define primary KPI and unit economics before tests: Purchase CPA/ROAS for sales, qualified lead cost for leads.
- Verify event quality and budget sufficiency.
- Do not infer statistical confidence from a few clicks or reactions.
- Document hypotheses, observations, decisions and next creative variations.

## Future ZENO workflow
Tracking QA → Category & Pricing Audit → Paid + Organic Creative Audit → Concept Taxonomy → Three-Concept Testing Plan → Results Review → Winning Concept → Hook Variations → Winner Validation → Scaling & Repeat.

## UI implementation ideas (not yet implemented)
- Client onboarding checklist and tracking gate.
- Category/product matrix with price, margin, stock, offer.
- Creative library with concept, hook, format and paid/organic source tags.
- Three-concept ad-set structure generator with editable budgets.
- UGC comment-quality review checklist.
- Winner-to-hook-testing workflow and decision log.
