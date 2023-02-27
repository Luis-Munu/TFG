from pandas import DataFrame
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['fotocasa']
collection = db['properties']

def load_from_mongo():
    # Load the data from MongoDB
    df = DataFrame(list(collection.find()))
    df = df.drop(columns=['_id'])
    return df
