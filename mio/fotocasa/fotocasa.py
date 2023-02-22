import processing
import scraping


def main(location='Cáceres'):
    # Get the data from the web
    data = scraping.scrape(location)

    # Process the data
    data = processing.preprocess_data(data)

    # Save the data to a file
    processing.save_to_file(data)

    # Save the data to MongoDB
    processing.save_to_mongo(data)

if __name__ == '__main__':
    main()