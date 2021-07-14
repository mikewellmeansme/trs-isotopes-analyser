# Функция для преобразования .raw файлов с данными по ширене годичного кольца в
# Нормальный табличный вид (.csv, .xlsx)
# file_path - Путь к .raw файлу
# tree_name_len - число символов в первой колонке
# (не знаю, во всех ли файлах оно восьми, поэтому его можно настраивать)

import pandas as pd
import numpy as np


def raw_to_df(file_path: str, tree_name_len=8) -> pd.DataFrame:
    tree = []
    year = []
    trw = []
    with open(file_path, 'r') as f:
        content = f.readlines()
        for line in content:
            if not len(line.strip()):
                continue
            start_year, *trws = line[tree_name_len:].split()
            start_year = int(start_year)
            tree += [line[0:tree_name_len].strip()]*len(trws)
            year += [start_year + i for i in range(len(trws))]
            trw += [int(i) for i in trws]
    return pd.DataFrame({'Tree':tree, 'Year':year, 'TRW':trw}).replace(-9999, np.nan)

def raw_to_excel(file_path: str, tree_name_len=8) -> None:
    df = raw_to_df(file_path, tree_name_len)
    df.to_excel(f"{file_path.split('.')[0]}.xlsx", index=False)

def raw_to_csv(file_path: str, tree_name_len=8) -> None:
    df = raw_to_df(file_path, tree_name_len)
    df.to_csv(f"{file_path.split('.')[0]}.csv", index=False)
