import pandas as pd
import numpy as np
from datetime import date

month_names = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']


def row_to_date(row: pd.Series):
    return date(int(row['Year']),
                int(row['Month']),
                int(row['Day']))


def fill_missing_dates(df: pd.DataFrame):
    """
    Добавляет все пропущенные в DataFrame дни для ежедневных измерений
    НЕ ДОБАВЛЯЕТ 29 ФЕВРАЛЯ!!! Это делается в rotate_daily_climate!!!
    На вход принимает DataFrame с колонками: Year, Month, Day и любым числом ежедневных измерений
    """
    df['Date'] = df.apply(lambda row: row_to_date(row), axis=1)
    r = pd.date_range(start=date(df.Year.min(),1,1), end=date(df.Year.max(), 12, 31))
    new_df = df.set_index('Date').reindex(r).rename_axis('Date').reset_index()
    new_df['Year'] = new_df.apply(lambda row: row['Date'].year, axis=1)
    new_df['Month'] = new_df.apply(lambda row: row['Date'].month, axis=1)
    new_df['Day'] = new_df.apply(lambda row: row['Date'].day, axis=1)
    return new_df


def rotate_daily_climate(df: pd.DataFrame):
    """
    Поворачивает климатические данные с meteo.ru так, чтобы годы шли по столбцам
    (сделано, чтобы не переписывать get_crn_climate_correlation под новый стандарт)
    На вход принимает DataFrame с колонками Year, Month, Day, Temp, Prec
    """
    temperature = dict()
    precipitation = dict()

    for year in list(set(df['Year'])):
        temp = df[df['Year']==year].reset_index(drop=True)
        if len(temp) < 366:
            temp.loc[58.5] = year, 2, 29, np.NaN, np.NaN
            temp = temp.sort_index().reset_index(drop=True)
        temperature[year] = temp['Temp']
        precipitation[year] = temp['Prec']

    temperature = pd.DataFrame(temperature)
    precipitation = pd.DataFrame(precipitation)
    return temperature, precipitation


def monthly_climate_offset_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Смещает осенние и декабрьские данные так, чтобы при обработки брались данные с прошлого года,
    а также выбрасывает годы, в которые больше трёх пропусков
    """
    df = df.copy()
    df['September'] = [np.NaN] + list(df['September'][:-1])
    df['October'] = [np.NaN] + list(df['October'][:-1])
    df['November'] = [np.NaN] + list(df['November'][:-1])
    df['December'] = [np.NaN] + list(df['December'][:-1])

    rows_to_drop = []
    for i, row in df.iterrows():
        if any(np.isnan(row[1:13])):
            l = sum([1 for o in np.isnan(row[1:13]) if o])
            if l > 3:
                rows_to_drop += [i]
    
    df = df.drop(rows_to_drop)
    return df.reset_index(drop=True)


def highlight_significant_cells(x):
    """
    Выделяет ячейку в DataFrame, если в ней p-value < 0.05. Я яейка должна иметь формат "0.00\n(p=0.0000)"
    Используется в DataFrame.style.applymap
    """
    try:
        r, p = x.split('=')
    except:
        return None
    r = float(r[:-3])
    p = float(p[:-1])
    if p<0.05:
        if r>0:
            return 'background-color: lightgreen'
        else:
            return 'background-color: lightcoral'
    return None


def get_climate_df_mean(df, columns=month_names):
    df = monthly_climate_offset_and_clean(df)
    df['Mean'] = df[columns].mean(axis=1, skipna=True)
    return df[['Year', 'Mean']]


def get_climate_df_sum(df, columns=month_names):
    df = monthly_climate_offset_and_clean(df)
    df['Sum'] = df[columns].sum(axis=1, skipna=True)
    return df[['Year', 'Sum']]
