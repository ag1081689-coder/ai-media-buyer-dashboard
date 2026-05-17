import pandas as pd


def load_report(path='meta_ads_report.csv'):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()
