# Скачивание и преобразование в DataFrame данных с
#  https://climate.weather.gc.ca/historical_data/search_historic_data_e.html
# А также конвертер этих данных из почасовых в дневные и помесячные

import pandas as pd
import requests as rec
import re
import json

header_1 = """Longitude (x),Latitude (y),Station Name,Climate ID,
Date/Time (LST),Year,Month,Day,Time (LST),Temp (°C),Temp Flag,
Dew Point Temp (°C),Dew Point Temp Flag,Rel Hum (%),Rel Hum Flag,
Wind Dir (10s deg),Wind Dir Flag,Wind Spd (km/h),Wind Spd Flag,
Visibility (km),Visibility Flag,Stn Press (kPa),Stn Press Flag,Hmdx,
Hmdx Flag,Wind Chill,Wind Chill Flag,Weather\n"""

header_2 = """Longitude (x),Latitude (y),Station Name,Climate ID,
Date/Time (LST),Year,Month,Day,Time (LST),Temp (°C),Temp Flag,
Dew Point Temp (°C),Dew Point Temp Flag,Rel Hum (%),Rel Hum Flag,
Precip. Amount (mm),Precip. Amount Flag,Wind Dir (10s deg),Wind Dir Flag,
Wind Spd (km/h),Wind Spd Flag,Visibility (km),Visibility Flag,Stn Press (kPa),
Stn Press Flag,Hmdx,Hmdx Flag,Wind Chill,Wind Chill Flag,Weather\n"""

need_cols_1 = ['Temp (°C)', 'Dew Point Temp (°C)',
 'Rel Hum (%)', 'Wind Dir (10s deg)', 
 'Wind Spd (km/h)', 'Visibility (km)',
 'Stn Press (kPa)', 'Hmdx',
 'Wind Chill']

need_cols_2 = ['Temp (°C)', 'Dew Point Temp (°C)',
 'Rel Hum (%)', 'Precip. Amount (mm)', 'Wind Dir (10s deg)', 
 'Wind Spd (km/h)', 'Visibility (km)',
 'Stn Press (kPa)', 'Hmdx',
 'Wind Chill']

months_names = ['January', 'February', 'March',
                'April', 'May', 'June', 'July',
                'August', 'September', 'October',
                'November', 'December']


def download_climate(station_id, start_year, end_year):
    """
    Скачивает данные с https://climate.weather.gc.ca/historical_data/search_historic_data_e.html
    (использовалось только для почасовых, но мб можно и другие)
    Для скачивания нужно station_id
    Чтобы его получить, нужно выбрать интересующую станцию, нажать Go, перейти на страницу скачивания,
    Нажать F12, выбрать Network, нажать галочку возде "Preserve Log", затем нажать кнопку "Download Data",
    скачать файл с климатикой (он нам не нужен), в окне Network появится окошко с заголовком Name, в нём запрос.
    Нажать на запрос, справа появится "Request URL", напротив него будет ссылка. В ссылке будет "stationID="
    и после -- номер станции. Вот его и вставлять в функцию как station_id

    Возвращает словарь, где ключи -- годы, а значения -- списки текстов ответов от сервера
    Тексты так-то в CSV формате, но каком-то ниочень, плюс ко всему они могут иметь разные колонки
    (один чёрт знает почему), так что после того, как функция вернула all_texts лучше его сохранить в .json
    для надёжности, чтоб потом не пришлось заново качать данные, и потом уже спокойно пихать в .csv

    Климатику надо скачать функцией.
    Я её дам.
    Функции нужно скормить station_id.
    station_id я не дам.
    """
    #station_id=1669 -- для INUVIK A 1959-2013 года
    #station_id=51477 -- для INUVIK A 2013-2020 года
    all_texts = dict()
    for year in range(start_year, end_year):
        texts = []
        print('    ', end='')
        for month in range(1,13):
            r = rec.request('GET', f"https://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID={station_id}&Year={year}&Month={month}&Day=1&time=LST&timeframe=1&submit=Download+Data")
            texts += [r.text]
            print(f'-', end='')
        all_texts[year] = texts
        print(f'Year {year} is done!')
    return all_texts


def dict_to_json(all_texts, file_name):
    """
    Сохраняет Словарь, полученный в download_climate в .json файл 
    """
    with open(f"{file_name}_HOURLY.json", "w") as outfile: 
        json.dump(all_texts, outfile)


