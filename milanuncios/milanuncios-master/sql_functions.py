import math
import sqlite3 as sq
from datetime import date, datetime, timedelta
from typing import List

date_now: str = date.today().strftime('%Y-%m-%d')


def get_last_entry(database_name: str, table_name: str) -> tuple:
    """Returns last entry from <database_name> <table_name>."""
    with sq.connect(database_name) as con:
        cur = con.cursor()
        cur.execute(f'''SELECT * 
                        FROM {table_name} 
                        ORDER BY rowid DESC 
                        LIMIT 1
        ''')
        last_entry = cur.fetchone()
        return last_entry


def diff_dates(start_day: str, stop_day: str) -> int:
    """Returns difference in days between two dates. Dates format is 'yyyy-mm-dd'."""
    start = datetime.strptime(start_day, '%Y-%m-%d').date()
    stop = datetime.strptime(stop_day, '%Y-%m-%d').date()
    difference = (stop - start).days
    return difference


def add_entrie(database_name: str, table_name: str, lst: List[list]) -> None:
    """Add entries into <database_name> <table_name> from list of tuples/lists."""
    with sq.connect(database_name) as con:
        cur = con.cursor()
        cur.executemany(f'INSERT INTO {table_name} VALUES(?,?,?,?,?,?,?,?,?,?,?)', lst)


def estimated_values(lst_1: list, lst_2: list, parts: int) -> List[list]:
    """Returns the suggested entries without dates as a list of lists of values
    for the missing days.
    """
    result_lst = []
    difference_lst = []
    entry = []
    for i in range(len(lst_1)):
        difference_lst.append(lst_2[i] - lst_1[i])
    for i in range(parts-1):
        for j in range(len(lst_1)):
            entry.append(lst_1[j] + math.trunc(difference_lst[j] / parts * (i+1)))
        result_lst.append(entry)
        entry = []
    return result_lst


def add_days(init_date: str, days: int) -> str:
    """Returns date adding days to initial date <init_date>."""
    date_init = datetime.strptime(init_date, '%Y-%m-%d')
    date_result = (date_init + timedelta(days=days)).date()
    return str(date_result)


def create_table(database_name: str, table_name: str):
    """Creates <table_name> in <database_name>."""
    with sq.connect(database_name) as con:
        cur = con.cursor()
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}(
        date DATE,
        malaga600_699 INTEGER NOT NULL,
        malaga700_799 INTEGER NOT NULL,
        malaga800_899 INTEGER NOT NULL,
        malaga900_999 INTEGER NOT NULL,
        torremolinos600_699 INTEGER NOT NULL,
        torremolinos700_799 INTEGER NOT NULL,
        torremolinos800_899 INTEGER NOT NULL,
        torremolinos900_999 INTEGER NOT NULL,
        malaga_4d INTEGER NOT NULL,
        torremolinos_4d INTEGER NOT NULL
        )
        ''')


def delete_table(database_name: str, table_name: str):
    """Deletes <table_name> from <database_name>."""
    with sq.connect(database_name) as con:
        cur = con.cursor()
        cur.execute(f'DROP TABLE IF EXISTS {table_name}')


if __name__ == '__main__':
    """Creates database 'db.sqlite3' with table 'prices' inside the directory 
    of the current project.
    """
    create_table('db.sqlite3', 'prices')
