import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver  # import webdriver
from selenium.webdriver.chrome.service import Service  # import Service
from selenium.webdriver.common.by import By  # import By
from selenium.webdriver.support.ui import WebDriverWait  # import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC  # import expected_conditions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, \
    ElementNotInteractableException  # import exceptions
from selenium.webdriver.common.keys import Keys  # import Keys
import pandas as pd  # import pandas
import time  # import time
from fake_useragent import UserAgent  # import UserAgent
import re


def fotocasa_bot(ciudad):
    """
    Bot that performs a search in Fotocasa and stores the features of the
    apartments from 'ciudad' in a dataframe.
    Parameters
    ----------
    ciudad : str
        Name of the city where the apartments will be searched.
    Returns
    -------
    df : pandas dataframe
        The dataframe containing the features of the apartments from 'ciudad'.
    """
    # User agent
    user_agent = UserAgent().random
    # print(user_agent, '\n')

    # Driver path
    driver_path = "../chromedriver/chromedriver.exe"

    # Specify driver (chromedriver)
    ser = Service(driver_path)
    ops = webdriver.ChromeOptions()
    ops.add_argument(f'user-agent={user_agent}')
    s = webdriver.Chrome(service=ser, options=ops)

    # Fotocasa url
    url = "https://www.fotocasa.es/es"

    # Open the website
    s.get(url)

    # Sleep 3 seconds
    time.sleep(3)

    # Print the title of the website
    # print(s.title, "\n")

    ## STEP 0: Accept cookies

    WebDriverWait(s, 60).until(
        EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="TcfAccept"]'))
    ).click()

    # print("Cookies accepted!", '\n')

    # Sleep 3 seconds
    time.sleep(3)

    ## STEP 1: Click to 'Alquilar'

    WebDriverWait(s, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, './/div[@class="re-HomeSearchSelector-item re-HomeSearchSelector-item--rent"]'))
    ).click()

    # print("Alquilar!", '\n')

    # Sleep 3 seconds
    time.sleep(3)

    ## STEP 2: Search 'Sabadell'

    bs = s.find_element(By.XPATH, '//input[@class="sui-AtomInput-input sui-AtomInput-input-size-m"]')

    WebDriverWait(s, 30).until(
        EC.element_to_be_clickable(bs)
    ).click()

    # print("Searching...", '\n')

    # Sleep 5 seconds
    time.sleep(5)

    try:
        actions = ActionChains(s)
        actions.move_to_element(bs).perform()

        # Send keys
        bs.send_keys(ciudad)

        # Sleep 3 seconds
        time.sleep(3)

        # Send ENTER
        bs.send_keys(Keys.ENTER)

    except ElementNotInteractableException:
        pass

    # Sleep 10 seconds
    time.sleep(10)

    ## STEP 3: Store the number of pages

    scroll = True
    while scroll == True:
        try:
            # Sleep 1 second
            time.sleep(1)
            # Scroll down
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            # Sleep 1 second
            time.sleep(1)
            actions.move_to_element(
                s.find_element(By.XPATH,
                               '//a[@class="sui-LinkBasic sui-AtomButton sui-AtomButton--primary sui-AtomButton--solid sui-AtomButton--center sui-AtomButton--small sui-AtomButton--link"]')
            ).perform()
            scroll = False
        except NoSuchElementException:
            pass

    # Convert to html
    html_txt = s.page_source
    # Convert to BeautifulSoup object
    soup = BeautifulSoup(html_txt, features="lxml")
    # Find page selector buttons
    pages = soup.find_all('li', class_="sui-MoleculePagination-item")
    if len(pages) > 1:
        n_pages = int(pages[-2].find('span').getText())
    else:
        n_pages = 1
    # print('Number of pages:', n_pages, '\n')
    # Sleep 2 seconds
    time.sleep(2)

    scroll = True
    while scroll == True:
        try:
            # Scroll down
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            # Sleep 1 second
            time.sleep(1)
            actions.move_to_element(
                s.find_element(By.XPATH, '//header[@class="re-SharedTopbar re-SharedTopbar--search"]')
            ).perform()
            scroll = False
        except NoSuchElementException:
            pass

    # Sleep 5 seconds
    time.sleep(5)

    ## STEP 4: Store the data in lists

    # Store the city
    city = re.split(' en ', soup.find('h1', class_='re-SearchTitle-text').getText())[1].strip()
    # List to store the prices
    lista_precios = []
    # List to store the types
    lista_tipos = []
    # List to store the titles
    lista_titulos = []
    # List to store the attributes
    lista_atributos = []
    # List to store the telephones
    lista_telefonos = []
    # List to store the cities
    lista_ciudades = []
    # List to store the IDs
    lista_ids = []

    for page in range(1, n_pages + 1):
        # print('Page:', page)
        for i in range(13):
            # Convert to html
            html_txt = s.page_source
            # Convert to BeautifulSoup object
            soup = BeautifulSoup(html_txt, features="lxml")

            try:
                # Find all prices in the page
                precios = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardPriceComposite')
                # Find all types in the page
                tipos = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTitle')
                # Find all titles in the page
                titulos = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('span', class_='re-CardTitle')
                # Find all attributes in the page
                attributes = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('ul', class_=re.compile('-wrapper'))
                atrs = []
                # Find all telephones in the page
                telefonos = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('div', class_='re-CardContact-appendix')
                # Find all IDs in the page
                ids = soup.find('div', class_='re-SearchOtherZonesBlock').find_all_previous('a', class_=re.compile('-info-container'))
            except AttributeError:
                # Find all prices in the page
                precios = soup.find_all('span', class_='re-CardPriceComposite')
                # Find all types in the page
                tipos = soup.find_all('span', class_='re-CardTitle')
                # Find all titles in the page
                titulos = soup.find_all('span', class_='re-CardTitle')
                # Find all attributes in the page
                attributes = soup.find_all('ul', class_=re.compile('-wrapper'))
                atrs = []
                # Find all telephones in the page
                telefonos = soup.find_all('div', class_='re-CardContact-appendix')
                # Find all IDs in the page
                ids = soup.find_all('a', class_=re.compile('-info-container'))

            pisos = []
            # Store prices at list
            for p, precio in enumerate(precios):
                preu = precio.find('span').getText()
                if preu != 'A consultar' and 'mes' in preu:
                    lista_precios.append(preu)
                    pisos.append(p)

            # Store types at list
            for t, tipo in enumerate(tipos):
                if t in pisos:
                    tip = tipo.find('span').getText()
                    lista_tipos.append(tip)

            # Store titles at list
            for t, titulo in enumerate(titulos):
                if t in pisos:
                    tit = titulo.getText()
                    lista_titulos.append(tit)

            # Store attributes at list
            k = 0
            for atributo in attributes:
                atributos = atributo.find_all('li', class_=re.compile('-feature'))
                for n_atr, atributo in enumerate(atributos):
                    if k in pisos:
                        try:
                            atr = atributo.find('span').getText()
                            # print('WITH ICONS')
                        except AttributeError:
                            atr = atributo.getText()
                            # print('WITHOUT ICONS')
                        # print(n_atr, atr)
                        if 'hab' in atr and len(atrs) > 0 or 'baño' in atr and len(atrs) >= 2 or 'm²' in atr and len(atrs) >= 3:
                            k += 1
                            # print(f'Añadir la lista local ({atrs}) a la lista global!')
                            lista_atributos.append(atrs)
                            atrs = []
                            # print(f'Y añadir {atr} a la lista local!')
                            atrs.append(atr)
                        elif n_atr == len(list(atributos)) - 1:
                            k += 1
                            atrs.append(atr)
                            lista_atributos.append(atrs)
                            # print(f'FINAL! Añadir {atr} a la lista local y {atrs} a la lista global!')
                            atrs = []
                        else:
                            # print(f'Añadir {atr} a la lista local ({atrs})!')
                            atrs.append(atr)
                    else:
                        k += 1

            # Store telephones at list
            for t, telefono in enumerate(telefonos):
                if t in pisos:
                    tel = telefono.find_all('span', class_='sui-AtomButton-inner')
                    if len(tel) == 1:
                        lista_telefonos.append("Unknown")
                    else:
                        lista_telefonos.append(tel[1].text)

            # Store cities at list
            for c in range(len(precios)):
                if c in pisos:
                    lista_ciudades.append(city)

            # Store IDs at list
            for i, ident in enumerate(ids):
                if i in pisos:
                    ide = re.split(r'/', ident['href'])[-1]
                    if ide == 'd':
                        ide = re.split(r'/', ident['href'])[-2]
                    lista_ids.append(ide)

            # Scroll down
            actions.key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
            # Sleep 0.5 seconds
            time.sleep(0.5)

        if page < n_pages:
            scroll = True
            while scroll == True:
                try:
                    # Sleep 1 second
                    time.sleep(1)
                    buttons = s.find_elements(By.XPATH, '//li[@class="sui-MoleculePagination-item"]')
                    WebDriverWait(s, 30).until(
                        EC.element_to_be_clickable(buttons[-1])
                    ).click()
                    # print('Next page!', '\n')
                    scroll = False
                except ElementClickInterceptedException:
                    # Scroll up
                    actions.key_down(Keys.PAGE_UP).key_up(Keys.PAGE_UP).perform()
                    pass

    ## STEP 5: Create the dataframe

    df = clean_fotocasa_data(lista_ids, lista_precios, lista_tipos, lista_titulos, lista_atributos, lista_telefonos,
                             lista_ciudades)

    return df


