import html
import streamlit as st


def render_kpi_cards(cards):
    """Render responsive KPI cards with full visible values."""

    items = []

    for card in cards:
        label = html.escape(str(card.get('label', '')))
        value = html.escape(str(card.get('value', '')))

        items.append(
            f'''
            <div class="custom-kpi-card">
                <div class="custom-kpi-label">{label}</div>
                <div class="custom-kpi-value">{value}</div>
            </div>
            '''
        )

    kpi_html = f'''
    <style>
    .custom-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
        gap: 16px;
        width: 100%;
        margin: 16px 0 12px;
    }}

    .custom-kpi-card {{
        background: #0f0f0f;
        border: 1px solid rgba(255,122,0,.35);
        border-radius: 18px;
        padding: 18px 20px;
        min-height: 112px;
        box-shadow: 0 14px 45px rgba(0,0,0,.45);
    }}

    .custom-kpi-label {{
        color: #ffffff;
        font-size: 15px;
        line-height: 1.35;
        margin-bottom: 14px;
        white-space: normal;
    }}

    .custom-kpi-value {{
        color: #ffffff;
        font-size: 30px;
        font-weight: 900;
        line-height: 1.1;
        white-space: nowrap;
        letter-spacing: -0.5px;
    }}

    @media (max-width: 1100px) {{
        .custom-kpi-grid {{
            grid-template-columns: repeat(auto-fit, minmax(165px, 1fr));
        }}
        .custom-kpi-value {{
            font-size: 26px;
        }}
    }}

    @media (max-width: 760px) {{
        .custom-kpi-grid {{
            grid-template-columns: 1fr 1fr;
        }}
        .custom-kpi-value {{
            font-size: 23px;
        }}
    }}
    </style>

    <div class="custom-kpi-grid">
        {''.join(items)}
    </div>
    '''

    st.markdown(kpi_html, unsafe_allow_html=True)
