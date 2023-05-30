import pandas as pd
from pymongo import MongoClient
from unidecode import unidecode

"""
This module provides functionality for loading and processing real estate data.
"""

# Establish a connection to MongoDB
client = MongoClient('localhost', 27017)
db = client['real_estate']
dbproperties = db['properties']; dbprocessedproperties = db['processed_properties']
dbzones = db['zones']; dbprocessedzones = db['processed_zones']

zone_cache = {}

###### Dataset loading ######

def load_properties():
    """
    Loads the real estate properties from the MongoDB database and returns them as a pandas DataFrame.

    Returns:
        pandas.DataFrame: The real estate properties.
    """
    properties = pd.DataFrame(list(dbproperties.find()))
    properties = properties.drop_duplicates(subset=['url'])
    properties["city"] = properties["city"].apply(unidecode)
    properties["address"] = properties["address"].apply(unidecode)
    return properties

def load_zones():
    """
    Loads the real estate zones from the MongoDB database and returns them as a pandas DataFrame.

    Returns:
        pandas.DataFrame: The real estate zones.
    """
    zones = [location for location in dbzones.find()][0]
    zones.pop('_id')
    zones = find_properties(zones, load_properties())
    
    def data_conv(zone):
        total = {}
        total[zone["name"] + ", " + zone["parent_zone"]] = zone

        if "subzones" in zone:
            for subzone in zone["subzones"].values():
                total.update(data_conv(subzone))
            total[zone["name"] + ", " + zone["parent_zone"]]["subzones"] = [subzone["name"] for 
                                                                            subzone in zone["subzones"].values()]

        return total
    
    zones = {key: value for zone in zones.values() for key, value in data_conv(zone).items()}
    zones = handle_nan_values(zones)
    
    zones = pd.DataFrame.from_dict(zones, orient="index")
    # create a new id column with an unique id for each zone
    zones["id"] = zones.apply(lambda row: hash(row["name"] + row["parent_zone"] + row["autonomous_community"]), axis=1)
    
    return zones

###### Dataset processing ######

def handle_nan_values(zones):
    """
    Fills NaN values in the zones DataFrame with default values.

    Args:
        zones (pandas.DataFrame): The zones DataFrame.

    Returns:
        pandas.DataFrame: The zones DataFrame with NaN values filled.
    """
    first_zone = list(zones.values())[0]
    sell_keys = [key for key in first_zone["sell"].keys()]
    rent_keys = [key for key in first_zone["rent"].keys()]
    for zone in zones.values():
        zone.setdefault("sell", {key: 0 for key in sell_keys})
        zone.setdefault("rent", {key: 0 for key in rent_keys})
        zone.setdefault("subzones", [])
        
    return zones

def update_properties(zones, properties):
    """
    Updates the properties for each zone in the zones list.

    Args:
        zones (pd.Dataframe): The zones to update.
        properties (pd.Dataframe): The properties to use for the update.

    Returns:
        zones (pd.Dataframe): The updated zones with a list of properties for each zone.
    """
    own_properties = properties.to_dict("records")
    zone_dict = {prop["_id"]: prop for prop in own_properties}
    zones["properties"] = zones["properties"].apply(lambda prop_ids: [zone_dict[prop_id] for prop_id in prop_ids])
    return zones

def link_datasets(properties, zones):
    """
    Links the properties and zones DataFrames by adding a 'zone' column to the properties DataFrame.

    Args:
        properties (pandas.DataFrame): The properties DataFrame.
        zones (pandas.DataFrame): The zones DataFrame.

    Returns:
        pandas.DataFrame: The updated properties DataFrame.
    """
    for _, zone in zones.iterrows():
        if "properties" in zone:
            for property in zone["properties"]:
                properties.loc[properties["_id"] == property, "zone"] = zone

    return properties


###### Auxiliary functions ######
# These functions are used to find objects of the other dataset.

def find_properties(zones, properties):
    """
    Finds the properties for each zone in the zones DataFrame and stores their id in a list for each zone.

    Args:
        zones (pandas.DataFrame): The zones DataFrame.
        properties (pandas.DataFrame): The properties DataFrame.

    Returns:
        pandas.DataFrame: The updated zones DataFrame.
    """
    for zone in zones.values():
        if "subzones" in zone and len(zone["subzones"]) > 0:
            zone["subzones"] = find_properties(zone["subzones"], properties)
        
        matching_properties = properties[(properties["city"] == unidecode(zone["parent_zone"])) & (properties["address"] == unidecode(zone["name"]))]
        
        if "properties" not in zone:
            zone["properties"] = []
        zone["properties"].extend(matching_properties["_id"].tolist())
        
        for subzone in zone.get("subzones", {}).values():
            if "properties" in subzone and len(subzone["properties"]) > 0:
                zone["properties"].extend(subzone["properties"])
            
    return zones

def find_zone(zones, property):
    """
    Finds the zone for a given property.

    Args:
        zones (pandas.DataFrame): The zones DataFrame.
        property (pandas.DataFrame): The property DataFrame.

    Returns:
        pandas.DataFrame: The zone DataFrame.
    """
    prop_zones =  zones.loc[zones['properties'].apply(lambda x: any(prop["url"] == property["url"] for prop in x)), :]
    if prop_zones.empty:
        return None
    
    names = prop_zones["name"]
    return prop_zones[prop_zones["subzones"].apply(lambda x: not any(name in x for name in names))]

def find_zone_by_name(zones, city, name):
    """
    Finds the zone for a given city and name.

    Args:
        zones (pandas.DataFrame): The zones DataFrame.
        city (str): The city name.
        name (str): The zone name.

    Returns:
        dict: The zone information.
    """
    key = f"{unidecode(name)}_{unidecode(city)}"
    if key in zone_cache:
        return zone_cache[key]

    name_uni = unidecode(name); city_uni = unidecode(city)
    zone = zones.query("name == @name_uni and parent_zone == @city_uni")
    if zone.empty:
        zone = zones.query(f"(name == @name_uni or parent_zone == @name_uni) and parent_zone == @city_uni")
        if zone.empty:
            zone_cache[key] = None
            return None

    zone = zone.iloc[0]
    result = zone.to_dict()
    zone_cache[key] = result
    return result

###### Save functions ######

def save_to_csv(dataframe, name):
    """
    Saves a DataFrame to a CSV file.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to save.
        name (str): The name of the file to save.
    """
    dataframe.to_csv(name + "_statistics.csv")
    
def save_properties(properties):
    """
    Saves the processed properties to the MongoDB database.

    Args:
        properties (pandas.DataFrame): The processed properties to save.
    """
    dbprocessedproperties.delete_many({})
    #properties = properties.drop('_id', axis=1)
    properties = properties.drop_duplicates(subset=['_id'])
    dbprocessedproperties.insert_many(properties.to_dict('records'))
    
def save_zones(zones):
    """
    Saves the processed zones to the MongoDB database.

    Args:
        zones (pandas.DataFrame): The processed zones to save.
    """
    dbprocessedzones.delete_many({})
    dbprocessedzones.insert_many(zones.to_dict('records'))