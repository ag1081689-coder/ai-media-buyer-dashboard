import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
import pandas as pd

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')

WINDOWS = {
    'TODAY': {'date_preset': 'today'},
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


def fetch_campaign_status(account):
    campaigns = account.get_campaigns(fields=['id', 'name', 'status', 'effective_status'])
    return {
        str(c.get('id')): {
            'campaign_status': c.get('status'),
            'campaign_effective_status': c.get('effective_status')
        }
        for c in campaigns
    }


def fetch_adset_status(account):
    adsets = account.get_ad_sets(fields=['id', 'name', 'status', 'effective_status', 'campaign_id'])
    return {
        str(a.get('id')): {
            'adset_status': a.get('status'),
            'adset_effective_status': a.get('effective_status')
        }
        for a in adsets
    }


def fetch_ad_status(account):
    ads = account.get_ads(fields=['id', 'name', 'status', 'effective_status', 'adset_id', 'campaign_id'])
    return {
        str(a.get('id')): {
            'ad_status': a.get('status'),
            'ad_effective_status': a.get('effective_status')
        }
        for a in ads
    }


def fetch_window(account, window_name, params, status_map, adset_status_map, ad_status_map):
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
        campaign_id = str(row.get('campaign_id'))
        adset_id = str(row.get('adset_id'))
        ad_id = str(row.get('ad_id'))
        status_info = status_map.get(campaign_id, {})
        adset_status = adset_status_map.get(adset_id, {})
        ad_status = ad_status_map.get(ad_id, {})

        website_purchases = get_action_value(actions, ['offsite_conversion.fb_pixel_purchase'])
        purchase_actions = get_action_value(actions, ['purchase'])
        purchases = website_purchases if website_purchases else purchase_actions

        atc = get_action_value(actions, ['offsite_conversion.fb_pixel_add_to_cart']) or get_action_value(actions, ['add_to_cart'])
        ic = get_action_value(actions, ['offsite_conversion.fb_pixel_initiate_checkout']) or get_action_value(actions, ['initiate_checkout'])
        vc = get_action_value(actions, ['offsite_conversion.fb_pixel_view_content']) or get_action_value(actions, ['view_content'])
        lpv = get_action_value(actions, ['landing_page_view'])

        row['window'] = window_name
        row['campaign_status'] = status_info.get('campaign_status')
        row['campaign_effective_status'] = status_info.get('campaign_effective_status')
        row['adset_status'] = adset_status.get('adset_status')
        row['adset_effective_status'] = adset_status.get('adset_effective_status')
        row['ad_status'] = ad_status.get('ad_status')
        row['ad_effective_status'] = ad_status.get('ad_effective_status')
        row['landing_page_view'] = lpv
        row['view_content'] = vc
        row['add_to_cart'] = atc
        row['initiate_checkout'] = ic
        row['purchases'] = purchases
        row['purchase_value'] = None
        row['cost_per_purchase'] = round(spend / purchases, 2) if purchases else None
        row['manual_roas'] = meta_roas
        row['meta_roas'] = meta_roas
        row['roas'] = meta_roas
        row['aov'] = None
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
    status_map = fetch_campaign_status(account)
    adset_status_map = fetch_adset_status(account)
    ad_status_map = fetch_ad_status(account)

    all_rows = []
    for window_name, params in WINDOWS.items():
        all_rows.extend(fetch_window(account, window_name, params, status_map, adset_status_map, ad_status_map))

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df['spend'] = pd.to_numeric(df['spend'], errors='coerce').fillna(0)
        df['meta_roas'] = pd.to_numeric(df['meta_roas'], errors='coerce')
        for window in df['window'].dropna().unique():
            mask = df['window'] == window
            spend_sum = df.loc[mask, 'spend'].sum()
            weighted_roas = ((df.loc[mask, 'spend'] * df.loc[mask, 'meta_roas']).sum() / spend_sum) if spend_sum else None
            if weighted_roas is not None:
                df.loc[mask, 'purchase_value'] = df.loc[mask, 'spend'] * df.loc[mask, 'meta_roas']
                df.loc[mask, 'window_roas_weighted'] = weighted_roas
    return df


if __name__ == '__main__':
    df = fetch_meta_ads_report()
    if not df.empty:
        df.to_csv('meta_ads_report.csv', index=False)
        print('Meta Ads report exported successfully.')
    else:
        print('No data found.')
