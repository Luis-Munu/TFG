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

from fake_useragent import UserAgent

from urllib3.exceptions import MaxRetryError

location = ''
current_page = 1
num_pages = 1

############# MANAGEMENT METHODS #############

def create_driver():
    options = webdriver.ChromeOptions()
    options.ignore_certificate_errors = True
    options.disable_blink_features = 'AutomationControlled'
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False) 
    options.allow_running_insecure_content = True
    options.user_agent = UserAgent().random
    options.log_level = 2
    #ptions.executable_path = 'C:/Users/Pepsisonico/Downloads/padres/TFG-FInal/extraction/properties/chromedriver' # replace with the actual path to the Chrome driver executable
    #options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})") 
    return driver

driver = ""

def refresh_driver():
    # get the url with a try except maxtryerror
    try:
        url = driver.current_url
    except MaxRetryError:
        print("We got a MaxRetryError refreshing the driver")
    
    # if we got the url, just change the user agent of the driver and refresh the page
    try:
        if not url is None:
            driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": UserAgent().random})
            driver.refresh()
            actions = ActionChains(driver)
            remove_cookie_banner()
            remove_annoying_add()
    # if we didn't get the url, create a new driver
        else:
            driver = create_driver()
            driver.get('https://www.fotocasa.es/es')
            actions = ActionChains(driver)
            remove_cookie_banner()
            remove_annoying_add()
            # search the location and go to the page we were
            search_location()
            while _ < num_pages: 
                sleep(2)
                next_page(actions)
                _ += 1
            sleep(2)
    except:
        print("We got an error refreshing the driver")
            
    
def remove_cookie_banner():
    # Wait for the accept cookies button to appear
    wait = WebDriverWait(driver, 10)
    try:
        accept_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="TcfAccept"]')))
        # Click the accept cookies button
        accept_button.click()
    except TimeoutException:
        pass
    
def remove_annoying_add():
    try:
        WebDriverWait(driver, 0.2).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="ab-close-button"]'))
        ).click()
    except TimeoutException:
        pass
    
def server_kick():
    try:
        WebDriverWait(driver, 0.3).until(
            EC.presence_of_element_located((By.XPATH, '//h1[text()="SENTIMOS LA INTERRUPCIÓN"]'))
        )
        sanity_check()
    except TimeoutException:
        pass
    
def sanity_check():
    sleep(60)
    try:
        url = driver.current_url
    except MaxRetryError:
        print("Hemos sido bloqueados.")
        
    # kill the driver and start a new one
    while True:
        try:
            refresh_driver()
            break
        except:
            print("Hemos vuelto a fallar, reintentando OTRA VEZ")
            
############# NAVIGATION METHODS #############

def search_location():
    locationa = location[0] + ", " + location[1]
    # use find_element By.XPATH with xpath = './/div[@class="sui-MoleculeAutosuggest-input-container"]/input'
    search_bar = driver.find_element(By.XPATH, '//input[@class="sui-AtomInput-input sui-AtomInput-input-size-m"]')
    # Click the search bar
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(search_bar)).click()
    # Enter the location in the search bar
    search_bar.send_keys(locationa)
    sleep(4)
    search_bar.send_keys(Keys.ENTER)
    sleep(3)
        

def number_of_pages(soup):
    global num_pages
    pages = soup.find_all('li', class_="sui-MoleculePagination-item")
    if len(pages) > 1:
        num_pages = int(pages[-2].find('span').getText())
    else:
        num_pages = 1
    print('Number of pages:', num_pages, '\n')
    return num_pages

def get_top_bar(actions):
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

def scroll_down(actions):
    start_time = time()

    while True:
        try:
            element = driver.find_element(By.XPATH, '//a[@class="sui-AtomButton sui-AtomButton--neutral sui-AtomButton--outline sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link sui-AtomButton--rounded"]')
            server_kick()
            remove_annoying_add()
            actions.move_to_element(element).perform()
            break
        except NoSuchElementException:
            if time() - start_time > 15:
                remove_annoying_add()
                remove_cookie_banner()
                break
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).pause(0.1).perform()
            sleep(0.3)
    
def next_page(actions):
    while True:
        try:
            sleep(0.1)
            server_kick()
            remove_annoying_add()
            buttons = driver.find_elements(By.XPATH, '//li[@class="sui-MoleculePagination-item"]')
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(buttons[-1])
            ).click()
            
            break
        except ElementClickInterceptedException:
            actions.key_down(Keys.PAGE_UP).key_up(Keys.PAGE_UP).perform()
            pass
        except TimeoutException:
            sanity_check()
            sleep(3)
            break
        
############# DATA EXTRACTION METHODS #############

def extract_page_data(soup):
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
    mobile_list = [mobile.find_all('span', class_='sui-AtomButton-inner') for mobile in mobiles_input]
    return [mobile[1].text if len(mobile) > 1 else "Unknown" for mobile in mobile_list]

def extract_property_ids(ids_input):
    return [re.split(r'/', ident['href'])[-2] if re.split(r'/', ident['href'])[-1] != 'd' 
             else re.split(r'/', ident['href'])[-2] for i, ident in enumerate(ids_input)]


def property_creation(soup, Property, city, actions):
    page_properties = []

    prices, titles, attributes, mobiles, urls, ages = extract_page_data(soup)
    attributes = extract_property_attributes(attributes)
    mobiles = extract_property_mobiles(mobiles)
    #ids = extract_property_ids(urls)
    
    shortest_len = min(len(prices), len(titles), len(attributes), len(mobiles), len(urls), len(ages))
    
    for i in range(shortest_len):
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

def extract_properties(soup, actions):
    global num_pages, current_page
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
    for page in range(1, num_pages + 1):
        server_kick()
        remove_annoying_add()

        for _ in range(25):
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            sleep(0.1)
        while True:
            try:
                soup = BeautifulSoup(driver.page_source, features="lxml")
                break
            except MaxRetryError:
                sanity_check()
                continue
        properties.extend(property_creation(soup, Property, city, actions))
        current_page = page
        if current_page < num_pages:
            next_page(actions)

    # Create a dict with the data
    properties = [property.__dict__ for property in properties]

    return properties

#############################################################################################################

def scrape(locationa):
    global location, num_pages, driver
    
    driver = create_driver()
    
    print("Buscando en fotocasa zona: " + locationa + "...")

    # split
    location = locationa.split(',')

    while True:
        try:
            driver.get('https://www.fotocasa.es/es')
            break
        except MaxRetryError as e:
            print(e)
            sanity_check()
    actions = ActionChains(driver)
    remove_cookie_banner()
    search_location()
    scroll_down(actions)
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, features="lxml")
            break
        except MaxRetryError as e:
            print(e)
            sanity_check()
    num_pages = min(number_of_pages(soup), 35)
    if not num_pages or num_pages == 0:
        return {}
    get_top_bar(actions)
    properties = extract_properties(soup, actions)
    driver.quit()
    return properties