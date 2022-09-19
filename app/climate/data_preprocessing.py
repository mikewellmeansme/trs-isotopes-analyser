import pandas as pd
from os import listdir

needed_columns = ['Year', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

characteristics = [
    'precipitation',
    'relative humidity',
    'sunshine duration',
    'temperature',
    'vpd'
]

class WrongMontlyDataColumns(Exception):
    pass


def check_monthly_climate_df(df):
    global needed_columns
    return set(needed_columns) == set(df.columns)


def load_data(path='input/climate/real', characteristics=characteristics):

    data = dict()

    for char in characteristics:
        for file in listdir(f'{path}/{char}'):
            file_path = f'{path}/{char}/{file}'
            loc_df = pd.read_csv(file_path)

            if 'WMO Index' in loc_df.columns:
                loc_df = loc_df.drop(columns=['WMO Index'])
            if 'Индекс ВМО' in loc_df.columns:
                loc_df = loc_df.drop(columns=['Индекс ВМО'])
            
            if not check_monthly_climate_df(loc_df):
                raise WrongMontlyDataColumns(f'File {file_path} does not match the monthly df climate format!')

            data[file.split('.')[0]] = loc_df
    
    return data
