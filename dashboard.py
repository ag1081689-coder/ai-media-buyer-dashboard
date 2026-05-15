import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.markdown('''
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"], .stApp {background:#050505 !important; color:#ffffff !important;}
[data-testid="stSidebar"] {background:#080808 !important;}
.block-container {padding-top:1.2rem; padding-bottom:4rem; max-width:1550px; background:#050505 !important;}
* {color:#ffffff;}
p, span, label, div {color:#ffffff;}
.smart-hero {background:linear-gradient(135deg,#0b0b0b,#160d04); border:1px solid rgba(255,122,0,.45); border-radius:16px; padding:20px 24px; margin-bottom:16px; box-shadow:0 18px 55px rgba(0,0,0,.6);}
.smart-hero h1 {font-size:32px; margin:0; color:#ffffff !important;}
.smart-hero p {color:#f5f5f5 !important; font-size:15px; margin:8px 0 0;}
.badge {display:inline-block; padding:6px 10px; border-radius:999px; background:rgba(255,122,0,.18); color:#ff9f1c !important; font-weight:900; font-size:12px; margin-bottom:10px; border:1px solid rgba(255,122,0,.45);}
[data-testid="stMetric"] {background:#0f0f0f; border:1px solid rgba(255,122,0,.35); border-radius:14px; padding:14px 16px; box-shadow:0 14px 45px rgba(0,0,0,.45);}
[data-testid="stMetricLabel"] {color:#ffffff !important; font-size:13px;}
[data-testid="stMetricValue"] {color:#ff9f1c !important; font-size:27px;}
.stButton button {border-radius:10px; background:linear-gradient(135deg,#ff7a00,#ff9f1c) !important; color:#050505 !important; border:0; font-weight:900; padding:.62rem .95rem;}
.stButton button:hover {background:#ffb347 !important; color:#050505 !important;}
[data-testid="stDataFrame"] {background:#0f0f0f; border-radius:14px; border:1px solid rgba(255,122,0,.3); box-shadow:0 18px 55px rgba(0,0,0,.45); overflow:hidden;}
.table-title {font-size:21px; font-weight:900; color:#ff9f1c !important; margin:20px 0 6px;}
.help-text {font-size:14px; color:#ffffff !important; margin-bottom:12px;}
.filter-card {background:#0f0f0f; border:1px solid rgba(255,122,0,.35); border-radius:14px; padding:14px 16px; margin:12px 0 16px; box-shadow:0 12px 40px rgba(0,0,0,.45);}
.action-card {background:#0f0f0f; border:1px solid rgba(255,122,0,.35); border-left:5px solid #ff7a00; border-radius:14px; padding:18px 20px; margin:18px 0; box-shadow:0 18px 55px rgba(0,0,0,.45);}
.action-card h3 {margin:0 0 8px 0; color:#ffffff !important;}
.action-grid {display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap:12px; margin-top:12px;}
.action-box {background:#181818; border:1px solid rgba(255,122,0,.25); border-radius:12px; padding:12px; color:#ffffff !important;}
.action-label {font-size:12px; color:#ff9f1c !important; font-weight:900; text-transform:uppercase; margin-bottom:4px;}
.stSegmentedControl button, [data-baseweb="tab"] {color:#ffffff !important;}
input, textarea, select {background:#111111 !important; color:#ffffff !important; border-color:#ff7a00 !important;}
</style>
''', unsafe_allow_html=True)


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
    ctr = safe_num(row.get('ctr'))
    freq = safe_num(row.get('frequency'))
    roas = safe_num(row.get('manual_roas'))
    purchases = safe_num(row.get('purchases'))
    cpp = safe_num(row.get('cost_per_purchase'))
    issues = []
    fixes = []

    if ctr < 1:
        issues.append('Hook issue')
        fixes.append('اعمل 5 هووكس جديدة: مشكلة مباشرة، صدمة سعر، إثبات اجتماعي، مقارنة، وافتتاحية UGC.')
    if freq > 3.5 and roas < 4:
        issues.append('Visual fatigue')
        fixes.append('غير الفيجوال: Thumbnail جديد، أول فريم مختلف، زاوية تصوير جديدة، ووش UGC جديد.')
    if purchases > 0 and cpp > 300:
        issues.append('Offer or caption issue')
        fixes.append('اكتب كابشن جديد يوضح القيمة، العرض، ضمانات الدفع أو التوصيل، وCTA واضح.')
    if roas >= 5 and purchases >= 10:
        issues.append('Winning angle')
        fixes.append('اعمل 3 نسخ جديدة من نفس الزاوية الكسبانة وشغلهم في تست Scaling محسوب.')
    if not issues:
        issues.append('No major creative issue')
        fixes.append('راقب فقط. متغيرش الإعلان الكسبان غير لو Frequency زاد أو ROAS بدأ ينزل.')
    return ', '.join(issues), ' | '.join(fixes)


