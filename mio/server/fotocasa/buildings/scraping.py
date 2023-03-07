import re
from dataclasses import dataclass
from time import sleep

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Set up the Chrome driver
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
driver = webdriver.Chrome(options=options)


# Navigate to the website
driver.get('https://www.fotocasa.es/es')
actions = ActionChains(driver)

def remove_cookie_banner():
    # Wait for the accept cookies button to appear
    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="TcfAccept"]')))

    # Click the accept cookies button
    accept_button.click()

def search_location(location):
    # use find_element By.XPATH with xpath = './/div[@class="sui-MoleculeAutosuggest-input-container"]/input'
    search_bar = driver.find_element(By.XPATH, '//input[@class="sui-AtomInput-input sui-AtomInput-input-size-m"]')
    # Click the search bar
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(search_bar)).click()
    # Enter the location in the search bar
    search_bar.send_keys(location)
    sleep(1)
    search_bar.send_keys(Keys.ENTER)
    sleep(3)

def scroll_down():
    scroll = True
    while scroll == True:
        try:
            sleep(0.3)
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            sleep(0.3)
            actions.move_to_element(
                driver.find_element(By.XPATH,
                               '//a[@class="sui-AtomButton sui-AtomButton--neutral sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--rounded"]')
            ).perform()
            scroll = False
        except NoSuchElementException:
            pass


def number_of_pages(soup):
    pages = soup.find_all('li', class_="sui-MoleculePagination-item")
    if len(pages) > 1:
        n_pages = int(pages[-2].find('span').getText())
    else:
        n_pages = 1
    print('Number of pages:', n_pages, '\n')
    return n_pages

def get_top_bar():
    scroll = True
    while scroll == True:
        try:
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            sleep(1)
            actions.move_to_element(
                driver.find_element(By.XPATH, '//header[@class="re-SharedTopbar re-SharedTopbar--search"]')
            ).perform()
            scroll = False
        except NoSuchElementException:
            pass
    sleep(5)

def extract_page_data(soup):
    try:
        # Find all prices in the page
        prices = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardPriceComposite')
        # Find all titles in the page
        titles = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTitle')
        # Find all attributes in the page
        attributes = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('ul', class_=re.compile('-wrapper'))
        # Find all mobiles in the page
        mobiles = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('div', class_='re-CardContact-appendix')
        # Find all IDs in the page
        urls = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('a', class_=re.compile('-info-container'))
        # Find all the ages of the ads
        ages = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTimeAgo')
        # Find companies, disabled currently
        #companies = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardPromotionBanner-title-name')


    except AttributeError:
        # Find all prices in the page
        prices = soup.find_all('span', class_='re-CardPriceComposite')
        # Find all titles in the page
        titles = soup.find_all('span', class_='re-CardTitle')
        # Find all attributes in the page
        attributes = soup.find_all('ul', class_=re.compile('-wrapper'))
        # Find all mobiles in the page
        mobiles = soup.find_all('div', class_='re-CardContact-appendix')
        # Find all IDs in the page
        urls = soup.find_all('a', class_=re.compile('-info-container'))
        # Find all the ages of the ads
        ages = soup.find_all('span', class_='re-CardTimeAgo')
        # Find companies, disabled currently
        #companies = soup.find_all('span', class_='re-CardPromotionBanner-title-name')
    
    return prices, titles, attributes, mobiles, urls, ages#, companies

def extract_building_attributes(attribute_input):
    
    k = 0
    attributes = []; atrs = []
    for attribute in attribute_input:
        found_attrs = attribute.find_all('li', class_=re.compile('-feature'))
        for n_atr, attribute in enumerate(found_attrs):
            try:
                atr = attribute.find('span').getText()
            except AttributeError:
                atr = attribute.getText()
            if 'hab' in atr and len(atrs) > 0 or 'baño' in atr and len(atrs) >= 2 or 'm²' in atr and len(atrs) >= 3:
                k += 1
                attributes.append(atrs)
                atrs = []
                atrs.append(atr)
            elif n_atr == len(list(found_attrs)) - 1:
                k += 1
                atrs.append(atr)
                attributes.append(atrs)
                atrs = []
            else:
                atrs.append(atr)
    return attributes

def extract_building_mobiles(mobiles_input):
    mobile_list = [mobile.find_all('span', class_='sui-AtomButton-inner') for mobile in mobiles_input]
    return [mobile[1].text if len(mobile) > 1 else "Unknown" for mobile in mobile_list]

def extract_building_ids(ids_input):
    return [re.split(r'/', ident['href'])[-2] if re.split(r'/', ident['href'])[-1] != 'd' 
             else re.split(r'/', ident['href'])[-2] for i, ident in enumerate(ids_input)]


def building_creation(soup, Building, city):

    page_buildings = []

    prices, titles, attributes, mobiles, urls, ages = extract_page_data(soup)
    attributes = extract_building_attributes(attributes)
    mobiles = extract_building_mobiles(mobiles)
    #ids = extract_building_ids(urls)
    


    for i in range(len(prices)):
        building = Building(
            price = prices[i].find('span').getText().replace('.', '').replace('€', '').strip(),
            type = titles[i].find('strong').getText().strip(),
            title = titles[i].getText().strip(),
            attributes = attributes[i],
            mobile = mobiles[i],
            address = titles[i].getText().split(' en ')[-1].split(',')[-1].strip(),
            city = city,
            age = 0 if 'Novedad' in ages[i].getText() else int(ages[i].getText().strip().split(' ')[1]),
            url = urls[i]['href']
            #company = companies[i].getText().strip(),
        )
        page_buildings.append(building)

    actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
    sleep(0.5)

    return page_buildings

def next_page():
    scroll = True
    while scroll == True:
        try:
            sleep(0.3)
            buttons = driver.find_elements(By.XPATH, '//li[@class="sui-MoleculePagination-item"]')
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable(buttons[-1])
            ).click()
            scroll = False
            remove_annoying_add()
        except ElementClickInterceptedException:
            actions.key_down(Keys.PAGE_UP).key_up(Keys.PAGE_UP).perform()
            pass

def extract_buildings(soup, n_pages):
    city = soup.find('h1', class_='re-SearchTitle-text').getText().split(' en ')[2].strip()

    @dataclass
    class Building:
        price: int
        type: str
        title: str
        attributes: str
        mobile: str
        address: str
        city: str
        age: int
        url: str
        #company: str

    buildings = []
    for page in range(1, 10):
        for i in range(25):
            soup = BeautifulSoup(driver.page_source, features="lxml")
            remove_annoying_add()
            buildings.extend(building_creation(soup, Building, city))

        if page < n_pages:
            next_page()

    # Create a dict with the data
    buildings = [building.__dict__ for building in buildings]

    return buildings

def remove_annoying_add():
    # find the button of class ab-close-button wait until it is clickable and click it
    try:
        WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="ab-close-button"]'))
        ).click()
    except TimeoutException:
        pass

def scrape(location):
    remove_cookie_banner()
    search_location(location)
    scroll_down()
    soup = BeautifulSoup(driver.page_source, features="lxml")
    n_pages = number_of_pages(soup)
    get_top_bar()
    buildings = extract_buildings(soup, n_pages)
    driver.quit()
    return buildings