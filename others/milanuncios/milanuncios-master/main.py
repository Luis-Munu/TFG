import os
from typing import List, Union

from requests_html import HTMLSession

from excel_functions import excel_writing
from sql_functions import (
    get_last_entry, diff_dates, add_entrie, estimated_values, add_days,
    date_now
)

START_PRICE = 600


class Blocked(Exception):
    pass


def get_number(lnk: str) -> int:
    """Returns an integer number of properties on the web page by reference lnk."""
    r = session.get(lnk)
    try:
        about = r.html.find('.ma-ContentListingSummary-label', first=True)
    except Exception:
        return 0

    try:
        target_str = about.text
    except Exception:
        raise Blocked('Your enter is blocked. Wait 60 minutes or change IP')

    if ' anuncios' in target_str:
        target_number = int(target_str[:target_str.find(' anuncios')])
        return target_number
    else:
        return 0


def prises_list(start_price: int) -> list:
    """List of twains (as a tuple) of price forks."""
    lst = []
    for i in range(0, 301, 100):
        twain = (str(start_price + i), str(start_price + i + 99))
        lst.append(twain)
    return lst


def visualization(count: int) -> str:
    """Visualization of the script process in terminal."""
    zero = lambda x: '' if x >= 10 else '0'
    num_dict = {1: 'st', 2: 'nd', 3: 'rd'}
    empty_space = 10 - count
    if count < 4:
        suffix = num_dict[count]
    else:
        suffix = 'th'
    return f'Parsing of {zero(count)}{count}-{suffix} page' + ' ' * empty_space + ' ...'


towns = ('malaga', 'torremolinos')
final_values_list = []
session = HTMLSession()
counter = 0
excel_file = 'Estadistica.xlsm'
db = 'db.sqlite3'
table_name = 'prices'

if __name__ == '__main__':
    for town in towns:
        for prise_from, prise_to in prises_list(START_PRICE):
            link = f'https://www.milanuncios.com/alquiler-de-pisos-en-{town}-malaga/?' \
                   f'desde={prise_from}&hasta={prise_to}&demanda=n&banosd=2&dormd=3'
            number = get_number(link)
            final_values_list.append(number)
            counter += 1
            print(visualization(counter))

    for town in towns:
        link = f'https://www.milanuncios.com/alquiler-de-pisos-en-{town}-malaga/?' \
               f'demanda=n&banosd=1&dormd=4'
        number = get_number(link)
        final_values_list.append(number)
        counter += 1
        print(visualization(counter))
    print(final_values_list)
    excel_writing(excel_file, final_values_list.copy())

    # work with database db.sqlite3
    final_list: List[Union[str, int]] = [date_now] + final_values_list
    last_entry: tuple = get_last_entry(db, table_name)
    last_entry_date: str = last_entry[0]
    last_entry_list: list = list(last_entry[1:])
    diff_days: int = diff_dates(last_entry_date, date_now)
    if diff_days == 1:
        print('when diff_days == 1:', final_list)
        add_entrie(db, table_name, [final_list])
    elif diff_days > 1:
        multi_list = estimated_values(last_entry_list, final_values_list, diff_days)
        for i in range(diff_days - 1):
            multi_list[i] = [add_days(last_entry_date, i + 1)] + multi_list[i]
        multi_final_list = multi_list + [final_list]
        print('when diff_days > 1:', multi_final_list)
        add_entrie(db, table_name, multi_final_list)
    os.startfile(db)

    os.startfile(excel_file)
