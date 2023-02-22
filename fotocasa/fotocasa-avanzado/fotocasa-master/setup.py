from setuptools import setup, find_packages
setup(
    name='fotocasa',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'psycopg2',
        'sqlalchemy'
        'scrapy-rotating-proxies'
    ],
    entry_points={'scrapy': ['settings = fotocasa.settings']}
)