def generate_content_pack(row):
    issue = str(row.get('creative_issue', ''))
    hooks = [
        'لسه بتقارن؟ ابدأ بالاختيار اللي العملاء بيرجعوله كل مرة.',
        'قبل ما تشتري، شوف ليه العرض ده واخد اهتمام.',
        'الترقية البسيطة اللي كانت ناقصة طلبك.',
        'وقف هنا لو عايز قيمة أعلى من غير ما تدفع زيادة.',
        'المنتج اللي الناس بتطلبه أكتر من مرة.'
    ]
    captions = [
        'اختيار معمول للناس اللي عايزة قيمة واضحة وتجربة شراء سهلة وسريعة. اطلب دلوقتي قبل انتهاء العرض.',
        'عرض واضح، قيمة قوية، وقرار شراء أسهل. شوف التفاصيل وكمل طلبك النهارده.',
        'العملاء بيختاروه لسبب. قارن القيمة، شوف المميزات، واطلب بثقة.'
    ]
    visuals = [
        'افتتاحية UGC بوش شخص ماسك المنتج في أول ثانيتين.',
        'لقطة قريبة للمنتج مع Overlay للسعر أو الميزة الأساسية.',
        'قبل/بعد أو مشكلة/حل مع Cuts سريعة في أول 3 ثواني.',
        'فيجوال إثبات اجتماعي: Reviews أو Orders أو Reaction من عميل.'
    ]
    testing = [
        'اختبر 3 هووكس على نفس الفيجوال الكسبان عشان تعزل تأثير الهووك.',
        'شغل 2 UGC و2 Static في ABO بميزانية متساوية.',
        'اقفل أي Creative أقل من 1% CTR بعد صرف كافي، وسيب اللي CPA وROAS بتاعه ثابت.',
        'متغيرش الجمهور والكرياتيف في نفس الوقت.'
    ]
    scaling = [
        'لو ROAS ثابت 48 ساعة، زود الميزانية 15-20%.',
        'لو المبيعات ثابتة، اعمل Duplicate للـ Ad Set الكسبان داخل CBO Scaling Campaign.',
        'قبل ما تزود الصرف بقوة، اعمل 3 Variations من نفس الزاوية الكسبانة.',
        'وقف السكيل لو CPA زاد فجأة أو ROAS نزل تحت التارجت يومين ورا بعض.'
    ]
    if 'Hook issue' in issue:
        hooks = ['غالبًا بتدفع زيادة من غير ما تاخد بالك.','الغلط اللي أغلب الناس بتعمله قبل ما تشتري.','جربته عشان أنت ماتحتارش.','ده اللي هختاره لو بدور على أعلى قيمة مقابل السعر.','متشتريش قبل ما تشوف النقطة دي.']
    if 'Visual fatigue' in issue:
        visuals = ['غير أول فريم بالكامل: خلفية جديدة، حركة إيد جديدة، وزاوية منتج مختلفة.','استخدم Creator جديد بنفس العرض لكن بافتتاحية مختلفة.','حوّل من Static لـ UGC أو من UGC لـ Product Demo نظيف.','ضيف حركة في أول ثانية: دخول المنتج في الكادر، Reveal سريع، أو مقارنة مباشرة.']
    if 'Offer or caption issue' in issue:
        captions = ['خد قيمة أعلى من غير تعقيد في الطلب. مميزات واضحة، Checkout سهل، وتوصيل سريع.','العرض ده معمول للي عايز يشتري بذكاء، مش يشتري أي منتج وخلاص.','قارن القيمة، شوف المميزات، واطلب قبل ما العرض يخلص.']
    return hooks, captions, visuals, testing, scaling


