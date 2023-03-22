# script usado para obtener un listado de zonas de la web de fotocasa y guardarlos en un csv
# La busqueda de nombres se realiza en forma de arbol, siendo el primer nivel las provincias.
import time
from json import dump

import bs4 as beautifulsoup
from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up the Chrome driver
options = webdriver.ChromeOptions()

# Set up the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument("disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)

# Base URL 
base_url = 'https://www.fotocasa.es/indice-precio-vivienda'
more_based_url = 'https://www.fotocasa.es'
driver.get(base_url)
actions = ActionChains(driver)

# create a global timer that every 30 seconds will refresh the page
global_timer = 0

zones = {}

def remove_cookie_banner():
    # Wait for the accept cookies button to appear
    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="TcfAccept"]')))
    # Click the accept cookies button
    accept_button.click()

def get_provinces():
    global zones
    # Get the provinces by xpath class popular-search_link
    provinces = driver.find_elements(By.XPATH, '//a[@class="popular-search_link"]')
    # Get the urls of the provinces
    provinces_urls = [province.get_attribute('href') for province in provinces]
    provinces_urls = [provinces_urls[37]]
    # Get the text of the provinces
    provinces_names = [province.text for province in provinces]
    # Remove "Precio viviendas " from the names
    provinces_names = [province.replace('Precio viviendas ', '') for province in provinces_names]
    provinces_names = [provinces_names[37]]
    # Append the provinces to the dictionary as keys
    for province in provinces_names: zones[province] = {}
    # Return the urls of the provinces
    return provinces_urls

def get_subzones(soup):

    subzone_table = soup.find('section', {'class': 'table-price-wrap'})
    if (subzone_table): subzone_table = subzone_table.find('div', {'class': 'table-price_left'})
    if (subzone_table):subzone_table = subzone_table.find('table', {'class': 'table-price'}).find('tbody')
    if (not subzone_table): return [], []
    subzone_table = [city.find_all('td') for city in subzone_table.find_all('tr')]
    urls = [more_based_url + city[0].find('a').get('href') for city in subzone_table]
    subzone_table = [[city.text for city in row] for row in subzone_table]
    subzone_table = [row[0] for row in subzone_table]

    return subzone_table, urls


def calculate_keys(description):

    keys = ["sqm1rooms", "sqm3rooms", "sqm2rooms", "sqm4rooms", "terrace","elevator", "furnished", "parking", "avgsqm", "avgtype", "avgrooms", "avgfloors"]

    if ('terraza' not in description.text): keys.remove("terrace")
    if ('ascensor' not in description.text): keys.remove("elevator")
    if ('Amueblado' not in description.text): keys.remove("furnished")
    if ('parking' not in description.text): keys.remove("parking")

    return keys

def get_container_stats(container):
    descriptions = container.find_elements(By.XPATH, './/div[@class="description-wrap"]')
    dict = {}

    keys = ["sqm1rooms", "sqm3rooms", "sqm2rooms", "sqm4rooms", "terrace","elevator", "furnished", "parking", "avgsqm", "avgtype", "avgrooms", "avgfloors"]
    calculate_keys(descriptions[1])
    # arregla esto por dios FIXME
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
    time.sleep(10)
    driver.refresh()
    time.sleep(10)

def get_zone_stats():
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
    

def get_zone(zone_url, parent_zone, depth):

    global global_timer, zones

    driver.get(zone_url)
    wait = WebDriverWait(driver, 3)
    try: wait.until(EC.presence_of_element_located((By.XPATH, '//div[@class="t-panel-container padding-bottom-0"]')))
    except TimeoutException: return {"parent_zone": parent_zone}
    soup = beautifulsoup.BeautifulSoup(driver.page_source, 'html.parser')

    zone = {
        "name": soup.find('h1', {'class': 'h1-title'}).text.split(" en ")[-1].split(",")[0].title().strip(), 
        "parent_zone": parent_zone
    }
    
    if any(banned_word in zone_url for banned_word in['calle', 'avenida', 'plaza', 'paseo', 'pasaje']):
        return zone
    if depth > 2: return zone

    time.sleep(3)
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
        sub = get_zone(subzone_url, zone["name"], depth + 1)
        if subzone not in zone["subzones"]: zone["subzones"][subzone] = sub
        else: zone["subzones"][subzone].update(sub)
    return zone

def save_to_json(zones):
    with open('zones.json', 'w') as f:
        dump(zones, f)

def delete_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    collection.delete_many({})

def save_to_mongo(zones):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["real_estate"]
    collection = db["zones"]
    collection.insert_one(zones)

def main():
    remove_cookie_banner()
    provinces_urls = get_provinces()
    locations = {}
    for url, name in zip(provinces_urls, zones.keys()):
        res = get_zone(url, name, 0)
        locations[res["name"]] = res
        
    
    save_to_json(locations)
    save_to_mongo(locations)

    driver.close()

    

if __name__ == '__main__':
    main()
