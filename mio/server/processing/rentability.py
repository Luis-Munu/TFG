import json
import math

import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['real_estate']
dbproperties = db['properties']
dbzones = db['zones']


def calculations(properties, zones, age, initial_amount):

    # filter rows if filter_by_mortgage returns False
    properties = properties[properties.apply(lambda x: filter_by_mortgage(x, age, initial_amount), axis=1)]
    if properties.empty:
        return properties
    properties["transfer_taxes"] = properties.apply(lambda x: calculate_transfer_taxes(x, zones), axis=1)
    properties["insurance"] = properties.apply(lambda x: calculate_insurance(x), axis=1)
    properties["ibi"] = properties.apply(lambda x: calculate_IBI(x), axis=1)
    properties["community"] = properties.apply(lambda x: calculate_community(x), axis=1)
    properties["maintenance"] = properties.apply(lambda x: calculate_maintenance(x), axis=1)
    properties["costs"] = properties.apply(lambda x: calculate_costs(x), axis=1)
    properties["amount_to_pay"] = properties.apply(lambda x: max(0, x["price"] - initial_amount), axis=1)
    properties["total_mortgage"] = properties.apply(lambda x: calculate_total_mortgage(x, age, initial_amount, 0.03), axis=1)
    properties['monthly_mortgage'] = properties.apply(lambda x: calculate_mortgage(x, age, initial_amount, 0.03), axis=1)
    properties['incomes'] = properties.apply(lambda x: calculate_incomes2(x, zones), axis=1)
    properties['costs'] = properties.apply(lambda x: calculate_costs(x), axis=1)
    properties['rentability'] = properties.apply(lambda x: calculate_rentability(x, initial_amount), axis=1)
    properties = properties.sort_values(by=['rentability'], ascending=False)
    return properties

def find_zone_by_name(zones, city, name):
    for zone in zones.values():
        if zone["name"] == name and zone["parent_zone"] == city:
            return zone
        if "subzones" in zone:
            subzone = find_zone_by_name(zone["subzones"], city, name)
            if subzone:
                return subzone
    return None

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

def calculate_rentability(house, initial_amount):
    # paso por paso como los de la clase xd
    monthly_income = house['incomes']
    monthly_costs = house['monthly_mortgage'] + house['costs']
    net_monthly_income = monthly_income - monthly_costs
    return net_monthly_income * 12 / (min(initial_amount, house["price"] + house["transfer_taxes"])) * 100

def calculate_incomes1(house, zones):
    zone = find_zone_by_name(zones, house["city"])
    if not zone: return -1

    zone = zone["rent"]
    # FIXME
    rooms = house["rooms"] if house["rooms"] != 0 else 1
    sqm = zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"]
    return sqm

def calculate_incomes2(house, zones):
    zone = find_zone_by_name(zones, house["city"], house["address"])
    if not zone: return -1
    zone = zone["rent"]

    rooms = house["rooms"] if house["rooms"] != 0 else 1
    price_by_rooms = zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"]
    price_by_sqms = zone["pricepersqm"] * house["m2"]
    price = max(price_by_rooms, price_by_sqms)
    features = ["elevator", "terrace", "parking"]
    for feature in features:
        if house[feature] == "Yes": price = (price + zone[feature])/2

    return price

def calculate_monthly_payment(amount, interest_rate, years):
    return max(0, (amount * interest_rate * (1 + interest_rate) ** years / ((1 + interest_rate) ** years - 1)) / 12)

def calculate_total_mortgage(house, age, initial_amount, interest_rate):
    years = min(abs(70 - age), 30)
    return calculate_monthly_payment(house["amount_to_pay"], interest_rate, years) * 12 * years

def calculate_mortgage(house, age, initial_amount, interest_rate):
    years = min(abs(70 - age), 30)
    return calculate_monthly_payment(house["amount_to_pay"], interest_rate, years)

def filter_by_mortgage(house, age, initial_amount):
    if initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    return True

"""def filter_by_mortgage(house, age, initial_amount, interest_rate, salary):
    if initial_amount > house["price"]:
        return True
    elif initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    elif salary < calculate_mortgage(house, age, initial_amount, interest_rate) / 12 * 0.3:
        return False
    return True"""

def get_ITP(city, zones):
    return 0.05

def calculate_insurance(house):
    return 100 + abs(house["m2"]-60) * 2.5

def calculate_IBI(house):
    return house["m2"] * 1.5

def calculate_community(house):
    community_cost = max(10, house["price"] * 0.0011 - 21.7)/2
    return (community_cost + sum([10 if house[feature] == "Yes" else 0 for feature in ["pool", "elevator"]]))

def calculate_maintenance(house):
    return 150 + abs(house["price"]-50000) * 0.001

def calculate_transfer_taxes(house, zones):
    return house["price"] * 0.10 # + get_ITP(house["city"], zones)

def calculate_costs(house):
    return (house["insurance"] + house["ibi"] + house["community"] + house["maintenance"]) / 12

def load_properties():
    properties = pd.DataFrame(list(dbproperties.find()))
    properties = properties.drop_duplicates(subset=['url'])

    return properties

def load_from_json():
    with open('zones.json', 'r') as file:
        return json.load(file)

def save_to_csv(properties):
    properties.to_csv("propertiess.csv")

def main():
    properties = load_properties()
    zones = load_from_json()
    #update_avgsqm(zones)
    df = calculations(properties, zones, 30, 100000)
    save_to_csv(df)

if __name__ == "__main__":
    main()
