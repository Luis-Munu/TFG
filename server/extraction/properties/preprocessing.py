import pandas as pd
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client['real_estate']
collection = db['properties']
zones = db['zones']

def get_top_10_subzones():
    """
    Returns the top 10 subzones based on the number of properties in each subzone.

    Returns:
        list: The top 10 subzones.
    """
    top_subzones = []
    locations = [location for location in zones.find()][0]
    locations.pop('_id')
    
    def traverse_subzones(subzones, parent_zone):
        subzone_names = []
        if not subzones:
            return []
        for subzone in subzones:
            if 'subzones' in subzone:
                subzone_names += traverse_subzones(list(subzone['subzones'].values()), subzone['name'])
            subzone_names.append(f"{subzone['name']}, {parent_zone}")
        return subzone_names
    
    for province in locations.values():
        subzones = list(province['subzones'].values())
        province_name = province['name']
        province_top_subzones = traverse_subzones(subzones, province_name)[:10]
        top_subzones += province_top_subzones
    return top_subzones

def get_locations_autonomous_community(autonomous_community):
    """
    Returns the locations (provinces and subzones) for a given autonomous community.

    Args:
        autonomous_community (str): The autonomous community to search for.

    Returns:
        list: The locations for the given autonomous community.
    """
    def get_subzones(zone):
        names = []
        if "subzones" in zone:
            for subzone in zone['subzones'].values():
                names.append(subzone['name'] + ', ' + zone['name'])
                names.extend(get_subzones(subzone))
        return names
    names = []
    mongo_locations = zones.find()
    mongo_locations = [location for location in mongo_locations][0]
    mongo_locations.pop('_id')
    for location in mongo_locations.values():
        if location['autonomous_community'] == autonomous_community:
            names.append(location['name'] + ', ' + location['parent_zone'].replace(" Provincia", ""))
            names.extend(get_subzones(location))

    return names

def explode_attributes(properties):
    """
    Separates the attributes of each property into different columns.

    Args:
        properties (list): The properties to explode.

    Returns:
        tuple: The exploded attributes.
    """
    rooms = []; bathrooms = []; m2 = []
    elevator = []; floor = []; balcony = []
    terrace = []; heating = []; air_conditioning = []
    parking = []; pool = []
    for property in properties:
        index = [i for i, x in enumerate(property['attributes']) if "hab" in x]
        rooms.append(property['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(property['attributes']) if "baño" in x]
        bathrooms.append(property['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(property['attributes']) if "m²" in x]
        m2.append(property['attributes'][index[0]].split(' ')[0] if len(index) > 0 else 0)
        index = [i for i, x in enumerate(property['attributes']) if "Planta" in x]
        floor.append(property['attributes'][index[0]][0] if len(index) > 0 else 0)
        elevator.append('Yes' if 'Ascensor' in property['attributes'] else 'No')
        balcony.append('Yes' if 'Balcón' in property['attributes'] else 'No')
        terrace.append('Yes' if 'Terraza' in property['attributes'] else 'No')
        heating.append('Yes' if 'Calefacción' in property['attributes'] else 'No')
        air_conditioning.append('Yes' if 'Aire acondicionado' in property['attributes'] else 'No')
        parking.append('Yes' if 'Parking' in property['attributes'] else 'No')
        pool.append('Yes' if 'Piscina' in property['attributes'] else 'No')
    return rooms, bathrooms, m2, elevator, floor, balcony, terrace, heating, air_conditioning, parking, pool

def preprocess_data(properties):
    """
    Preprocesses the real estate properties.

    Args:
        properties (list): The properties to preprocess.

    Returns:
        pandas.DataFrame: The preprocessed properties.
    """
    # Separate attributes into different columns
    rooms, bathrooms, m2, elevator, floor, balcony, terrace, heating, air_conditioning, parking, pool = explode_attributes(properties)

    # Create dataframe and add the new columns
    df = pd.DataFrame(properties)
    new_columns = {'rooms': rooms, 'bathrooms': bathrooms, 'm2': m2, 'elevator': elevator, 'floor': floor, 'balcony': balcony, 'terrace': terrace, 'heating': heating, 'air_conditioning': air_conditioning, 'parking': parking, 'pool': pool}

    for key, value in new_columns.items():
        df[key] = value
    df['id'] = df.index

    # remove all houses with price "A consultar"
    df = df[df['price'] != 'A consultar']

    for key in df.keys():
        # try to cast to int, if it fails, it's a string
        try: df[key] = df[key].astype(int)
        except: pass

    df = df.drop(columns=['attributes'])

    print(df.head())
    return df

def remove_duplicates():
    """
    Removes duplicate properties from the MongoDB database.
    """
    # load the info from the properties collection
    df = pd.DataFrame(list(collection.find()))
    # remove duplicates by id
    df = df.drop_duplicates(subset=['url'], keep='last')
    # save the new data to the properties collection deleting the old one
    collection.delete_many({})
    records = df.to_dict('records')
    collection.insert_many(records)

def append_to_csv(df):
    """
    Appends the given DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to append.
    """
    # Append the data to a file
    df.to_csv('data.csv', mode='a', header=False)

def append_to_json(df):
    """
    Appends the given DataFrame to a JSON file.

    Args:
        df (pandas.DataFrame): The DataFrame to append.
    """
    # Append the data to a file
    df.to_json('data.json', orient='records', lines=True)

def save_to_csv(df):
    """
    Saves the given DataFrame to a CSV file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
    """
    # Save the data to a file
    df.to_csv('data.csv')

def save_to_json(df):
    """
    Saves the given DataFrame to a JSON file.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
    """
    # Save the data to a file
    df.to_json('data.json')

def save_to_mongo(df):
    """
    Saves the given DataFrame to the MongoDB database.

    Args:
        df (pandas.DataFrame): The DataFrame to save.
    """
    # Save the data to MongoDB
    records = df.to_dict('records')
    collection.insert_many(records)

def delete_from_mongo():
    """
    Deletes all properties from the MongoDB database.
    """
    collection.delete_many({})

def main():
    delete_from_mongo()