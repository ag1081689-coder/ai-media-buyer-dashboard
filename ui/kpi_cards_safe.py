import streamlit as st


def render_kpi_cards(cards):
    """Render KPI cards safely using native Streamlit containers."""

    if not cards:
        return

    for start in range(0, len(cards), 3):
        row_cards = cards[start:start + 3]
        cols = st.columns(len(row_cards))

        for col, card in zip(cols, row_cards):
            label = str(card.get('label', ''))
            value = str(card.get('value', ''))

            with col:
                st.markdown(
                    f'''
                    <div style="
                        background:#0f0f0f;
                        border:1px solid rgba(255,122,0,.35);
                        border-radius:18px;
                        padding:18px 20px;
                        min-height:112px;
                        box-shadow:0 14px 45px rgba(0,0,0,.45);
                        margin-bottom:14px;
                    ">
                        <div style="
                            color:#ffffff;
                            font-size:15px;
                            line-height:1.35;
                            margin-bottom:14px;
                            white-space:normal;
                        ">{label}</div>

                        <div style="
                            color:#ffffff;
                            font-size:30px;
                            font-weight:900;
                            line-height:1.1;
                            white-space:normal;
                        ">{value}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True,
                )