def score_campaign(row, overall_roas):
    score = 0
    reasons = []
    roas = safe_num(row.get('manual_roas'))
    spend = safe_num(row.get('spend'))
    purchases = safe_num(row.get('purchases'))
    ctr = safe_num(row.get('ctr'))
    frequency = safe_num(row.get('frequency'))
    cpp = safe_num(row.get('cost_per_purchase'))
    campaign_status = str(row.get('campaign_effective_status', ''))
    if roas >= overall_roas * 1.2 and purchases >= 5:
        score += 35; reasons.append('ROAS above account average')
    elif roas >= overall_roas and purchases >= 3:
        score += 25; reasons.append('ROAS around or above average')
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
        score -= 10; reasons.append('Possible creative fatigue')
    if cpp and cpp <= 250:
        score += 15; reasons.append('Good cost per purchase')
    elif cpp and cpp <= 400:
        score += 7; reasons.append('Average cost per purchase')
    elif cpp:
        score -= 10; reasons.append('High cost per purchase')
    if spend < 500:
        score = min(score, 45); reasons.append('Low spend, decision not confirmed')
    score = max(0, min(100, round(score)))
    if score >= 80:
        status = 'Scale'; action = 'Scale carefully: raise budget 15-20% or duplicate into CBO.'
    elif score >= 60:
        status = 'Watch'; action = 'Keep it running. Review again in 24-48 hours.'
    elif score >= 40:
        status = 'Test/Fix'; action = 'Test new hooks, captions, or visuals before scaling.'
    else:
        status = 'Kill/Pause'; action = 'Reduce budget or pause if spend is enough.'
    reopen = 'No'
    if campaign_status != 'ACTIVE' and score >= 70:
        reopen = 'YES'; action = 'This campaign is off but has strong past data. Reopen with a controlled test budget.'
    if campaign_status == 'ACTIVE' and score < 35:
        action = 'Active but weak. Review immediately or pause.'
    return score, status, action, reopen, ' | '.join(reasons[:4])


def show_table(title, help_text, data, cols):
    st.markdown(f'<div class="table-title">{title}</div><div class="help-text">{help_text}</div>', unsafe_allow_html=True)
    existing_cols = [c for c in cols if c in data.columns]
    st.dataframe(data[existing_cols], use_container_width=True, hide_index=True)


st.markdown('''
<div class="smart-hero">
  <span class="badge">Orange Performance OS</span>
  <h1>AI Media Buyer Dashboard</h1>
  <p>Black and orange decision workspace for campaign scoring, creative fixes, testing plans, and scaling actions.</p>
</div>
''', unsafe_allow_html=True)

if st.button('Fetch Latest Meta Data'):
    try:
        df_live = fetch_meta_ads_report()
        df_live.to_csv('meta_ads_report.csv', index=False)
        st.success('Meta data updated successfully.')
    except Exception as e:
        st.error(f'Error fetching Meta data: {e}')

