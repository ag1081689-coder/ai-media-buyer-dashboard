import pandas as pd
import streamlit as st
from pandas.errors import EmptyDataError, ParserError
from meta_ads_fetcher import fetch_meta_ads_report, fetch_business_ad_accounts

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.markdown('''
<style>
@property --num { syntax: '<integer>'; initial-value: 1; inherits: false; }
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], .stApp {background:#050505 !important; color:#ffffff !important;}
.block-container {padding-top:1.2rem; padding-bottom:4rem; max-width:1550px; background:#050505 !important;}
* {color:#ffffff;}
.smart-hero {position:relative; overflow:hidden; background:radial-gradient(circle at 70% 40%, rgba(255,122,0,.28), transparent 28%), linear-gradient(135deg,#070707,#160d04); border:1px solid rgba(255,122,0,.48); border-radius:24px; padding:34px 38px; margin-bottom:22px; box-shadow:0 28px 90px rgba(0,0,0,.75); min-height:280px; display:grid; grid-template-columns:1.15fr .85fr; gap:24px; align-items:center;}
.smart-hero:before {content:''; position:absolute; inset:-2px; background:linear-gradient(90deg, transparent, rgba(255,122,0,.14), transparent); transform:translateX(-100%); animation:scan 4s infinite;}
.hero-copy {position:relative; z-index:2;}.smart-hero h1 {font-size:54px; line-height:1.02; margin:0; color:#ffffff !important; letter-spacing:-1.8px; max-width:760px;}.hero-sub {color:#f5f5f5 !important; font-size:18px; margin:18px 0 0; max-width:720px; line-height:1.6;}.hero-tov {color:#ff9f1c !important; font-size:18px; font-weight:900; margin-top:16px;}.badge {display:inline-block; padding:8px 14px; border-radius:999px; background:rgba(255,122,0,.18); color:#ff9f1c !important; font-weight:900; font-size:12px; margin-bottom:14px; border:1px solid rgba(255,122,0,.45); letter-spacing:.5px;}
.counter-wrap {position:relative; z-index:2; display:flex; justify-content:center; align-items:center; min-height:230px;}.counter-orb {width:230px; height:230px; border-radius:50%; background:radial-gradient(circle,#1f1308 0%,#070707 65%); border:1px solid rgba(255,122,0,.55); box-shadow:0 0 0 12px rgba(255,122,0,.05), 0 0 80px rgba(255,122,0,.38); display:flex; flex-direction:column; align-items:center; justify-content:center; position:relative; overflow:hidden;}.counter-orb:before {content:''; position:absolute; inset:-40%; background:conic-gradient(from 0deg, transparent, #ff7a00, transparent 35%); animation:spin 2.2s linear infinite;}.counter-orb:after {content:''; position:absolute; inset:10px; border-radius:50%; background:#090909; border:1px solid rgba(255,122,0,.25);}.counter-number {position:relative; z-index:3; font-size:70px; font-weight:1000; color:#ff9f1c !important; line-height:1; animation:countUp 2.3s steps(99) forwards; counter-reset:num var(--num);}.counter-number:after {content:counter(num);}.counter-label {position:relative; z-index:3; margin-top:10px; font-size:13px; color:#ffffff !important; text-transform:uppercase; letter-spacing:1.8px; font-weight:800;}
@keyframes countUp {from {--num:1;} to {--num:100;}}@keyframes spin {to {transform:rotate(360deg);}}@keyframes scan {0% {transform:translateX(-100%);} 45%,100% {transform:translateX(100%);}}
[data-testid="stMetric"], .os-card, .filter-card, .action-card {background:#0f0f0f; border:1px solid rgba(255,122,0,.35); border-radius:16px; box-shadow:0 14px 45px rgba(0,0,0,.45);}
[data-testid="stMetric"] {padding:14px 16px;}[data-testid="stMetricLabel"] {color:#ffffff !important; font-size:13px;}[data-testid="stMetricValue"] {color:#ff9f1c !important; font-size:27px;}
.stButton button {border-radius:12px; background:linear-gradient(135deg,#ff7a00,#ff9f1c) !important; color:#050505 !important; border:0; font-weight:900; padding:.7rem 1.1rem;}.stButton button:hover {background:#ffb347 !important; color:#050505 !important;}
[data-testid="stDataFrame"] {background:#0f0f0f; border-radius:14px; border:1px solid rgba(255,122,0,.3); box-shadow:0 18px 55px rgba(0,0,0,.45); overflow:hidden;}
.table-title {font-size:21px; font-weight:900; color:#ff9f1c !important; margin:20px 0 6px;}.help-text {font-size:14px; color:#ffffff !important; margin-bottom:12px;}.filter-card {padding:14px 16px; margin:12px 0 16px;}.action-card {border-left:5px solid #ff7a00; padding:18px 20px; margin:18px 0;}.action-card h3 {margin:0 0 8px; color:#ffffff !important;}.action-grid {display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap:12px; margin-top:12px;}.action-box {background:#181818; border:1px solid rgba(255,122,0,.25); border-radius:12px; padding:12px; color:#ffffff !important;}.action-label {font-size:12px; color:#ff9f1c !important; font-weight:900; text-transform:uppercase; margin-bottom:4px;}.os-card {padding:16px; margin:12px 0;}.os-card h4 {margin:0 0 8px; color:#ff9f1c !important;}.alert-hot {border-left:5px solid #ff3b30;}.alert-good {border-left:5px solid #ff9f1c;}.alert-info {border-left:5px solid #64748b;}.stSegmentedControl button, [data-baseweb="tab"] {color:#ffffff !important;}input, textarea, select {background:#111111 !important; color:#ffffff !important; border-color:#ff7a00 !important;}
@media (max-width:900px){.smart-hero{grid-template-columns:1fr;}.smart-hero h1{font-size:38px}.counter-orb{width:190px;height:190px}.counter-number{font-size:56px}.action-grid{grid-template-columns:1fr}}
</style>
''', unsafe_allow_html=True)

