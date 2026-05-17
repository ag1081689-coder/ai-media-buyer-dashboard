import html
import streamlit as st


def render_kpi_cards(cards):
    """Render responsive KPI cards with full visible values.

    cards: list of dicts with keys: label, value
    """
    items = []
    for card in cards:
        label = html.escape(str(card.get('label', '')))
        value = html.escape(str(card.get('value', '')))
        items.append(
            f"""
            <div class="custom-kpi-card">
                <div class="custom-kpi-label">{label}</div>
                <div class="custom-kpi-value">{value}</div>
            </div>
            """
        )

    st.markdown(
        """
        <style>
        .custom-kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
            gap: 16px;
            width: 100%;
            margin: 16px 0 12px;
        }
        .custom-kpi-card {
            background: #0f0f0f;
            border: 1px solid rgba(255,122,0,.35);
            border-radius: 18px;
            padding: 18px 20px;
            min-height: 118px;
            box-shadow: 0 14px 45px rgba(0,0,0,.45);
            overflow: visible;
        }
        .custom-kpi-label {
            color: #ffffff;
            font-size: 15px;
            line-height: 1.35;
            margin-bottom: 14px;
            white-space: normal;
            overflow: visible;
            text-overflow: clip;
        }
        .custom-kpi-value {
            color: #ffffff;
            font-size: 31px;
            font-weight: 900;
            line-height: 1.1;
            white-space: nowrap;
            overflow: visible;
            text-overflow: clip;
            letter-spacing: -0.5px;
        }
        @media (max-width: 1100px) {
            .custom-kpi-grid {
                grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
            }
            .custom-kpi-value {
                font-size: 27px;
            }
        }
        @media (max-width: 760px) {
            .custom-kpi-grid {
                grid-template-columns: 1fr 1fr;
            }
            .custom-kpi-value {
                font-size: 24px;
            }
        }
        </style>
        """
        + '<div class="custom-kpi-grid">'
        + ''.join(items)
        + '</div>',
        unsafe_allow_html=True,
    )
