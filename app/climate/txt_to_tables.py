import pandas as pd

# Функции для конвертации данных с http://meteo.ru/data  (http://aisori-m.meteo.ru/waisori/)
# из .txt формата в .csv и .xlsx
# Топорные ибо требуют ручного ввода имён колонок
# В будущем хорошо бы доработать, но они вроде как одноразовые поэтому пока сойдёт

daily_columns_names_ru = [
    "Индекс ВМО", "Год", "Месяц", "День",
    "Общий признак качества температур",
    "Минимальная температура воздуха",
    "Средняя температура воздуха",
    "Максимальная температура воздуха",
    "Количество осадков"
]

montly_columns_names_ru = [
    "Индекс ВМО", "Год",
    "Январь", "Февраль", "Март",
    "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь",
    "Октябрь", "Ноябрь", "Декабрь"
]

montly_columns_names_en = [
    "WMO Index", "Year" ,
    "January", "February", "March",
    "April", "May", "June",
    "July", "August", "September",
    "October", "November", "December"
]

def delete_all_spaces_from_txt(file_path: str) -> None:
    with open(file_path, 'r+') as f:
        txt = f.read().replace(' ', '')
        f.seek(0)
        f.write(txt)
        f.truncate()


def txt_to_df(station: str, char: str,
              colums_names: list,
              input_path='input', output_path='output',
              save_csv=True, save_ecel=False) -> pd.DataFrame:
    """
    input_path: Relative path to txt station file INCLUDING name of a file
    output_path: Relative path to folder to save resulst EXCLUDING name of a file
    """
    delete_all_spaces_from_txt(input_path)
    df = pd.read_csv(input_path, sep=';', header=None)

    df = df.rename(columns={i:colums_names[i] for i in range(len(colums_names))})

    if save_csv:
        df.to_csv(f'{output_path}/{char}_{station}.csv', index=False)
    if save_ecel:
        df.to_excel(f'{output_path}/{char}_{station}.xlsx', index=False)
    return df



# функция для преобразования .dat файлов с 
# https://climexp.knmi.nl/selectfield_obs2.cgi?id=someone@somewhere
# в DataFrame
def dat_to_df(file_path: str, monthly=True, save_csv=True, save_ecel=False) -> pd.DataFrame:
    df = pd.DataFrame(columns=montly_columns_names_en[1:] if monthly else ['Year', 'Month', 'Day', 'Measurement'])
    with open(file_path, 'r') as f:
        text = f.readlines()
        for line in text:
            if line[0] == '#':
                pass
            else:
                temp = [float(el) if "E" in el else el for el in line.split()]
                df.loc[len(df)] = temp
    if save_csv:
        df.to_csv(file_path.split('.')[0]+'.csv', index=False)
    if save_ecel:
        df.to_excel(file_path.split('.')[0]+'.csv', index=False)
    return df
