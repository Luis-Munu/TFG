import pandas as pd
import scipy.stats
from sklearn.cluster import KMeans
from loader import find_zone_by_name
from unidecode import unidecode

"""
Processes the properties data, adding a great amount of metrics and statistics.
"""


def update_stats(properties, zones):
    """
    Update the statistics of the given properties DataFrame.
    
    Args:
    - properties: A pandas DataFrame containing the properties to update.
    - zones: A pandas DataFrame containing the zones to use for the update.
    
    Returns:
    - A pandas DataFrame containing the updated properties.
    """
    
    zones = zones.copy()
    zones['name'] = zones['name'].apply(lambda x: unidecode(x))
    zones['parent_zone'] = zones['parent_zone'].apply(lambda x: unidecode(x))
    # Add a new column to the properties DataFrame that maps each property to its corresponding zone
    properties["zone"] = properties.apply(lambda x: find_zone_by_name(zones, x["city"], x["address"]) if not isinstance(x["zone"], dict) else x["zone"], axis=1)
    # Update the dataframe with the new estimated metrics.
    properties["itp"] = properties.apply(lambda x: get_ITP(x), axis=1)
    properties["transfer_taxes"] = properties.apply(lambda x: transfer_taxes(x), axis=1)
    properties["insurance"] = properties.apply(lambda x: insurance(x), axis=1)
    properties["ibi"] = properties.apply(lambda x: IBI(x), axis=1)
    properties["community"] = properties.apply(lambda x: community(x), axis=1)
    properties["maintenance"] = properties.apply(lambda x: maintenance(x), axis=1)
    properties['ext_costs'] = properties.apply(lambda x: costs(x), axis=1)
    properties['exp_income'] = properties.apply(lambda x: incomes(x), axis=1)
    properties["zone"] = properties.apply(lambda x: x["zone"]["id"] if isinstance(x["zone"], dict) else x["zone"] if not pd.isna(x["zone"]) else 0, axis=1)
    
    properties = properties.sort_values(by=['exp_income'], ascending=True)
    return properties

def predict_property_cluster(properties, zones):
    """
    Predict the cluster of each property in the given properties DataFrame.
    
    Args:
    - properties: A pandas DataFrame containing the properties to cluster.
    - zones: A pandas DataFrame containing the zones to use for the clustering.
    
    Returns:
    - A pandas DataFrame containing the updated properties with the predicted clusters.
    """
    updated_props = pd.DataFrame(columns=properties.columns)
    for index, zone in zones.iterrows():
        props = pd.DataFrame(zone["properties"])
        if props.empty or zone["groups"] == 0:
            continue
        # Create a KMeans model with the number of clusters equal to the number of groups in the zone
        kmeans = KMeans(n_clusters=zone.groups, max_iter=1000).fit(props["price"].values.reshape(-1, 1))
        # Predict the cluster for each property in the zone
        props["group"] = kmeans.predict(props["price"].values.reshape(-1, 1))
        # Convert the group to a string and format it like this "numgroup/totalgroups" for example (1/3)
        props["group"] = props["group"].apply(lambda x: str(x + 1) + "/" + str(zone["groups"]))
        # Add a new percentile column, which returns the percentile of the price in the group
        props["percentile"] = props.apply(lambda x: scipy.stats.percentileofscore(props[props["group"] == x["group"]]["price"], x["price"]), axis=1)

        # Append the updated properties to the new DataFrame
        updated_props = updated_props.append(props)
    
    # Add an empty group and percentile to properties that have no suitable zone
    ungrouped_properties = properties[~properties.index.isin(updated_props.index)]
    ungrouped_properties["group"] = "0/0"
    ungrouped_properties["percentile"] = 0
    updated_props = updated_props.append(ungrouped_properties)

    # Sort the updated properties DataFrame by index
    updated_props = updated_props.sort_index()
    return updated_props

def incomes(house):
    """
    Calculate the expected monthly income for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the expected monthly income for the property.
    """
    # Get the rent zone for the given property
    zone = house["zone"]
    if not zone: return 0

    # Get the rent prices for the given property
    zone = zone["rent"]
    rooms = house["rooms"] if house["rooms"] != 0 else 1
    prices = []
    prices.append(zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"])
    prices.append(zone["pricepersqm"] * house["m2"])
    features = ["elevator", "terrace", "parking"]
    for feature in features:
        if house[feature] == "Yes": prices.append(zone[feature])

    # Calculate the weighted average of the rent prices for the given property
    total_weight = sum(range(1, len(prices) + 1))
    weighted_sum = sum([(i+1)*price for i, price in enumerate(sorted(prices))])
    return weighted_sum / total_weight

def get_ITP(house):
    """
    Calculate the ITP value for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the ITP value for the property.
    """
    # Calculate the ITP value for the given property
    if house["zone"]:
        return house["price"] * ITP_VALUES[house["zone"]["autonomous_community"]]
    return house["price"] * 0.08

def insurance(house):
    """
    Calculate the insurance cost for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the insurance cost for the property.
    """
    # Calculate the insurance cost for the given property
    return 120 + abs(house["m2"]-60) * 2.5

def IBI(house):
    """
    Calculate the IBI cost for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the IBI cost for the property.
    """
    # Calculate the IBI cost for the given property
    return house["price"] * 0.005

def community(house):
    """
    Calculate the community cost for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the community cost for the property.
    """
    # Calculate the community cost for the given property
    community_cost = max(30, house["price"] * 0.0011 - 21.7)/2
    
    return (community_cost + sum([10 if house[feature] == "Yes" else 0 for feature in ["pool", "elevator"]])) * 12

def maintenance(house):
    """
    Calculate the maintenance cost for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the maintenance cost for the property.
    """
    # Calculate the maintenance cost for the given property
    return 150 + abs(house["price"]-50000) * 0.001

def transfer_taxes(house):
    """
    Calculate the transfer taxes for the given property.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the transfer taxes for the property.
    """
    # Calculate the transfer taxes for the given property
    return house["price"] * 0.0085 + house["itp"]

def costs(house):
    """
    Calculate the total monthly costs for the given property without mortgage.
    
    Args:
    - house: A pandas Series containing the property information.
    
    Returns:
    - A float representing the total monthly costs for the property without mortgage.
    """
    # Calculate the total monthly costs for the given property without mortgage
    return (house["insurance"] + house["ibi"] + house["community"] + house["maintenance"]) / 12

# ITP_VALUES is a dictionary that maps each autonomous community to its corresponding ITP value
ITP_VALUES = {
    'Andalucía': 0.07, 'Aragón': 0.08,
    'Asturias': 0.08, 'Illes Balears': 0.08,
    'Canarias': 0.065, 'Cantabria': 0.1,
    'Castilla y León': 0.08, 'Castilla La Mancha': 0.09,
    'Cataluña': 0.1, 'Comunitat Valenciana': 0.1,
    'Extremadura': 0.08, 'Galicia': 0.09,
    'Madrid': 0.06, 'Murcia': 0.08,
    'Navarra': 0.06, 'País Vasco': 0.07,
    'La Rioja': 0.07, 'Ceuta': 0.06,
    'Melilla': 0.06
}