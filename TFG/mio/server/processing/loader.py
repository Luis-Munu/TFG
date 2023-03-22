import json

import pandas as pd
from pymongo import MongoClient
from unidecode import unidecode

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['real_estate']
dbproperties = db['properties']
dbzones = db['zones']

def load_properties():
    properties = pd.DataFrame(list(dbproperties.find()))
    properties = properties.drop_duplicates(subset=['url'])
    return properties

"""def load_zones():
    with open('zones.json', 'r') as file:
        return json.load(file)"""

def load_zones():
    return pd.read_json('zoness.json')

def split_by_type(dataframe):
    # split properties by unique types in different csv files
    types = dataframe["type"].unique()
    for type in types:
        dataframe[dataframe["type"] == type].to_csv(type + ".csv")

def find_zone_by_name(zones, city, name):
    zone = zones[(zones["name"].apply(unidecode) == unidecode(name)) & (zones["parent_zone"].apply(unidecode) == unidecode(city))]
    if len(zone) == 0: return None
    
    zone = zone.values[0]
    return {
    "name": zone[0],
    "parent_zone": zone[1],
    "sell": zone[2],
    "rent": zone[3],
    "subzones": zone[4]
}

def find_zone_properties(zone, properties):
    props =  properties[(properties["city"].apply(unidecode) == unidecode(zone["parent_zone"])) & (properties["address"].apply(unidecode) == unidecode(zone["name"]))]
    if len(props) == 0: return None
    return props

def save_to_csv(dataframe, name):
    dataframe.to_csv(name + "_statistics.csv")


"""
def update_avgsqm(zones):
    for zone in zones.values():
        if isinstance(zone, dict) and "rent" in zone:
            zone["rent"]["sqm1rooms"] = zone["rent"]["sqm1rooms"] / 1000
            zone["rent"]["sqm2rooms"] = zone["rent"]["sqm2rooms"] / 1000
            zone["rent"]["sqm3rooms"] = zone["rent"]["sqm3rooms"] / 1000
            zone["rent"]["sqm4rooms"] = zone["rent"]["sqm4rooms"] / 1000
        if isinstance(zone, dict) and "subzones" in zone:
            update_avgsqm(zone["subzones"])"""