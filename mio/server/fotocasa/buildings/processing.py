import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['real_estate']
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
        rooms.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(building['attributes']) if "baño" in x]
        bathrooms.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(building['attributes']) if "m²" in x]
        m2.append(building['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(building['attributes']) if "Planta" in x]
        floor.append(building['attributes'][index[0]][0] if len(index) > 0 else 0)
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

    # remove all houses with price "A consultar"
    df = df[df['price'] != 'A consultar']
    # convert all rooms of value

    for key in df.keys():
        # try to cast to int, if it fails, it's a string
        try:
            df[key] = df[key].astype(int)
        except:
            pass



    df = df.drop(columns=['attributes'])

    print(df.head())
    return df

def save_to_csv(df):
    # Save the data to a file
    df.to_csv('data.csv')

def save_to_json(df):
    # Save the data to a file
    df.to_json('data.json')

def save_to_mongo(df):
    # Save the data to MongoDB
    records = df.to_dict('records')
    collection.insert_many(records)

def delete_from_mongo():
    # Delete the data from MongoDB
    collection.delete_many({})

def main():
    delete_from_mongo()

