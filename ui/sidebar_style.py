import streamlit as st


def apply_sidebar_style():
    st.markdown(
        '''
        <style>
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #101014 0%, #17171d 55%, #0b0b0f 100%) !important;
            border-right: 1px solid rgba(255,122,0,.22);
            box-shadow: 18px 0 50px rgba(0,0,0,.45);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 26px;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] span,
        section[data-testid="stSidebar"] div {
            color: #f7f7f7 !important;
        }

        section[data-testid="stSidebar"] [role="radiogroup"] {
            background: rgba(255,255,255,.035);
            border: 1px solid rgba(255,122,0,.14);
            border-radius: 18px;
            padding: 10px;
            margin-bottom: 18px;
        }

        section[data-testid="stSidebar"] [role="radio"] {
            padding: 10px 12px !important;
            border-radius: 13px !important;
            margin: 3px 0 !important;
            transition: .2s ease;
        }

        section[data-testid="stSidebar"] [role="radio"]:hover {
            background: rgba(255,122,0,.10) !important;
        }

        section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
            background: linear-gradient(135deg, rgba(255,122,0,.28), rgba(255,159,28,.12)) !important;
            border: 1px solid rgba(255,122,0,.45) !important;
            box-shadow: 0 10px 28px rgba(255,122,0,.10);
        }

        section[data-testid="stSidebar"] [data-baseweb="select"] > div {
            background: #0d0d12 !important;
            border: 1px solid rgba(255,122,0,.25) !important;
            border-radius: 14px !important;
            min-height: 52px;
        }

        section[data-testid="stSidebar"] .stButton button {
            width: 100%;
            border-radius: 14px !important;
            min-height: 54px;
            background: linear-gradient(135deg, #ff7a00, #ffb347) !important;
            color: #050505 !important;
            font-weight: 900 !important;
            box-shadow: 0 18px 40px rgba(255,122,0,.22);
        }

        .sidebar-brand-card {
            background: radial-gradient(circle at 80% 20%, rgba(255,122,0,.28), transparent 35%), #0d0d12;
            border: 1px solid rgba(255,122,0,.32);
            border-radius: 22px;
            padding: 18px 16px;
            margin-bottom: 18px;
            box-shadow: 0 18px 40px rgba(0,0,0,.35);
        }

        .sidebar-brand-title {
            color: #ff9f1c !important;
            font-size: 18px;
            font-weight: 900;
            letter-spacing: -.2px;
            margin-bottom: 6px;
        }

        .sidebar-brand-subtitle {
            color: #ffffff !important;
            font-size: 12px;
            opacity: .82;
            line-height: 1.5;
        }
        </style>
        ''',
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.sidebar.markdown(
        '''
        <div class="sidebar-brand-card">
            <div class="sidebar-brand-title">AI Media Buyer OS</div>
            <div class="sidebar-brand-subtitle">Control center for spend, ROAS, tracking, and daily actions.</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )
