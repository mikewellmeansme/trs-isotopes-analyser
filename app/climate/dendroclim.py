import sys
import numpy as np
import pandas as pd
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import traceback
from utils.functions import dropna_pearsonr

sys.path.append('..')
# Функции построения дендроклиматического отклика

m_names = ['S', 'O', 'N', 'D', 'J', 'F', 'M', 'A', 'M ', 'J', 'J', 'A']
months = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']
default_ylim = [-0.7, 0.8]



def get_month_correlation(df_crn:pd.DataFrame, df_clim:pd.DataFrame, month: str, observ: str) -> tuple[float, float]:
    """
    Возвращает корреляцию (и её p-value) между хронологией и климатической характеристикой
    за месяц
    """

    clim_result = df_clim[['Year', month]]

    if month in ['September', 'October', 'November', 'December']:
        clim_result['Year'] = clim_result['Year'] + 1
    
    coh_result = df_crn[['Year', observ]]

    res = pd.merge(clim_result, coh_result, how='outer', on = 'Year').sort_values(by='Year').reset_index(drop=True)
    try:
        r, p = dropna_pearsonr(res[observ], res[month])
    except:
        r, p = None, None

    return r, p

Month2Value = dict[str, float]
Char2Months = dict[str, Month2Value]


def get_monthly_dendroclim(df_crn:pd.DataFrame, df_clim:pd.DataFrame, observ: str) -> tuple[Month2Value, Month2Value]:
    """
    Возвращает корреляцию между хронологией и климатической характеристикой
    за все месяцы
    """

    r_coeffs, p_values = dict(), dict()

    for month in months:
        r, p = get_month_correlation(df_crn, df_clim, month, observ)
        r_coeffs[month] = r
        p_values[month] = p
    
    return r_coeffs, p_values


def get_multiple_monthly_dendroclim(df_crn:pd.DataFrame, clim_dfs:dict[str, pd.DataFrame], observ: str) -> tuple[Char2Months, Char2Months]:
    """
    Возвращает корреляцию между хронологией и несколькими климатическими характеристиками
    за все месяцы
    """
    res_r, res_p = dict(), dict()

    for clim_char in clim_dfs:
        df_clim = clim_dfs[clim_char]
        
        r_coeffs, p_values = get_monthly_dendroclim(df_crn, df_clim, observ)
        r_coeffs, p_values = list(r_coeffs.values()), list(p_values.values())
        res_r[clim_char] = r_coeffs
        res_p[clim_char] = p_values

    return res_r, res_p


def plot_multiple_monthly_dendroclim(rs: Char2Months, ps: Char2Months,
                                     colors:list, title:str='',
                                     ylim=default_ylim, savepath=''):
    fig, ax = plt.subplots(figsize=(6,5))
    plt.subplots_adjust(right=0.9)

    for i, clim_char in enumerate(rs):
        
        ax.plot(rs[clim_char], label=clim_char, color=colors[i])
        ax.plot([j for j, p in enumerate(ps[clim_char]) if p and p<0.05],
                [rs[clim_char][j] for j, p in enumerate(ps[clim_char]) if p and p<0.05],
                marker='D', linestyle = 'None', color=colors[i])
    
    ax.legend(frameon=False) 
    ax.set_xticks([i for i in range(0,12)])
    ax.set_xticklabels(m_names)
    ax.set_ylim(ylim)
    ax.set_xlabel('Months')
    ax.set_ylabel('Pearson R')
    ax.set_title(title)

    if savepath:
        plt.savefig(f'{savepath}/dendroclim_monthly_{title}.png', dpi=200)
    plt.close(fig)

    return fig, ax



def get_crn_climate_correlation(temperature:pd.DataFrame, precipitation:pd.DataFrame,
                                chronology:pd.DataFrame, crn_name='std', window=21, grab=150):
    """
    temperature, precipitation: DataFrame, где по колонкам идут годы
    chronology: DataFrame с колонкой Year и колонками,
    crn_name: Имя колонки требуемой хронологии 
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
    plt.savefig(f'../output/dendroclim_daily_{title}.png', dpi=200)
    plt.close(fig)
    return fig, ax
