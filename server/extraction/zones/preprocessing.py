from json import load
from fuzzywuzzy import fuzz
from pymongo import MongoClient
import os

file_path = os.path.join(os.path.dirname(__file__), 'provinces.json')

# Load the provinces from a JSON file
provinces = {}
with open(file_path, 'r') as f:
    provinces = load(f)

def get_autonomous_community(province):
    """
    Compares the given province against all the provinces of each autonomous community.
    If the province is similar enough to one of the provinces of the autonomous community, returns the autonomous community.
    If no match is found, returns "Unknown".

    Parameters:
    province (str): The name of the province.

    Returns:
    str: The name of the autonomous community.
    """
    for com in provinces:
        for prov in com["provinces"]:
            if (fuzz.ratio(prov["name"], province) > 80): 
                return com["name"]
    return "Unknown"

def update_nonames(zone):
    """
    Updates the name of each subzone in the given zone if it doesn't have a name.

    Parameters:
    zone (dict): The zone to update.
    """
    if "subzones" in zone:
        for subzone in zone["subzones"].items():
            if "name" not in subzone[1]:
                subzone[1]["name"] = subzone[0]
            update_nonames(subzone[1])

def spread_autonomous_community(zone):
    """
    Updates the autonomous community of each subzone in the given zone to match the autonomous community of the parent zone.

    Parameters:
    zone (dict): The zone to update.
    """
    if "subzones" in zone:
        for subzone in zone["subzones"].values():
            subzone["autonomous_community"] = zone["autonomous_community"]
            spread_autonomous_community(subzone)

def load_zones():
    """
    Loads the zones from the MongoDB collection and returns them as a dictionary.

    Returns:
    dict: A dictionary of zones.
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    zones = {}
    for zone in collection.find():
        zone.pop("_id", None)
        zone = {k: v for k, v in zone.items() if v}
        if not zone: continue
        for province in zone.values():
            zones[province["name"]] = province
    return zones

def update_zones(zones):
    """
    Updates the given zones by calling update_nonames and spread_autonomous_community on each zone.

    Parameters:
    zones (dict): The zones to update.

    Returns:
    dict: The updated zones.
    """
    for zone in zones.values():
        update_nonames(zone)
        zone["autonomous_community"] = get_autonomous_community(zone["parent_zone"])
        spread_autonomous_community(zone)
    return zones

def zone_preprocessing():
    """
    Loads the zones, updates them, deletes the old collection, and inserts the updated zones into the MongoDB collection.
    """
    zones = load_zones()
    zones = update_zones(zones)
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    collection.delete_many({})
    collection.insert_one(zones)