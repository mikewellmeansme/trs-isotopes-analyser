import pandas as pd
from climate.dendroclim import (
    plot_mothly_dendroclim,
    get_multiple_monthly_dendroclim,
    plot_multiple_monthly_dendroclim
)

pd.options.mode.chained_assignment = None 

month_names = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']

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


def get_coh_corr_table(climate_data:dict, df_COH: pd.DataFrame,
                       locs: list, regs: list, ind_titels: dict, char_to_color: dict,
                       fig_savepath:str='', years: str='', ylim0:float=-.7, ylim1:float=.8) -> pd.DataFrame:
    """
    Функция построения таблицы помесячной корреляции между данными по C, O, H и климатическими данными

    climate_data: dict в котором ключи имеют вид Показатель_Станция, а значения -- DataFrame с климатическими данными
    df_COH: DataFrame с колонками Year и C, O, H по регионам в формате Регион_Показатель
    locs: Список названий метеостанкий (Station name in Sites.csv)
    regs: Список кодовых названий участков (Site code in Sites.csv)
    ind_titels: dict с показателями COH в ключах и LaTEX формат их отображения на графиках в значениях.
    Пример:
        ind_titels = {
            '2H': '$δH$',
            '13C': '$δ^{13}C$',
            '18O': '$δ^{18}O$'
        }
    char_to_color: dict с климатическими характеристиками в ключах и цветами для их отображения на графиках в значениях
    Пример:
        char_to_clolr = {
            'Temp': 'red',
            'Prec': 'blue',
            'VPD': 'green',
            'SD': 'orange',
            'RH': 'lightblue'
        }
    fig_savepath: Путь, по которому будут сохранены графики (если '', То не будут сохранены)
    years: Годы, за которые строится измерение
    ylim0: Нижняя граница графика по оси y
    ylim1: Верхняя граница графика по оси y
    """

    r_values, p_values = dict(), dict()
    for ind in ind_titels:
        for loc, reg in zip(locs, regs):
            column = f'{reg}_{ind}'
            if not column in df_COH.columns:
                continue
            title = f'{loc} {ind_titels[ind]} {years}'
            keys, chars = get_multiple_values(climate_data, [f'Temp_{loc}', f'Prec_{loc}', f'VPD_{loc}', f'SD_{loc}', f'RH_{loc}'])
            keys = [key.split('_')[0] for key in keys]
            colors = [char_to_color[key] for key in keys]

            fig, ax, rs, ps = plot_mothly_dendroclim(
                df_crn=df_COH[['Year', column]],
                dfs_char=chars,
                ylabels=keys,
                colors=colors,
                title=title,
                ylim=[ylim0, ylim1],
                savepath=fig_savepath
            )
            r_values[f'{column} {loc}'] = rs
            p_values[f'{column} {loc}' ] = ps

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
                    text = f'{r:.2f}\n(p={p:.3f})'
                    df_COH_corr[column][key].append(text)

    df_reform = {(outerKey, innerKey): values for outerKey, innerDict in df_COH_corr.items() for innerKey, values in innerDict.items()}
    df_reform = pd.DataFrame(df_reform)
    return df_reform


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
