import loader
import property_statistics
import zone_statistics


def main():
    # Load properties and zones
    properties = loader.load_properties()
    zones = loader.load_zones()

    # Link datasets
    properties = loader.link_datasets(properties, zones)

    # Update property statistics
    properties = property_statistics.update_stats(properties, zones)

    # Update zone statistics
    zones = zone_statistics.update_stats(zones, properties)

    # Predict property cluster
    properties = property_statistics.predict_property_cluster(properties, zones)

    # update the zone dataset, replacing the properties with just their ids, also extract the text of the objectid of mongodb
    zones["properties"] = zones["properties"].apply(lambda props: [prop["_id"] for prop in props])
    zones['properties'] = zones['properties'].apply(lambda x: [str(objId) for objId in x])
    # convert any objectid to string in zones


    # Save properties and zones to CSV files
    loader.save_to_csv(properties, "properties")
    loader.save_properties(properties)
    loader.save_to_csv(zones, "zones")
    loader.save_zones(zones)


if __name__ == "__main__":
    main()