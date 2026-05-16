import io
from datetime import datetime
from html import escape

import pandas as pd


TAX_NET_RATE = 0.86


def _num(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def compact_money(value):
    value = _num(value)
    sign = '-' if value < 0 else ''
    value = abs(value)
    if value >= 1_000_000:
        return f'{sign}{value / 1_000_000:.2f}M EGP'
    if value >= 1_000:
        return f'{sign}{value / 1_000:.1f}K EGP'
    return f'{sign}{value:,.0f} EGP'


def compact_num(value):
    value = _num(value)
    if value >= 1_000_000:
        return f'{value / 1_000_000:.2f}M'
    if value >= 1_000:
        return f'{value / 1_000:.1f}K'
    return f'{value:,.0f}'


def build_client_report_data(window_df, level_df=None, management_fee=0):
    df = window_df.copy() if window_df is not None else pd.DataFrame()
    total_spend = _num(df.get('spend', pd.Series(dtype=float)).sum()) if not df.empty else 0
    total_revenue = _num(df.get('purchase_value', pd.Series(dtype=float)).sum()) if not df.empty else 0
    purchases = _num(df.get('purchases', pd.Series(dtype=float)).sum()) if not df.empty else 0
    clicks = _num(df.get('clicks', pd.Series(dtype=float)).sum()) if not df.empty else 0
    impressions = _num(df.get('impressions', pd.Series(dtype=float)).sum()) if not df.empty else 0
    estimated_recharge = total_spend / TAX_NET_RATE if total_spend else 0
    fees = estimated_recharge - total_spend
    roas = total_revenue / total_spend if total_spend else 0
    cpp = total_spend / purchases if purchases else 0
    ctr = clicks / impressions * 100 if impressions else 0
    cpc = total_spend / clicks if clicks else 0
    cpm = total_spend / impressions * 1000 if impressions else 0
    total_due = estimated_recharge + _num(management_fee)

    top_campaigns = pd.DataFrame()
    if level_df is not None and not level_df.empty:
        top_campaigns = level_df.copy().head(20)
    elif not df.empty and 'campaign_name' in df.columns:
        top_campaigns = df.groupby('campaign_name', as_index=False).agg({
            'spend': 'sum',
            'purchase_value': 'sum',
            'purchases': 'sum',
            'clicks': 'sum',
            'impressions': 'sum',
        })
        top_campaigns['manual_roas'] = top_campaigns.apply(lambda r: r['purchase_value'] / r['spend'] if r['spend'] else 0, axis=1)
        top_campaigns = top_campaigns.sort_values('purchase_value', ascending=False).head(20)

    return {
        'total_spend': total_spend,
        'estimated_recharge': estimated_recharge,
        'fees': fees,
        'total_revenue': total_revenue,
        'purchases': purchases,
        'roas': roas,
        'cpp': cpp,
        'ctr': ctr,
        'cpc': cpc,
        'cpm': cpm,
        'management_fee': _num(management_fee),
        'total_due': total_due,
        'top_campaigns': top_campaigns,
    }


def build_html_report(client_name, period_label, account_name, report_data, notes=''):
    client_name = escape(client_name or 'Client')
    period_label = escape(period_label or 'Selected period')
    account_name = escape(account_name or 'Selected ad account')
    notes = escape(notes or '')
    now = datetime.now().strftime('%Y-%m-%d %H:%M')

    metrics = [
        ('Real Ad Spend', compact_money(report_data['total_spend'])),
        ('Estimated Recharge', compact_money(report_data['estimated_recharge'])),
        ('Tax / Fawry Fees', compact_money(report_data['fees'])),
        ('Revenue', compact_money(report_data['total_revenue'])),
        ('Purchase ROAS', f"{report_data['roas']:.2f}"),
        ('Website Purchases', compact_num(report_data['purchases'])),
        ('Cost Per Purchase', compact_money(report_data['cpp'])),
        ('CTR', f"{report_data['ctr']:.2f}%"),
        ('CPC', compact_money(report_data['cpc'])),
        ('CPM', compact_money(report_data['cpm'])),
        ('Management Fee', compact_money(report_data['management_fee'])),
        ('Total Due', compact_money(report_data['total_due'])),
    ]
    metric_html = ''.join([f'<div class="metric"><span>{escape(k)}</span><strong>{escape(v)}</strong></div>' for k, v in metrics])

    top = report_data.get('top_campaigns', pd.DataFrame())
    table_html = '<p>No campaign data available.</p>'
    if top is not None and not top.empty:
        cols = [c for c in ['campaign_name', 'campaign_effective_status', 'score', 'spend', 'purchase_value', 'manual_roas', 'purchases', 'cost_per_purchase', 'growth_recommendation_ar'] if c in top.columns]
        display = top[cols].copy()
        for col in ['spend', 'purchase_value', 'cost_per_purchase']:
            if col in display.columns:
                display[col] = display[col].apply(compact_money)
        if 'manual_roas' in display.columns:
            display['manual_roas'] = display['manual_roas'].apply(lambda x: f'{_num(x):.2f}')
        table_html = display.to_html(index=False, escape=True, border=0)

    return f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Client Performance Report - {client_name}</title>
<style>
body {{ background:#050505; color:#fff; font-family:Arial, Helvetica, sans-serif; margin:0; padding:32px; }}
.report {{ max-width:1100px; margin:auto; }}
.hero {{ border:1px solid rgba(255,122,0,.55); border-radius:24px; padding:28px; background:radial-gradient(circle at 80% 30%, rgba(255,122,0,.22), transparent 30%), #0d0d0d; }}
h1 {{ font-size:42px; margin:0 0 10px; }}
.orange {{ color:#ff9f1c; }}
.meta {{ color:#cfcfcf; line-height:1.7; }}
.grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:22px 0; }}
.metric {{ background:#101010; border:1px solid rgba(255,122,0,.35); border-radius:16px; padding:16px; }}
.metric span {{ display:block; color:#d5d5d5; font-size:13px; margin-bottom:8px; }}
.metric strong {{ color:#ff9f1c; font-size:24px; }}
.section {{ margin-top:28px; background:#0d0d0d; border:1px solid rgba(255,122,0,.25); border-radius:18px; padding:20px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ text-align:left; color:#ff9f1c; border-bottom:1px solid rgba(255,122,0,.35); padding:10px; }}
td {{ border-bottom:1px solid #222; padding:10px; color:#f3f3f3; vertical-align:top; }}
.notes {{ color:#eee; line-height:1.7; white-space:pre-wrap; }}
@media(max-width:900px){{ .grid{{grid-template-columns:repeat(2,1fr)}} h1{{font-size:32px}} }}
</style>
</head>
<body>
<div class="report">
  <div class="hero">
    <h1>Client Performance <span class="orange">Report</span></h1>
    <div class="meta">
      <b>Client:</b> {client_name}<br>
      <b>Ad Account:</b> {account_name}<br>
      <b>Period:</b> {period_label}<br>
      <b>Generated:</b> {now}
    </div>
  </div>
  <div class="grid">{metric_html}</div>
  <div class="section">
    <h2 class="orange">Performance Summary</h2>
    <p>This report summarizes the ad performance, spend, revenue, ROAS, purchase volume, and next recommended actions for the selected period.</p>
  </div>
  <div class="section">
    <h2 class="orange">Campaign Performance</h2>
    {table_html}
  </div>
  <div class="section">
    <h2 class="orange">Notes</h2>
    <div class="notes">{notes or 'No additional notes.'}</div>
  </div>
</div>
</body>
</html>
"""


def report_csv_bytes(report_data):
    top = report_data.get('top_campaigns', pd.DataFrame())
    if top is None or top.empty:
        top = pd.DataFrame([report_data]).drop(columns=['top_campaigns'], errors='ignore')
    return top.to_csv(index=False).encode('utf-8')
