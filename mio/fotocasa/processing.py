import pandas as pd
import pymongo
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['fotocasa']
collection = db['properties']

def explode_attributes(buildings):
    rooms = []
    bathrooms = []
    m2 = []
    elevator = []
    floor = []
    balcony = []
    terrace = []
    heating = []
    air_conditioning = []
    parking = []
    pool = []
    for building in buildings:
        index = [i for i, x in enumerate(building['attributes']) if "hab" in x]
        rooms.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 'Unknown')
        index = [i for i, x in enumerate(building['attributes']) if "baño" in x]
        bathrooms.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 'Unknown')
        index = [i for i, x in enumerate(building['attributes']) if "m²" in x]
        m2.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 'Unknown')
        index = [i for i, x in enumerate(building['attributes']) if "Planta" in x]
        floor.append(building['attributes'][index[0]][0] if len(index) > 0 else 'Unknown')
        elevator.append('Yes' if 'Ascensor' in building['attributes'] else 'No')
        balcony.append('Yes' if 'Balcón' in building['attributes'] else 'No')
        terrace.append('Yes' if 'Terraza' in building['attributes'] else 'No')
        heating.append('Yes' if 'Calefacción' in building['attributes'] else 'No')
        air_conditioning.append('Yes' if 'Aire acondicionado' in building['attributes'] else 'No')
        parking.append('Yes' if 'Parking' in building['attributes'] else 'No')
        pool.append('Yes' if 'Piscina' in building['attributes'] else 'No')
    return rooms, bathrooms, m2, elevator, floor, balcony, terrace, heating, air_conditioning, parking, pool

def preprocess_data(buildings):
    # Separate attributes into different columns
    rooms, bathrooms, m2, elevator, floor, balcony, terrace, heating, air_conditioning, parking, pool = explode_attributes(buildings)

    # Create dataframe and add the new columns
    df = pd.DataFrame(buildings)
    new_columns = {'rooms': rooms, 'bathrooms': bathrooms, 'm2': m2, 'elevator': elevator, 'floor': floor, 'balcony': balcony, 'terrace': terrace, 'heating': heating, 'air_conditioning': air_conditioning, 'parking': parking, 'pool': pool}

    for key, value in new_columns.items():
        df[key] = value
    df['id'] = df.index
    df = df.drop(columns=['attributes'])

    print(df.head())
    return df

def save_to_file(df):
    # Save the data to a file
    df.to_csv('data.csv')

def save_to_mongo(df):
    # Save the data to MongoDB
    records = df.to_dict('records')
    collection.insert_many(records)




    """if 'hab' in building['attributes'][0]:
        rooms.append(building['attributes'][0].split(' ')[0])
    else:
        rooms.append('Unknown')
    if 'baño' in building['attributes'][1]:
        bathrooms.append(building['attributes'][1].split(' ')[0])
    else:
        bathrooms.append('Unknown')
    if 'm²' in building['attributes'][2]:
        m2.append(building['attributes'][2].split(' ')[0])
    else:
        m2.append('Unknown')
    if 'Ascensor' in building['attributes']:
        elevator.append('Yes')
    else:
        elevator.append('No')
    index = [i for i, x in enumerate(building['attributes']) if "Planta" in x]
    if len(index) > 0:
        floor.append(building['attributes'][index[0]][0])
    else:
        floor.append('Unknown')
    if 'Balcón' in building['attributes']:
        balcony.append('Yes')
    else:
        balcony.append('No')
    if 'Terraza' in building['attributes']:
        terrace.append('Yes')
    else:
        terrace.append('No')
    if 'Calefacción' in building['attributes']:
        heating.append('Yes')
    else:
        heating.append('No')
    if 'Aire acondicionado' in building['attributes']:
        air_conditioning.append('Yes')
    else:
        air_conditioning.append('No')
    if 'Parking' in building['attributes']:
        parking.append('Yes')
    else:
        parking.append('No')
    if 'Piscina' in building['attributes']:
        pool.append('Yes')
    else:
        pool.append('No')"""



