"""Campaign Structure Architect: educational planning, no Meta API writes."""
import json
import streamlit as st

STRUCTURES = {
 "Testing": [
  ("ABO Creative Testing", "Ad set budget controls to compare distinct angles/concepts with comparable conditions.", "New creatives; need deliberate budget allocation.", "Avoid overfragmentation and treating ad sets as a perfect randomized experiment."),
  ("CBO / Advantage Campaign Budget Testing", "Campaign-level budget optimization lets delivery favor promising ad sets.", "Enough conversion signal; testing under algorithmic budget allocation.", "Unequal spend makes clean head-to-head creative comparisons difficult."),
  ("Angle Testing", "Different customer motivations: pain, value, trust, convenience, objections.", "Discover the persuasion hypothesis.", "Do not confuse a new hook with a new angle."),
  ("Concept Testing", "Different story executions of one angle: demo, UGC, comparison, FAQ.", "Find the strongest storytelling mechanism.", "Keep angle and offer as consistent as possible."),
  ("Hook Testing", "Vary first seconds or opening copy while keeping concept/body stable where possible.", "Improve attention after a concept shows promise.", "Hook metrics alone are not business outcomes."),
  ("Offer Testing", "Test verified price, bundle or value proposition changes.", "When offer is a plausible conversion constraint.", "Account for margin, returns and landing page consistency."),
  ("Audience / Geo Testing", "Compare meaningful geographic or audience hypotheses where supported.", "Distinct markets or meaningful audience hypotheses.", "Avoid unnecessary audience splits and special-category violations."),
 ],
 "Scaling": [
  ("Broad Scaling", "Consolidated broad delivery with validated creatives; use current Meta Advantage+ options where eligible.", "Stable purchase or qualified lead signal.", "Creative and measurement quality matter more than excessive targeting."),
  ("SKAG / Winner Interest Scaling", "Legacy agency shorthand for isolated proven interest/targeting hypotheses; not a Meta-native campaign type.", "Only when supported targeting demonstrably adds incremental value.", "Meta automation and special ad categories can limit detailed targeting; do not assume this beats broad."),
  ("CBO / Advantage Campaign Budget Scaling", "Campaign-level budget allocation across eligible ad sets.", "Multiple meaningful ad sets with stable signal.", "Budget shifts may concentrate delivery; check account-level incrementality."),
  ("Advantage+ Eligible Setup", "Use the account/objective/API-version supported automated sales or leads setup.", "When account capabilities and policy allow.", "Never assume a legacy ASC switch or universal API payload."),
  ("Vertical Scaling", "Increase budget of an existing winner gradually, monitoring efficiency and conversion lag.", "Stable performance with headroom.", "No universal 20%/48-hour rule; thresholds depend on volatility and volume."),
  ("Horizontal Scaling", "Expand via distinct proven creatives, geographies, offers or justified audience groups.", "Winner saturation or genuine new demand.", "Duplicating identical ad sets can fragment learning."),
  ("Creative Scaling", "Extend a proven angle into new concepts, hooks, creators and formats.", "A creative hypothesis shows repeatable results.", "Track creative lineage and avoid near-duplicate spam."),
 ],
 "Supporting": [
  ("Retargeting", "Relevant warm-audience messaging and exclusions subject to privacy and account setup.", "Enough warm audience size and incremental value.", "Do not assume retargeting is necessary for every account."),
  ("Catalog / Dynamic Product Ads", "Product-feed-driven ads with accurate inventory, pricing and event match.", "Catalog and tracking are healthy.", "Broken feeds or mismatched products create poor experiences."),
  ("Promotion / Seasonal", "Time-bound verified offers with budget caps and landing page consistency.", "Genuine promotions and clear stock/terms.", "Never invent scarcity or discounts."),
  ("Real Estate Lead Quality", "Optimize toward qualified leads, appointments and downstream CRM outcomes.", "Property leads and sales cycles.", "Housing special-ad-category constraints and privacy apply."),
 ]
}
def render_campaign_architect():
 st.title("Campaign Structure Architect")
 st.caption("Learn campaign types, choose a test, and build a reviewable plan. These are strategic patterns, not Meta platform guarantees.")
 industry = st.selectbox("Business", ["E-commerce", "Real Estate", "Other"], key="arch_industry")
 budget = st.number_input("Monthly budget (EGP)", min_value=0.0, step=1000.0, key="arch_budget")
 volume = st.selectbox("Recent conversion signal", ["Unknown / New account", "Low", "Moderate", "High"], key="arch_volume")
 goal = st.selectbox("Primary goal", ["Purchases", "Qualified Leads", "Appointments", "Catalog Sales"], key="arch_goal")
 tab = st.selectbox("Structure family", list(STRUCTURES), key="arch_family")
 names = [x[0] for x in STRUCTURES[tab]]
 selected = st.selectbox("Choose a structure to learn", names, key="arch_structure")
 item = next(x for x in STRUCTURES[tab] if x[0] == selected)
 st.markdown(f"### {selected}")
 st.write("**What it does:** " + item[1])
 st.write("**When to use:** " + item[2])
 st.write("**Common mistake / risk:** " + item[3])
 st.info("2026 Meta compatibility: verify live account capabilities, campaign objective, API version, budget settings, category restrictions and measurement before implementation.")
 if volume == "Unknown / New account":
  st.warning("New account: prioritize tracking and a small number of distinct creative hypotheses before complex scaling.")
 elif volume == "Low":
  st.warning("Low signal: consolidate where feasible; many ad sets can dilute learning.")
 if industry == "Real Estate":
  st.warning("Real estate: assess applicable housing restrictions and downstream lead quality, not only cost per lead.")
 st.subheader("Build your campaign plan")
 hypothesis = st.text_area("Hypothesis / angle to validate", key="arch_hypothesis")
 creative_count = st.number_input("Planned distinct creatives", min_value=1, max_value=50, value=3, key="arch_creatives")
 success = st.text_input("Success metric and review window", value="Define target CPA/CPL, minimum signal, attribution lag and review period", key="arch_success")
 st.caption("Learning path: Research → Angle → Concept → Hook → Body → Creative Testing → Winner Validation → Scaling.")
 if st.button("Prepare structure brief", key="arch_prepare"):
  st.session_state["arch_plan"] = {
   "business":industry,"monthly_budget_egp":budget,"signal":volume,"goal":goal,
   "family":tab,"structure":selected,"description":item[1],"when_to_use":item[2],
   "risk":item[3],"hypothesis":hypothesis,"creative_count":creative_count,
   "success_criteria":success,"status":"DRAFT_REQUIRES_REVIEW",
   "meta_publication_authorized":False
  }
 if "arch_plan" in st.session_state:
  plan = st.session_state["arch_plan"]
  st.json(plan)
  st.download_button("Download campaign structure brief",json.dumps(plan,ensure_ascii=False,indent=2),file_name="zeno-campaign-structure.json",mime="application/json")
