import pandas as pd
from os import listdir


characteristics = [
        'precipitation',
        'relative humidity',
        'sunshine duration',
        'temperature',
        'vpd'
    ]

def load_data(path='input/climate/real', characteristics=characteristics):

    data = dict()

    for char in characteristics:
        for file in listdir(f'{path}/{char}'):
            loc_df = pd.read_csv(f'{path}/{char}/{file}')
            if 'WMO Index' in loc_df.columns:
                loc_df = loc_df.drop(columns=['WMO Index'])
            if 'Индекс ВМО' in loc_df.columns:
                loc_df = loc_df.drop(columns=['Индекс ВМО'])
            data[file.split('.')[0]] = loc_df
    
    return data
