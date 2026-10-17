"""ZENO OS onboarding workspace: guide a media buyer from the first client brief.
Local session draft only; persistent multi-user storage comes with PostgreSQL.
"""
import json
import uuid
from datetime import datetime, timezone
import streamlit as st

STEPS = [
    ("Brand", "Understand the business, offer and economics"),
    ("Customer", "Define buyer pains, objections and evidence"),
    ("Measurement", "Audit the signals before spending"),
    ("Strategy", "Choose a measurable objective and experiment plan"),
    ("Creative", "Proceed to Angle → Concept → Hook → Body"),
    ("Launch", "Review policy, tracking and permissions"),
]
def render_media_buyer_journey():
    st.title("ZENO OS · Start From Zero")
    st.caption("A guided media-buying workflow. Your answers remain in this browser session until exported.")
    if "zeno_journey" not in st.session_state:
        st.session_state.zeno_journey = {}
    data = st.session_state.zeno_journey
    step = st.radio("Your workflow", range(len(STEPS)), format_func=lambda n: f"{n+1}. {STEPS[n][0]}", horizontal=True, key="zeno_journey_step")
    st.progress((step + 1) / len(STEPS))
    st.subheader(STEPS[step][1])
    if step == 0:
        data["brand"] = st.text_input("Brand / client", value=data.get("brand", ""), key="journey_brand")
        data["industry"] = st.selectbox("Industry", ["E-commerce", "Real Estate", "Lead Generation", "Other"], key="journey_industry")
        data["product"] = st.text_input("Hero product / project", value=data.get("product", ""), key="journey_product")
        data["price"] = st.number_input("Selling price (EGP, optional)", min_value=0.0, value=float(data.get("price", 0)), key="journey_price")
        data["margin"] = st.number_input("Contribution margin % before ads (optional)", min_value=0.0, max_value=100.0, value=float(data.get("margin", 0)), key="journey_margin")
        data["budget"] = st.number_input("Monthly media budget EGP", min_value=0.0, value=float(data.get("budget", 0)), key="journey_budget")
        st.info("Why: pricing, margin and fulfillment determine whether an apparently strong ROAS is profitable.")
        if data["price"] > 0 and data["margin"] > 0:
            st.metric("Illustrative break-even ROAS (before other unentered costs)", f"{100 / data['margin']:.2f}×")
    elif step == 1:
        data["audience"] = st.text_area("Who buys and why?", value=data.get("audience", ""), key="journey_audience")
        data["pain"] = st.text_area("Customer's own words: pain or desire", value=data.get("pain", ""), key="journey_pain")
        data["objections"] = st.text_area("Main objections", value=data.get("objections", ""), key="journey_objections")
        data["research"] = st.text_area("Research sources / proof (or mark as hypothesis)", value=data.get("research", ""), key="journey_research")
        st.info("Why: angle and hook choices must start with customer evidence, not generic copy.")
    elif step == 2:
        for name, label in [("pixel","Meta Pixel events tested"),("capi","CAPI / deduplication checked"),("crm","CRM or delivered-order feedback connected"),("utm","UTM and landing page QA completed")]:
            data[name] = st.checkbox(label, value=data.get(name, False), key=f"journey_{name}")
        st.warning("Missing checks are launch blockers to review, not proof of broken tracking.")
    elif step == 3:
        data["objective"] = st.selectbox("Business objective", ["Purchases", "Qualified Leads", "Appointments", "Other"], key="journey_objective")
        data["target"] = st.number_input("Target cost per outcome (EGP, optional)", min_value=0.0, value=float(data.get("target", 0)), key="journey_target")
        data["test_plan"] = st.text_area("Initial experiment: angle, audience hypothesis, creative variations, budget and evaluation window", value=data.get("test_plan", ""), key="journey_test_plan")
        st.info("Why: decide what success looks like before evaluating ads. Meta campaign options depend on account and API capability.")
    elif step == 4:
        st.write("Next: use **Creative Strategy Academy** in the sidebar. Choose the customer angle first, then concept, hook and body.")
        st.caption("Suggested input from this brief: " + (data.get("pain") or "Add customer research in step 2"))
    else:
        checks = ["Creative claims verified", "Offer and landing page consistent", "Meta category and policy reviewed", "Tracking tested", "Human launch approval"]
        for label in checks:
            st.checkbox(label, key="launch_" + label.replace(" ", "_"))
        st.warning("This workflow cannot publish ads or change budgets. Publishing requires explicit authorization and account-specific Meta checks.")
    col1, col2 = st.columns(2)
    with col1:
        st.button("Previous", disabled=step == 0, on_click=lambda: st.session_state.update(zeno_journey_step=max(0, step-1)))
    with col2:
        st.button("Next", disabled=step == len(STEPS)-1, on_click=lambda: st.session_state.update(zeno_journey_step=min(len(STEPS)-1, step+1)))
    payload = {"id": data.get("id") or str(uuid.uuid4()), "exported_at": datetime.now(timezone.utc).isoformat(), "status": "DRAFT", "answers": data}
    st.download_button("Export onboarding brief", json.dumps(payload, ensure_ascii=False, indent=2), file_name="zeno-brand-onboarding.json", mime="application/json")
