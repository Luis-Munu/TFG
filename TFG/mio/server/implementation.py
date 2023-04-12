import sys

import Ice
import pandas as pd
from pymongo import MongoClient

import server

client = MongoClient('localhost', 27017)
db = client['real_estate']
properties = db['properties']
zones = db['zones']

class MyServerI(server.serverInterface):

    def return_collection(self, collection_name, current=None):
        if collection_name == "properties":
            collection = properties
        elif collection_name == "zones":
            collection = zones
        else:
            return "{}"

        df = pd.DataFrame(list(collection.find()))
        return df.to_json()

if __name__ == '__main__':
    with Ice.initialize(sys.argv) as communicator:
        adapter = communicator.createObjectAdapterWithEndpoints("RealEstateAdapter", "default -p 12545")
        object = MyServerI()
        adapter.add(object, communicator.stringToIdentity("RealEstateServer"))
        adapter.activate()
        communicator.waitForShutdown()
