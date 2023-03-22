import loader
import property_statistics
import zone_statistics


def main():
    properties = loader.load_properties()
    zones = loader.load_zones()
    properties = property_statistics.update_stats(properties, zones, 30, 100000)
    zones = zone_statistics.update_stats(zones, properties)
    properties = property_statistics.predict_property_cluster(properties, zones)
    loader.save_to_csv(properties, "properties")
    loader.split_by_type(properties)
    loader.save_to_csv(zones, "zones")

if __name__ == "__main__":
    main()