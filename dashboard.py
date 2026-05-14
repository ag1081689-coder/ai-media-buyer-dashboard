import pandas as pd
import streamlit as st

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.title('AI Media Buyer Dashboard')

try:
    df = pd.read_csv('meta_ads_report.csv')

    st.subheader('Campaign Performance')
    st.dataframe(df)

    if 'spend' in df.columns:
        st.metric('Total Spend', round(df['spend'].astype(float).sum(), 2))

    if 'ctr' in df.columns:
        avg_ctr = df['ctr'].astype(float).mean()
        st.metric('Average CTR', round(avg_ctr, 2))

except FileNotFoundError:
    st.warning('Run meta_ads_fetcher.py first to generate the report.')
