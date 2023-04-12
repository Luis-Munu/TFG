import Ice
import pandas as pd
import server


def get_proxy():
    Ice.loadSlice("server.ice")
    with Ice.initialize() as communicator:
        proxy = communicator.stringToProxy("RealEstateServer:default -p 12545")
        server_obj = server.serverInterfacePrx.checkedCast(proxy)
    if not server_obj:
        raise RuntimeError("Invalid proxy")
    return server_obj

def retrieve_properties():
    server_obj = get_proxy()
    collection_name = "properties"
    json_df = server_obj.return_collection(collection_name)
    df = pd.read_json(json_df)
    return df

def retrieve_zones():
    server_obj = get_proxy()
    collection_name = "zones"
    json_df = server_obj.return_collection(collection_name)
    df = pd.read_json(json_df)
    return df