import sys
import numpy as np
import pandas as pd
import matplotlib.dates as dates
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
import traceback
from app.utils.functions import dropna_pearsonr

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
