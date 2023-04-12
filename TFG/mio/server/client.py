import Ice
import pandas as pd

import server

Ice.loadSlice("server.ice")

def retrieve_properties(proxy):
    collection_name = "properties"
    json_df = proxy.return_collection(collection_name)
    df = pd.read_json(json_df)
    return df

def retrieve_zones(proxy):
    collection_name = "zones"
    json_df = proxy.return_collection(collection_name)
    df = pd.read_json(json_df)
    return df

with Ice.initialize() as communicator:
    proxy = communicator.stringToProxy("RealEstateServer:default -p 12545")
    server_obj = server.serverInterfacePrx.checkedCast(proxy)

if not server_obj:
    raise RuntimeError("Invalid proxy")

properties_df = retrieve_properties(server_obj)
zones_df = retrieve_zones(server_obj)