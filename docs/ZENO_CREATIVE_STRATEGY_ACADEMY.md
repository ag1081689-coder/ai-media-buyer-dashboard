# ZENO Creative Strategy Academy & Builder — 2026

## Goal
Teach a media buyer to reason from customer evidence to **Angle → Concept → Hook → Body → Format → CTA**, then test, validate, scale and learn. Not a random caption generator. Works for e-commerce and real estate, with different conversion and compliance goals.

## Distinctions
- **Research / Voice of Customer**: evidence, pain, objections, desires, proof, awareness, buying context.
- **Funnel stage**: TOF/MOF/BOF; map to Unaware, Problem Aware, Solution Aware, Product Aware, Most Aware. Awareness and funnel stage are related but not identical.
- **Angle**: the persuasive argument or buying motivation (e.g. savings, proof, convenience, identity, quality, objection handling, comparison, urgency *only if real*).
- **Concept**: the specific creative idea/story mechanism (e.g. customer unboxing, side-by-side comparison, founder demo, objection Q&A, price breakdown).
- **Hook**: first-frame/first-sentence attention device; must match concept and promise.
- **Body**: problem/context → mechanism or solution → evidence/demo → objection handling → offer; can be reordered for format.
- **Format**: UGC, talking head, demo, static, carousel, testimonial with verified permissions, founder story.
- **CTA**: one next action aligned with funnel stage and destination.

## Campaign structure — recommendation engine, not hard-coded Meta policy
Default 2026 hypothesis for many e-commerce accounts:
1. **Main / Scale**: simplified consolidated delivery structure, broad/Advantage+ eligible where supported.
2. **Creative Testing**: controlled concept/angle experiments with budget and measurement plan.
3. Optional **Retargeting/Catalog** only where incrementality, account setup and data justify it.
4. Optional **Experiments/Promos** for bounded offers or Meta experiments.
This is a starting strategy, not universal. Account-specific objective, budget, conversion volume, geo, special ad category, Meta API capabilities and current guidance determine final structure. Avoid overfragmenting audiences. Creative differentiation is not synonymous with multiplying near-identical ads.

## Interactive teaching workflow
1. Brand and product selection; require truthful offer, margins and approved proof.
2. Persona / pain / objection / awareness stage; cite source or mark as hypothesis.
3. AI recommends 3–5 **distinct angles** with rationale, objections and evidence; user selects one.
4. Generate 3 distinct **concepts** for the selected angle (not merely different wording).
5. Generate 3 **hooks** per concept, with visual opening, spoken line, and claim/policy checks.
6. Build **body** using chosen hook, mechanism, demonstration, proof, objection handling, offer.
7. Select **format**, duration, shot list, editor instructions, CTA and landing-page match.
8. Policy preflight: sensitive personal attributes, misleading outcomes, restricted categories, unsupported claims, IP/trademarks, housing/employment/credit category if applicable. Human reviewer approves.
9. Generate immutable **Creative ID** and variant lineage: brand > angle > concept > hook > version.
10. Design a testing matrix: isolate hypotheses, predefine primary KPI, spend/volume thresholds and stopping criteria; don't auto-claim statistical significance.
11. Import Meta performance by ad ID: spend, impressions, reach, frequency, CTR, CPC, CPM, leads/purchases, qualified leads/COD delivered, CPA/ROAS where measurable, hook/hold rates only if relevant video metrics available.
12. Label Learning: winner, inconclusive, fatigue, revise. Recommend 3 next experiments and send validated creatives to Main / Scale after human approval.

## Teaching cards (per step)
Every recommendation must include:
- **What it means**
- **Why it fits this brand and stage**
- **Example**
- **Common mistake**
- **How to test**
- **What evidence would change the decision**

## Example: Egyptian e-commerce (hypothetical)
- Persona: hesitant first-time buyer.
- Stage: MOF / Product Aware.
- Angle: purchase confidence.
- Concept: first-order unboxing with real delivery process.
- Hook: “كنت متردد أطلب أونلاين، فخليني أوريك اللي وصل.”
- Body: actual unboxing, verified quality details, authentic returns policy, specific offer.
- Format: UGC vertical video.
- CTA: “شوف التفاصيل وسياسة الاستبدال واطلب.”
Do not invent testimonials, policies, scarcity, discounts or guarantees.

## Testing design
- Differentiate **angle tests** (different persuasion hypothesis), **concept tests** (different narrative execution of same angle), and **hook tests** (opening change holding body/offer as constant as feasible).
- A matrix such as 3 hooks × 3 offers × 3 CTAs yields 27 variants, but is a planning illustration, **not** a recommended initial launch size for every budget.
- Track hook rate / hold rate only when available with consistent definitions; tie optimization to business outcomes.
- Document attribution windows, lag, sample size and confounding before making winner claims.
- Do not treat one-day ROAS snapshots as causal proof; compare 3D/7D/30D trends and downstream quality.

## Data schema for the builder
creative_brief: id, org_id, brand_id, product_id, audience_id, awareness_stage, funnel_stage, research_refs[], customer_pain, objection, offer_id, angle_id, angle_rationale, concept_id, concept_description, hook_id, hook_visual, hook_spoken, body_beats[], format, duration, shot_list[], on_screen_copy[], cta, landing_page_url, proof_refs[], policy_flags[], approval_status, test_hypothesis, primary_kpi, success_threshold, experiment_id, creative_version, meta_ad_id, performance_snapshot_ids[], learning_status, created_by, reviewed_by.

## MVP acceptance criteria
- User cannot jump to hook generation without choosing or confirming an angle and concept.
- Changing angle invalidates dependent concept/hook/body drafts, with user warning.
- Each stage has teach/explain, AI suggestions, editable user choice, approval.
- All performance recommendations use real linked data or are clearly hypothetical.
- No publish/spend changes without role authorization and explicit approval.
- Account/brand isolation is enforced in the backend, not only UI filters.
