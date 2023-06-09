import re
from dataclasses import dataclass
from time import sleep, time

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


def remove_cookie_banner(driver):
    """
    Accepts the cookies on the website.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.

    Returns:
    None
    """
    # Wait for the accept cookies button to appear
    wait = WebDriverWait(driver, 10)
    accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="TcfAccept"]')))

    # Click the accept cookies button
    accept_button.click()

def search_location(location, driver):
    """
    Searches for a location on the website.

    Parameters:
    location (str): The location to search for.
    driver (selenium.webdriver): The webdriver instance.

    Returns:
    None
    """
    # use find_element By.XPATH with xpath = './/div[@class="sui-MoleculeAutosuggest-input-container"]/input'
    search_bar = driver.find_element(By.XPATH, '//input[@class="sui-AtomInput-input sui-AtomInput-input-size-m"]')
    # Click the search bar
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(search_bar)).click()
    # Enter the location in the search bar
    search_bar.send_keys(location)
    sleep(2)
    search_bar.send_keys(Keys.ENTER)
    sleep(3)
    
    
def scroll_down(driver, actions):
    """
    Scrolls down the website.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    None
    """
    start_time = time()

    while True:
        try:
            element = driver.find_element(By.XPATH, '//a[@class="sui-AtomButton sui-AtomButton--neutral sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--rounded"]')
            server_kick(driver)
            remove_annoying_add(driver)
            actions.move_to_element(element).perform()
            break
        except NoSuchElementException:
            if time() - start_time > 60:
                sanity_check(driver)
                break
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).pause(0.1).perform()
            sleep(0.3)
        


def number_of_pages(soup):
    """
    Gets the number of pages from the given soup.

    Parameters:
    soup (bs4.BeautifulSoup): The soup to get the number of pages from.

    Returns:
    int: The number of pages.
    """
    pages = soup.find_all('li', class_="sui-MoleculePagination-item")
    if len(pages) > 1:
        n_pages = int(pages[-2].find('span').getText())
    else:
        n_pages = 1
    print('Number of pages:', n_pages, '\n')
    return n_pages

def get_top_bar(driver, actions):
    """
    Gets the top bar from the website.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    None
    """
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
    """
    Extracts the data of the different properties displayed on the website from the given soup.

    Parameters:
    soup (bs4.BeautifulSoup): The soup to extract the data from.

    Returns:
    list: A list of dictionaries containing the extracted data.
    """
    try:

        prices = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardPriceComposite')
        titles = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTitle')
        attributes = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('ul', class_=re.compile('-wrapper'))
        mobiles = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('div', class_='re-CardContact-appendix')
        urls = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('a', class_=re.compile('-info-container'))
        ages = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTimeAgo')
        
        # Find companies, disabled currently
        #companies = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardPromotionBanner-title-name')


    except AttributeError:
        prices = soup.find_all('span', class_='re-CardPriceComposite')
        titles = soup.find_all('span', class_='re-CardTitle')
        attributes = soup.find_all('ul', class_=re.compile('-wrapper'))
        mobiles = soup.find_all('div', class_='re-CardContact-appendix')
        urls = soup.find_all('a', class_=re.compile('-info-container'))
        ages = soup.find_all('span', class_='re-CardTimeAgo')
        
        # Find companies, disabled currently
        #companies = soup.find_all('span', class_='re-CardPromotionBanner-title-name')
    
    return prices, titles, attributes, mobiles, urls, ages #, companies

def extract_property_attributes(attribute_input):
    """
    Extracts the property attributes from the given attribute input.

    Parameters:
    attribute_input (bs4.element.Tag): The attribute input to extract the property attributes from.

    Returns:
    list: A list of the extracted property attributes.
    """
    
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

def extract_property_mobiles(mobiles_input):
    """
    Extracts the property mobiles from the given mobiles input.

    Parameters:
    mobiles_input (bs4.element.ResultSet): The mobiles input to extract the property mobiles from.

    Returns:
    list: A list of the extracted property mobiles.
    """
    mobile_list = [mobile.find_all('span', class_='sui-AtomButton-inner') for mobile in mobiles_input]
    return [mobile[1].text if len(mobile) > 1 else "Unknown" for mobile in mobile_list]

def extract_property_ids(ids_input):
    """
    Extracts the property IDs from the given IDs input.

    Parameters:
    ids_input (bs4.element.ResultSet): The IDs input to extract the property IDs from.

    Returns:
    list: A list of the extracted property IDs.
    """
    return [re.split(r'/', ident['href'])[-2] if re.split(r'/', ident['href'])[-1] != 'd' 
             else re.split(r'/', ident['href'])[-2] for i, ident in enumerate(ids_input)]


