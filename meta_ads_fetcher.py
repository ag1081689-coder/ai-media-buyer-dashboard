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
    'campaign_id','campaign_name','adset_id','adset_name','ad_id','ad_name',
    'spend','impressions','reach','clicks','inline_link_clicks','landing_page_view',
    'cpc','cpm','ctr','frequency','actions','action_values','purchase_roas','website_purchase_roas'
]

params = {'date_preset': 'last_7d', 'level': 'ad'}


def get_action_value(actions, names):
    total = 0
    for action in actions or []:
        if action.get('action_type') in names:
            total += float(action.get('value', 0) or 0)
    return total

insights = account.get_insights(fields=fields, params=params)
rows = []

for item in insights:
    row = item.export_all_data()
    actions = row.get('actions', []) or []
    values = row.get('action_values', []) or []
    spend = float(row.get('spend', 0) or 0)
    clicks = float(row.get('clicks', 0) or 0)
    lpv = float(row.get('landing_page_view', 0) or 0)

    purchases = get_action_value(actions, ['purchase','omni_purchase','offsite_conversion.fb_pixel_purchase'])
    atc = get_action_value(actions, ['add_to_cart','omni_add_to_cart','offsite_conversion.fb_pixel_add_to_cart'])
    ic = get_action_value(actions, ['initiate_checkout','omni_initiated_checkout','offsite_conversion.fb_pixel_initiate_checkout'])
    vc = get_action_value(actions, ['view_content','omni_view_content','offsite_conversion.fb_pixel_view_content'])
    revenue = get_action_value(values, ['purchase','omni_purchase','offsite_conversion.fb_pixel_purchase'])

    row['view_content'] = vc
    row['add_to_cart'] = atc
    row['initiate_checkout'] = ic
    row['purchases'] = purchases
    row['purchase_value'] = revenue
    row['cost_per_purchase'] = round(spend / purchases, 2) if purchases else None
    row['roas'] = round(revenue / spend, 2) if spend else None
    row['aov'] = round(revenue / purchases, 2) if purchases else None
    row['atc_rate'] = round((atc / lpv) * 100, 2) if lpv else None
    row['checkout_rate'] = round((ic / atc) * 100, 2) if atc else None
    row['purchase_rate'] = round((purchases / ic) * 100, 2) if ic else None
    row['lpv_rate'] = round((lpv / clicks) * 100, 2) if clicks else None
    rows.append(row)

if rows:
    pd.DataFrame(rows).to_csv('meta_ads_report.csv', index=False)
    print('E-commerce report exported successfully.')
else:
    print('No data found.')
