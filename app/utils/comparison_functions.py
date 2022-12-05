import numpy as np

from pandas import DataFrame
from typing import Tuple
from zhutils.correlation import dropna_pearsonr


def compare_pearsonr(df: DataFrame, index: str) -> Tuple[float, float]:
    if len(df.dropna()) < 2:
        return np.nan, np.nan
    r, p = dropna_pearsonr(df[index], df['Value'])
    return r, p
