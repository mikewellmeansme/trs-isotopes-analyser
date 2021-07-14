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

def plot_trend(data: pd.DataFrame, ax:'mp.axes._subplots.AxesSubplot',
               start_year: int, end_year: int, ylabel: str,
               season_number=0, with_trends:bool=True) -> None:
    """
    season_number: 0 - весь год, 1 - весна, 2 - лето, 3 - осень, 4 - зима
                   ИЛИ кастомный, список содержащий номера месяцев от 1 до 12
    """
    data = data[(data['Год']>=start_year) & (data['Год']<=end_year)]
    years = data['Год']
    means = data.iloc[:,
                      cols[season_number] if type(season_number)==int else season_number
                     ].mean(axis=1, skipna=True)
    
    if with_trends:
        nas = np.logical_or(np.isnan(years), np.isnan(means))
        x, y = years[~nas], means[~nas]
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        
        r_pearson, p_value = pearsonr(y, p(x))

        if p_value < 0.01:
            p_v_str = '<0.01'
        elif p_value <0.05:
            p_v_str = '<0.05'
        else:
            p_v_str = '>0.05'
        
        ax.plot(x,p(x),"r--")
        text = f"$y={z[0]:0.3f}\;x{z[1]:0.2f}$\n$r={r_pearson:0.2f}, p{p_v_str}$"
        #ax.text(0.2, 0.80, text, transform=ax.transAxes)
        anchored_text = AnchoredText(text, loc='upper center', frameon=False)
        ax.add_artist(anchored_text)
    
    ax.plot(years, means, color='red', marker='o')
    
    if type(season_number)==int:
        title = season_names[season_number]
    else:
        title = ' '.join([months_names[i-1] for i in season_number])
    
    ax.set_title(title, loc='left')
    ax.set_ylabel(ylabel)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)


def plot_trends(data: pd.DataFrame, station:str, ylabel:str,
                start_year: int, end_year: int, with_trends:bool=True) -> None:
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
        plot_trend(data, axes[i], start_year, end_year, ylabel, i, with_trends)
    label = ylabel.split()
    label = ' '.join(label[:len(label)-1])
    plt.savefig(f'output/{station}-{label}.png', dpi=200)
    plt.close(fig)
