import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.business import Business
import pandas as pd

load_dotenv()

ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
AD_ACCOUNT_ID = os.getenv('META_AD_ACCOUNT_ID')
BUSINESS_ID = os.getenv('META_BUSINESS_ID')

WINDOWS = {
    'TODAY': {'date_preset': 'today'},
    '3D': {'date_preset': 'last_3d'},
    '7D': {'date_preset': 'last_7d'},
    'MTD': {'date_preset': 'this_month'},
    '30D': {'date_preset': 'this_month'},
    'LAST_MONTH': {'date_preset': 'last_month'},
    'THIS_YEAR': {'date_preset': 'this_year'},
}


def init_api():
    if not ACCESS_TOKEN:
        raise ValueError('Missing META_ACCESS_TOKEN')
    FacebookAdsApi.init(access_token=ACCESS_TOKEN)


def normalize_account_id(account_id):
    if not account_id:
        return None
    account_id = str(account_id)
    return account_id if account_id.startswith('act_') else f'act_{account_id}'


def fetch_business_ad_accounts():
    init_api()
    accounts = []
    seen = set()

    def add_account(acc, source):
        acc_id = acc.get('id') or normalize_account_id(acc.get('account_id'))
        if not acc_id or acc_id in seen:
            return
        seen.add(acc_id)
        accounts.append({'id': acc_id, 'account_id': acc.get('account_id'), 'name': acc.get('name') or acc_id, 'source': source})

    if BUSINESS_ID:
        business = Business(BUSINESS_ID)
        for acc in business.get_owned_ad_accounts(fields=['id', 'name', 'account_id']):
            add_account(acc.export_all_data(), 'owned')
        for acc in business.get_client_ad_accounts(fields=['id', 'name', 'account_id']):
            add_account(acc.export_all_data(), 'client')

    if not accounts and AD_ACCOUNT_ID:
        default_id = normalize_account_id(AD_ACCOUNT_ID)
        accounts.insert(0, {'id': default_id, 'account_id': default_id.replace('act_', ''), 'name': default_id, 'source': 'default'})

    return accounts


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


def fetch_window(account, window_name, params, account_id=None, account_name=None):
    fields = [
        'campaign_id','campaign_name','adset_id','adset_name','ad_id','ad_name',
        'spend','impressions','reach','clicks','inline_link_clicks','cpc','cpm','ctr','frequency',
        'actions','purchase_roas','website_purchase_roas'
    ]
    insights = account.get_insights(fields=fields, params={**params, 'level': 'ad', 'limit': 5000})
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

        row['account_id'] = account_id
        row['account_name'] = account_name
        row['window'] = window_name
        row['campaign_status'] = 'UNKNOWN'
        row['campaign_effective_status'] = 'UNKNOWN'
        row['adset_status'] = 'UNKNOWN'
        row['adset_effective_status'] = 'UNKNOWN'
        row['ad_status'] = 'UNKNOWN'
        row['ad_effective_status'] = 'UNKNOWN'
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


def fetch_meta_ads_report(ad_account_id=None, account_name=None, selected_window=None):
    selected_account_id = normalize_account_id(ad_account_id or AD_ACCOUNT_ID)
    if not selected_account_id:
        raise ValueError('Missing META_AD_ACCOUNT_ID or selected ad account')
    init_api()
    account = AdAccount(selected_account_id)

    windows_to_fetch = WINDOWS
    if selected_window and selected_window in WINDOWS:
        windows_to_fetch = {selected_window: WINDOWS[selected_window]}

    all_rows = []
    for window_name, params in windows_to_fetch.items():
        all_rows.extend(fetch_window(account, window_name, params, selected_account_id, account_name))

    df = pd.DataFrame(all_rows)
    if not df.empty:
        df['spend'] = pd.to_numeric(df['spend'], errors='coerce').fillna(0)
        df['meta_roas'] = pd.to_numeric(df['meta_roas'], errors='coerce').fillna(0)
        df['purchase_value'] = df['spend'] * df['meta_roas']
        for window in df['window'].dropna().unique():
            mask = (df['window'] == window) & (df['account_id'] == selected_account_id)
            spend_sum = df.loc[mask, 'spend'].sum()
            if spend_sum:
                df.loc[mask, 'window_roas_weighted'] = df.loc[mask, 'purchase_value'].sum() / spend_sum
    return df


if __name__ == '__main__':
    df = fetch_meta_ads_report()
    if not df.empty:
        df.to_csv('meta_ads_report.csv', index=False)
        print('Meta Ads report exported successfully.')
    else:
        print('No data found.')
