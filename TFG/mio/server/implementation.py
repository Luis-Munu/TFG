import sys

import Ice
import pandas as pd
import server
from pymongo import MongoClient

from mio.server.processing.property_statistics import calculations

client = MongoClient('localhost', 27017)
db = client['real_estate']
collection = db['properties']

class MyServerI(server.serverInterface):

    def update_calculations(self):
        # Retrieve the data from MongoDB
        df = pd.DataFrame(list(collection.find()))
        # Perform the calculations
        df = calculations(df)
        # Save the data to MongoDB
        collection.insert_many(df.to_dict('records'))

    def updateDB(self, json_df, current=None):
        # Convert the JSON dataframe to a Pandas dataframe
        df = pd.read_json(json_df)
        # Save the data to MongoDB
        collection.insert_many(df.to_dict('records'))

    def returnDataframe(self, current=None):
        # Retrieve the data from MongoDB and return it as a JSON dataframe
        df = pd.DataFrame(list(collection.find()))
        return df.to_json()

if __name__ == '__main__':
    with Ice.initialize(sys.argv) as communicator:
        adapter = communicator.createObjectAdapterWithEndpoints("RealEstateAdapter", "default -p 12545")
        object = MyServerI()
        adapter.add(object, communicator.stringToIdentity("RealEstateServer"))
        adapter.activate()
        communicator.waitForShutdown()