TAX_NET_RATE = 0.86
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
MONTH_WINDOW_MAP = {m: f'MONTH_{i:02d}' for i, m in enumerate(MONTHS, start=1)}


def safe_num(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def format_money(value):
    return f"{safe_num(value):,.0f} EGP"


def get_creative_diagnosis(row):
    ctr, freq, roas, purchases, cpp = [safe_num(row.get(x)) for x in ['ctr','frequency','manual_roas','purchases','cost_per_purchase']]
    issues, fixes = [], []
    if ctr < 1:
        issues.append('Hook issue'); fixes.append('اعمل 5 هووكس جديدة: مشكلة مباشرة، صدمة سعر، إثبات اجتماعي، مقارنة، وافتتاحية UGC.')
    if freq > 3.5 and roas < 4:
        issues.append('Visual fatigue'); fixes.append('غير الفيجوال: Thumbnail جديد، أول فريم مختلف، زاوية تصوير جديدة، ووش UGC جديد.')
    if purchases > 0 and cpp > 300:
        issues.append('Offer or caption issue'); fixes.append('اكتب كابشن جديد يوضح القيمة، العرض، ضمانات الدفع أو التوصيل، وCTA واضح.')
    if roas >= 5 and purchases >= 10:
        issues.append('Winning angle'); fixes.append('اعمل 3 نسخ جديدة من نفس الزاوية الكسبانة وشغلهم في تست Scaling محسوب.')
    if not issues:
        issues.append('No major creative issue'); fixes.append('راقب فقط. متغيرش الإعلان الكسبان غير لو Frequency زاد أو ROAS بدأ ينزل.')
    return ', '.join(issues), ' | '.join(fixes)


def generate_content_pack(row):
    issue = str(row.get('creative_issue', ''))
    hooks = ['لسه بتقارن؟ ابدأ بالاختيار اللي العملاء بيرجعوله كل مرة.','قبل ما تشتري، شوف ليه العرض ده واخد اهتمام.','الترقية البسيطة اللي كانت ناقصة طلبك.','وقف هنا لو عايز قيمة أعلى من غير ما تدفع زيادة.','المنتج اللي الناس بتطلبه أكتر من مرة.']
    captions = ['اختيار معمول للناس اللي عايزة قيمة واضحة وتجربة شراء سهلة وسريعة. اطلب دلوقتي قبل انتهاء العرض.','عرض واضح، قيمة قوية، وقرار شراء أسهل. شوف التفاصيل وكمل طلبك النهارده.','العملاء بيختاروه لسبب. قارن القيمة، شوف المميزات، واطلب بثقة.']
    visuals = ['افتتاحية UGC بوش شخص ماسك المنتج في أول ثانيتين.','لقطة قريبة للمنتج مع Overlay للسعر أو الميزة الأساسية.','قبل/بعد أو مشكلة/حل مع Cuts سريعة في أول 3 ثواني.','فيجوال إثبات اجتماعي: Reviews أو Orders أو Reaction من عميل.']
    testing = ['اختبر 3 هووكس على نفس الفيجوال الكسبان عشان تعزل تأثير الهووك.','شغل 2 UGC و2 Static في ABO بميزانية متساوية.','اقفل أي Creative أقل من 1% CTR بعد صرف كافي، وسيب اللي CPA وROAS بتاعه ثابت.','متغيرش الجمهور والكرياتيف في نفس الوقت.']
    scaling = ['لو ROAS ثابت 48 ساعة، زود الميزانية 15-20%.','لو المبيعات ثابتة، اعمل Duplicate للـ Ad Set الكسبان داخل CBO Scaling Campaign.','قبل ما تزود الصرف بقوة، اعمل 3 Variations من نفس الزاوية الكسبانة.','وقف السكيل لو CPA زاد فجأة أو ROAS نزل تحت التارجت يومين ورا بعض.']
    if 'Hook issue' in issue:
        hooks = ['غالبًا بتدفع زيادة من غير ما تاخد بالك.','الغلط اللي أغلب الناس بتعمله قبل ما تشتري.','جربته عشان أنت ماتحتارش.','ده اللي هختاره لو بدور على أعلى قيمة مقابل السعر.','متشتريش قبل ما تشوف النقطة دي.']
    if 'Visual fatigue' in issue:
        visuals = ['غير أول فريم بالكامل: خلفية جديدة، حركة إيد جديدة، وزاوية منتج مختلفة.','استخدم Creator جديد بنفس العرض لكن بافتتاحية مختلفة.','حوّل من Static لـ UGC أو من UGC لـ Product Demo نظيف.','ضيف حركة في أول ثانية: دخول المنتج في الكادر، Reveal سريع، أو مقارنة مباشرة.']
    if 'Offer or caption issue' in issue:
        captions = ['خد قيمة أعلى من غير تعقيد في الطلب. مميزات واضحة، Checkout سهل، وتوصيل سريع.','العرض ده معمول للي عايز يشتري بذكاء، مش يشتري أي منتج وخلاص.','قارن القيمة، شوف المميزات، واطلب قبل ما العرض يخلص.']
    return hooks, captions, visuals, testing, scaling


def score_row(row, avg_roas, level='campaign'):
    score, reasons = 0, []
    roas, spend, purchases, ctr, frequency, cpp = [safe_num(row.get(x)) for x in ['manual_roas','spend','purchases','ctr','frequency','cost_per_purchase']]
    effective_status = str(row.get(f'{level}_effective_status', row.get('campaign_effective_status', '')))
    if roas >= avg_roas * 1.2 and purchases >= 3:
        score += 35; reasons.append('ROAS above average')
    elif roas >= avg_roas and purchases >= 2:
        score += 25; reasons.append('ROAS around average')
    elif roas > 0:
        score += 10; reasons.append('ROAS below average')
    if purchases >= 20:
        score += 25; reasons.append('Strong purchase volume')
    elif purchases >= 5:
        score += 15; reasons.append('Enough purchases to judge')
    elif purchases > 0:
        score += 5; reasons.append('Low purchase volume')
    if ctr >= 2:
        score += 15; reasons.append('Strong CTR')
    elif ctr >= 1:
        score += 8; reasons.append('Acceptable CTR')
    else:
        reasons.append('CTR needs work')
    if frequency <= 2.5:
        score += 10; reasons.append('Healthy frequency')
    elif frequency <= 4:
        score += 4; reasons.append('Frequency rising')
    else:
        score -= 10; reasons.append('Possible fatigue')
    if cpp and cpp <= 250:
        score += 15; reasons.append('Good CPP')
    elif cpp and cpp <= 400:
        score += 7; reasons.append('Average CPP')
    elif cpp:
        score -= 10; reasons.append('High CPP')
    if spend < 500:
        score = min(score, 45); reasons.append('Low spend')
    score = max(0, min(100, round(score)))
    if score >= 80:
        status, action = 'Scale', 'Scale carefully or duplicate into CBO.'
    elif score >= 60:
        status, action = 'Watch', 'Keep running and review again in 24-48h.'
    elif score >= 40:
        status, action = 'Test/Fix', 'Test hooks, captions, visuals, or offer.'
    else:
        status, action = 'Kill/Pause', 'Reduce budget or pause if spend is enough.'
    reopen = 'YES' if effective_status != 'ACTIVE' and score >= 70 else 'No'
    if reopen == 'YES':
        action = 'Old asset looks strong. Reopen with controlled test budget.'
    if effective_status == 'ACTIVE' and score < 35:
        action = 'Active but weak. Review now or pause.'
    return score, status, action, reopen, ' | '.join(reasons[:4])


def daily_budget_action(row, avg_roas):
    roas, spend, purchases, cpp, ctr, freq = [safe_num(row.get(x)) for x in ['manual_roas','spend','purchases','cost_per_purchase','ctr','frequency']]
    if spend >= 800 and purchases == 0:
        return 'PAUSE TODAY', 'اقفلها النهارده. صرفت من غير مبيعات.'
    if spend >= 500 and roas and roas < max(1.5, avg_roas * 0.35):
        return 'CUT 30-50%', 'قلل الميزانية 30% لـ 50% وراجع الكرياتيف.'
    if roas >= avg_roas * 1.2 and purchases >= 5 and freq < 3:
        return 'SCALE 15-20%', 'زود الميزانية 15% لـ 20% لو الأداء ثابت آخر اليوم.'
    if ctr < 1 and spend >= 300:
        return 'CREATIVE FIX', 'المشكلة غالبًا في الهووك أو أول فريم.'
    if freq > 4:
        return 'REFRESH VISUAL', 'فيه Fatigue. غير الفيجوال قبل ما تزود صرف.'
    if cpp and cpp > 400:
        return 'CUT 20-30%', 'الـ CPA عالي. قلل الصرف وجرب عرض/كابشن أقوى.'
    return 'WATCH', 'راقبها. مفيش قرار عنيف دلوقتي.'


def tracking_diagnostics(row):
    clicks, lpv, atc, ic, purchases = [safe_num(row.get(x)) for x in ['clicks','landing_page_view','add_to_cart','initiate_checkout','purchases']]
    lpv_rate = (lpv / clicks * 100) if clicks else 0
    atc_rate = (atc / lpv * 100) if lpv else 0
    checkout_rate = (ic / atc * 100) if atc else 0
    purchase_rate = (purchases / ic * 100) if ic else 0
    score = 100
    leak, rec, priority = 'No major leak', 'الفانل شكله مستقر. ركز على السكيل أو تحسين الكرياتيف.', 'Scale/Watch'
    if clicks > 50 and lpv_rate < 55:
        score -= 35; leak = 'Click → LPV leak'; rec = 'راجع سرعة اللاندنج والتراكينج. في Clicks كتير مش بتوصل LPV.'; priority = 'Fix Tracking / Landing Speed'
    elif lpv > 50 and atc_rate < 3:
        score -= 30; leak = 'LPV → ATC leak'; rec = 'الناس بتدخل الصفحة بس مش بتضيف للسلة. راجع العرض، السعر، الصور، والثقة.'; priority = 'Fix Offer / Product Page'
    elif atc > 10 and checkout_rate < 35:
        score -= 25; leak = 'ATC → Checkout leak'; rec = 'في مشكلة في السلة: شحن، سعر نهائي، كود خصم، أو ثقة.'; priority = 'Fix Cart'
    elif ic > 5 and purchase_rate < 35:
        score -= 25; leak = 'Checkout → Purchase leak'; rec = 'في احتكاك في الدفع أو checkout. راجع طرق الدفع، COD، والرسائل.'; priority = 'Fix Checkout'
    if clicks > 100 and purchases == 0:
        score -= 25; leak = 'Traffic with no purchases'; rec = 'الترافيك غير مؤهل أو التراكينج ناقص. راجع event purchase والـ audience intent.'; priority = 'Fix Tracking / Audience'
    return max(0, round(score)), leak, priority, rec


def growth_recommendation(row):
    action = str(row.get('today_action',''))
    leak = str(row.get('funnel_leak_stage',''))
    status = str(row.get('status',''))
    if action == 'SCALE 15-20%': return 'زود الميزانية تدريجي 15-20%، واعمل نسخة من نفس الزاوية الكسبانة قبل ما تزود بقوة.'
    if action.startswith('CUT'): return 'قلل الميزانية مؤقتًا، وشغل تست جديد على الهووك أو العرض بدل ما تزود صرف على نفس المشكلة.'
    if action == 'PAUSE TODAY': return 'اقفلها النهارده. متفتحهاش تاني غير بعد ما تغير الكرياتيف أو الجمهور أو العرض.'
    if 'LPV' in leak: return 'ابدأ بتحسين سرعة الصفحة والتراكينج قبل أي تست كرياتيف جديد.'
    if 'ATC' in leak: return 'اشتغل على العرض وصفحة المنتج. زود proof، وضح السعر، وخلّي CTA أقوى.'
    if 'Checkout' in leak: return 'راجع checkout وطرق الدفع والشحن. المشكلة مش في الإعلان لو الناس وصلت checkout.'
    if status == 'Scale': return 'الأصل قوي. اعمل variations من نفس الزاوية، ومتغيرش كل حاجة مرة واحدة.'
    return 'راقب الأداء، ولو مفيش تحسن خلال 24-48 ساعة اعمل تست Hook + Visual جديد.'


def aggregate_level(df, level, overall_roas):
    id_cols = {'campaign':['campaign_name','campaign_status','campaign_effective_status'],'adset':['campaign_name','adset_name','adset_status','adset_effective_status'],'ad':['campaign_name','adset_name','ad_name','ad_status','ad_effective_status']}[level]
    existing = [c for c in id_cols if c in df.columns]
    if not existing: return pd.DataFrame()
    agg = df.groupby(existing, as_index=False, dropna=False).agg({'spend':'sum','purchase_value':'sum','purchases':'sum','clicks':'sum','impressions':'sum','frequency':'mean','cost_per_purchase':'mean','landing_page_view':'sum','view_content':'sum','add_to_cart':'sum','initiate_checkout':'sum'})
    agg['manual_roas'] = agg.apply(lambda r: round(r['purchase_value'] / r['spend'], 2) if r['spend'] else 0, axis=1)
    agg['ctr'] = agg.apply(lambda r: round((r['clicks'] / r['impressions']) * 100, 2) if r['impressions'] else 0, axis=1)
    agg[['score','status','next_action','reopen_signal','why']] = agg.apply(lambda r: score_row(r, overall_roas, level), axis=1, result_type='expand')
    agg[['creative_issue','creative_fix']] = agg.apply(lambda r: pd.Series(get_creative_diagnosis(r)), axis=1)
    agg[['today_action','today_reason']] = agg.apply(lambda r: daily_budget_action(r, overall_roas), axis=1, result_type='expand')
    agg[['tracking_health_score','funnel_leak_stage','growth_priority','tracking_recommendation_ar']] = agg.apply(lambda r: pd.Series(tracking_diagnostics(r)), axis=1)
    agg['growth_recommendation_ar'] = agg.apply(growth_recommendation, axis=1)
    return agg.sort_values(['today_action','score'], ascending=[True, False])


def show_table(title, help_text, data, cols, name_col=None):
    st.markdown(f'<div class="table-title">{title}</div><div class="help-text">{help_text}</div>', unsafe_allow_html=True)
    existing_cols = [c for c in cols if c in data.columns]
    table_df = data[existing_cols].copy()
    if name_col and name_col in table_df.columns:
        table_df = table_df.set_index(name_col)
    st.dataframe(table_df, use_container_width=True)


def show_growth_center(df):
    if df.empty: return
    st.markdown('<div class="table-title">Growth Command Center</div><div class="help-text">ابدأ من هنا. دي أهم الحاجات اللي تعملها عشان تعلي النتائج.</div>', unsafe_allow_html=True)
    scale = df[df['today_action'] == 'SCALE 15-20%'].head(1)
    pause = df[df['today_action'] == 'PAUSE TODAY'].head(1)
    fix = df[df['growth_priority'].astype(str).str.contains('Fix', na=False)].head(1)
    cols = st.columns(3)
    for col, title, subset, cls in [(cols[0], 'Scale Now', scale, 'alert-good'), (cols[1], 'Fix First', fix, 'alert-info'), (cols[2], 'Pause / Cut', pause, 'alert-hot')]:
        if subset.empty:
            col.markdown(f'<div class="os-card {cls}"><h4>{title}</h4><div>No urgent item.</div></div>', unsafe_allow_html=True)
        else:
            r = subset.iloc[0]
            name = r.get('campaign_name') or r.get('adset_name') or r.get('ad_name')
            col.markdown(f'<div class="os-card {cls}"><h4>{title}</h4><div><b>{name}</b></div><div>{r.get("growth_recommendation_ar")}</div></div>', unsafe_allow_html=True)


def show_alerts(df):
    if df.empty: return
    pause_count = int((df['today_action'] == 'PAUSE TODAY').sum()); scale_count = int((df['today_action'] == 'SCALE 15-20%').sum()); fix_count = int(df['growth_priority'].astype(str).str.contains('Fix', na=False).sum())
    a,b,c = st.columns(3)
    a.markdown(f'<div class="os-card alert-hot"><h4>Kill Switch Alerts</h4><div>{pause_count} items need pause review today.</div></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="os-card alert-good"><h4>Scale Opportunities</h4><div>{scale_count} items can be scaled carefully.</div></div>', unsafe_allow_html=True)
    c.markdown(f'<div class="os-card alert-info"><h4>Tracking / Funnel Fixes</h4><div>{fix_count} items need funnel or tracking work.</div></div>', unsafe_allow_html=True)


def show_budget_simulator(row):
    current_spend = safe_num(row.get('spend')); roas = safe_num(row.get('manual_roas'))
    st.markdown('<div class="table-title">Budget Simulator</div><div class="help-text">Estimate impact before changing budget.</div>', unsafe_allow_html=True)
    pct = st.slider('Budget change %', -50, 100, 20, 5)
    new_spend = current_spend * (1 + pct / 100); est_revenue = new_spend * roas
    a,b,c = st.columns(3)
    a.metric('Estimated spend', format_money(new_spend)); b.metric('Estimated revenue', format_money(est_revenue)); c.metric('Current ROAS assumption', roas)

st.markdown('''<div class="smart-hero"><div class="hero-copy"><span class="badge">Orange Performance OS</span><h1>Turn messy ad numbers into clear daily moves.</h1><p class="hero-sub">One dashboard to decide what to scale, cut, pause, reopen, and refresh across campaigns, ad sets, and ads.</p><div class="hero-tov">From data chaos to media buying clarity.</div></div><div class="counter-wrap"><div class="counter-orb"><div class="counter-number"></div><div class="counter-label">Decision Score</div></div></div></div>''', unsafe_allow_html=True)

try:
    ad_accounts = fetch_business_ad_accounts()
except Exception as e:
    ad_accounts = []
    st.error(f'Could not load ad accounts: {e}')

if ad_accounts:
    account_labels = [f"{a.get('name')} — {a.get('id')}" for a in ad_accounts]
    selected_label = st.selectbox('Select Ad Account', account_labels)
    selected_account = ad_accounts[account_labels.index(selected_label)]
    selected_account_id = selected_account.get('id'); selected_account_name = selected_account.get('name')
    st.markdown(f'<div class="os-card"><h4>Selected Ad Account</h4><div>{selected_account_name} — {selected_account_id}</div></div>', unsafe_allow_html=True)
else:
    selected_account_id = None; selected_account_name = None
    st.warning('No ad accounts found. Check META_BUSINESS_ID, token permissions, and system user assets.')

fetch_window_choice = st.selectbox('Fetch window from Meta', ['All saved windows','Today','Last 3 Days','Last 7 Days','This Month','Last Month','This Year','Specific Month'])
fetch_specific_month = None
if fetch_window_choice == 'Specific Month':
    fetch_specific_month = st.selectbox('Select Month to Fetch', MONTHS)

if st.button('Fetch Latest Meta Data'):
    try:
        selected_window = None
        if fetch_window_choice == 'Today': selected_window = 'TODAY'
        elif fetch_window_choice == 'Last 3 Days': selected_window = '3D'
        elif fetch_window_choice == 'Last 7 Days': selected_window = '7D'
        elif fetch_window_choice == 'This Month': selected_window = '30D'
        elif fetch_window_choice == 'Last Month': selected_window = 'LAST_MONTH'
        elif fetch_window_choice == 'This Year': selected_window = 'THIS_YEAR'
        elif fetch_window_choice == 'Specific Month': selected_window = MONTH_WINDOW_MAP.get(fetch_specific_month)
        df_live = fetch_meta_ads_report(selected_account_id, selected_account_name, selected_window=selected_window)
        if df_live is None or df_live.empty:
            st.warning(f'No Meta data returned for {selected_account_name or selected_account_id}. Try another time window or account.')
        else:
            df_live.to_csv('meta_ads_report.csv', index=False)
            st.success(f'Meta data updated successfully for {selected_account_name or selected_account_id}.')
    except Exception as e:
        st.error(f'Error fetching Meta data: {e}')

try:
    try:
        df = pd.read_csv('meta_ads_report.csv')
    except (EmptyDataError, ParserError):
        st.warning('The saved report is empty or corrupted. Click Fetch Latest Meta Data again for the selected ad account.')
        st.stop()
    if df.empty:
        st.warning('No data saved yet. Click Fetch Latest Meta Data for the selected ad account.')
        st.stop()
    if selected_account_id and 'account_id' in df.columns:
        df = df[df['account_id'] == selected_account_id]
    if df.empty:
        st.warning('No saved data for this selected ad account. Click Fetch Latest Meta Data.')
        st.stop()
    if 'window' not in df.columns:
        df['window'] = 'TODAY'
    df['window'] = df['window'].fillna('TODAY').replace({'MTD':'30D','this_month':'30D', 'None':'TODAY'})
    for col in ['spend','ctr','cpc','cpm','frequency','roas','purchases','cost_per_purchase','purchase_value','aov','add_to_cart','initiate_checkout','purchase_rate','lpv_rate','atc_rate','manual_roas','meta_roas','clicks','impressions','landing_page_view','view_content']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        else:
            df[col] = 0
    window_choice = st.segmented_control('Time window', ['Today','Last 3 Days','Last 7 Days','This Month','Last Month','This Year','Specific Month'], default='Today')
    report_specific_month = None
    if window_choice == 'Specific Month':
        report_specific_month = st.selectbox('Report Month', MONTHS, key='report_month')
    window_map = {'Today':'TODAY','Last 3 Days':'3D','Last 7 Days':'7D','This Month':'30D','Last Month':'LAST_MONTH','This Year':'THIS_YEAR'}
    selected_window_value = MONTH_WINDOW_MAP.get(report_specific_month) if window_choice == 'Specific Month' else window_map.get(window_choice, 'TODAY')
    window_df = df[df['window'] == selected_window_value].copy()
    if window_df.empty:
        st.warning('No data available for this window. Fetch this window first or try another account.')
    else:
        total_spend = window_df['spend'].sum()
        total_revenue = window_df['purchase_value'].sum()
        estimated_recharge = total_spend / TAX_NET_RATE if total_spend else 0
        estimated_tax_fees = estimated_recharge - total_spend
        overall_roas = round(total_revenue / total_spend, 2) if total_spend else 0
        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric('Real Ad Spend', format_money(total_spend))
        c2.metric('Estimated Recharge', format_money(estimated_recharge))
        c3.metric('Tax / Fawry Fees', format_money(estimated_tax_fees))
        c4.metric('Purchase Value', format_money(total_revenue))
        c5.metric('Purchase ROAS', overall_roas)
        c6.metric('Website Purchases', int(window_df['purchases'].sum()))
        st.caption('Real Ad Spend is Meta Amount Spent. Estimated Recharge = Real Ad Spend / 0.86. AI decisions use Real Ad Spend.')
        level_choice = st.segmented_control('Level', ['Campaigns','Ad Sets','Ads'], default='Campaigns')
        level = {'Campaigns':'campaign','Ad Sets':'adset','Ads':'ad'}[level_choice]
        level_df = aggregate_level(window_df, level, overall_roas)
        if level_df.empty:
            st.warning('No grouped data available for this level.')
            st.stop()
        show_growth_center(level_df); show_alerts(level_df)
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        view_choice = st.segmented_control('View', ['Growth Recommendations','Tracking Diagnostics','All','Active Only','Scale','Watch','Test/Fix','Kill/Pause','Reopen','Creative Fixes','Today Actions','Charts'], default='Growth Recommendations')
        col_a,col_b,col_c,col_d = st.columns(4)
        min_score = col_a.slider('Min score', 0, 100, 0, 5)
        min_roas = col_b.number_input('Min ROAS', min_value=0.0, value=0.0, step=0.5)
        action_filter = col_c.multiselect('Today action', sorted(level_df['today_action'].dropna().unique().tolist()), default=[])
        search = col_d.text_input('Search')
        st.markdown('</div>', unsafe_allow_html=True)
        filtered = level_df[(level_df['score'] >= min_score) & (level_df['manual_roas'] >= min_roas)].copy()
        name_col = {'campaign':'campaign_name','adset':'adset_name','ad':'ad_name'}[level]
        active_col = {'campaign':'campaign_effective_status','adset':'adset_effective_status','ad':'ad_effective_status'}[level]
        if action_filter:
            filtered = filtered[filtered['today_action'].isin(action_filter)]
        if search:
            filtered = filtered[filtered[name_col].astype(str).str.contains(search, case=False, na=False)]
        if view_choice == 'Active Only': filtered = filtered[filtered[active_col] == 'ACTIVE']
        elif view_choice in ['Scale','Watch','Test/Fix','Kill/Pause']: filtered = filtered[filtered['status'] == view_choice]
        elif view_choice == 'Reopen': filtered = filtered[filtered['reopen_signal'] == 'YES']
        elif view_choice == 'Creative Fixes': filtered = filtered[filtered['creative_issue'] != 'No major creative issue']
        elif view_choice == 'Today Actions': filtered = filtered[filtered['today_action'] != 'WATCH']
        elif view_choice == 'Tracking Diagnostics': filtered = filtered.sort_values('tracking_health_score')
        elif view_choice == 'Growth Recommendations': filtered = filtered[filtered['growth_priority'] != 'Scale/Watch'].copy()
        base_cols = {'campaign':['campaign_name','campaign_effective_status'],'adset':['campaign_name','adset_name','adset_effective_status'],'ad':['campaign_name','adset_name','ad_name','ad_effective_status']}[level]
        decision_cols = base_cols + ['score','tracking_health_score','growth_priority','growth_recommendation_ar','funnel_leak_stage','tracking_recommendation_ar','status','today_action','today_reason','next_action','creative_issue','creative_fix','reopen_signal','why','spend','purchase_value','manual_roas','purchases','cost_per_purchase','ctr','frequency','landing_page_view','add_to_cart','initiate_checkout']
        if view_choice == 'Charts':
            chart_df = level_df.copy().head(15)
            label = 'campaign_name' if 'campaign_name' in chart_df.columns else chart_df.columns[0]
            chart_df = chart_df.set_index(label)
            st.bar_chart(chart_df[['spend','purchase_value','manual_roas','score','tracking_health_score']])
        else:
            show_table(f'{window_choice} — {level_choice} {view_choice}', 'الاسم متثبت كـ index عشان يفضل ظاهر وانت بتسكرول أفقياً.', filtered, decision_cols, name_col=name_col)
        if not filtered.empty:
            selected_item = st.selectbox('Select item for action card', filtered[name_col].dropna().tolist())
            selected_row = filtered[filtered[name_col] == selected_item].iloc[0]
            hooks, captions, visuals, testing_plan, scaling_plan = generate_content_pack(selected_row)
            st.markdown(f'''<div class="action-card"><h3>{selected_item}</h3><div class="action-grid"><div class="action-box"><div class="action-label">Score</div>{selected_row.get('score')}</div><div class="action-box"><div class="action-label">Tracking Health</div>{selected_row.get('tracking_health_score')}</div><div class="action-box"><div class="action-label">Growth Priority</div>{selected_row.get('growth_priority')}</div><div class="action-box"><div class="action-label">Today action</div>{selected_row.get('today_action')}</div><div class="action-box"><div class="action-label">Funnel Leak</div>{selected_row.get('funnel_leak_stage')}</div><div class="action-box"><div class="action-label">Creative issue</div>{selected_row.get('creative_issue')}</div></div></div>''', unsafe_allow_html=True)
            st.markdown(f'<div class="os-card"><h4>What to do to improve results</h4><div>{selected_row.get("growth_recommendation_ar")}</div><br><div>{selected_row.get("tracking_recommendation_ar")}</div></div>', unsafe_allow_html=True)
            action_tabs = st.tabs(['Hooks', 'Captions', 'Visual Directions', 'Testing Roadmap', 'Scaling Roadmap', 'Budget Simulator'])
            for tab, items in zip(action_tabs[:5], [hooks, captions, visuals, testing_plan, scaling_plan]):
                with tab:
                    for item in items: st.write(f'• {item}')
            with action_tabs[5]: show_budget_simulator(selected_row)
            export_cols = [c for c in decision_cols if c in filtered.columns]
            st.download_button('Export filtered action plan CSV', filtered[export_cols].to_csv(index=True), 'action_plan.csv', 'text/csv')
except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the report for the selected ad account.')
