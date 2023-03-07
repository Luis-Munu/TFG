# TFG

# TODO
Refine rent calculation.
Search for the exact ITP for an autonomy, how will we find on which autonomy a house is, don't know yet.
Fix the Json utf overflow error.
Filter by house type.
Redefine the structure of the zone extractor script to better fit MongoDB. (Must find a good key for an element, maybe parent+name).
Create an idealista scrapper.
Merge the information from idealista to the houses database.
Add more parameters to the rentability function in order for the user to customize them via file.
Fix the SCP server to work with the new processing module.
Create an skeleton for the website and connect it to the SCP server.
Enhance the website and create new functions for the processing module based on new needs.
Documentation....

# DONE
Created the Fotocasa scraping system for houses, it extracts the maximum amount of information possible (except for the uploader) from the house sheet. Looks human-like.
Refined said scraping system to include several more unaccounted values and formatted them properly to pass to processing.
Created a Fotocasa processing system for the houses, to correctly format the attributes of the house and explode its properties (heating, parking...).
Created a scrapper for Fotocasa zones, it currently returns the average prices of houses for both renting and selling in every single place in Spain. Currently tested in Cáceres.
Created a processing module that calculates useful metrics such as mortgage stats or rentability for the house database.
Heavily upgraded the calculations of the rents and rentabilities, by taking into account values such as IBI, insurance, community, maintenance or transfer taxes.
Refined the formulae of the rentability, now using the inputted money instead of just mortgage + taxes.
Created a RCP server skeleton, still not quite functional, can't read JSONs due to overflow error.



After that is working, must retrieve zone information from fotocasa, linking the zones with the houses. 

When that is done, create a settings file with parameters such as interest rates to calculate mortgages and rentabilities.

Add compatibility to the server functions to the processing part of the app.

If idealista doesn't provide us an API we'll have to take our own actions.

When all the data is ready and the server is responding, the website must be designed.
