import json

import pandas as pd


def data_conv(zone):
    total = {}
    total[zone["name"] + ", " + zone["parent_zone"]] = zone

    # update the dictionary with a call to data_conv for each subzone in subzones
    if "subzones" in zone:
        for subzone in zone["subzones"].values():
            total.update(data_conv(subzone))
        # now remove the content of subzones, saving just the name of the subzone
        total[zone["name"] + ", " + zone["parent_zone"]]["subzones"] = [subzone["name"] for subzone in zone["subzones"].values()]

    return total

def main():
    zones = json.load(open("zones.json", "r"))
    # zones is equal to a dictionary with the keys and values of each call to data_conv for each zone in zones
    zones = {key: value for zone in zones.values() for key, value in data_conv(zone).items()}
    zones = pd.DataFrame.from_dict(zones, orient="index")
    # change the col names to name, parent_zone, rent, sell, subzones
    zones.columns = ["name", "parent_zone", "rent", "sell", "subzones"]
    zones.to_json("zoness.json")

if __name__ == "__main__":
    main()
    
    