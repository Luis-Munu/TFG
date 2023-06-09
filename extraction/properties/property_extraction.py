from . import preprocessing
from . import scraping


def location_loop(location):
    preprocessing.remove_duplicates()

    # Get the data from the web
    data = scraping.scrape(location)

    # Process the data
    data = preprocessing.preprocess_data(data)

    # Append the new data to a file
    preprocessing.append_to_csv(data)
    preprocessing.append_to_json(data)

    # Save the data to MongoDB
    preprocessing.save_to_mongo(data)

def property_extraction(location = None, autonomous_community = None):
    preprocessing.remove_duplicates()
    # get the locations from the zones collection
    if location:
        locations = [location]
    elif autonomous_community:
        locations = preprocessing.get_locations_autonomous_community(autonomous_community)
    else:
        locations = preprocessing.get_top_10_subzones()
    #processing.delete_from_mongo()
    for location in locations:
        location_loop(location)