"""ZENO AI Strategy Studio — goals to actionable strategy, copy and product-image creatives.
All model calls are opt-in, server-side, and use configured OPENAI_API_KEY.
"""
import base64
import json
import os
import requests
import streamlit as st

ANGLES = ["Pain / Problem", "Value / Price", "Social Proof", "Trust / Risk Reversal", "Comparison", "Convenience", "Urgency (verified only)", "Identity / Aspiration"]
FORMATS = ["Premium product hero", "Offer / Price design", "Lifestyle scene", "Problem / Solution", "Social proof (verified)", "Minimal product ad"]

def _chat(system, prompt):
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is missing in Railway Variables.")
    res = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        json={"model": os.getenv("ZENO_TEXT_MODEL", "gpt-4.1-mini"),
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
              "temperature": 0.5}, timeout=110)
    res.raise_for_status()
    return res.json()["choices"][0]["message"]["content"]

def _image_edit(image_file, instruction):
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("OPENAI_API_KEY is missing in Railway Variables.")
    image_file.seek(0)
    mime = image_file.type or "image/png"
    res = requests.post("https://api.openai.com/v1/images/edits",
        headers={"Authorization": "Bearer " + key},
        data={"model": os.getenv("ZENO_IMAGE_MODEL", "gpt-image-1.5"),
              "prompt": instruction, "size": "1024x1024", "n": "1"},
        files={"image": (image_file.name, image_file.getvalue(), mime)}, timeout=180)
    res.raise_for_status()
    data = res.json()["data"][0]
    if "b64_json" not in data:
        raise RuntimeError("Image provider returned no image bytes.")
    return base64.b64decode(data["b64_json"])

SYSTEM = """You are ZENO OS, a senior Egyptian performance marketing director and creative strategist.
Reply in clear practical Egyptian Arabic with precise English Meta Ads terms. Generate a specific complete, executable plan from user brief, not generic slogans.
Sections in this exact order:
1) فهم الهدف والافتراضات الناقصة
2) KPI economics: allowable CPA, break-even ROAS when margin known; don't invent conversion data
3) Campaign architecture: each campaign's exact name, objective, budget (EGP/day and month), ABO/CBO if appropriate, audience/geo, ad sets, creatives per ad set, placements, optimization event, exclusions if justified
4) Testing: angles, concepts, hooks, budgets, hypotheses, minimum evaluation signals, decision rules
5) Scaling: Broad/Advantage+ where eligible, CBO, vertical/horizontal/creative scaling; explicit gates and stop conditions, no universal percentage rules
6) 14-day execution calendar
7) Measurement: Pixel, CAPI, dedup, UTMs, CRM/COD quality and attribution limitations
8) Meta policy and account capability checklist
9) risks, questions and immediate next 3 actions.
Total proposed monthly budgets must match the user budget. Clearly label budget allocations as hypotheses, not Meta rules.
Use real product/offer facts only; never invent reviews, scarcity, guaranteed ROAS, performance or policy approval.
Real estate: account for housing special ad category if applicable, long lead cycle and qualified appointments.
Use supported current Meta account settings, avoid asserting a fixed universal 2026 campaign structure.
"""
CREATIVE_SYSTEM = """You are ZENO's creative strategist writing in concise persuasive Egyptian Arabic.
For the selected angle, produce:
1) Why this angle fits the objective and customer stage (identify assumptions)
2) Three truly distinct creative concepts
3) Three hooks per concept, with first-frame visual and spoken/on-screen text
4) A complete 20-35 second video body for each concept: scene sequence, proof, objections, offer, CTA
5) Six ready-to-test ad captions, with headline and CTA; distinct approaches and truthful claims
6) Six static/carousel design briefs: art direction, layout, headline, overlay, background, product placement, aspect ratios 1:1 and 4:5
7) testing matrix: what variable to isolate, primary business KPI, evaluation and next iteration.
Never fabricate reviews, warranties, discounts or stock levels. Flag missing evidence.
"""

