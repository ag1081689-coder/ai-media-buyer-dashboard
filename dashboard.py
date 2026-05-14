import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')


def safe_num(value, default=0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def score_campaign(row, overall_roas):
    score = 0
    reasons = []

    roas = safe_num(row.get('manual_roas'))
    spend = safe_num(row.get('spend'))
    purchases = safe_num(row.get('purchases'))
    ctr = safe_num(row.get('ctr'))
    frequency = safe_num(row.get('frequency'))
    cpp = safe_num(row.get('cost_per_purchase'))

    if roas >= overall_roas * 1.2 and purchases >= 5:
        score += 35
        reasons.append('ROAS أعلى من متوسط الحساب')
    elif roas >= overall_roas and purchases >= 3:
        score += 25
        reasons.append('ROAS قريب أو أعلى من المتوسط')
    elif roas > 0:
        score += 10
        reasons.append('ROAS ضعيف مقارنة بالمتوسط')

    if purchases >= 20:
        score += 25
        reasons.append('حجم مبيعات قوي')
    elif purchases >= 5:
        score += 15
        reasons.append('فيه مبيعات كفاية للحكم')
    elif purchases > 0:
        score += 5
        reasons.append('مبيعات قليلة')

    if ctr >= 2:
        score += 15
        reasons.append('CTR قوي')
    elif ctr >= 1:
        score += 8
        reasons.append('CTR مقبول')
    else:
        reasons.append('CTR محتاج تحسين')

    if frequency <= 2.5:
        score += 10
        reasons.append('Frequency صحي')
    elif frequency <= 4:
        score += 4
        reasons.append('Frequency بدأ يعلى')
    else:
        score -= 10
        reasons.append('Creative fatigue محتمل')

    if cpp and cpp <= 250:
        score += 15
        reasons.append('Cost per purchase جيد')
    elif cpp and cpp <= 400:
        score += 7
        reasons.append('Cost per purchase متوسط')
    elif cpp:
        score -= 10
        reasons.append('Cost per purchase عالي')

    if spend < 500:
        score = min(score, 45)
        reasons.append('الصرف قليل، القرار غير مؤكد')

    score = max(0, min(100, round(score)))

    if score >= 80:
        status = 'Scale'
        action = 'افتحها وادرس السكيل. زود ميزانية تدريجي أو دوبليكيت CBO.'
    elif score >= 60:
        status = 'Watch'
        action = 'كويسة. راقبها 24-48 ساعة وشوف الثبات.'
    elif score >= 40:
        status = 'Test/Fix'
        action = 'محتاجة تستينج. جرب هووكس أو أوفر أو كرياتيف جديد.'
    else:
        status = 'Kill/Pause'
        action = 'ضعيفة. قلل الصرف أو وقفها لو الصرف كافي.'

    return score, status, action, ' | '.join(reasons[:4])


st.title('AI Media Buyer Dashboard')
st.caption('Professional E-commerce Scaling & Testing System')

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

    numeric_cols = [
        'spend','ctr','cpc','cpm','frequency','roas','purchases',
        'cost_per_purchase','purchase_value','aov','add_to_cart',
        'initiate_checkout','purchase_rate','lpv_rate','atc_rate','manual_roas','meta_roas'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    tabs = st.tabs(['Last 3 Days', 'Last 7 Days', 'This Month'])

    window_map = {
        'Last 3 Days': '3D',
        'Last 7 Days': '7D',
        'This Month': '30D'
    }

    for tab_name, tab in zip(window_map.keys(), tabs):
        with tab:
            current_window = window_map[tab_name]
            window_df = df[df['window'] == current_window].copy()

            if window_df.empty:
                st.warning('No data available. Click Fetch Latest Meta Data again after the latest deployment.')
                continue

            total_spend = window_df['spend'].sum()
            total_revenue = window_df['purchase_value'].sum()
            overall_roas = round(total_revenue / total_spend, 2) if total_spend else 0

            top1, top2, top3, top4 = st.columns(4)

            with top1:
                st.metric('Spend', round(total_spend, 2))

            with top2:
                st.metric('Revenue', round(total_revenue, 2))

            with top3:
                st.metric('Overall ROAS', overall_roas)

            with top4:
                st.metric('Purchases', int(window_df['purchases'].sum()))

            campaign_df = window_df.groupby('campaign_name', as_index=False).agg({
                'spend': 'sum',
                'purchase_value': 'sum',
                'purchases': 'sum',
                'clicks': 'sum',
                'impressions': 'sum',
                'frequency': 'mean',
                'cost_per_purchase': 'mean'
            })

            campaign_df['manual_roas'] = campaign_df.apply(
                lambda r: round(r['purchase_value'] / r['spend'], 2) if r['spend'] else 0,
                axis=1
            )
            campaign_df['ctr'] = campaign_df.apply(
                lambda r: round((r['clicks'] / r['impressions']) * 100, 2) if r['impressions'] else 0,
                axis=1
            )

            scored_rows = campaign_df.apply(
                lambda r: score_campaign(r, overall_roas),
                axis=1,
                result_type='expand'
            )
            campaign_df[['score', 'status', 'next_action', 'why']] = scored_rows
            campaign_df = campaign_df.sort_values('score', ascending=False)

            st.subheader('Campaign Scorecard')
            score_cols = [
                'campaign_name','score','status','next_action','why',
                'spend','purchase_value','manual_roas','purchases','cost_per_purchase','ctr','frequency'
            ]
            st.dataframe(campaign_df[score_cols], use_container_width=True)

            st.subheader('Open These First')
            priority_df = campaign_df[campaign_df['status'].isin(['Scale', 'Kill/Pause', 'Test/Fix'])].head(10)
            st.dataframe(priority_df[score_cols], use_container_width=True)

            st.subheader('Ad Level Performance')

            display_cols = [
                'campaign_name','adset_name','ad_name','spend','purchase_value',
                'manual_roas','meta_roas','ctr','cpc','frequency','purchases',
                'cost_per_purchase','atc_rate','purchase_rate'
            ]

            existing_cols = [c for c in display_cols if c in window_df.columns]
            st.dataframe(window_df[existing_cols], use_container_width=True)

            st.subheader('AI Recommendations')

            for idx, row in campaign_df.iterrows():
                if row['status'] == 'Scale':
                    with st.container(border=True):
                        st.markdown(f"### {row.get('campaign_name')} — Score {row.get('score')}")
                        st.write(row.get('next_action'))
                        st.write(row.get('why'))
                        st.markdown('#### Scaling Ideas')
                        st.write('• زود الميزانية 15-20% فقط لو الأداء ثابت آخر 3 أيام')
                        st.write('• دوبليكيت CBO لو نفس الكرياتيف مستقر ومفيش fatigue')
                        st.write('• اعمل نسخة Broad بنفس الهووك الفائز')

                elif row['status'] == 'Test/Fix':
                    with st.container(border=True):
                        st.markdown(f"### {row.get('campaign_name')} — Score {row.get('score')}")
                        st.write(row.get('next_action'))
                        st.write(row.get('why'))
                        st.markdown('#### Testing Hooks')
                        st.write('• Problem → Solution hook')
                        st.write('• Price shock opening')
                        st.write('• UGC reaction style')
                        st.write('• Before / After transformation')

                elif row['status'] == 'Kill/Pause':
                    with st.container(border=True):
                        st.markdown(f"### {row.get('campaign_name')} — Score {row.get('score')}")
                        st.write(row.get('next_action'))
                        st.write(row.get('why'))
                        st.markdown('#### Action')
                        st.write('• افتحها وراجع آخر 3 أيام')
                        st.write('• لو مفيش تحسن، قلل الميزانية أو وقفها')

except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