try:
    df = pd.read_csv('meta_ads_report.csv')
    if 'window' in df.columns:
        df['window'] = df['window'].replace({'MTD': '30D', 'this_month': '30D'})
    numeric_cols = ['spend','ctr','cpc','cpm','frequency','roas','purchases','cost_per_purchase','purchase_value','aov','add_to_cart','initiate_checkout','purchase_rate','lpv_rate','atc_rate','manual_roas','meta_roas']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    window_choice = st.segmented_control('Time window', ['Last 3 Days', 'Last 7 Days', 'This Month'], default='This Month')
    window_map = {'Last 3 Days': '3D', 'Last 7 Days': '7D', 'This Month': '30D'}
    window_df = df[df['window'] == window_map[window_choice]].copy()
    if window_df.empty:
        st.warning('No data available.')
    else:
        total_spend = window_df['spend'].sum()
        total_revenue = window_df['purchase_value'].sum()
        overall_roas = round(total_revenue / total_spend, 2) if total_spend else 0
        c1, c2, c3, c4 = st.columns(4)
        c1.metric('Amount spent', format_money(total_spend))
        c2.metric('Purchase value', format_money(total_revenue))
        c3.metric('Purchase ROAS', overall_roas)
        c4.metric('Website purchases', int(window_df['purchases'].sum()))
        campaign_df = window_df.groupby(['campaign_name', 'campaign_status', 'campaign_effective_status'], as_index=False).agg({'spend': 'sum','purchase_value': 'sum','purchases': 'sum','clicks': 'sum','impressions': 'sum','frequency': 'mean','cost_per_purchase': 'mean'})
        campaign_df['manual_roas'] = campaign_df.apply(lambda r: round(r['purchase_value'] / r['spend'], 2) if r['spend'] else 0, axis=1)
        campaign_df['ctr'] = campaign_df.apply(lambda r: round((r['clicks'] / r['impressions']) * 100, 2) if r['impressions'] else 0, axis=1)
        scored_rows = campaign_df.apply(lambda r: score_campaign(r, overall_roas), axis=1, result_type='expand')
        campaign_df[['score', 'status', 'next_action', 'reopen_signal', 'why']] = scored_rows
        campaign_df[['creative_issue', 'creative_fix']] = campaign_df.apply(lambda r: pd.Series(get_creative_diagnosis(r)), axis=1)
        campaign_df = campaign_df.sort_values('score', ascending=False)
        st.markdown('<div class="filter-card">', unsafe_allow_html=True)
        view_choice = st.segmented_control('View', ['All Campaigns', 'Active Only', 'Scale', 'Watch', 'Test/Fix', 'Kill/Pause', 'Reopen', 'Creative Fixes', 'Ad Level'], default='All Campaigns')
        col_a, col_b, col_c, col_d = st.columns(4)
        min_score = col_a.slider('Min score', 0, 100, 0, 5)
        status_filter = col_b.multiselect('Campaign status', sorted(campaign_df['campaign_effective_status'].dropna().unique().tolist()), default=[])
        min_roas = col_c.number_input('Min ROAS', min_value=0.0, value=0.0, step=0.5)
        search = col_d.text_input('Search campaign')
        st.markdown('</div>', unsafe_allow_html=True)
        filtered = campaign_df.copy()
        filtered = filtered[filtered['score'] >= min_score]
        filtered = filtered[filtered['manual_roas'] >= min_roas]
        if status_filter:
            filtered = filtered[filtered['campaign_effective_status'].isin(status_filter)]
        if search:
            filtered = filtered[filtered['campaign_name'].str.contains(search, case=False, na=False)]
        if view_choice == 'Active Only':
            filtered = filtered[filtered['campaign_effective_status'] == 'ACTIVE']
        elif view_choice in ['Scale', 'Watch', 'Test/Fix', 'Kill/Pause']:
            filtered = filtered[filtered['status'] == view_choice]
        elif view_choice == 'Reopen':
            filtered = filtered[filtered['reopen_signal'] == 'YES']
        elif view_choice == 'Creative Fixes':
            filtered = filtered[filtered['creative_issue'] != 'No major creative issue']
        score_cols = ['campaign_name','campaign_effective_status','score','status','next_action','creative_issue','creative_fix','reopen_signal','why','spend','purchase_value','manual_roas','purchases','cost_per_purchase','ctr','frequency']
        if view_choice == 'Ad Level':
            ad_filtered = window_df.copy()
            if search:
                ad_filtered = ad_filtered[ad_filtered['campaign_name'].str.contains(search, case=False, na=False)]
            display_cols = ['campaign_name','adset_name','ad_name','spend','purchase_value','manual_roas','meta_roas','ctr','cpc','frequency','purchases','cost_per_purchase','atc_rate','purchase_rate']
            show_table('Ad Level Performance', 'Use this when you want to inspect specific ad sets or ads.', ad_filtered, display_cols)
        else:
            show_table(view_choice, 'Filtered campaign decision table. Change the filters above to narrow the view.', filtered, score_cols)
            if not filtered.empty:
                selected_campaign = st.selectbox('Select campaign for action card', filtered['campaign_name'].tolist())
                selected_row = filtered[filtered['campaign_name'] == selected_campaign].iloc[0]
                hooks, captions, visuals, testing_plan, scaling_plan = generate_content_pack(selected_row)
                st.markdown(f'''
                <div class="action-card">
                  <h3>{selected_campaign}</h3>
                  <div class="action-grid">
                    <div class="action-box"><div class="action-label">Score</div>{selected_row.get('score')}</div>
                    <div class="action-box"><div class="action-label">Status</div>{selected_row.get('status')}</div>
                    <div class="action-box"><div class="action-label">Next action</div>{selected_row.get('next_action')}</div>
                    <div class="action-box"><div class="action-label">Creative issue</div>{selected_row.get('creative_issue')}</div>
                  </div>
                </div>
                ''', unsafe_allow_html=True)
                action_tabs = st.tabs(['Hooks', 'Captions', 'Visual Directions', 'Testing Roadmap', 'Scaling Roadmap'])
                with action_tabs[0]:
                    for item in hooks:
                        st.write(f'• {item}')
                with action_tabs[1]:
                    for item in captions:
                        st.write(f'• {item}')
                with action_tabs[2]:
                    for item in visuals:
                        st.write(f'• {item}')
                with action_tabs[3]:
                    for item in testing_plan:
                        st.write(f'• {item}')
                with action_tabs[4]:
                    for item in scaling_plan:
                        st.write(f'• {item}')
                export_df = filtered[score_cols].copy()
                st.download_button('Export filtered action plan CSV', export_df.to_csv(index=False), 'action_plan.csv', 'text/csv')
except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
