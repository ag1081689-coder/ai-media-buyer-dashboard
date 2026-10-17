"""Interactive, deterministic Creative Strategy Academy for ZENO OS.
No external AI calls or claims of AI generation. Human-approved drafts only.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import streamlit as st

STAGES = ["Unaware", "Problem Aware", "Solution Aware", "Product Aware", "Most Aware"]
ANGLES = {
    "Problem / Pain": "Start with a concrete customer problem and demonstrate a truthful solution.",
    "Value / Savings": "Explain total value or verified savings; avoid invented discounts.",
    "Trust / Proof": "Use verified evidence, real policies and authorized testimonials.",
    "Comparison": "Compare verifiable features without misleading competitor claims.",
    "Convenience": "Show the actual time, effort or steps saved.",
    "Objection Handling": "Answer the strongest customer objection with evidence.",
    "Identity / Aspiration": "Connect product benefits to customer goals without personal-attribute targeting.",
}
CONCEPTS = {
    "Problem / Pain": ["Problem → Solution Demo", "Mistake vs Better Way", "Day-in-the-life"],
    "Value / Savings": ["Value Breakdown", "Cost-per-use Explanation", "Offer Walkthrough"],
    "Trust / Proof": ["Verified Customer Experience", "Behind-the-scenes", "Unboxing and Policy Walkthrough"],
    "Comparison": ["Side-by-side Features", "Three Buying Criteria", "Product Selection Guide"],
    "Convenience": ["Fast Process Demo", "Before / After Workflow", "Step-by-step Tutorial"],
    "Objection Handling": ["FAQ Conversation", "Myth vs Fact", "Real Customer Questions"],
    "Identity / Aspiration": ["Lifestyle Story", "Use-case Montage", "Founder Story"],
}
HOOKS = {
    "Question": "إيه أهم حاجة بتدور عليها قبل ما تختار {product}؟",
    "Mistake": "3 حاجات لازم تراجعها قبل ما تختار {product}.",
    "Demonstration": "تعالى أوريك {product} بيشتغل إزاي على الحقيقة.",
    "Comparison": "إيه الفرق بين الاختيارات المتاحة في {product}؟",
}
def _reset_downstream(changed):
    keys = {
        "angle": ["zeno_concept", "zeno_hook_type", "zeno_body", "zeno_cta"],
        "concept": ["zeno_hook_type", "zeno_body", "zeno_cta"],
        "hook": ["zeno_body", "zeno_cta"],
    }
    for key in keys.get(changed, []):
        st.session_state.pop(key, None)

def render_creative_academy():
    st.title("ZENO Creative Strategy Academy")
    st.caption("Research → Angle → Concept → Hook → Body → Brief → Testing. Drafts are suggestions, not verified customer claims.")
    with st.expander("1 · Brand and customer research", expanded=True):
        brand = st.text_input("Brand", key="zeno_brand")
        product = st.text_input("Product / project", key="zeno_product")
        business = st.selectbox("Business type", ["E-commerce", "Real Estate", "Lead Generation", "Other"], key="zeno_business")
        stage = st.selectbox("Customer awareness", STAGES, key="zeno_stage")
        pain = st.text_area("Customer pain / desire", key="zeno_pain", placeholder="Write what customers actually say, or mark as a hypothesis")
        objection = st.text_input("Main objection", key="zeno_objection")
        evidence = st.text_area("Verified proof / source (optional)", key="zeno_evidence", placeholder="Actual product facts, permitted reviews, real policies")
        offer = st.text_input("Verified offer (optional)", key="zeno_offer")
    st.subheader("2 · Choose Angle")
    angle = st.selectbox("Persuasion angle", list(ANGLES), key="zeno_angle", on_change=_reset_downstream, args=("angle",))
    st.info(ANGLES[angle])
    st.caption("Why this angle? Connect it to the customer pain, awareness stage and available proof.")
    st.subheader("3 · Build Concept")
    concept = st.selectbox("Creative concept", CONCEPTS[angle], key="zeno_concept", on_change=_reset_downstream, args=("concept",))
    st.caption("The concept is the execution idea; changing it is more than rewriting the hook.")
    st.subheader("4 · Select Hook")
    hook_type = st.selectbox("Hook style", list(HOOKS), key="zeno_hook_type", on_change=_reset_downstream, args=("hook",))
    suggested_hook = HOOKS[hook_type].format(product=product or "المنتج")
    hook = st.text_input("Hook — edit before approval", value=suggested_hook, key=f"zeno_hook_text_{angle}_{concept}_{hook_type}")
    st.subheader("5 · Write Body")
    body_seed = "\n".join([
        f"المشكلة / السياق: {pain or '[أضف مشكلة العميل]'}",
        f"الفكرة: {concept} — وضّح إزاي {product or 'المنتج'} بيساعد.",
        f"الإثبات: {evidence or '[أضف دليل حقيقي أو احذف الادعاء]'}",
        f"الاعتراض: {objection or '[أضف اعتراض العميل]'}",
        f"العرض: {offer or '[اختياري: عرض مؤكد فقط]'}",
    ])
    body = st.text_area("Body script", value=body_seed, height=210, key=f"zeno_body_{angle}_{concept}")
    fmt = st.selectbox("Format", ["UGC Video", "Product Demo", "Talking Head", "Static", "Carousel", "Founder Story"], key="zeno_format")
    cta = st.text_input("CTA", value="شوف التفاصيل واعرف أكتر", key="zeno_cta")
    st.subheader("6 · Creative brief and testing")
    kpi = st.selectbox("Primary KPI", ["Qualified Leads", "Cost per Purchase", "Purchase ROAS", "Cost per Lead", "Landing Page Views"], key="zeno_kpi")
    hypothesis = st.text_area("Test hypothesis", value=f"Testing '{angle}' via '{concept}' for {stage} customers.", key=f"zeno_hypothesis_{angle}_{concept}")
    st.warning("Policy preflight: verify all claims, permissions, offer availability, sensitive attributes and applicable Meta Special Ad Category rules. Approval is not guaranteed.")
    reviewed = st.checkbox("I reviewed claims, proof, offer and CTA", key="zeno_reviewed")
    if st.button("Create creative brief", type="primary", disabled=not (brand.strip() and product.strip() and pain.strip() and reviewed)):
        brief = {
            "id": str(uuid.uuid4()), "created_at": datetime.now(timezone.utc).isoformat(),
            "brand": brand.strip(), "product": product.strip(), "business": business,
            "awareness_stage": stage, "customer_pain": pain.strip(), "objection": objection.strip(),
            "evidence": evidence.strip(), "offer": offer.strip(), "angle": angle,
            "angle_rationale": ANGLES[angle], "concept": concept, "hook": hook.strip(),
            "body": body.strip(), "format": fmt, "cta": cta.strip(),
            "primary_kpi": kpi, "test_hypothesis": hypothesis.strip(),
            "status": "DRAFT", "approved_for_publication": False,
        }
        st.session_state["zeno_latest_brief"] = brief
    if "zeno_latest_brief" in st.session_state:
        brief = st.session_state["zeno_latest_brief"]
        st.success("Draft brief created. Review and approve separately before publishing.")
        st.json(brief)
        st.download_button("Download creative brief JSON", data=json.dumps(brief, ensure_ascii=False, indent=2), file_name=f"zeno-creative-{brief['id'][:8]}.json", mime="application/json")