def property_creation(soup, Property, city, actions):
    """
    Creates a list of Property objects from the given soup.

    Parameters:
    soup (bs4.BeautifulSoup): The soup to create the Property objects from.
    Property (class): The Property class.
    city (str): The city of the properties.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    list: A list of Property objects.
    """
    page_properties = []

    prices, titles, attributes, mobiles, urls, ages = extract_page_data(soup)
    attributes = extract_property_attributes(attributes)
    mobiles = extract_property_mobiles(mobiles)
    #ids = extract_property_ids(urls)
    
    for i in range(len(prices)):
        property = Property(
            price = prices[i].find('span').getText().replace('.', '').replace('€', '').strip(),
            type = titles[i].find('strong').getText().strip(),
            title = titles[i].getText().strip(),
            attributes = attributes[i],
            mobile = mobiles[i],
            address = titles[i].getText().split(' en ')[-1].split(',')[-1].strip(),
            city = city if "," not in city else city.split(',')[1].strip(),
            age = 0 if 'Novedad' in ages[i].getText() else int(ages[i].getText().strip().split(' ')[1]),
            url = urls[i]['href']
            #company = companies[i].getText().strip(),
        )
        page_properties.append(property)
        actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()

    return page_properties

def sanity_check(driver):
    """
    If the driver is stuck in a page, this function will kill the driver and start a new one after 60 seconds.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.

    Returns:
    None
    """
    sleep(60)
    url = driver.current_url
    # kill the driver and start a new one
    driver.quit()
    
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

    driver.get(url)
    
    sleep(2)
    remove_cookie_banner(driver)
    remove_annoying_add(driver)
        


def next_page(driver, actions):
    """
    Clicks the next page button on the website.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    None
    """
    while True:
        try:
            sleep(0.1)
            server_kick(driver)
            remove_annoying_add(driver)
            buttons = driver.find_elements(By.XPATH, '//li[@class="sui-MoleculePagination-item"]')
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(buttons[-1])
            ).click()
            
            break
        except ElementClickInterceptedException:
            actions.key_down(Keys.PAGE_UP).key_up(Keys.PAGE_UP).perform()
            pass
        except TimeoutException:
            sanity_check(driver)
            sleep(3)
            break

def extract_properties(soup, n_pages, driver, actions):
    """
    Extracts the properties from the given soup.

    Parameters:
    soup (bs4.BeautifulSoup): The soup to extract the properties from.
    n_pages (int): The number of pages to extract the properties from.
    driver (selenium.webdriver): The webdriver instance.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    list: A list of Property objects.
    """
    city = soup.find('h1', class_='re-SearchTitle-text').getText().split(' en ')[2].strip()

    @dataclass
    class Property:
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
        

    properties = []
    for page in range(1, n_pages):
        server_kick(driver)
        remove_annoying_add(driver)

        for _ in range(25):
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            sleep(0.1)
        soup = BeautifulSoup(driver.page_source, features="lxml")
        properties.extend(property_creation(soup, Property, city, actions))
        if page < n_pages:
            next_page(driver, actions)

    # Create a dict with the data
    properties = [property.__dict__ for property in properties]

    return properties

def remove_annoying_add(driver):
    """
    Removes pop-up adds that appear on the screen.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.

    Returns:
    None
    """
    # find the button of class ab-close-button wait until it is clickable and click it
    try:
        WebDriverWait(driver, 0.2).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="ab-close-button"]'))
        ).click()
    except TimeoutException:
        pass
    
def server_kick(driver):
    """
    Finds if the server has kicked us out of the website and refreshes the page if it has after waiting a minute.

    Parameters:
    driver (selenium.webdriver): The webdriver instance.

    Returns:
    None
    """
    # search for an h1 with the text "SENTIMOS LA INTERRUPCIÓN" if it exists wait a minute and refresh the page
    try:
        WebDriverWait(driver, 0.3).until(
            EC.presence_of_element_located((By.XPATH, '//h1[text()="SENTIMOS LA INTERRUPCIÓN"]'))
        )
        sanity_check(driver)
    except TimeoutException:
        pass

def scrape(location):
    """
    Extracts the properties from the given soup.

    Parameters:
    soup (bs4.BeautifulSoup): The soup to extract the properties from.
    n_pages (int): The number of pages to extract the properties from.
    driver (selenium.webdriver): The webdriver instance.
    actions (selenium.webdriver.common.action_chains.ActionChains): The ActionChains instance.

    Returns:
    list: A list of Property objects.
    """
    # Set up the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

    # split
    location = location.split(',')

    # Navigate to the website
    driver.get('https://www.fotocasa.es/es')
    actions = ActionChains(driver)
    remove_cookie_banner(driver)
    search_location(location[0] + ", " + location[1], driver)
    scroll_down(driver, actions)
    soup = BeautifulSoup(driver.page_source, features="lxml")
    n_pages = min(number_of_pages(soup), 6)
    if not n_pages or n_pages == 0:
        return {}
    get_top_bar(driver, actions)
    properties = extract_properties(soup, n_pages, driver, actions)
    driver.quit()
    return properties