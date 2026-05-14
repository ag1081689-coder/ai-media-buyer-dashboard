import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

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

    numeric_cols = [
        'spend','ctr','cpc','cpm','frequency','roas','purchases',
        'cost_per_purchase','purchase_value','aov','add_to_cart',
        'initiate_checkout','purchase_rate','lpv_rate','atc_rate','manual_roas','meta_roas'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    tabs = st.tabs(['Last 3 Days', 'Last 7 Days', 'Last 30 Days'])

    window_map = {
        'Last 3 Days': '3D',
        'Last 7 Days': '7D',
        'Last 30 Days': '30D'
    }

    for tab_name, tab in zip(window_map.keys(), tabs):
        with tab:
            current_window = window_map[tab_name]
            window_df = df[df['window'] == current_window].copy()

            if window_df.empty:
                st.warning('No data available.')
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

            st.subheader('Campaign Performance')

            display_cols = [
                'campaign_name','adset_name','ad_name','spend','purchase_value',
                'manual_roas','meta_roas','ctr','cpc','frequency','purchases',
                'cost_per_purchase','atc_rate','purchase_rate'
            ]

            existing_cols = [c for c in display_cols if c in window_df.columns]
            st.dataframe(window_df[existing_cols], use_container_width=True)

            st.subheader('AI Recommendations')

            for idx, row in window_df.iterrows():
                recommendations = []
                hooks = []

                if row.get('manual_roas', 0) > 4 and row.get('frequency', 0) < 2.5:
                    recommendations.append('Scale horizontally with +20% budget.')

                if row.get('manual_roas', 0) > 6 and row.get('purchases', 0) > 5:
                    recommendations.append('Duplicate into new CBO scaling campaign.')

                if row.get('ctr', 0) < 1:
                    recommendations.append('CTR is weak. Test stronger hooks and first 3-second creatives.')
                    hooks.extend([
                        'Problem → Solution hook',
                        'Before / After transformation',
                        'UGC reaction style',
                        'Price shock opening'
                    ])

                if row.get('frequency', 0) > 3:
                    recommendations.append('Creative fatigue detected. Launch fresh creatives immediately.')
                    hooks.extend([
                        'New angle with different persona',
                        'Founder story hook',
                        'Social proof opening'
                    ])

                if row.get('purchase_rate', 0) < 20:
                    recommendations.append('Optimize checkout flow and offer clarity.')

                if row.get('cost_per_purchase', 0) > 300:
                    recommendations.append('Reduce spend or pause weak ad set.')

                if recommendations:
                    with st.container(border=True):
                        st.markdown(f"### {row.get('campaign_name')}")
                        st.write(f"Ad Set: {row.get('adset_name')}")
                        st.write(f"ROAS: {row.get('manual_roas')}")

                        st.markdown('#### Recommended Actions')
                        for rec in recommendations:
                            st.write(f'• {rec}')

                        if hooks:
                            st.markdown('#### Suggested Hooks & Angles')
                            for hook in hooks:
                                st.write(f'• {hook}')

                        unique_key = f"approve_{idx}_{row.get('campaign_id')}_{row.get('adset_id')}_{row.get('ad_id')}"
                        st.button('Approve Action Plan', key=unique_key)

except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
