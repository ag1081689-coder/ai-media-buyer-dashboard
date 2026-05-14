import pandas as pd
import streamlit as st

st.set_page_config(page_title='AI Media Buyer Dashboard', layout='wide')

st.title('AI Media Buyer Dashboard')
st.caption('Manual Approval Mode')

try:
    df = pd.read_csv('meta_ads_report.csv')

    numeric_cols = ['spend', 'ctr', 'cpc', 'cpm', 'frequency', 'leads', 'cost_per_lead']

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric('Total Spend', round(df['spend'].sum(), 2))

    with col2:
        st.metric('Average CTR', round(df['ctr'].mean(), 2))

    with col3:
        st.metric('Total Leads', int(df['leads'].sum()))

    st.subheader('Campaign Performance')
    st.dataframe(df)

    st.subheader('AI Recommendations')

    for _, row in df.iterrows():
        recommendation = None

        if row.get('cost_per_lead') and row['cost_per_lead'] > 200:
            recommendation = 'Pause Ad Set - High CPL'

        elif row.get('ctr') and row['ctr'] < 1:
            recommendation = 'Test New Creative - Low CTR'

        elif row.get('frequency') and row['frequency'] > 3:
            recommendation = 'Creative Fatigue Warning'

        if recommendation:
            with st.container(border=True):
                st.write(f"Campaign: {row.get('campaign_name')}")
                st.write(f"Ad Set: {row.get('adset_name')}")
                st.write(f"Recommendation: {recommendation}")

                st.button(
                    f"Approve Action for {row.get('adset_id')}",
                    key=f"approve_{row.get('adset_id')}"
                )

except FileNotFoundError:
    st.warning('Run meta_ads_fetcher.py first to generate the report.')
