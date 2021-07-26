import numpy as np
import pandas as pd
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from utils.functions import dropna_pearsonr


m_names = ['S', 'O', 'N', 'D', 'J', 'F', 'M', 'A', 'M ', 'J', 'J', 'A']


def plot_mothly_dendroclim(df_crn:pd.DataFrame, dfs_char:list, ylabels:list, colors:list, title:str=''):
    """
    df_crn: DataFrame c хронологией - первая колонка (Year) годы, вторая - хронология (названа как угодно)
    dfs_char: список DataFrame'ов с характеристиками, с которыми требуется корреляция
              первая колонка -- годы (Year), все остальные -- месяцы (названы как угодно)
    ylabels: список названий характеристик
    clors: цвета, которыми нужно рисовать линии для измерения
    """
    if len(dfs_char)!=len(ylabels) or len(dfs_char)!=len(colors):
        raise Exception('Not every DataFrame have its own label!')

    rs, ps = {name:[] for name in ylabels}, {name:[] for name in ylabels}
    
    for key, df in zip(ylabels, dfs_char):
        l = list(set(df_crn['Year']) & set(df['Year']))
        lmax, lmin = max(l), min(l)

        for i in range(1, 13):
            df1 = df_crn[(df_crn['Year']>=lmin) & (df_crn['Year']<=lmax)]
            df2 = df[(df['Year']>=lmin) & (df['Year']<=lmax)]
            x = np.array(df1.iloc[:, 1])
            y = np.array(df2.iloc[:, i])
            if 9 <= i <= 12:
                y = np.insert(y, 0, np.nan)
                y = np.delete(y, -1)
            r, p = dropna_pearsonr(x, y)
            rs[key] += [r]
            ps[key] += [p]
    
        rs[key] = np.concatenate([rs[key][8:12], rs[key][:8]])
        ps[key] = np.concatenate([ps[key][8:12], ps[key][:8]])

    fig, ax = plt.subplots(figsize=(6,5))
    plt.subplots_adjust(right=0.9)

    for o, key in enumerate(ylabels):
        
        ax.plot(rs[key], label=key, color=colors[o])
        ax.plot([j for j, p in enumerate(ps[key]) if p<0.05],
                [rs[key][j] for j, p in enumerate(ps[key]) if p<0.05],
                marker='D', linestyle = 'None', color=colors[o])
    
    ax.legend(frameon=False) 
    ax.set_xticks([i for i in range(0,12)])
    ax.set_xticklabels(m_names)
    ax.set_ylim([-0.6, 0.6])
    ax.set_xlabel('Months')
    ax.set_ylabel('Pearson R')
    ax.set_title(title)

    plt.savefig(f'output/dendroclim_monthly_{title}.png', dpi=200)
    plt.close(fig)

    return fig, ax


