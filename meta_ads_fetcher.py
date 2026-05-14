import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

WINDOWS = {
    '3D': {'date_preset': 'last_3d'},
    '7D': {'date_preset': 'last_7d'},
    'MTD': {'date_preset': 'this_month'},
}


def get_roas_value(row):
    for field in ['website_purchase_roas', 'purchase_roas']:
        values = row.get(field) or []
        if isinstance(values, list) and values:
            try:
                return float(values[0].get('value', 0) or 0)
            except Exception:
                return None
    return None


def get_action_value(actions, names):
    total = 0
    for action in actions or []:
        if action.get('action_type') in names:
            total += float(action.get('value', 0) or 0)
    return total


def fetch_window(account, window_name, params):
    fields = [
        'campaign_id','campaign_name','adset_id','adset_name','ad_id','ad_name',
        'spend','impressions','reach','clicks','inline_link_clicks',
        'cpc','cpm','ctr','frequency','actions','purchase_roas','website_purchase_roas'
    ]

    insights = account.get_insights(fields=fields, params={**params, 'level': 'ad'})
    rows = []

    for item in insights:
        row = item.export_all_data()
        actions = row.get('actions', []) or []
        spend = float(row.get('spend', 0) or 0)
        link_clicks = float(row.get('inline_link_clicks', 0) or 0)
        meta_roas = get_roas_value(row)

        website_purchases = get_action_value(actions, ['offsite_conversion.fb_pixel_purchase'])
        purchase_actions = get_action_value(actions, ['purchase'])
        purchases = website_purchases if website_purchases else purchase_actions

        atc = get_action_value(actions, ['offsite_conversion.fb_pixel_add_to_cart']) or get_action_value(actions, ['add_to_cart'])
        ic = get_action_value(actions, ['offsite_conversion.fb_pixel_initiate_checkout']) or get_action_value(actions, ['initiate_checkout'])
        vc = get_action_value(actions, ['offsite_conversion.fb_pixel_view_content']) or get_action_value(actions, ['view_content'])
        lpv = get_action_value(actions, ['landing_page_view'])
        revenue = round(spend * meta_roas, 2) if meta_roas is not None else None

        row['window'] = window_name
        row['landing_page_view'] = lpv
        row['view_content'] = vc
        row['add_to_cart'] = atc
        row['initiate_checkout'] = ic
        row['purchases'] = purchases
        row['purchase_value'] = revenue
        row['cost_per_purchase'] = round(spend / purchases, 2) if purchases else None
        row['manual_roas'] = meta_roas
        row['meta_roas'] = meta_roas
        row['roas'] = meta_roas
        row['aov'] = round(revenue / purchases, 2) if revenue and purchases else None
        row['atc_rate'] = round((atc / lpv) * 100, 2) if lpv else None
        row['checkout_rate'] = round((ic / atc) * 100, 2) if atc else None
        row['purchase_rate'] = round((purchases / ic) * 100, 2) if ic else None
        row['lpv_rate'] = round((lpv / link_clicks) * 100, 2) if link_clicks else None
        rows.append(row)

    return rows


def fetch_meta_ads_report():
    if not ACCESS_TOKEN or not AD_ACCOUNT_ID:
        raise ValueError('Missing META_ACCESS_TOKEN or META_AD_ACCOUNT_ID')

    FacebookAdsApi.init(access_token=ACCESS_TOKEN)
    account = AdAccount(AD_ACCOUNT_ID)

    all_rows = []
    for window_name, params in WINDOWS.items():
        all_rows.extend(fetch_window(account, window_name, params))

    return pd.DataFrame(all_rows)


if __name__ == '__main__':
    df = fetch_meta_ads_report()
    if not df.empty:
        df.to_csv('meta_ads_report.csv', index=False)
        print('Meta Ads report exported successfully.')
    else:
        print('No data found.')
