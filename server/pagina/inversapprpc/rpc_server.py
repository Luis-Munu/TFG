import Ice, sys, subprocess
import RealEstate
import pandas as pd
from pymongo import MongoClient

args = sys.argv
args.append("--Ice.MessageSizeMax=104857600")

client = MongoClient('localhost', 27017)
db = client['real_estate']
properties = db['processed_properties']
zones = db['processed_zones']

subprocess.call(["slice2py", "RealEstate.ice"])

class RealEstateServerI(RealEstate.RealEstateInterface):
    def getZoneData(self, current=None):
        df = pd.DataFrame(list(zones.find()))
        df = pd.DataFrame(df)
        print(df)
        return df.to_json()

    def getPropertyData(self, current=None):
        df = pd.DataFrame(list(properties.find()))
        #print(df)
        return df.to_json()


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


if __name__ == "__main__":
    app = RealEstateServerApp()
    sys.exit(app.main(sys.argv))