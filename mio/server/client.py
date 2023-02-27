import Ice
import pandas as pd

Ice.loadSlice("server.ice")  # load the Slice definition for the server

import server

with Ice.initialize() as communicator:
    proxy = communicator.stringToProxy("RealEstateServer:default -p 12545")
    server_obj = server.serverInterfacePrx.checkedCast(proxy)
    json_df = server_obj.returnDataframe()

    if not server_obj:
        raise RuntimeError("Invalid proxy")

    # Call a method on the server
    result = server_obj.updateDB(json_df)