# script usado para obtener un listado de zonas de la web de fotocasa y guardarlos en un csv
# La busqueda de nombres se realiza en forma de arbol, siendo el primer nivel las provincias.
import time
from json import dump, load
import os

import bs4 as beautifulsoup
from fuzzywuzzy import fuzz
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

"""
    Script used to get the tree hierarchy of zones from the fotocasa website.
    First, it gets the names of the provinces, along with their urls.
    Then it recursively gets the names of the subzones, and their statistics.
    The results are stored on a MongoDB collection called "zones".
"""

# Set up the Chrome driver
options = webdriver.ChromeOptions()

# Set up the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("disable-blink-features=AutomationControlled")
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# Base URL 
base_url = 'https://www.fotocasa.es/indice-precio-vivienda'
more_based_url = 'https://www.fotocasa.es'
driver.get(base_url)
actions = ActionChains(driver)

# create a global timer that every 30 seconds will refresh the page
global_timer = 0

zones = {}
provinces = {}

file_path = os.path.join(os.path.dirname(__file__), 'provinces.json')

# Load the provinces from a JSON file
with open(file_path, 'r') as f:
    provinces = load(f)


def remove_cookie_banner():
    # This method removes the cookie banner by click the accept cookies button 
    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="TcfAccept"]')))
    accept_button.click()

def get_provinces():
    """
    Retrieves province information including urls and names from the fotocasa website,
    adds provinces to a global dictionary, and returns the province urls.

    Returns:
        list: A list of province urls.
    """
    global zones
    
    # Get the provinces by xpath class popular-search_link
    provinces = driver.find_elements(By.XPATH, '//a[@class="popular-search_link"]')
    # Get the urls of the provinces
    provinces_urls = [province.get_attribute('href') for province in provinces]

    # Get the text of the provinces
    provinces_names = [province.text for province in provinces]
    provinces_names = [province.replace('Precio viviendas ', '') for province in provinces_names]


    for province in provinces_names: zones[province] = {}

    return provinces_urls

def get_subzones(soup):
    """
    Retrieves subzone information within a soup object, extracting subzone names and urls
    and returning them as lists.

    Args:
        soup (BeautifulSoup): A BeautifulSoup object representing the HTML content.

    Returns:
        tuple: A tuple containing two lists. The first list contains subzone names and the
        second list contains subzone urls.
    """
    subzone_table = soup.find('section', {'class': 'table-price-wrap'})
    if (subzone_table): subzone_table = subzone_table.find('div', {'class': 'table-price_left'})
    if (subzone_table):subzone_table = subzone_table.find('table', {'class': 'table-price'}).find('tbody')
    if (not subzone_table): return [], []
    subzone_table = [city.find_all('td') for city in subzone_table.find_all('tr')]
    urls = [more_based_url + city[0].find('a').get('href') for city in subzone_table]
    subzone_table = [[city.text for city in row] for row in subzone_table]
    subzone_table = [row[0] for row in subzone_table]

    return subzone_table, urls

def get_autonomous_community(province):
    """
    Compares a province against all provinces in autonomous communities, returning the associated
    community if a similarity greater than 80 is found, or "Unknown" otherwise.

    Args:
        province (str): The name of the province to compare.

    Returns:
        str: The name of the autonomous community associated with the province, or "Unknown" if no
        match is found.
    """
    for com in provinces:
        for prov in com["provinces"]:
            if (fuzz.ratio(prov["name"], province) > 80): 
                return com
    return "Unknown"



def calculate_keys(description):
    """
    Calculates the keys/features to include in the dictionary based on the housing description provided.

    Args:
        description (BeautifulSoup): A BeautifulSoup object representing the housing description.

    Returns:
        list: A list of keys/features to include in the dictionary.
    """

    keys = ["sqm1rooms", "sqm3rooms", "sqm2rooms", "sqm4rooms", "terrace","elevator", "furnished", "parking", "avgsqm", "avgtype", "avgrooms", "avgfloors"]
    keys_to_remove = [("terraza", "terrace"), ("ascensor", "elevator"), ("Amueblado", "furnished"), ("parking", "parking")]

    for keyword, key in keys_to_remove:
        if keyword not in description.text:
            keys.remove(key)

    return keys

def get_container_stats(container):
    """
    Extracts statistics from various housing web elements, organizing them into a dictionary
    and returning it.

    Args:
        container (BeautifulSoup): A BeautifulSoup object representing the container element.

    Returns:
        dict: A dictionary containing the extracted statistics.
    """
    descriptions = container.find_elements(By.XPATH, './/div[@class="description-wrap"]')
    dict = {}

    keys = ["sqm1rooms", "sqm3rooms", "sqm2rooms", "sqm4rooms", "terrace","elevator", "furnished", "parking", "avgsqm", "avgtype", "avgrooms", "avgfloors"]
    calculate_keys(descriptions[1])
    for i in range(0, 3):
        ct = descriptions[i].text.split('\n'); n = min(int(len(ct)/2), 4)

        if (i == 1): keys = calculate_keys(descriptions[1])
        else: keys = ["sqm1rooms", "sqm3rooms", "sqm2rooms", "sqm4rooms", "terrace","elevator", "furnished", "parking", "avgsqm", "avgtype", "avgrooms", "avgfloors"]
        
        for j in range(0, n):
            dict[keys[i*n+j]] = ct[j*2].split('€')[0].replace('.', '').replace('m²', '').strip()


    avgprices = container.find_elements(By.XPATH, './/div[@class="b-detail"]')
    dict["pricepersqm"] = avgprices[0].text.split(' €')[0].replace('.', '').strip()
    dict["price"] = avgprices[1].text.split(' €')[0].replace('.', '').strip()

    b100 = container.find_element(By.XPATH, './/div[contains(text(), "Precio por < 100 m²")]/..//div[@class="description-item_semibold"]').text
    dict["b100"] = b100.replace(' €/m²', '').replace(' €', '').replace('.', '')
    b100 = container.find_element(By.XPATH, './/div[contains(text(), "Precio por > 100 m²")]/..//div[@class="description-item_semibold"]').text
    dict["a100"] = b100.replace(' €/m²', '').replace(' €', '').replace('.', '')

    for key in keys:
        if key not in dict:
            dict[key] = 0

    for key in dict.keys():
        if (dict[key] == '-'): dict[key] = -1
        try: 
            dict[key] = float(dict[key])
            if "sqm" in key: dict[key] = dict[key]
        except ValueError: pass
        

    return dict

