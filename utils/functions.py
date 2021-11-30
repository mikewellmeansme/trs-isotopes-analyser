import numpy as np
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
