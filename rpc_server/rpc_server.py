import Ice, sys, subprocess
import RealEstate
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
import json


client = MongoClient('localhost', 27017)
db = client['real_estate']
properties = db['processed_properties']
zones = db['processed_zones']

subprocess.call(["slice2py", "RealEstate.ice"])

class RealEstateServerI(RealEstate.RealEstateInterface):
    def getZoneData(self, current=None):
        df = list(zones.find())
        # if there is any item of the list that is a ObjectId, convert it to string
        for i in range(len(df)):
            if isinstance(df[i]['_id'], ObjectId):
                df[i]['_id'] = str(df[i]['_id'])
        
        df = json.dumps(df)
        print(df)
        return df

    def getPropertyData(self, current=None):
        df = list(properties.find())
        # if there is any item of the list that is a ObjectId, convert it to string
        for i in range(len(df)):
            if isinstance(df[i]['_id'], ObjectId):
                df[i]['_id'] = str(df[i]['_id'])
        df = json.dumps(df)
        print(df)
        return df
    
    """def getZoneData(self, current=None):
        df = pd.DataFrame(list(zones.find()))
        #df = df.drop('_id', axis=1)
        df = pd.DataFrame(df)
        print(df)
        return df.to_json()

    def getPropertyData(self, current=None):
        df = pd.DataFrame(list(properties.find()))
        #df = df.drop('_id', axis=1)
        #print(df)
        return df.to_json()"""


class RealEstateServerApp(Ice.Application):
    def run(self, args):
        args = sys.argv
        args.append("--Ice.MessageSizeMax=104857600")
        ice = Ice.initialize(args)
        broker = self.communicator()
        adapter = broker.createObjectAdapterWithEndpoints("RealEstateAdapter", "default -p 12545")
        server = RealEstateServerI()

        adapter.add(server, broker.stringToIdentity("RealEstateServer"))
        adapter.activate()

        print("RPC server is running...")
        self.shutdownOnInterrupt()
        broker.waitForShutdown()

        return 0

def start_rpc():
    app = RealEstateServerApp()
    sys.exit(app.main(sys.argv))