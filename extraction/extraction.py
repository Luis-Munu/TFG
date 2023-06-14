from .properties.property_extraction import *
from .zones.zone_extraction import *

def data_extraction():
    """
    Extracts the data from the web, processes it and saves it to certain files and to MongoDB.
    """
    property_extraction()
    zone_extraction()