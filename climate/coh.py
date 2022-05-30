import pandas as pd
import matplotlib.pyplot as plt

from climate.dendroclim import (
    get_multiple_monthly_dendroclim,
    plot_multiple_monthly_dendroclim
)
from utils.plots import (
    combine_hex_colors,
    month_names,
    m_names,
    ind_titels,
    char_2_characteristic
)

pd.options.mode.chained_assignment = None 

#TODO: Add comments and function signatures

def get_multiple_values(d: dict, keys: list) -> list:
    """

    """
    result = []
    existing_keys = []
    for key in keys:
        value = d.get(key)
        if not value is None:
            result.append(value)
            existing_keys.append(key)
    return existing_keys, result


def get_coh_corr(climate_data:dict, df_COH: pd.DataFrame,
                 locs: list, regs: list, ind_titels: dict):
    r_values, p_values = dict(), dict()
    for ind in ind_titels:
        for loc, reg in zip(locs, regs):
            column = f'{reg}_{ind}'
            if not column in df_COH.columns:
                continue
            char_names, chars = get_multiple_values(climate_data, [f'Temp_{loc}', f'Prec_{loc}', f'VPD_{loc}', f'SD_{loc}', f'RH_{loc}'])
            char_names = [char.split('_')[0] for char in char_names]
            chars = dict(zip(char_names, chars))

            rs, ps = get_multiple_monthly_dendroclim(df_COH, chars, column)

            r_values[f'{column} {loc}'] = rs
            p_values[f'{column} {loc}' ] = ps
    return r_values, p_values


def plot_coh_corr(r_values, p_values, ind_titels: dict, char_to_color: dict,
                 fig_savepath:str='', years: str='', ylim0:float=-.7, ylim1:float=.8):
    for key in r_values:
        reg, _ = key.split('_')
        ind, loc = _.split() 
        title = f'{loc} {ind_titels[ind]} {years}'
        
        rs = r_values[key]
        ps = p_values[key]

        char_names, _ = get_multiple_values(rs, [f'Temp', f'Prec', f'VPD', f'SD', f'RH'])
        char_names = [char.split('_')[0] for char in char_names]
        colors = [char_to_color[char] for char in char_names]

        plot_multiple_monthly_dendroclim(rs, ps, colors, title, [ylim0, ylim1], fig_savepath)


#TODO: Refactor
def plot_multiple_coh_corr(r_values, p_values, char, ind, ylim0:float=-.75, ylim1:float=1.0):
    fig, ax = plt.subplots(figsize=(6,5), dpi=300)
    plt.subplots_adjust(right=0.9)

    max_i = 0
    for key in r_values:
        if ind in key:
            if char in r_values[key]:
                max_i+=1

    colors = []

    for i in range(1, max_i+1):
        color = combine_hex_colors({"ff1100": 1.0 - i*(1.0/max_i), "0012ff": i*(1.0/max_i)})
        colors.append(color)

    i = 0
    for key in r_values:
        if ind in key:
            if char in r_values[key]:
                color = colors[i]
                i+=1 
                ax.plot(r_values[key][char], label=key, color=color)
                ax.plot([j for j, p in enumerate(p_values[key][char]) if p and p<0.05],
                    [r_values[key][char][j] for j, p in enumerate(p_values[key][char]) if p and p<0.05],
                    marker='D', linestyle = 'None', color=color)

    ax.set_xticks([i for i in range(0,12)])
    ax.set_xticklabels(m_names)
    ax.set_ylim([ylim0, ylim1])
    ax.set_xlabel('Months')
    ax.set_ylabel('Pearson R')
    ax.set_title(f"{char_2_characteristic[char]} ({ind_titels[ind]})")
    ax.legend(loc=(1.04,0))
    return ax, fig


def coh_corr_to_table(r_values, p_values, climate_data):
    df_COH_corr = {
    'Month' : {'':  month_names},
    }
    for column in r_values:
        df_COH_corr[column] = dict()
        loc = column.split()[-1]
        for char in ['Temp', 'Prec', 'VPD', 'SD', 'RH']:
            if f'{char}_{loc}' in climate_data:
                df_COH_corr[column][char] = []

        rs = r_values[column]
        ps = p_values[column]
        for key in rs:
            if key in df_COH_corr[column]:
                for r,p in zip(rs[key], ps[key]):
                    if r and p:
                        text = f'{r:.2f}\n(p={p:.3f})'
                    else:
                        text = ''
                    df_COH_corr[column][key].append(text)

    df_reform = {(outerKey, innerKey): values for outerKey, innerDict in df_COH_corr.items() for innerKey, values in innerDict.items()}
    df_reform = pd.DataFrame(df_reform)

    return df_reform
