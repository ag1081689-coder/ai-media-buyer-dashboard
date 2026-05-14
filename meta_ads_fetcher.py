import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

if not ACCESS_TOKEN or not AD_ACCOUNT_ID:
    raise ValueError('Missing META_ACCESS_TOKEN or META_AD_ACCOUNT_ID')

FacebookAdsApi.init(access_token=ACCESS_TOKEN)
account = AdAccount(AD_ACCOUNT_ID)

fields = [
    'campaign_id',
    'campaign_name',
    'adset_id',
    'adset_name',
    'ad_id',
    'ad_name',
    'spend',
    'impressions',
    'reach',
    'clicks',
    'cpc',
    'cpm',
    'ctr',
    'frequency',
    'actions'
]

params = {
    'date_preset': 'last_7d',
    'level': 'ad'
}

insights = account.get_insights(fields=fields, params=params)
rows = []

for item in insights:
    row = item.export_all_data()
    leads = 0
    for action in row.get('actions', []) or []:
        if action.get('action_type') in ['lead', 'onsite_conversion.lead_grouped']:
            leads += int(float(action.get('value', 0)))
    row['leads'] = leads
    spend = float(row.get('spend', 0) or 0)
    row['cost_per_lead'] = round(spend / leads, 2) if leads else None
    rows.append(row)

if rows:
    df = pd.DataFrame(rows)
    df.to_csv('meta_ads_report.csv', index=False)
    print('Report exported successfully.')
else:
    print('No data found.')
