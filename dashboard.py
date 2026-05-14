import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.markdown('''
<style>
.stApp {background:#f0f2f5; color:#1c1e21;}
.block-container {padding-top:1.2rem; padding-bottom:4rem; max-width:1550px;}
.smart-hero {background:#ffffff; border:1px solid #dadde1; border-radius:14px; padding:22px 26px; margin-bottom:18px; box-shadow:0 1px 2px rgba(0,0,0,.08);}
.smart-hero h1 {font-size:34px; margin:0; color:#1c1e21; letter-spacing:-.5px;}
.smart-hero p {color:#606770; font-size:15px; margin:8px 0 0;}
.badge {display:inline-block; padding:6px 10px; border-radius:999px; background:#e7f3ff; color:#1877f2; font-weight:700; font-size:12px; margin-bottom:10px;}
[data-testid="stMetric"] {background:#ffffff; border:1px solid #dadde1; border-radius:12px; padding:14px 16px; box-shadow:0 1px 2px rgba(0,0,0,.08);}
[data-testid="stMetricLabel"] {color:#606770; font-size:13px;}
[data-testid="stMetricValue"] {color:#1c1e21; font-size:28px;}
.stButton button {border-radius:8px; background:#1877f2; color:white; border:0; font-weight:700; padding:.65rem 1rem;}
.stButton button:hover {background:#166fe5; color:white;}
[data-testid="stDataFrame"] {background:#ffffff; border-radius:12px; border:1px solid #dadde1; box-shadow:0 1px 2px rgba(0,0,0,.08); overflow:hidden;}
.table-title {font-size:22px; font-weight:800; color:#1c1e21; margin:22px 0 8px;}
.help-text {font-size:14px; color:#606770; margin-bottom:12px;}
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
        fixes.append('Create 5 new first-line hooks focused on problem, price shock, proof, comparison, and UGC reaction.')
    if freq > 3.5 and roas < 4:
        issues.append('Visual fatigue')
        fixes.append('Refresh the visual: new thumbnail, new opening frame, new product shot, and new UGC face.')
    if purchases > 0 and cpp > 300:
        issues.append('Offer or caption issue')
        fixes.append('Rewrite caption with stronger value stack, delivery/payment reassurance, and clearer CTA.')
    if roas >= 5 and purchases >= 10:
        issues.append('Winning angle')
        fixes.append('Create 3 variations from the same winning angle and duplicate into a controlled scaling test.')

    if not issues:
        issues.append('No major creative issue')
        fixes.append('Keep monitoring. Do not change the winning ad unless frequency rises or ROAS drops.')

    return ', '.join(issues), ' | '.join(fixes)


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
        reopen = 'YES - Reopen This Campaign'; action = 'This campaign is off but has strong past data. Reopen with a controlled test budget.'
    if campaign_status == 'ACTIVE' and score < 35:
        action = 'Active but weak. Review immediately or pause.'
    return score, status, action, reopen, ' | '.join(reasons[:4])


st.markdown('''
<div class="smart-hero">
  <span class="badge">Meta Ads Decision Dashboard</span>
  <h1>AI Media Buyer Dashboard</h1>
  <p>Clear campaign scoring, Meta-style tables, and direct creative actions for hooks, captions, and visuals.</p>
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

            score_cols = ['campaign_name','campaign_effective_status','score','status','next_action','creative_issue','creative_fix','reopen_signal','why','spend','purchase_value','manual_roas','purchases','cost_per_purchase','ctr','frequency']

            st.markdown('<div class="table-title">Campaign Scorecard</div><div class="help-text">Start here. This table tells you what to scale, watch, fix, pause, or reopen.</div>', unsafe_allow_html=True)
            st.dataframe(campaign_df[score_cols], use_container_width=True, hide_index=True)

            reopen_df = campaign_df[campaign_df['reopen_signal'] == 'YES - Reopen This Campaign']
            if not reopen_df.empty:
                st.markdown('<div class="table-title">Campaigns You Should Reopen</div>', unsafe_allow_html=True)
                st.dataframe(reopen_df[score_cols], use_container_width=True, hide_index=True)

            weak_live_df = campaign_df[(campaign_df['campaign_effective_status'] == 'ACTIVE') & (campaign_df['score'] < 35)]
            if not weak_live_df.empty:
                st.markdown('<div class="table-title">Weak Active Campaigns</div>', unsafe_allow_html=True)
                st.dataframe(weak_live_df[score_cols], use_container_width=True, hide_index=True)

            creative_df = campaign_df[campaign_df['creative_issue'] != 'No major creative issue']
            if not creative_df.empty:
                st.markdown('<div class="table-title">Creative Fix List</div><div class="help-text">Use this to know exactly when to change hook, caption, offer, or visual.</div>', unsafe_allow_html=True)
                st.dataframe(creative_df[['campaign_name','score','status','creative_issue','creative_fix','manual_roas','ctr','frequency','cost_per_purchase']], use_container_width=True, hide_index=True)

            st.markdown('<div class="table-title">Ad Level Performance</div>', unsafe_allow_html=True)
            display_cols = ['campaign_name','adset_name','ad_name','spend','purchase_value','manual_roas','meta_roas','ctr','cpc','frequency','purchases','cost_per_purchase','atc_rate','purchase_rate']
            existing_cols = [c for c in display_cols if c in window_df.columns]
            st.dataframe(window_df[existing_cols], use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
