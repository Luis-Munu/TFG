from . import preprocessing
from . import scraping

"""
Script encargado de extraer información de las diferentes localizaciones de Fotocasa y procesarlas.
Este es un proceso destructivo, si se tiene información guardada previamente, se perderá.
Dura varias horas.
"""

def zone_extraction():
    scraping.name_extraction()
    preprocessing.zone_preprocessing()