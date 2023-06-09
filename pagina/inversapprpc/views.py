import sys
from time import sleep

import Ice
import pandas as pd
from django.http import JsonResponse

from unidecode import unidecode
from . import RealEstate




#############################################################################################
# Connection establishment

args = sys.argv
args.append("--Ice.MessageSizeMax=104857600")
communicator = Ice.initialize(args)
properties = communicator.getProperties()
properties.setProperty("Ice.MessageSizeMax", "2097152")
base = communicator.stringToProxy("RealEstateServer:default -p 12545")
server = RealEstate.RealEstate_ice._M_RealEstate.RealEstateInterfacePrx.checkedCast(base)
if not server:
        raise RuntimeError("Invalid proxy")
    
#############################################################################################
# Dataset retrieval, done at the start to avoid having to do it every time a request is made

# Load the zone data from the RPC server
zone_dataset = pd.read_json(server.getZoneData(), )

# Load the property data from the RPC server
property_dataset = pd.read_json(server.getPropertyData(), orient='records')
    
#############################################################################################
# Endpoint functions

def get_zone_data(request):
    global zone_dataset
    autonomous_community = request.GET.get('autonomous_community', 'Extremadura')
    zones = zone_dataset[zone_dataset['autonomous_community'] == autonomous_community]
    return JsonResponse(zones.to_dict())

def get_property_data(request):
    global property_dataset
    salary = request.GET.get('salary', 3500)
    age = request.GET.get('age', 30)
    savings = request.GET.get('savings', 20000)
    max_age = request.GET.get('max_mortgage_age', 80)
    interest_rate = request.GET.get('interest_rate', 0.0523)
    autonomous_community = request.GET.get('autonomous_community', 'Extremadura')
    
    properties = update_properties(property_dataset, int(salary), int(age), int(savings), int(max_age), float(interest_rate), autonomous_community)
    return JsonResponse(properties)


#############################################################################################
# Property processing functions with frontend data

def community_filter(properties, autonomous_community):
    global zone_dataset

    zones = zone_dataset[zone_dataset['autonomous_community'] == autonomous_community]
    
    # now we have to get the list of all properties that are contained in these zones
    property_ids = [id for zone in zones['properties'] for id in zone]
    properties = properties[properties['_id'].isin(property_ids)]
    
    return properties

def update_properties(properties, salary, age, savings, max_age, interest_rate, autonomous_community):
    global zone_dataset
    
    #extract_real_communities()
    # apply unidecode to the parent_zone and name columns
    zones = zone_dataset.applymap(lambda x: unidecode(x) if isinstance(x, str) else x)
    
    # remove all duplicates by url
    properties = properties.drop_duplicates(subset=['url'])
    # filter the properties by the salary, currently disabled.
    
    # Filter the properties by the autonomous community, use check_community
    properties = community_filter(properties, autonomous_community)
    properties["amount_to_pay"] = properties.apply(lambda x: max(0, x["price"] - savings), axis=1)
    properties["total_mortgage"] = properties.apply(lambda x: total_mortgage(x, age, max_age, interest_rate, savings), axis=1)
    properties['monthly_mortgage'] = properties.apply(lambda x: mortgage(x, age, max_age, interest_rate), axis=1)
    properties['profitability'] = properties.apply(lambda x: profitability(x), axis=1)
    properties = properties.sort_values(by=['profitability'], ascending=False)
    

    return properties.to_dict()
    


def filter_by_mortgage(house, age, initial_amount):
    """Calculate the minimum amount required for a down payment based on the house price and the buyer's age"""
    if initial_amount < house["price"] * (0.2 + 0.015 * age):
        return False
    return True

def monthly_payment(amount, interest_rate, years):
    """Calculate the monthly payment for a mortgage based on the amount, interest rate, and number of years"""
    return max(0, (amount * (interest_rate / 12)) / (1 - (1 + interest_rate / 12) ** (-years * 12)))

def total_mortgage(house, age, max_age, interest_rate, savings):
    """Calculate the total mortgage payment for a house based on the amount left to pay, the buyer's age, and the interest rate"""
    years = min(abs(max_age - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years) * 12 * years + savings

def mortgage(house, age, max_age, interest_rate):
    """Calculate the monthly mortgage payment for a house based on the amount left to pay, the buyer's age, and the interest rate"""
    years = min(abs(max_age - age), 30)
    return monthly_payment(house["amount_to_pay"], interest_rate, years)

def profitability(house):
    """Calculate the profitability of a house based on expected income, monthly mortgage payment, external costs, price, transfer taxes, and initial amount"""
    net_monthly_income = house['exp_income'] - (house['monthly_mortgage'] + house['ext_costs'])
    return net_monthly_income * 12 / (house["price"] + house["transfer_taxes"]) * 100

def extract_real_communities():
    global zone_dataset, property_dataset
    
    # ultimately, we want to write on a txt file the list of autonomous communities whose zones have at least one property
    # first, we get the list of autonomous communities from the zone dataset
    autonomous_communities = zone_dataset['autonomous_community'].unique()
    # now we have to filter the properties by autonomous community
    winner_communities = []
    for community in autonomous_communities:
        if len(community_filter(property_dataset, community)) > 0:
            winner_communities.append(community)
    with open('real_communities.txt', 'w') as f:
        for community in winner_communities:
            f.write(community + '\n')
