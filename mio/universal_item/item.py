# Class used to represent a single building from a real estate listing.

class Building:
    def __init__(self, building_data):
        self.name = building_data["name"] if "name" in building_data else ""
        self.address = building_data["address"] if "address" in building_data else ""
        self.price = building_data["price"] if "price" in building_data else ""
        self.size = building_data["size"] if "size" in building_data else ""
        self.rooms = building_data["rooms"] if "rooms" in building_data else ""
        self.url = building_data["url"] if "url" in building_data else ""

    def __str__(self):
        return f"{self.name} {self.address} {self.price} {self.size} {self.rooms} {self.url}"

    def __repr__(self):
        return self.__str__()