# Функцим для построения графиков трендов для средних значений по месяцам
# Колонки DataFrame'а должны быть названы: Год, Январь, Февраль, ... Декабрь

import matplotlib as mp
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import pearsonr
from matplotlib.offsetbox import AnchoredText


months_names = ['January', 'February', 'March',
                'April', 'May', 'June', 'July',
                'August', 'September', 'October',
                'November', 'December']

season_names = {
    0: '(a) annual',
    1: '(b) spring',
    2: '(c) summer',
    3: '(d) autumn',
    4: '(e) winter'
}

cols = {
    0: range(1, 13),
    1: [3, 4, 5],
    2: [6, 7, 8],
    3: [9, 10, 11],
    4: [-1, 1, 2]
}

colors = ['red', 'blue']

trend_colors = {
    'red': 'maroon',
    'blue': 'navy',
    'black': 'black'
}

locs = {
    'black':'upper center',
    'red':'lower left',
    'blue':'lower right'
}

prefixes = {
    'black':'1&2: ',
    'red':'1: ',
    'blue':'2: '
}

def plot_trend(x:list, y:list,
               ax:'mp.axes._subplots.AxesSubplot', color:str, plot=True) -> tuple:
    """
    Строит линию тренда для данных x y на осях ax если plot==True
    Возвращает:
        Значим ли коэф-т корреляции?
        Текст с уравнением линии тренда
        Текст с коэф-том корреляции и p-value
    """
    nas = np.logical_or(np.isnan(x), np.isnan(y))
    x, y = x[~nas], y[~nas]
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
        
    r_pearson, p_value = pearsonr(y, p(x))

    if p_value < 0.01:
        p_v_str = '<0.01'
    elif p_value <0.05:
        p_v_str = '<0.05'
    else:
        p_v_str = '>0.05'
    
    if plot:
        ax.plot(x, p(x), "--", color=trend_colors[color])
    sign = '' if z[1]<0 else '+'
    text_eq = f"$y={z[0]:0.3f}\;x{sign}{z[1]:0.2f}$"
    text_r = f"$r={r_pearson:0.2f}, p{p_v_str}$"
    
    return p_value<0.05, text_eq, text_r


def plot_measurement(data: pd.DataFrame, ax:'mp.axes._subplots.AxesSubplot',
                      start_year: int, end_year: int, ylabel: str,
                      season_number=0, color:str='red',
                      with_trends:bool=True, with_plot:bool=True) -> str:
    """
    season_number: 0 - весь год, 1 - весна, 2 - лето, 3 - осень, 4 - зима
                   ИЛИ кастомный, список содержащий номера месяцев от 1 до 12
    если with_trends, то строит линию тренда
    если with_plot, то строит сами данные
    """
    data = data[(data['Год']>=start_year) & (data['Год']<=end_year)]
    years = data['Год']
    means = data.iloc[:,
                      cols[season_number] if type(season_number)==int else season_number
                     ].mean(axis=1, skipna=True)
    
    if with_plot:
        ax.plot(years, means, color=color, marker='o')
    
    is_significant, text_eq, text_r = plot_trend(years, means, ax, color, with_trends)
    
    if is_significant:
        text = prefixes[color] + text_r
    else:
        text = ''

    if with_trends and text:
        anchored_text = AnchoredText(text, loc=locs[color], frameon=True, prop=dict(fontsize=10))
        ax.add_artist(anchored_text)
        #ax.text(text, loc=0, bbox=dict(facecolor='white', edgecolor='white', boxstyle='round'))
        
    
    if type(season_number)==int:
        title = season_names[season_number]
    else:
        title = ' '.join([months_names[i-1] for i in season_number])
    
    ax.set_title(title, loc='left')
    ax.set_ylabel(ylabel)
    ax.set_xlabel('Year')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    return text


def plot_measurements(data: pd.DataFrame, station:str, ylabel:str,
                      start_year: int, end_year: int, with_trends:bool=True, colors:list=colors) -> None:
    """
    Строит пять графиков трендов (за весь год и для каждого из сезонов) 
    на одном изображении
    data: DataFrame с средними данными по месяцам. Первый столбец должен называться "Год",
          остальные 12 -- по месяцам (назавния не важны, главное чтоб порядок был как в году)
    station: название станции, откуда взяты измерения
    ylabel: Название величины и её единицы измерения
    start_year, end_year: период, на котором смотрится тренд (ВКЛЮЧИТЕЛЬНО)
    """
    fig = plt.figure(constrained_layout=True, figsize=(8,8), dpi=200)
    #plt.subplots_adjust(right=0.95, hspace=0.05, wspace=0.05, bottom=0.01)
    gs = fig.add_gridspec(3, 4)
    axes = [
        fig.add_subplot(gs[0, 1:3]),
        fig.add_subplot(gs[1, 0:2]),
        fig.add_subplot(gs[1, 2:4]),
        fig.add_subplot(gs[2, 0:2]),
        fig.add_subplot(gs[2, 2:4])
    ]
    for i in range(5):
        if type(start_year)==list and type(end_year)==list:
            for color, s_y, e_y in zip(colors, start_year, end_year):
                plot_measurement(data, axes[i], s_y, e_y, ylabel, i, color)
            plot_measurement(data, axes[i], min(start_year), max(end_year), ylabel, i, 'black', True, False)
        else:
            plot_measurement(data, axes[i], start_year, end_year, ylabel, i, 'red', with_trends)
    label = ylabel.split()
    label = ' '.join(label[:len(label)-1])
    plt.savefig(f'output/{station}-{label}.png', dpi=200)
    plt.close(fig)
