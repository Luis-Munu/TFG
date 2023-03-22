#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import sys
import os
from datetime import datetime
from utils.fotocasa import fotocasa_bot


def main():
    # Check if parameters are passed
    if len(sys.argv) <= 1:
        print('No cities selected. \nExiting...')
        return -1

    # Set working directory
    os.chdir(os.path.abspath(''))

    # Get parameters
    cities_list = sys.argv[1:]
    print(f'Downloading rent data for {len(sys.argv)-1} cities...')
    print(','.join(cities_list))

    # Create empty dataframe
    df = pd.DataFrame()

    # Perform web scraping
    for city in cities_list:
        print(city)
        df_city = fotocasa_bot(city)
        df = df.append(df_city, ignore_index=True)
    print('Data downloaded from:')
    print(df['Ciudad'].unique())
    print(f'Total number: {df.shape[0]}')

    # Print dataframe info
    print(df.info())

    # Export data
    export_folder = 'data'
    filename = 'data_'+datetime.now().strftime("%Y-%m-%d_%H_%M_%S")+'.csv'
    dir_export = os.path.join(os.path.dirname(os.getcwd()), export_folder)
    full_exp_path = os.path.join(dir_export, filename)

    if not os.path.exists(dir_export):
        os.makedirs(dir_export)

    df.to_csv(full_exp_path, index=False, sep=';')


if __name__ == '__main__':
    main()
