import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

def dropna(x,y):
    x, y = np.array(x), np.array(y)
    nas = np.logical_or(np.isnan(x), np.isnan(y))
    x, y = x[~nas], y[~nas]
    return x, y

def dropna_pearsonr(x, y):
    x, y = dropna(x,y)
    r, p = pearsonr(x, y)
    return r, p

def dropna_spearmanr(x, y):
    x, y = dropna(x,y)
    r, p = spearmanr(x, y)
    return r, p

def get_df_corr(df, method='pearson'):
    """
    Функция вычисления корреляций и p-value для DataFrame'а df.
    Поддерживает method pearson и spearman
    """
    dfcols = pd.DataFrame(columns=df.columns)
    result = dfcols.transpose().join(dfcols, how='outer')

    if method == 'pearson':
        get_corr = dropna_spearmanr
    elif method == 'spearman':
        get_corr = dropna_spearmanr
    else:
        raise Exception('Wrong correlation method!')
    
    for c1 in df.columns:
        for c2 in df.columns:
            r, p = get_corr(df[c1], df[c2])
            result[c1][c2] = f'{r:.2f}\n(p={p:.3f})'
    
    return result
