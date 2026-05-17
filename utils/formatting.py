def format_money(value):
    try:
        value = float(value)
    except:
        value = 0

    if value >= 1000000:
        return f'{value/1000000:.1f}M EGP'

    if value >= 1000:
        return f'{value/1000:.1f}K EGP'

    return f'{value:,.0f} EGP'