def clean_fotocasa_data(ids, precios, tipos, titulos, atributos, telefonos, ciudades):
    """
    Function that creates the dataframe from the input lists and cleans it.
    Parameters
    ----------
    ids : list
        List containing the ID of each apartment.
    precios : list
        List containing the price of each apartment.
    tipos : list
        List containing the type of each apartment.
    titulos : list
        List containing the title of each apartment.
    atributos : list
        List containing the attributes of each apartment.
    telefonos : list
        List containing the phone number of each apartment.
    ciudades : list
        List containing the city of each apartment.
    Returns
    -------
    df : pandas dataframe
        The cleaned dataframe created from the input lists.
    """
    dfr = {'ID': ids,
           'Precio (€/mes)': precios,
           'Tipo': tipos,
           'Título': titulos,
           'Atributos': atributos,
           'Teléfono': telefonos,
           'Ciudad': ciudades
           }

    # Create dataframe
    df = pd.DataFrame(dfr)

    # Clean price column
    df.replace(' € /mes', '', regex=True, inplace=True)
    df.replace('\.', '', regex=True, inplace=True)
    df['Precio (€/mes)'] = pd.to_numeric(df['Precio (€/mes)'])

    # Clean phone number column -> Remove spaces
    df['Teléfono'] = df['Teléfono'].str.replace(' ', '')

    # Process "Título" column
    df['Título'] = df['Título'].apply(lambda x: x.split(' en ')[1])
    df['Dirección'] = [item.split(',')[0].strip() if ',' in item else np.nan for item in df['Título']]
    df['Barrio'] = [item.split(',')[-1].strip() if ',' in item else item for item in df['Título']]
    df['Dirección'] = df['Dirección'].str.strip()
    df['Barrio'] = df['Barrio'].str.strip()
    df = df.drop(['Título'], axis=1)

    # Atributes dictionary with attribute name and string to find
    attr = {'Habitaciones': 'hab',
            'Baños': 'baño',
            'Superficie (m2)': 'm²',
            'Planta': 'Planta',
            'Ascensor': 'Ascensor',
            'Terraza': 'Terraza',
            'Parking': 'Parking',
            'Calefacción': 'Calefacción',
            'Aire': 'Aire',
            'Balcón': 'Balcón'
            }

    # Lists with numeric and boolean attributes
    num_attrs = list(attr.keys())[0:4]
    bool_attrs = list(attr.keys())[4:10]

    # Create new columns for numerical attributes
    for at in num_attrs:
        df[at] = df['Atributos'].apply(process_col_num, str_find=attr[at])

    # Create new columns for boolean attributes
    for at in bool_attrs:
        df[at] = df['Atributos'].apply(process_col_bool, str_find=attr[at])

    # Drop 'Atributos' column
    df.drop(['Atributos'], axis=1, inplace=True)

    # Drop duplicates
    df.drop_duplicates(inplace=True, ignore_index=True)

    # Create Price per m^2
    df['Precio del m2 (€/m2)'] = df['Precio (€/mes)'] / df['Superficie (m2)']

    return df


def process_col_num(attr_list, str_find):
    """
    Function that creates the numerical columns.
    Parameters
    ----------
    attr_list : list
        List containing the numerical attributes of an apartment.
    str_find : str
        String to find in each attribute from 'attr_list'.
    Returns
    -------
    float(re.findall(r'\d+', attr)[0]) : float
        Numerical value if 'attrlist' contains an attribute containing 'str_find'.
    np.nan : float
        NaN value if 'attrlist' does not contain any attribute containing 'str_find'.
    """
    for attr in attr_list:
        if str_find in attr:
            return float(re.findall(r'\d+', attr)[0])
    return np.nan


def process_col_bool(attr_list, str_find):
    """
    Function that creates the boolean columns.
    Parameters
    ----------
    attr_list : list
        List containing the boolean attributes of an apartment.
    str_find : str
        String to find in each attribute from 'attr_list'.
    Returns
    -------
    True : bool
        Numerical value if 'attrlist' contains an attribute containing 'str_find'.
    False : bool
        NaN value if 'attrlist' does not contain any attribute containing 'str_find'.
    """
    for attr in attr_list:
        if str_find in attr:
            return True
    return False
