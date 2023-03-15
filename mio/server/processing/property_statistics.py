from unidecode import unidecode


def update_stats(properties, zones, age, initial_amount):

    properties = properties[properties.apply(lambda x: filter_by_mortgage(x, age, initial_amount), axis=1)]
    if properties.empty:
        return properties
    properties["transfer_taxes"] = properties.apply(lambda x: transfer_taxes(x, zones), axis=1)
    properties["insurance"] = properties.apply(lambda x: insurance(x), axis=1)
    properties["ibi"] = properties.apply(lambda x: IBI(x), axis=1)
    properties["community"] = properties.apply(lambda x: community(x), axis=1)
    properties["maintenance"] = properties.apply(lambda x: maintenance(x), axis=1)
    properties["costs"] = properties.apply(lambda x: costs(x), axis=1)
    properties["amount_to_pay"] = properties.apply(lambda x: max(0, x["price"] - initial_amount), axis=1)
    properties["total_mortgage"] = properties.apply(lambda x: total_mortgage(x, age, 0.03), axis=1)
    properties['monthly_mortgage'] = properties.apply(lambda x: mortgage(x, age, 0.03), axis=1)
    properties['incomes'] = properties.apply(lambda x: incomes2(x, zones), axis=1)
    properties['costs'] = properties.apply(lambda x: costs(x), axis=1)
    properties['rentability'] = properties.apply(lambda x: rentability(x, initial_amount), axis=1)
    properties = properties.sort_values(by=['rentability'], ascending=False)
    return properties

def find_zone_by_name(zones, city, name):
    # zones is a pandas dataframe, return the zone whose zone name = name and parent_zone = city
    # apply unidecode to zones["name"] and zones["parent_zone"] to avoid errors
    # apply unidecode fucker
    zone = zones[(zones["name"].apply(unidecode) == unidecode(name)) & (zones["parent_zone"].apply(unidecode) == unidecode(city))]
    # if no zone is found, return None
    if len(zone) == 0:
        return None
    zone = zone.values[0]
    return {
    "name": zone[0],
    "parent_zone": zone[1],
    "sell": zone[2],
    "rent": zone[3],
    "subzones": zone[4]
}
    
"""
def find_zone_by_name(zones, city, name):
    for zone in zones.values():
        if zone["name"] == name and zone["parent_zone"] == city:
            return zone
        if "subzones" in zone:
            subzone = find_zone_by_name(zone["subzones"], city, name)
            if subzone:
                return subzone
    return None"""

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

def rentability(house, initial_amount):
    if house["url"] == "/es/comprar/vivienda/caceres-capital/mejostilla/176099979/d?from=list":
        print("test")
    monthly_income = house['incomes']
    monthly_costs = house['monthly_mortgage'] + house['costs']
    net_monthly_income = monthly_income - monthly_costs
    return net_monthly_income * 12 / (min(initial_amount, house["price"] + house["transfer_taxes"])) * 100

"""def incomes1(house, zones):
    zone = find_zone_by_name(zones, house["city"])
    if not zone: return -1

    zone = zone["rent"]
    rooms = house["rooms"] if house["rooms"] != 0 else 1
    sqm = zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"]
    return sqm"""

def incomes2(house, zones):
    zone = find_zone_by_name(zones, house["city"], house["address"])
    if not zone: return -1
    zone = zone["rent"]

    if house["url"] == "/es/comprar/vivienda/caceres-capital/mejostilla/176099979/d?from=list":
        print("test")

    rooms = house["rooms"] if house["rooms"] != 0 else 1
    prices = []
    prices.append(zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"])
    prices.append(zone["pricepersqm"] * house["m2"])
    features = ["elevator", "terrace", "parking"]
    for feature in features:
        if house[feature] == "Yes": prices.append(zone[feature])
    # devuelve la WMA de la lista
    total_weight = sum(range(1, len(prices) + 1))
    weighted_sum = sum([weight * value for weight, value in zip(range(1, len(prices) + 1), sorted(prices))])
    return weighted_sum / total_weight
    return sorted(prices)[len(prices) // 2]

    """price_by_rooms = zone[f"sqm{rooms}rooms"] if rooms < 4 else zone["sqm4rooms"]
    price_by_sqms = zone["pricepersqm"] * house["m2"]
    price = max(price_by_rooms, price_by_sqms)
    features = ["elevator", "terrace", "parking"]
    for feature in features:
        if house[feature] == "Yes": price = (price + zone[feature])/2"""

    return price

def monthly_payment(amount, interest_rate, years):
    return max(0, (amount * interest_rate * (1 + interest_rate) ** years / ((1 + interest_rate) ** years - 1)) / 12)

def total_mortgage(house, age, interest_rate):
    years = min(abs(70 - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years) * 12 * years

def mortgage(house, age, interest_rate):
    years = min(abs(70 - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years)

def filter_by_mortgage(house, age, initial_amount):
    if initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    return True

"""def filter_by_mortgage(house, age, initial_amount, interest_rate, salary):
    if initial_amount > house["price"]:
        return True
    elif initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    elif salary < mortgage(house, age, initial_amount, interest_rate) / 12 * 0.3:
        return False
    return True"""

def get_ITP(city, zones):
    return 0.05

def insurance(house):
    return 100 + abs(house["m2"]-60) * 2.5

def IBI(house):
    return house["m2"] * 1.5

def community(house):
    community_cost = max(10, house["price"] * 0.0011 - 21.7)/2
    return (community_cost + sum([10 if house[feature] == "Yes" else 0 for feature in ["pool", "elevator"]]))

def maintenance(house):
    return 150 + abs(house["price"]-50000) * 0.001

def transfer_taxes(house, zones):
    return house["price"] * 0.10 # + get_ITP(house["city"], zones)

def costs(house):
    if house["url"] == "/es/comprar/vivienda/caceres-capital/mejostilla/176099979/d?from=list":
        print("test")
    return (house["insurance"] + house["ibi"] + house["community"] + house["maintenance"]) / 12

"""
def main():
    properties = load_properties()
    zones = load_from_json()
    #update_avgsqm(zones)
    df = calculations(properties, zones, 60, 100000)
    save_to_csv(df)

if __name__ == "__main__":
    main()
"""