def dict_to_csv(all_texts, file_name, header=header_2):
    """
    Объединяет csv ответы из download_climate в единый csv файл
    ОСТОРОЖНО! Ответы могут иметь разное число колонок, поэтому их лучше проверить
    И если это так -- разбить на группы с одинаковым числом и названием колонок
    """
    with open(f"{file_name}_HOURLY.csv", "w") as ouf:
        ouf.write(header)
        for year in range(2013, 2021):
            for month in range(12):
                is_header = True
                for line in all_texts[year][month].replace('"', '').replace('\r', '').split('\n'):
                    if is_header:
                        is_header = False
                        continue
                    try:
                        while True:
                            sub, _ = re.search(r'[a-z],[A-Z]', line).span()
                            sub += 1
                            line = line[:sub]+'/'+line[sub+1:]
                    except AttributeError:
                        ouf.write(line + '\n')


def hourly_to_daily(df, need_cols=need_cols_2, file_name=''):
    """
    Преобразовывает почасовые данные, полученные в dict_to_csv в ежедневные,
    путём усреднения показателей на протяжении дня.
    В need_cols указываем те показатели, что нам нужны.
    Если file_name не пустой, то сохраняет данные в .csv файл.
    """
    years = sorted(list(set(df['Year'])))
    y, m, d = [], [], []
    daily_df = pd.DataFrame(columns=need_cols)
    for year in years:
        months = list(set(df[(df['Year']==year)]['Month']))
        print(f'Year {year}: ', end='')
        for month in months:
            print('-', end='')
            days = list(set(df[(df['Year']==year) & (df['Month']==month)]['Day']))
            for day in days:
                day_df = df[(df['Year']==year) & (df['Month']==month) &(df['Day']==day)]
                daily_df = daily_df.append(day_df[need_cols].mean(skipna=True), ignore_index=True)
                y += [year]
                m += [month]
                d += [day]
        print()
    daily_df['Year'] = y
    daily_df['Month'] = m
    daily_df['Day'] = d
    daily_df = daily_df[['Year', 'Month', 'Day'] + need_cols]
    if file_name:
        daily_df.to_csv(f'{file_name}_DAILY.csv', index=False)
    return daily_df


def daily_to_monthly(df, need_cols=need_cols_2, file_name=''):
    """
    Преобразовывает ежедневные данные, полученные в hourly_to_daily в ежемесячные,
    путём усреднения показателей на протяжении месяца.
    В need_cols указываем те показатели, что нам нужны.
    Если file_name не пустой, то сохраняет данные в .csv файл.
    """
    years = sorted(list(set(df['Year'])))
    y, m, d = [], [], []
    monthly_df = pd.DataFrame(columns=need_cols)
    for year in years:
        months = list(set(df[(df['Year']==year)]['Month']))
        print(f'Year {year}: ', end='')
        for month in months:
            print('-', end='')
            mon_df = df[(df['Year']==year) & (df['Month']==month)]
            monthly_df = monthly_df.append(mon_df[need_cols].mean(skipna=True), ignore_index=True)
            y += [year]
            m += [month]
        print()
    monthly_df['Year'] = y
    monthly_df['Month'] = m
    monthly_df = monthly_df[['Year', 'Month'] + need_cols]
    if file_name:
        monthly_df.to_csv(f'{file_name}_MONTHLY.csv', index=False)
    return monthly_df


def hourly_to_monthly(df, file_name=''):
    """
    Ну тут всё понятно
    """
    d_df = hourly_to_daily(df)
    m_df = daily_to_monthly(d_df)
    if file_name:
        m_df.to_csv(f'{file_name}_MONTHLY.csv', index=False)
    return m_df


def montly_to_measurement(df:pd.DataFrame, mes:str):
    """
    df - DataFrame полученный из daily_to_monthly
    mes - название колонки с измерением, по которой нужно построить отдельный DF

    Возвращает DF, пригодный для plot_trends
    (первая колонка -- год, остальные -- месяцы, в ячейках значения по mes)
    """
    res_df = df[df['Month']==1][['Year', mes]].rename(columns={mes:months_names[0]})
    for month in range(2,13):
        temp_df = df[df['Month']==month][['Year', mes]].rename(columns={mes:months_names[month-1]})
        res_df = pd.merge(res_df, temp_df)
    return res_df
