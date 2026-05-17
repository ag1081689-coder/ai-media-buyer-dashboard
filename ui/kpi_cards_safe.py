import streamlit as st


def render_kpi_cards(cards):
    """Render KPI cards safely using native Streamlit containers."""

    if not cards:
        return

    card_style = {
        'background-color': '#0f0f0f',
        'border': '1px solid rgba(255,122,0,.35)',
        'border-radius': '18px',
        'padding': '18px 20px',
        'min-height': '112px',
        'box-shadow': '0 14px 45px rgba(0,0,0,.45)',
        'margin-bottom': '14px',
    }

    for start in range(0, len(cards), 3):
        row_cards = cards[start:start + 3]
        cols = st.columns(len(row_cards))

        for col, card in zip(cols, row_cards):
            label = str(card.get('label', ''))
            value = str(card.get('value', ''))

            with col:
                with st.container(border=False):
                    st.markdown(f"**{label}**")
                    st.markdown(
                        f"<div style='font-size:30px;font-weight:900;line-height:1.1;color:#ffffff;white-space:normal;'>{value}</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    """
                    <style>
                    div[data-testid="stVerticalBlock"]:has(> div div[data-testid="stMarkdownContainer"] strong) {
                        background:#0f0f0f;
                        border:1px solid rgba(255,122,0,.35);
                        border-radius:18px;
                        padding:18px 20px;
                        min-height:112px;
                        box-shadow:0 14px 45px rgba(0,0,0,.45);
                        margin-bottom:14px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
