import pandas as pd
from math import isnan
from loader import update_properties
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from kneed import KneeLocator

""" Processes the zones data, adding the following statistics:
    - averages of most of the important features of the properties
    - profitability of the zone
    - number of groups of properties in the zone
"""


def update_stats(zones, properties):
    """
    Updates the statistics for each zone based on the given properties.

    Args:
        zones (pandas.DataFrame): The zones to update.
        properties (pandas.DataFrame): The properties to use for the update.

    Returns:
        pandas.DataFrame: The updated zones.
    """
    zones = update_properties(zones, properties)
    zoness = zones.to_dict(orient="index")
    for zone in zoness.values():
        zone.update(zone_profitability(zones, zone))
        zone.update(update_averages(zone, properties))
        
        draw_gaussian_prices(zone)
    return pd.DataFrame.from_dict(zoness, orient="index")


def draw_gaussian_prices(zone):
    """
    Draws a histogram of the prices for the given zone and determines the optimal number of clusters.

    Args:
        zone (dict): The zone to draw the histogram for.
    """
    plt.clf()
    props = pd.DataFrame(zone["properties"])
    # if empty, return 0 groups
    if len(props) == 0: zone["groups"] = 0; return
    prices = props["price"].values.reshape(-1, 1)
    if len(prices) < 10: zone["groups"] = 1; return

    sns.histplot(prices, kde=True, color='blue', alpha=0.5)
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Count')

    plt.clf()
    zone["groups"] = find_clusters(prices)


def find_clusters(prices):
    """
    Determines the optimal number of clusters for the given prices using the elbow method.

    Args:
        prices (numpy.ndarray): The prices to cluster.

    Returns:
        int: The optimal number of clusters.
    """
    sse = {}
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, max_iter=1000).fit(prices)
        sse[k] = kmeans.inertia_
    kl = KneeLocator(list(sse.keys()), list(sse.values()), curve="convex", direction="decreasing")
    return kl.elbow


def zone_profitability(zones, zone):
    """
    Calculates the profitability of the given zone based on the sell and rent prices.

    Args:
        zones (pandas.DataFrame): The zones to use for the calculation.
        zone (dict): The zone to calculate the profitability for.

    Returns:
        dict: The updated zone with the profitability values.
    """
    sell = zone["sell"]; rent = zone["rent"]
    
    sell_keys = [key for key in sell.keys() if not key.startswith("avg") and key not in ["price", "b100", "a100", "pricepersqm"]]
    rent_keys = [key for key in rent.keys() if not key.startswith("avg") and key not in ["price", "b100", "a100", "pricepersqm"]]
    avg_sqm = sell["avgsqm"]
    for key in sell_keys:
        try:
            if (not isnan(sell[key]) and key in rent_keys and not isnan(rent[key])) and sell[key] > 0 and rent[key] > 0:
                zone["roi_" + key] = rent[key] * 12 / (sell[key] * avg_sqm) * 100
            else:
                zone["roi_" + key] = 0
        except:
            zone["roi_" + key] = 0
    zone["avg_roi"] = sum([zone["roi_" + key] for key in sell_keys]) / len(sell_keys)
    return zone

    
def normalize_binary_stat(properties, key):
    """
    Normalizes the binary stat for the given key in the properties.

    Args:
        properties (pandas.DataFrame): The properties to use for the normalization.
        key (str): The key to normalize.

    Returns:
        str: The normalized binary stat.
    """
    stat = properties[key].apply(lambda x: 1 if x == "Yes" else 0)
    return "Yes" if stat.mean() > 0.5 else "No"
    
def update_averages(zone, properties):
    """
    Updates the averages for the given zone based on the properties.

    Args:
        zone (dict): The zone to update.
        properties (pandas.DataFrame): The properties to use for the update.

    Returns:
        dict: The updated zone.
    """
    own_properties = zone["properties"]
    keys = ['price', 'age', 'rooms', 'bathrooms', 'm2', 'elevator', 'floor', 'balcony', 'terrace', 
    'heating', 'air_conditioning', 'parking', 'pool', 'itp', 'transfer_taxes', 'insurance', 'ibi', 
    'community', 'maintenance', 'ext_costs', 'exp_income']
    if own_properties:
        own_properties_df = pd.DataFrame(own_properties)
        for key in keys:
            if key in ["elevator", "balcony", "terrace", "heating", "air_conditioning", "parking", "pool"]:
                zone[f"avg_{key}"] = normalize_binary_stat(own_properties_df, key)
            else:
                zone[f"avg_{key}"] = pd.to_numeric(own_properties_df[key], errors='coerce').mean(skipna=True)
        own_properties_df['ppsqm'] = own_properties_df.apply(lambda row: row['price'] / row['m2'] if row['m2'] != 0 else 0, axis=1)
        zone['avg_ppsqm'] = own_properties_df['ppsqm'].mean(skipna=True)
    else:
        for key in keys + ["ppsqm"]:
            if key in ["elevator", "balcony", "terrace", "heating", "air_conditioning", "parking", "pool"]:
                zone[f"avg_{key}"] = "No"
            else:
                zone[f"avg_{key}"] = 0
    return zone