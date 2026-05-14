import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

FacebookAdsApi.init(access_token=ACCESS_TOKEN)

account = AdAccount(AD_ACCOUNT_ID)

fields = [
    'campaign_name',
    'adset_name',
    'ad_name',
    'spend',
    'impressions',
    'reach',
    'clicks',
    'cpc',
    'cpm',
    'ctr',
    'frequency'
]

params = {
    'date_preset': 'last_7d',
    'level': 'ad'
}

insights = account.get_insights(fields=fields, params=params)

data = []

for item in insights:
    data.append(item.export_all_data())

if data:
    df = pd.DataFrame(data)
    df.to_csv('meta_ads_report.csv', index=False)
    print('Report exported successfully.')
else:
    print('No data found.')
