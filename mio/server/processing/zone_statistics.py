import pandas as pd


def update_stats(zones):
    # zones is a pandas dataframe, we have to convert it to a dictionary to use the recursive function
    zoness = zones.to_dict(orient="index")
    for zone in zoness.values():
        zone_rentability(zone)
    return pd.DataFrame.from_dict(zoness, orient="index")
"""
def apply_to_subzones(zone, func):
    if "subzones" in zone:
        for subzone in zone["subzones"].values():
            func(subzone)
            apply_to_subzones(subzone, func)"""

def wma(list):
    total_weight = sum(range(1, len(list) + 1))
    weighted_sum = sum([weight * value for weight, value in zip(range(1, len(list) + 1), sorted(list))])
    return weighted_sum / total_weight

def zone_rentability(zone):
    sell = zone["sell"]; rent = zone["rent"]
    sell_keys = [key for key in sell.keys() if not key.startswith("avg") and key != "price"]
    rent_keys = [key for key in rent.keys() if not key.startswith("avg") and key != "price"]
    avg_sqm = sell["avgsqm"]

    for key in sell_keys:
        zone["rentability_" + key] = rent[key] / (sell[key]*avg_sqm) * 100 if key in rent_keys else 0
    zone["avg_rentability"] = wma([rent[key] for key in sorted(rent_keys)]) / wma([sell[key] for key in sorted(sell_keys)]) * 100


