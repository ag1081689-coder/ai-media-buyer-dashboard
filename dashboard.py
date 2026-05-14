import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.markdown('''
<style>
.stApp {background: radial-gradient(circle at top left, #172554 0, #050816 38%, #030712 100%); color: #f8fafc;}
.block-container {padding-top: 2rem; padding-bottom: 4rem; max-width: 1500px;}
[data-testid="stMetric"] {background: rgba(15, 23, 42, 0.78); border: 1px solid rgba(148, 163, 184, .18); border-radius: 22px; padding: 18px 20px; box-shadow: 0 22px 70px rgba(0,0,0,.22); animation: fadeUp .55s ease both;}
[data-testid="stMetricLabel"] {color: #94a3b8;}
[data-testid="stMetricValue"] {font-size: 34px; color: #ffffff;}
.stButton button {border-radius: 14px; border: 1px solid rgba(59,130,246,.55); background: linear-gradient(135deg,#2563eb,#7c3aed); color: white; padding: .7rem 1.1rem; font-weight: 700; box-shadow: 0 14px 40px rgba(37,99,235,.25);}
.stButton button:hover {transform: translateY(-1px); border: 1px solid #93c5fd;}
[data-testid="stDataFrame"] {border-radius: 18px; overflow: hidden; border: 1px solid rgba(148,163,184,.16); box-shadow: 0 24px 70px rgba(0,0,0,.2);}
.smart-hero {position: relative; border: 1px solid rgba(148,163,184,.18); border-radius: 30px; padding: 34px; margin-bottom: 24px; background: linear-gradient(135deg, rgba(15,23,42,.95), rgba(30,41,59,.75)); box-shadow: 0 30px 90px rgba(0,0,0,.35); overflow: hidden; animation: fadeUp .5s ease both;}
.smart-hero:before {content: ''; position: absolute; width: 420px; height: 420px; right: -130px; top: -170px; background: radial-gradient(circle, rgba(59,130,246,.45), transparent 62%); filter: blur(10px); animation: pulse 5s infinite ease-in-out;}
.smart-hero h1 {font-size: 54px; line-height: 1.02; margin: 0; letter-spacing: -1.8px;}
.smart-hero p {color: #cbd5e1; font-size: 17px; max-width: 760px;}
.badge {display:inline-block; padding: 8px 12px; border-radius: 999px; background: rgba(37,99,235,.18); color:#bfdbfe; border:1px solid rgba(96,165,250,.25); font-size:13px; margin-bottom:14px;}
.section-card {background: rgba(15,23,42,.68); border: 1px solid rgba(148,163,184,.16); border-radius: 24px; padding: 22px; margin: 18px 0; box-shadow: 0 20px 70px rgba(0,0,0,.22); animation: fadeUp .6s ease both;}
.meta-table-title {display:flex; align-items:center; gap:10px; font-size:24px; font-weight:800; margin: 12px 0 14px;}
.status-pill {padding:5px 10px; border-radius:999px; font-weight:700; font-size:12px;}
@keyframes fadeUp {from {opacity:0; transform: translateY(12px);} to {opacity:1; transform: translateY(0);}}
@keyframes pulse {0%,100% {transform: scale(1); opacity:.7;} 50% {transform: scale(1.14); opacity:1;}}
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
        score += 35; reasons.append('ROAS أعلى من متوسط الحساب')
    elif roas >= overall_roas and purchases >= 3:
        score += 25; reasons.append('ROAS قريب أو أعلى من المتوسط')
    elif roas > 0:
        score += 10; reasons.append('ROAS ضعيف مقارنة بالمتوسط')
    if purchases >= 20:
        score += 25; reasons.append('حجم مبيعات قوي')
    elif purchases >= 5:
        score += 15; reasons.append('فيه مبيعات كفاية للحكم')
    elif purchases > 0:
        score += 5; reasons.append('مبيعات قليلة')
    if ctr >= 2:
        score += 15; reasons.append('CTR قوي')
    elif ctr >= 1:
        score += 8; reasons.append('CTR مقبول')
    else:
        reasons.append('CTR محتاج تحسين')
    if frequency <= 2.5:
        score += 10; reasons.append('Frequency صحي')
    elif frequency <= 4:
        score += 4; reasons.append('Frequency بدأ يعلى')
    else:
        score -= 10; reasons.append('Creative fatigue محتمل')
    if cpp and cpp <= 250:
        score += 15; reasons.append('Cost per purchase جيد')
    elif cpp and cpp <= 400:
        score += 7; reasons.append('Cost per purchase متوسط')
    elif cpp:
        score -= 10; reasons.append('Cost per purchase عالي')
    if spend < 500:
        score = min(score, 45); reasons.append('الصرف قليل، القرار غير مؤكد')

    score = max(0, min(100, round(score)))
    if score >= 80:
        status = 'Scale'; action = 'افتحها وادرس السكيل. زود ميزانية تدريجي أو دوبليكيت CBO.'
    elif score >= 60:
        status = 'Watch'; action = 'كويسة. راقبها 24-48 ساعة وشوف الثبات.'
    elif score >= 40:
        status = 'Test/Fix'; action = 'محتاجة تستينج. جرب هووكس أو أوفر أو كرياتيف جديد.'
    else:
        status = 'Kill/Pause'; action = 'ضعيفة. قلل الصرف أو وقفها لو الصرف كافي.'

    reopen = 'No'
    if campaign_status != 'ACTIVE' and score >= 70:
        reopen = 'YES - Reopen This Campaign'; action = 'الكامبين مقفولة لكن أرقامها قوية. افتحها تاني واختبرها.'
    if campaign_status == 'ACTIVE' and score < 35:
        action = 'الكامبين شغالة لكن ضعيفة. راجعها فوراً أو وقفها.'
    return score, status, action, reopen, ' | '.join(reasons[:4])


st.markdown('''
<div class="smart-hero">
  <span class="badge">AI Performance Command Center</span>
  <h1>AI Media Buyer Dashboard</h1>
  <p>Meta-style performance control room for ecommerce. Score campaigns, detect weak active spend, find reopen opportunities, and plan testing or scaling actions faster.</p>
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

    tabs = st.tabs(['Last 3 Days', 'Last 7 Days', 'This Month'])
    window_map = {'Last 3 Days': '3D', 'Last 7 Days': '7D', 'This Month': '30D'}

    for tab_name, tab in zip(window_map.keys(), tabs):
        with tab:
            window_df = df[df['window'] == window_map[tab_name]].copy()
            if window_df.empty:
                st.warning('No data available.')
                continue
            total_spend = window_df['spend'].sum()
            total_revenue = window_df['purchase_value'].sum()
            overall_roas = round(total_revenue / total_spend, 2) if total_spend else 0

            c1, c2, c3, c4 = st.columns(4)
            c1.metric('Amount Spent', format_money(total_spend))
            c2.metric('Purchase Value', format_money(total_revenue))
            c3.metric('Purchase ROAS', overall_roas)
            c4.metric('Website Purchases', int(window_df['purchases'].sum()))

            campaign_df = window_df.groupby(['campaign_name', 'campaign_status', 'campaign_effective_status'], as_index=False).agg({'spend': 'sum','purchase_value': 'sum','purchases': 'sum','clicks': 'sum','impressions': 'sum','frequency': 'mean','cost_per_purchase': 'mean'})
            campaign_df['manual_roas'] = campaign_df.apply(lambda r: round(r['purchase_value'] / r['spend'], 2) if r['spend'] else 0, axis=1)
            campaign_df['ctr'] = campaign_df.apply(lambda r: round((r['clicks'] / r['impressions']) * 100, 2) if r['impressions'] else 0, axis=1)
            scored_rows = campaign_df.apply(lambda r: score_campaign(r, overall_roas), axis=1, result_type='expand')
            campaign_df[['score', 'status', 'next_action', 'reopen_signal', 'why']] = scored_rows
            campaign_df = campaign_df.sort_values('score', ascending=False)

            score_cols = ['campaign_name','campaign_effective_status','score','status','reopen_signal','next_action','why','spend','purchase_value','manual_roas','purchases','cost_per_purchase','ctr','frequency']

            st.markdown('<div class="meta-table-title">Campaign Scorecard</div>', unsafe_allow_html=True)
            st.dataframe(campaign_df[score_cols], use_container_width=True, hide_index=True)

            reopen_df = campaign_df[campaign_df['reopen_signal'] == 'YES - Reopen This Campaign']
            if not reopen_df.empty:
                st.markdown('<div class="meta-table-title">Campaigns You Should Reopen</div>', unsafe_allow_html=True)
                st.dataframe(reopen_df[score_cols], use_container_width=True, hide_index=True)

            weak_live_df = campaign_df[(campaign_df['campaign_effective_status'] == 'ACTIVE') & (campaign_df['score'] < 35)]
            if not weak_live_df.empty:
                st.markdown('<div class="meta-table-title">Weak Active Campaigns</div>', unsafe_allow_html=True)
                st.dataframe(weak_live_df[score_cols], use_container_width=True, hide_index=True)

            st.markdown('<div class="meta-table-title">Ad Level Performance</div>', unsafe_allow_html=True)
            display_cols = ['campaign_name','adset_name','ad_name','spend','purchase_value','manual_roas','meta_roas','ctr','cpc','frequency','purchases','cost_per_purchase','atc_rate','purchase_rate']
            existing_cols = [c for c in display_cols if c in window_df.columns]
            st.dataframe(window_df[existing_cols], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
