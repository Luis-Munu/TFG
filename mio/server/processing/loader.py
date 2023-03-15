import json

import pandas as pd
from pymongo import MongoClient

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