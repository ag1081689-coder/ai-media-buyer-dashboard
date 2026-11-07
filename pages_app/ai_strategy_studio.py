"""ZENO manual Strategy Studio: no AI API, no automatic publishing."""
import json
import streamlit as st

ANGLES = {
 "Value / Price": ["قيمة تستاهل قرارك", "اختيار ذكي بسعر واضح", "شوف القيمة قبل ما تقارن السعر"],
 "Problem / Solution": ["حل عملي لمشكلتك", "الفرق يبدأ من التفاصيل", "اختار الحل المناسب ليك"],
 "Trust / Proof": ["تفاصيل تخليك تختار بثقة", "شوف الجودة بنفسك", "القرار يبدأ بمعلومة واضحة"],
 "Convenience": ["اختيار أسهل كل يوم", "وقت أقل، تجربة أسهل", "كل التفاصيل في مكان واحد"],
 "Comparison": ["قارن قبل ما تقرر", "إيه اللي يفرق فعلًا؟", "اختار على أساس واضح"],
 "Offer": ["اكتشف العرض المتاح", "فرصتك تختار الأنسب", "شوف تفاصيل العرض دلوقتي"],
 "Lifestyle": ["تفاصيل تناسب أسلوبك", "اختيار يكمل يومك", "خلي التفاصيل تتكلم"],
}
STRUCTURES = [
 ("Lean / Consolidated", [("MAIN | Broad", 80, "CBO / Advantage+ where eligible"), ("TEST | Creative", 20, "ABO controlled tests")],
  "حساب جديد أو بيانات قليلة: تجميع الإشارات وتجنب تقسيم الميزانية."),
 ("Testing-Led", [("TEST | Angles", 35, "ABO"), ("TEST | Concepts & Hooks", 25, "ABO"), ("MAIN | Proven Creatives", 40, "CBO / supported setup")],
  "لما الهدف اكتشاف الرسائل والكرياتيفات الكسبانة مع وجود حد أدنى من الميزانية."),
 ("Scaling-Led", [("SCALE | Broad Winners", 65, "CBO / supported Advantage+"), ("TEST | New Creatives", 20, "ABO"), ("SCALE | New Angles", 15, "CBO / justified split")],
  "للحسابات اللي عندها نتائج مستقرة وكرياتيفات مثبتة."),
]
def render_ai_strategy_studio():
 st.title("ZENO · Media Buyer Strategy Builder")
 st.caption("Manual-first: اشرح هدفك → قارن 3 Structures → اختار Angle → خُد Headlines وCreative Brief جاهزين للنسخ في ChatGPT. بدون API.")
 with st.form("manual_strategy"):
  objective=st.text_area("1. اشرح هدفك بالتفصيل (إجباري)",height=145,placeholder="مثال: عندي براند ساعات في مصر، عايز أختبر 3 Angles وأوصل لتكلفة شراء مناسبة قبل ما أبدأ Scaling...")
  industry=st.selectbox("النشاط",["E-commerce","Real Estate","Lead Generation","Other"])
  product=st.text_input("المنتج أو المشروع")
  budget=st.number_input("الميزانية الشهرية بالجنيه",min_value=1000,value=100000,step=1000)
  stage=st.selectbox("حالة الحساب",["جديد / بدون بيانات","Testing","Stable / Ready to Scale","Performance Declining"])
  results=st.text_area("النتائج الحالية إن وجدت (CPA / ROAS / Leads / Sales)")
  audience=st.text_input("الجمهور أو المنطقة")
  offer=st.text_input("العرض الحقيقي إن وجد")
  submitted=st.form_submit_button("اعرض 3 Campaign Structures",type="primary")
 if submitted:
  if len(objective.strip())<25:
   st.error("اشرح الهدف بشكل أوضح الأول (25 حرف على الأقل).")
  else:
   st.session_state["manual_brief"]={"goal":objective,"industry":industry,"product":product,"budget":budget,"stage":stage,"results":results,"audience":audience,"verified_offer":offer}
   st.session_state.pop("manual_selected_structure",None)
 brief=st.session_state.get("manual_brief")
 if not brief:
  st.info("اكتب هدفك واضغط عرض 3 Campaign Structures. مش هنرشح أي حاجة قبل فهم الهدف.")
  return
 st.subheader("2. قارن بين 3 Campaign Structures")
 recommended=2 if brief["stage"]=="Stable / Ready to Scale" else (1 if brief["stage"]=="Testing" else 0)
 st.caption("الميزانيات المقترحة أمثلة تخطيطية وليست قواعد Meta؛ لازم تراجع إعدادات الحساب الفعلية.")
 for i,(name,campaigns,reason) in enumerate(STRUCTURES):
  with st.expander(("مقترح مبدئي · " if i==recommended else "")+name,expanded=i==recommended):
   st.write(reason)
   for cname,pct,kind in campaigns:
    monthly=round(brief["budget"]*pct/100)
    st.markdown("**"+cname+"** — "+kind+" | "+str(pct)+"% | "+f"{monthly:,}"+" EGP/month | "+f"{monthly/30:,.0f}"+" EGP/day")
   st.caption("حدّد Objective وConversion Event وGeo والـAd Sets وعدد الإعلانات بعد مراجعة نوع النشاط، جودة التتبع والبيانات.")
 options=[x[0] for x in STRUCTURES]
 choice=st.selectbox("اختار الـStructure اللي عايز تبني عليه",options,index=recommended)
 st.session_state["manual_selected_structure"]=choice
 st.subheader("3. Angle → Concept → Hook → Body")
 angle=st.selectbox("اختار الـAngle",list(ANGLES))
 concept=st.selectbox("Creative Concept",["Product Hero","UGC Experience","Problem → Solution","Product Demo","Comparison","FAQ / Objection","Offer Breakdown"])
 st.markdown("**Headlines للديزاين (جاهزة للنسخ):**")
 for h in ANGLES[angle]:
  st.code(h,language=None)
 custom=st.text_input("Headline مخصص",value=ANGLES[angle][0])
 st.markdown("**Body Framework:** Hook → مشكلة/رغبة العميل → شرح المنتج → إثبات حقيقي → عرض مؤكد → CTA")
 st.markdown("**Caption Template:** "+custom+" — "+(brief["product"] or "المنتج")+" | "+(brief["verified_offer"] or "شوف المميزات والتفاصيل")+" | اطلب التفاصيل دلوقتي.")
 st.subheader("4. Product Design Brief")
 photo=st.file_uploader("ارفع صورة المنتج (للمعاينة فقط، بدون إرسال لأي API)",type=["png","jpg","jpeg","webp"])
 if photo: st.image(photo,caption="الصورة الأصلية — استخدمها يدويًا في ChatGPT",width=300)
 style=st.selectbox("نوع التصميم",["Premium Hero","Offer Visual","Lifestyle","UGC Thumbnail","Comparison","Minimal"])
 prompt=("استخدم صورة المنتج المرفقة كمرجع أساسي وحافظ على شكله وألوانه وعلاماته الأصلية بدقة. "
         "اعمل تصميم إعلان سوشيال ميديا احترافي بنمط "+style+". "
         "البراند/المنتج: "+(brief["product"] or "غير محدد")+". "
         "الـAngle: "+angle+". الـConcept: "+concept+". "
         "اكتب على التصميم Headline: "+custom+". "
         "خلي مساحة واضحة للـCTA، وماتضيفش أي خصم أو ضمان أو تقييم غير مؤكد. "
         "اعمل نسخة 4:5 للـFeed ونسخة 9:16 للـStories.")
 st.text_area("Prompt جاهز تنسخه في ChatGPT مع صورة المنتج",value=prompt,height=175)
 st.subheader("5. انسخ الخطة الكاملة لـChatGPT")
 selected=next(x for x in STRUCTURES if x[0]==choice)
 full_prompt=("أنت Senior Performance Marketing Strategist متخصص في Meta Ads 2026. "
  "حلل البريف ده أولًا، واسأل عن البيانات الحرجة الناقصة بدل ما تخمن. "
  "ابني خطة تنفيذ كاملة للحملات مع أسماء الحملات والـObjectives والـAd Sets والـAudience والـPlacements "
  "والـOptimization Events وتوزيع الميزانيات اليومية والشهرية، وخطة Testing وScaling وشروط نقل الـWinners. "
  "وضح قيود Meta الفعلية وسياسات الإعلانات. "
  "ثم ابنِ Creative Strategy تشمل Angles وConcepts وHooks وBodies و6 Captions و6 Design Briefs. "
  "لا تخترع نتائج أو خصومات أو شهادات عملاء.\n\n"
  "البريف: "+json.dumps(brief,ensure_ascii=False)+"\n"
  "الـStructure المختار: "+choice+"\n"
  "توزيع الميزانية المبدئي: "+json.dumps(selected[1],ensure_ascii=False)+"\n"
  "الـAngle: "+angle+"\nConcept: "+concept+"\nHeadline: "+custom+"\n"
  "Design prompt: "+prompt)
 st.text_area("الـPrompt الكامل — انسخه واستخدمه يدويًا",value=full_prompt,height=260)
 st.download_button("تحميل الخطة والـPrompt",full_prompt,file_name="zeno-manual-plan.txt",mime="text/plain")