def render_ai_strategy_studio():
    st.title("ZENO AI · Strategy & Creative Studio")
    st.caption("اكتب هدفك → خطة حملات كاملة → اختار Angle → كابشنات وديزاينات → ارفع صورة المنتج")
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("AI غير متصل. أضف OPENAI_API_KEY في Railway Variables لتفعيل توليد الخطط والتصميمات.")
    with st.form("zeno_ai_brief"):
        objective = st.text_area("اكتب هدفك ووصف البراند بالتفصيل", height=155, placeholder="مثال: براند ساعات في مصر، عايز أزود المبيعات بميزانية 100 ألف شهريًا، سعر المنتج 1200 جنيه، هامش الربح 40%...")
        business = st.selectbox("نوع النشاط", ["E-commerce", "Real Estate", "Lead Generation", "Other"])
        budget = st.number_input("الميزانية الشهرية (EGP)", min_value=0, value=100000, step=5000)
        product = st.text_input("اسم المنتج / المشروع")
        offer = st.text_input("العرض الحقيقي (اختياري)")
        audience = st.text_input("الجمهور / السوق")
        margin = st.number_input("هامش المساهمة قبل الإعلانات % (لو معروف)", min_value=0, max_value=100, value=0)
        create_plan = st.form_submit_button("ابنيلي Marketing & Campaign Plan كاملة", type="primary")
    brief = {"objective":objective, "business":business, "budget_egp_month":budget,
             "product":product, "verified_offer":offer, "audience":audience, "contribution_margin_pct":margin}
    if create_plan:
        if not objective.strip():
            st.error("اكتب هدفك الأول.")
        else:
            try:
                with st.spinner("بنبني الاستراتيجية والـCampaign Structure..."):
                    st.session_state["zeno_ai_plan"] = _chat(SYSTEM, json.dumps(brief, ensure_ascii=False))
                    st.session_state["zeno_ai_brief"] = brief
            except Exception as exc:
                st.error("تعذر إنشاء الخطة. راجع مفتاح الـAI والاتصال وحدود الاستخدام. " + str(exc)[:250])
    if st.session_state.get("zeno_ai_plan"):
        st.subheader("Your complete marketing & campaign plan")
        st.markdown(st.session_state["zeno_ai_plan"])
        st.download_button("تحميل الخطة", st.session_state["zeno_ai_plan"], "zeno-campaign-plan.md", mime="text/markdown")
    st.divider()
    st.subheader("Creative Strategy: Angle → Concept → Hook → Body")
    angle = st.selectbox("اختار الـAngle", ANGLES)
    stage = st.selectbox("مرحلة العميل", ["Unaware", "Problem Aware", "Solution Aware", "Product Aware", "Most Aware"])
    creative_notes = st.text_area("معلومات عن المنتج، المميزات، الاعتراضات، وأي Proof متاح")
    if st.button("طلعلي Concepts + Hooks + Bodies + Captions + Design Ideas"):
        active_brief = st.session_state.get("zeno_ai_brief", brief)
        if not active_brief.get("objective", "").strip():
            st.warning("اكتب وصف الهدف في الفورم الأول.")
        else:
            try:
                with st.spinner("بنجهز الكرياتيفات..."):
                    st.session_state["zeno_ai_creative"] = _chat(CREATIVE_SYSTEM, json.dumps({
                        "brief":active_brief, "angle":angle, "awareness_stage":stage, "notes":creative_notes
                    }, ensure_ascii=False))
            except Exception as exc:
                st.error("تعذر توليد الكرياتيفات: " + str(exc)[:250])
    if st.session_state.get("zeno_ai_creative"):
        st.markdown(st.session_state["zeno_ai_creative"])
        st.download_button("تحميل Creative Pack", st.session_state["zeno_ai_creative"], "zeno-creative-pack.md", mime="text/markdown")
    st.divider()
    st.subheader("AI Product Design")
    uploaded = st.file_uploader("ارفع صورة المنتج", type=["png","jpg","jpeg","webp"], key="zeno_product_photo")
    design_style = st.selectbox("اختار نوع الديزاين", FORMATS)
    design_instructions = st.text_area("تفاصيل الديزاين المطلوبة", placeholder="خلفية فخمة، المنتج في المنتصف، بدون أي لوجو أو ادعاء غير مؤكد")
    if uploaded:
        st.image(uploaded, caption="Original product image", width=300)
    if st.button("Generate Product Ad Design", disabled=uploaded is None):
        try:
            prompt = ("Create a premium square Meta feed ad creative using the attached product photograph as the exact visual reference. "
                      "Preserve the product's actual appearance, colors, markings and proportions; do not invent logos, branding or claims. "
                      "Visual style: " + design_style + ". User instructions: " + design_instructions +
                      ". Verified product and offer context: " + json.dumps(brief, ensure_ascii=False) +
                      ". Use clean commercially polished art direction. Avoid adding text unless explicitly requested. "
                      "Do not alter brand marks to impersonate or misrepresent products.")
            with st.spinner("بنجهز الديزاين..."):
                st.session_state["zeno_generated_design"] = _image_edit(uploaded, prompt)
        except Exception as exc:
            st.error("تعذر توليد الصورة. تأكد من صلاحيات Image API ونوع الصورة والرصيد: " + str(exc)[:250])
    if st.session_state.get("zeno_generated_design"):
        st.image(st.session_state["zeno_generated_design"], caption="AI-generated draft — review product accuracy before use")
        st.download_button("تحميل الديزاين PNG", st.session_state["zeno_generated_design"], "zeno-product-design.png", mime="image/png")
