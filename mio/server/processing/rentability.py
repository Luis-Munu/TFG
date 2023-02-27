import pandas as pd


def calculations(df):
    df['price_after_costs'] = df['price'] * 1.1
    return df
