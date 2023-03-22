import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from kneed import KneeLocator
from loader import find_zone_properties
from sklearn.cluster import KMeans


def update_stats(zones, properties):
    zoness = zones.to_dict(orient="index")
    for zone in zoness.values():
        zone_rentability(zone)
        draw_gaussian_prices(zone, properties)
    return pd.DataFrame.from_dict(zoness, orient="index")

def draw_gaussian_prices(zone, properties):

    plt.clf()
    props = find_zone_properties(zone, properties)
    if props is None: zone["groups"] = 0; return
    prices = props["price"].values

    sns.histplot(prices, kde=True, color='blue', alpha=0.5)
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Count')
    #plt.show()

    plt.clf()
    prices = prices.reshape(-1, 1)
    zone["groups"] = find_clusters(prices)
    print_centroids(prices, zone["groups"])

def find_clusters(prices):
    # use the elbow method to determine the optimal number of clusters
    sse = {}
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, max_iter=1000).fit(prices)
        sse[k] = kmeans.inertia_
    kl = KneeLocator(list(sse.keys()), list(sse.values()), curve="convex", direction="decreasing")
    return kl.elbow

def print_centroids(prices, n_clusters):
    # perform k-means clustering with the determined number of clusters
    kmeans = KMeans(n_clusters=n_clusters, max_iter=1000).fit(prices)
    centroids = kmeans.cluster_centers_

    # create a histogram of the values with the centroids overlaid
    plt.hist(prices, bins=20)
    plt.axvline(centroids[0], color='red')
    for centroid in centroids[1:]:
        plt.axvline(centroid, color='red', linestyle='--')
    #plt.show()


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
    sell_keys = [key for key in sell.keys() if not key.startswith("avg") and key not in ["price", "b100", "a100", "pricepersqm"]]
    rent_keys = [key for key in rent.keys() if not key.startswith("avg") and key not in ["price", "b100", "a100", "pricepersqm"]]
    avg_sqm = sell["avgsqm"]

    for key in sell_keys:
        zone["rentability_" + key] = rent[key] / (sell[key]*avg_sqm) * 100 if key in rent_keys else 0
    zone["avg_rentability"] = sum([zone["rentability_" + key] for key in sell_keys]) / len(sell_keys)
    #wma([rent[key] for key in sorted(rent_keys)]) / wma([sell[key] for key in sorted(sell_keys)])


