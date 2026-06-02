import os
import json
import re
from datetime import datetime

import gspread
import pandas as pd
import streamlit as st


SHEET_ID = "1x5CfKVrgXZy1-1yVPoqAwcS0KpxeOyzxfA8shDt2qkw"
AV_SHEET_ID = "1f-1lkgr7nGiQofoREnhfbszjaJFu17OtZaMJ09_sLWw"

PROJECTS = ["D11 BUSINESS", "D12 Medical", "METRO +", "TIJAN", "WW1", "WW2", "STAGE X", "RESALE", "MIDST"]

PROJECT_ALIASES = {
    "d11": "D11 BUSINESS",
    "d12": "D12 Medical",
    "ww1": "WW1",
    "ww2": "WW2",
    "tijan": "TIJAN",
    "midst": "MIDST",
    "stage x": "STAGE X",
    "resale": "RESALE",
    "metro": "METRO +",
}


st.set_page_config(page_title="ZENO Sales OS", layout="wide")

st.markdown(
    """
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
    background:#050505 !important;
    color:#ffffff !important;
}
.block-container {padding-top:1.2rem; max-width:1550px;}
* {color:#ffffff;}
.hero {
    background:radial-gradient(circle at 75% 20%, rgba(255,122,0,.22), transparent 30%), linear-gradient(135deg,#070707,#140b02);
    border:1px solid rgba(255,122,0,.42);
    border-radius:26px;
    padding:34px 38px;
    margin-bottom:22px;
    box-shadow:0 28px 90px rgba(0,0,0,.7);
}
.hero .tag {color:#ff9f1c;font-weight:900;letter-spacing:1.8px;font-size:13px;margin-bottom:10px;}
.hero h1 {font-size:52px;line-height:1;margin:0;color:#fff;letter-spacing:-1.5px;}
.hero p {font-size:17px;color:#d7d7d7;margin:14px 0 0;line-height:1.7;}
.card {
    background:#0f0f0f;
    border:1px solid rgba(255,122,0,.28);
    border-radius:18px;
    padding:18px;
    box-shadow:0 16px 45px rgba(0,0,0,.45);
    margin-bottom:14px;
}
.card h3, .card h4 {margin-top:0;color:#ff9f1c;}
.metric-card {
    background:#0f0f0f;
    border:1px solid rgba(255,122,0,.28);
    border-radius:18px;
    padding:18px;
    min-height:110px;
    box-shadow:0 16px 45px rgba(0,0,0,.45);
}
.metric-label {color:#cfcfcf;font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;}
.metric-value {color:#ff9f1c;font-size:31px;font-weight:1000;margin-top:8px;}
.table-title {font-size:22px;font-weight:1000;color:#ff9f1c;margin:20px 0 8px;}
.help-text {font-size:14px;color:#cfcfcf;margin-bottom:14px;}
.stButton button {
    border-radius:12px;
    background:linear-gradient(135deg,#ff7a00,#ff9f1c) !important;
    color:#050505 !important;
    border:0;
    font-weight:900;
}
input, textarea, select {background:#111111 !important;color:#ffffff !important;border-color:#ff7a00 !important;}
[data-testid="stDataFrame"] {border:1px solid rgba(255,122,0,.22);border-radius:14px;overflow:hidden;}
.status-available {color:#24d26a;font-weight:900;}
.status-reserved {color:#ff4d4d;font-weight:900;}
.status-hold {color:#5aa7ff;font-weight:900;}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_clients():
    creds_json = os.environ.get("GOOGLE_CREDENTIALS")
    if not creds_json:
        raise RuntimeError("GOOGLE_CREDENTIALS env var is missing.")
    creds = json.loads(creds_json)
    gc = gspread.service_account_from_dict(creds)
    return gc.open_by_key(SHEET_ID), gc.open_by_key(AV_SHEET_ID)


def normalize_digits(text):
    return str(text).translate(str.maketrans("٠١٢٣٤٥٦٧٨٩٫٬", "0123456789.,"))


def clean(s):
    try:
        return float(re.sub(r"[^\d.]", "", normalize_digits(str(s))))
    except Exception:
        return 0


def money(v):
    try:
        return f"{float(v):,.0f} EGP"
    except Exception:
        return "0 EGP"


def detect_project(text):
    t = str(text).lower()
    for a, r in PROJECT_ALIASES.items():
        if a in t:
            return r
    for p in PROJECTS:
        if p.lower() in t:
            return p
    return None


def get_headers(rows):
    h = {}
    for row in rows[:3]:
        for i, c in enumerate(row):
            k = str(c).strip().lower().replace("_", "")
            kc = k.replace(" ", "")
            if kc in ["code", "u.", "unit", "unitcode"]:
                h["code"] = i
            elif kc == "area":
                h["area"] = i
            elif kc in ["price", "pricepermeter", "pricem2"]:
                h["price"] = i
            elif kc == "status":
                h["status"] = i
            elif "totalpriceafterdi" in kc:
                h["total_after"] = i
            elif kc in ["totalprice", "total"]:
                if "total_after" not in h:
                    h["total"] = i
            elif "down" in kc and ("pay" in kc or kc == "down"):
                h["down"] = i
            elif kc in ["instalments", "installments", "batchafteryear", "insta"]:
                h["inst"] = i
            elif kc in ["cashdiscount", "discount"]:
                h["disc"] = i
            elif "delivery" in kc:
                h["delivery"] = i
    return h


def gcell(row, h, k, d=""):
    i = h.get(k)
    return str(row[i]).strip() if i is not None and i < len(row) else d


def get_status(row, h):
    i = h.get("status")
    if i is not None and i < len(row):
        v = str(row[i]).strip().lower()
        if v in ["available", "reserved", "hold"]:
            return v
    for c in row:
        v = str(c).strip().lower()
        if v in ["available", "reserved", "hold"]:
            return v
    return ""


def row_to_unit(row, ws_title, h):
    bad = ["available", "reserved", "hold", ""]
    total = gcell(row, h, "total_after") or gcell(row, h, "total")
    down = gcell(row, h, "down")
    return {
        "project": ws_title,
        "code": gcell(row, h, "code"),
        "area": gcell(row, h, "area"),
        "price_m2": gcell(row, h, "price") if gcell(row, h, "price").lower() not in bad else "",
        "total_price": total,
        "total_num": clean(total),
        "down_payment": down if str(down).lower() not in bad else "",
        "down_num": clean(down),
        "installments": gcell(row, h, "inst") if gcell(row, h, "inst").lower() not in bad else "",
        "delivery": gcell(row, h, "delivery") if gcell(row, h, "delivery").lower() not in bad else "",
        "status": get_status(row, h),
    }


@st.cache_data(ttl=120, show_spinner=False)
def load_units():
    _, av_sh = get_clients()
    units = []
    for ws in av_sh.worksheets():
        rows = ws.get_all_values() or []
        if not rows:
            continue
        h = get_headers(rows)
        ci = h.get("code", 0)
        for row in rows[1:]:
            if row and ci < len(row) and str(row[ci]).strip():
                u = row_to_unit(row, ws.title, h)
                if u["code"]:
                    units.append(u)
    return pd.DataFrame(units)


def project_stats(df):
    if df.empty:
        return pd.DataFrame()
    res = df.groupby(["project", "status"]).size().unstack(fill_value=0).reset_index()
    for col in ["available", "reserved", "hold"]:
        if col not in res.columns:
            res[col] = 0
    res["total"] = res[["available", "reserved", "hold"]].sum(axis=1)
    return res[["project", "available", "reserved", "hold", "total"]]


def calc_plan(total, dp, years):
    t = clean(total)
    d = t * (dp / 100)
    r = t - d
    return {"total": t, "down": d, "rem": r, "quarter": r / (years * 4), "month": r / (years * 12)}


def unit_card(u):
    status = str(u.get("status", "")).lower()
    cls = "status-available" if status == "available" else "status-reserved" if status == "reserved" else "status-hold"
    return f"""
    <div class="card">
        <h3>{u.get('code', '')} - {u.get('project', '')}</h3>
        <div><b>Area:</b> {u.get('area', '')} m2</div>
        <div><b>Price/m2:</b> {u.get('price_m2', '')}</div>
        <div><b>Total:</b> {u.get('total_price', '')}</div>
        <div><b>Down Payment:</b> {u.get('down_payment', '')}</div>
        <div><b>Installments:</b> {u.get('installments', '')}</div>
        <div><b>Delivery:</b> {u.get('delivery', '')}</div>
        <div><b>Status:</b> <span class="{cls}">{status}</span></div>
    </div>
    """


def whatsapp_message(u):
    return (
        f"أهلا بحضرتك، عندنا وحدة مناسبة في {u.get('project','')}\n"
        f"الكود: {u.get('code','')}\n"
        f"المساحة: {u.get('area','')} م\n"
        f"الإجمالي: {u.get('total_price','')} جنيه\n"
        f"المقدم: {u.get('down_payment','')}\n"
        f"الأقساط: {u.get('installments','')}\n"
        f"التسليم: {u.get('delivery','')}\n\n"
        "لو مناسب لحضرتك أقدر أبعتلك التفاصيل كاملة أو أحددلك معاد معاينة."
    )


def save_sale(project, unit, price, client_name, sales_name, phone, notes):
    sh, _ = get_clients()
    try:
        ws = sh.worksheet("المبيعات")
    except Exception:
        ws = sh.add_worksheet("المبيعات", 1000, 12)
        ws.append_row(["المشروع", "الوحدة", "السعر", "العميل", "رقم العميل", "السيلز", "ملاحظات", "التاريخ"])
    ws.append_row([project, unit, price, client_name, phone, sales_name, notes, datetime.now().strftime("%Y-%m-%d %H:%M")])


def render_metrics(df):
    total = len(df)
    available = int((df["status"] == "available").sum()) if not df.empty else 0
    reserved = int((df["status"] == "reserved").sum()) if not df.empty else 0
    hold = int((df["status"] == "hold").sum()) if not df.empty else 0
    cols = st.columns(4)
    data = [("Total Units", total), ("Available", available), ("Reserved", reserved), ("Hold", hold)]
    for col, (label, value) in zip(cols, data):
        col.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


st.markdown(
    """
<div class="hero">
  <div class="tag">ZENO SALES OS</div>
  <h1>Sales Dashboard</h1>
  <p>Inventory search, budget finder, payment plans, WhatsApp scripts, and sales logging connected to your current Google Sheet.</p>
</div>
""",
    unsafe_allow_html=True,
)

try:
    df = load_units()
except Exception as e:
    st.error(f"Could not load Google Sheets data: {e}")
    st.stop()

if df.empty:
    st.warning("No units found in the availability sheet.")
    st.stop()

page = st.sidebar.radio(
    "ZENO Sales OS",
    ["Overview", "Available Units", "Budget Finder", "Unit Search", "Payment Plan", "WhatsApp Scripts", "Project Stats", "Register Sale"],
)

st.sidebar.caption("Connected to current Google Sheet")
if st.sidebar.button("Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

projects = ["All"] + sorted(df["project"].dropna().unique().tolist())

if page == "Overview":
    render_metrics(df)
    st.markdown('<div class="table-title">Project Stats</div>', unsafe_allow_html=True)
    st.dataframe(project_stats(df), use_container_width=True, hide_index=True)
    st.markdown('<div class="table-title">Latest Available Units</div>', unsafe_allow_html=True)
    st.dataframe(df[df["status"] == "available"].head(30), use_container_width=True, hide_index=True)

elif page == "Available Units":
    st.markdown('<div class="table-title">Available Units</div><div class="help-text">Filter and search units from the current sheet.</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    project = c1.selectbox("Project", projects)
    status = c2.selectbox("Status", ["All", "available", "reserved", "hold"])
    min_total = c3.number_input("Min Total", min_value=0, value=0, step=100000)
    max_total = c4.number_input("Max Total", min_value=0, value=0, step=100000)
    search = st.text_input("Search by code or project")

    f = df.copy()
    if project != "All":
        f = f[f["project"] == project]
    if status != "All":
        f = f[f["status"] == status]
    if min_total:
        f = f[f["total_num"] >= min_total]
    if max_total:
        f = f[f["total_num"] <= max_total]
    if search:
        s = search.lower()
        f = f[f["code"].str.lower().str.contains(s, na=False) | f["project"].str.lower().str.contains(s, na=False)]

    st.dataframe(f, use_container_width=True, hide_index=True)

elif page == "Budget Finder":
    st.markdown('<div class="table-title">Budget Finder</div><div class="help-text">Find available units by total price and down payment.</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    project = c1.selectbox("Project", projects, key="budget_project")
    total_min = c2.number_input("Total From", min_value=0, value=0, step=100000)
    total_max = c3.number_input("Total To", min_value=0, value=5000000, step=100000)
    d1, d2 = st.columns(2)
    down_min = d1.number_input("Down From", min_value=0, value=0, step=50000)
    down_max = d2.number_input("Down To", min_value=0, value=0, step=50000)

    f = df[df["status"] == "available"].copy()
    if project != "All":
        f = f[f["project"] == project]
    if total_min:
        f = f[f["total_num"] >= total_min]
    if total_max:
        f = f[f["total_num"] <= total_max]
    if down_min:
        f = f[f["down_num"] >= down_min]
    if down_max:
        f = f[f["down_num"] <= down_max]

    st.dataframe(f.sort_values("total_num"), use_container_width=True, hide_index=True)

elif page == "Unit Search":
    st.markdown('<div class="table-title">Unit Search</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    project = c1.selectbox("Project", projects, key="unit_project")
    code = c2.text_input("Unit Code")
    f = df.copy()
    if project != "All":
        f = f[f["project"] == project]
    if code:
        f = f[f["code"].str.upper().str.replace(" ", "").str.contains(code.upper().replace(" ", ""), na=False)]
    if not f.empty:
        u = f.iloc[0].to_dict()
        st.markdown(unit_card(u), unsafe_allow_html=True)
        st.text_area("WhatsApp Message", whatsapp_message(u), height=210)
    else:
        st.warning("No matching unit found.")

elif page == "Payment Plan":
    st.markdown('<div class="table-title">Payment Plan Calculator</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    project = c1.selectbox("Project", projects, key="plan_project")
    code = c2.text_input("Unit Code", key="plan_code")
    dp = st.slider("Down Payment %", 0, 100, 20, 5)
    years = st.slider("Years", 1, 10, 5, 1)
    f = df.copy()
    if project != "All":
        f = f[f["project"] == project]
    if code:
        f = f[f["code"].str.upper().str.replace(" ", "").str.contains(code.upper().replace(" ", ""), na=False)]
    if not f.empty:
        u = f.iloc[0].to_dict()
        plan = calc_plan(u["total_price"], dp, years)
        render_metrics(pd.DataFrame([u]))
        st.markdown(unit_card(u), unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="card">
                <h3>Payment Plan</h3>
                <div><b>Total:</b> {money(plan['total'])}</div>
                <div><b>Down Payment:</b> {money(plan['down'])}</div>
                <div><b>Remaining:</b> {money(plan['rem'])}</div>
                <div><b>Quarterly:</b> {money(plan['quarter'])}</div>
                <div><b>Monthly:</b> {money(plan['month'])}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Choose a unit to calculate the payment plan.")

elif page == "WhatsApp Scripts":
    st.markdown('<div class="table-title">WhatsApp Scripts</div>', unsafe_allow_html=True)
    project = st.selectbox("Project", projects, key="wa_project")
    code = st.text_input("Unit Code", key="wa_code")
    style = st.selectbox("Script Style", ["Direct", "FOMO", "Investment", "Follow Up", "Comparison"])
    f = df.copy()
    if project != "All":
        f = f[f["project"] == project]
    if code:
        f = f[f["code"].str.upper().str.replace(" ", "").str.contains(code.upper().replace(" ", ""), na=False)]
    if not f.empty:
        u = f.iloc[0].to_dict()
        base = whatsapp_message(u)
        if style == "FOMO":
            base += "\n\nالوحدة متاحة حسب آخر تحديث، ولو حضرتك مهتم الأفضل نتحرك بسرعة قبل ما حالتها تتغير."
        elif style == "Investment":
            base += "\n\nالميزة هنا إنك داخل على أصل عقاري في مشروع قائم بداتا واضحة وسعر محدد من الشيت."
        elif style == "Follow Up":
            base = f"حبيت أتابع مع حضرتك بخصوص وحدة {u.get('code','')} في {u.get('project','')}. لو لسه مهتم أقدر أبعتلك التفاصيل أو نرتب معاينة."
        elif style == "Comparison":
            base += "\n\nممكن كمان أقارنها لحضرتك بوحدات تانية قريبة في السعر أو المساحة."
        st.markdown(unit_card(u), unsafe_allow_html=True)
        st.text_area("Ready Message", base, height=240)
    else:
        st.info("Choose a unit to generate a message.")

elif page == "Project Stats":
    st.markdown('<div class="table-title">Project Stats</div>', unsafe_allow_html=True)
    stats = project_stats(df)
    st.dataframe(stats, use_container_width=True, hide_index=True)

elif page == "Register Sale":
    st.markdown('<div class="table-title">Register Sale</div><div class="help-text">Save a sale into the sales sheet.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    project = c1.selectbox("Project", projects[1:], key="sale_project")
    unit = c2.text_input("Unit Code")
    c3, c4 = st.columns(2)
    price = c3.text_input("Sale Price")
    client_name = c4.text_input("Client Name")
    c5, c6 = st.columns(2)
    phone = c5.text_input("Client Phone")
    sales_name = c6.text_input("Sales Name")
    notes = st.text_area("Notes")
    if st.button("Save Sale", use_container_width=True):
        if not unit or not client_name:
            st.error("Unit code and client name are required.")
        else:
            save_sale(project, unit, price, client_name, sales_name, phone, notes)
            st.success("Sale registered successfully.")
