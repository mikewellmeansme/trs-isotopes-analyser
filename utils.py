import numpy as np
from scipy.stats import pearsonr

def dropna_pearsonr(x, y):
    nas = np.logical_or(np.isnan(x), np.isnan(y))
    x, y = x[~nas], y[~nas]
    r, p = pearsonr(x, y)
    return r, p