def get_crn_climate_correlation(temperature:pd.DataFrame, precipitation:pd.DataFrame,
                                chronology:list, start_year, end_year, window=21, grab=0):
    """
    temperature, precipitation: DataFrame, где по колонкам идут годы
    chronology: список значений хронологии по которой идёт сравнение
    window: окно скользящего среднего, сглаживающее температуры и осадки
    grab: то, сколько дней захватываем с прошлого года

    Метод нахождения коррелции между заданной хронолгией и климатикой,
    сглаженной скользящим средним с окном равным window

    !!!ПОКА ЧТО РАБОТАЕТ ТОЛЬКО С ЗАРАНЕЕ ОБРЕЗАННЫМИ ДАННЫМИ!!!
    (в климатики и хронологии должно быть одинаковое число лет)
    """
    # TODO: Нормальную обрезку по start_year, end_year
    # Вставляем данные window последних дней предыдущих лет в начала DataFrame'ов температуры и осадков
    # Для просчёта скользящего среднего сквозным через годы образом 
    _temp = temperature.iloc[-grab-window//2:]
    _temp = _temp.rename(columns={i:i+1 for i in _temp.columns})
    _temp = _temp.drop(_temp.columns[-1], axis=1)
    _temp.insert(0, _temp.columns[0]-1, np.NaN)
    _temp = pd.concat([_temp.reset_index(drop=True), temperature.reset_index(drop=True)],
                        axis=0,
                        ignore_index=True)
    _prec = precipitation.iloc[-grab-window//2:]
    _prec = _prec.rename(columns={i:i+1 for i in _prec.columns})
    _prec = _prec.drop(_prec.columns[-1], axis=1)
    _prec.insert(0, _prec.columns[0]-1, np.NaN)
    _prec = pd.concat([_prec.reset_index(drop=True), precipitation.reset_index(drop=True)],
                        axis=0,
                        ignore_index=True)
    # Сглаживаем климатику скользящим средним с окном равным window
    _temp = _temp.rolling(window=window, min_periods=1, center=True).mean()
    _temp = _temp.drop(range(0, window//2+1), axis=0)
    _temp[_temp.columns[0]][0:window//2] = np.NaN
    _temp = _temp.reset_index(drop=True)
    _prec = _prec.rolling(window=window, min_periods=1, center=True).sum()
    _prec = _prec.drop(range(0, window//2+1), axis=0)
    _prec[_prec.columns[0]][0:window//2] = np.NaN
    _prec = _prec.reset_index(drop=True)
    # Считаем корреляции
    temp_corr = []
    for index, row in _temp.iterrows():
        temp_corr += [dropna_pearsonr(row, chronology)[0]]
    prec_corr = []
    for index, row in _prec.iterrows():
        prec_corr += [dropna_pearsonr(row, chronology)[0]]
    return temp_corr, prec_corr


def plot_daily_dendroclim(t:list, p:list, title:str='', p_val=0.27, p_label='p<0.01'):
    """
    t: список коэффицентов корреляции, полученный в get_crn_climate_correlation для температуры
    p: |------| для осадков
    """
    template_df = pd.DataFrame()
    template_df['Date'] = pd.date_range('1999-01-01', '2000-12-31')
    template_df['Temp'] = [np.NaN for _ in range(731-len(t))] + t
    template_df['Prec'] = [np.NaN for _ in range(731-len(p))] + p

    fig, ax = plt.subplots()
    ax.plot(template_df['Date'], [p_val for _ in template_df['Date']], color='gray', label=p_label, linestyle='--')
    ax.plot(template_df['Date'], [-p_val for _ in template_df['Date']], color='gray', linestyle='--')
    ax.plot(template_df['Date'], template_df['Temp'], color='red', label='Temperature')
    ax.plot(template_df['Date'], template_df['Prec'], color='blue', label='Precipitation')
    ax.legend(frameon=False)
    ax.xaxis.set_major_locator(dates.MonthLocator())
    # 16 is a slight approximation since months differ in number of days.
    ax.xaxis.set_minor_locator(dates.MonthLocator(bymonthday=16))

    ax.xaxis.set_major_formatter(ticker.NullFormatter())
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%b'))

    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')

    ax.set_title(title)
    ax.set_ylabel('Pearson R')
    ax.set_xlabel('Month')
    ax.set_xlim(pd.Timestamp('1999-09-01'), pd.Timestamp('2000-08-31'))
    plt.savefig(f'output/dendroclim_daily_{title}.png', dpi=200)
    plt.close(fig)
    return fig, ax


def rotate_daily_climate(df):
    """
    Поворачивает климатические данные с meteo.ru так, чтобы годы шли по столбцам
    (сделано, чтобы не переписывать get_crn_climate_correlation под новый стандарт)
    """
    temperature = dict()
    precipitation = dict()

    for year in list(set(df['Год'])):
        temp = df[df['Год']==year].reset_index(drop=True)
        if len(temp) < 366:
            temp.loc[58.5] = year, 2, 29, np.NaN, np.NaN
            temp = temp.sort_index().reset_index(drop=True)
        temperature[year] = temp['Средняя температура воздуха']
        precipitation[year] = temp['Количество осадков']

    temperature = pd.DataFrame(temperature)
    precipitation = pd.DataFrame(precipitation)
    return temperature, precipitation