def calm_down():
    """
    Causes a delay and refreshes the driver to avoid triggering anti-scraping measures.
    """
    time.sleep(10)
    driver.refresh()
    time.sleep(10)

def get_zone_stats():
    """
    Retrieves statistics for a specific zone by identifying the containers holding sell and rent data
    and collecting their respective statistics.

    Returns:
        dict: A dictionary containing the statistics for the zone. The dictionary has two keys:
        "sell" and "rent". The "sell" key maps to a dictionary containing the statistics for the
        sell data, while the "rent" key maps to a dictionary containing the statistics for the rent
        data.
    """
    try:
        stat_container = driver.find_element(By.XPATH, '//div[@class="t-panel-container padding-bottom-0"]')
        sell_container = stat_container.find_element(By.XPATH, '//div[@class="t-panel comprar active"]')
        rent_container = stat_container.find_element(By.XPATH, '//div[@class="t-panel alquiler"]')
    except NoSuchElementException:
        return None

    stats = {
        "sell": get_container_stats(sell_container),
        "rent": {}
    }

    driver.find_elements(By.XPATH, '//div[@class="t-btn-container"]//p')[1].click()
    wait = WebDriverWait(driver, 10)
    rent_container = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="t-panel alquiler active"]')))

    stats["rent"] = get_container_stats(rent_container)


    return stats
    

def get_zone(zone_url, parent_zone, community, depth):
    """
    Gathers zone information, including zone name, parent zone, subzones, and statistics by parsing
    HTML content and calling appropriate support functions.

    Args:
        zone_url (str): The URL of the zone to gather information for.
        parent_zone (str): The name of the parent zone.
        community (str): The name of the autonomous community the zone belongs to.
        depth (int): The depth of the zone in the hierarchy.

    Returns:
        dict: A dictionary containing the gathered zone information. The dictionary has the following
        keys: "name", "parent_zone", "subzones", "stats", and "depth". The "name" key maps to the name
        of the zone, the "parent_zone" key maps to the name of the parent zone, the "subzones" key maps
        to a list of subzone dictionaries, the "stats" key maps to a dictionary containing the zone
        statistics, and the "depth" key maps to the depth of the zone in the hierarchy.
    """
    global global_timer, zones

    driver.get(zone_url)
    wait = WebDriverWait(driver, 3)
    try: wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="t-panel-container padding-bottom-0"]')))
    except TimeoutException: return {"parent_zone": parent_zone}
    soup = beautifulsoup.BeautifulSoup(driver.page_source, 'html.parser')

    zone = {
        "name": soup.find('h1', {'class': 'h1-title'}).text.split(" en ")[-1].split(",")[0].title().strip(), 
        "parent_zone": parent_zone,
        "community": community
    }
    time.sleep(1)
    if any(banned_word in zone_url for banned_word in['calle', 'avenida', 'plaza', 'paseo', 'pasaje']):
        return zone
    if depth > 2: return zone

    time.sleep(2)
    global_timer += 1
    if global_timer > 30:
        calm_down()
        global_timer = 0

    zone_stats = get_zone_stats()
    if not zone_stats:
        calm_down()
        return zone
    zone.update(zone_stats)
    
    subzones, subzones_urls = get_subzones(soup)
    zone["subzones"] = {}

    for subzone, subzone_url in zip(subzones, subzones_urls):
        sub = get_zone(subzone_url, zone["name"], community, depth + 1)
        if subzone not in zone["subzones"]: zone["subzones"][subzone] = sub
        else: zone["subzones"][subzone].update(sub)
    return zone

def save_to_json(zones):
    """
    Saves the zones to a JSON file named "zones.json".

    Args:
        zones (list): A list of dictionaries representing the zones.

    Returns:
        None
    """
    with open('zones.json', 'w') as f:
        dump(zones, f)

def delete_mongo():
    """
    Deletes all documents in the `zones` collection of the MongoDB database.

    Returns:
        None
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    collection.delete_many({})

def save_to_mongo(zones):
    """
    Saves the zones to a MongoDB database in the `zones` collection.

    Args:
        zones (list): A list of dictionaries representing the zones.

    Returns:
        None
    """
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    collection.insert_one(zones)


def name_extraction():
    delete_mongo()
    remove_cookie_banner()
    provinces_urls = get_provinces()
    locations = {}
    for url, name in zip(provinces_urls, zones.keys()):
        res = get_zone(url, name, get_autonomous_community(name),0)
        locations[res["name"]] = res
        
    save_to_json(locations)
    save_to_mongo(locations)

    driver.close()