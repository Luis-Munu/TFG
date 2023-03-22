# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class UniversalScraperItem(scrapy.Item):
    referencia = Field()
    precio = Field()
    particular = Field()
    habitaciones = Field()
    banos = Field()
    superficie = Field()
    link = Field()
    web = Field()
    ciudad = Field()
    comunidad = Field()
