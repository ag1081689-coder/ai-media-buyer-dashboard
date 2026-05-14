from config.rules import RULES


def diagnose(row):
    diagnoses = []

    spend = row.get('spend', 0)
    ctr = row.get('ctr', 0)
    frequency = row.get('frequency', 0)
    roas = row.get('roas', 0)
    lpv_rate = row.get('lpv_rate', 0)
    atc_rate = row.get('atc_rate', 0)
    purchase_rate = row.get('purchase_rate', 0)
    purchases = row.get('purchases', 0)

    if spend < RULES['min_spend_for_decision']:
        diagnoses.append('Not enough spend for confident decision')
        return diagnoses

    if ctr < RULES['low_ctr']:
        diagnoses.append('Hook / creative problem')

    if lpv_rate < RULES['low_lpv_rate']:
        diagnoses.append('Landing page speed or mismatch problem')

    if atc_rate < RULES['low_atc_rate']:
        diagnoses.append('Product page or offer problem')

    if purchase_rate < RULES['low_purchase_rate']:
        diagnoses.append('Checkout or trust problem')

    if frequency > RULES['high_frequency']:
        diagnoses.append('Creative fatigue detected')

    if roas > RULES['strong_roas'] and purchases >= RULES['min_purchases_to_scale']:
        diagnoses.append('Scaling-ready winner')

    return diagnoses
