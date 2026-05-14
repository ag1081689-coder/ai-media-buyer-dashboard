import os
import pandas as pd
import streamlit as st
from meta_ads_fetcher import fetch_meta_ads_report

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.title('AI Media Buyer Dashboard')
st.caption('E-commerce AI Scaling & Testing System')

if st.button('Fetch Latest Meta Data'):
    try:
        df_live = fetch_meta_ads_report()
        df_live.to_csv('meta_ads_report.csv', index=False)
        st.success('Meta data fetched successfully.')
    except Exception as e:
        st.error(f'Error fetching Meta data: {e}')

try:
    df = pd.read_csv('meta_ads_report.csv')

    numeric_cols = [
        'spend','ctr','cpc','cpm','frequency','roas','purchases',
        'cost_per_purchase','purchase_value','aov','add_to_cart',
        'initiate_checkout','purchase_rate','lpv_rate','atc_rate'
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    top1, top2, top3, top4 = st.columns(4)

    with top1:
        st.metric('Total Spend', round(df['spend'].sum(), 2))

    with top2:
        st.metric('Average ROAS', round(df['roas'].mean(), 2))

    with top3:
        st.metric('Purchases', int(df['purchases'].sum()))

    with top4:
        st.metric('Revenue', round(df['purchase_value'].sum(), 2))

    st.subheader('Performance Table')
    st.dataframe(df)

    st.subheader('AI Scaling Recommendations')

    for _, row in df.iterrows():
        recommendations = []

        if row.get('roas') and row['roas'] > 4 and row.get('frequency', 0) < 2.5:
            recommendations.append('Horizontal Scale Winning Ad Set +20%')

        if row.get('roas') and row['roas'] > 6:
            recommendations.append('Duplicate Into New CBO Campaign')

        if row.get('ctr') and row['ctr'] < 1:
            recommendations.append('Test New Hooks & Creatives')

        if row.get('frequency') and row['frequency'] > 3:
            recommendations.append('Creative Fatigue - Refresh Creatives')

        if row.get('atc_rate') and row['atc_rate'] < 5:
            recommendations.append('Improve Landing Page or Product Offer')

        if row.get('purchase_rate') and row['purchase_rate'] < 20:
            recommendations.append('Optimize Checkout Experience')

        if row.get('cost_per_purchase') and row['cost_per_purchase'] > 300:
            recommendations.append('Reduce Budget or Pause Ad Set')

        if recommendations:
            with st.container(border=True):
                st.write(f"Campaign: {row.get('campaign_name')}")
                st.write(f"Ad Set: {row.get('adset_name')}")
                st.write(f"ROAS: {row.get('roas')}")

                for rec in recommendations:
                    st.write(f"• {rec}")

                st.button(
                    f"Approve Manual Action {row.get('adset_id')}",
                    key=f"approve_{row.get('adset_id')}"
                )

except FileNotFoundError:
    st.info('Click Fetch Latest Meta Data to generate the first report.')
