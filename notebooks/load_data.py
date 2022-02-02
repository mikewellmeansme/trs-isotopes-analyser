import pandas as pd
import numpy as np

mean_rh_C = pd.read_csv('../input/climate/real/relative humidity/RH_Chokurdakh.csv')
mean_sol_C = pd.read_csv('../input/climate/real/sunshine duration/SD_Chokurdakh.csv')

mean_temp_C = pd.read_csv('../input/climate/real/temperature/Temp_Chokurdakh.csv').drop(['Индекс ВМО'], axis=1)
mean_prec_C = pd.read_csv('../input/climate/real/precipitation/Prec_Chokurdakh.csv').drop(['Индекс ВМО'], axis=1)
mean_vpd_C = pd.read_csv('../input/climate/real/vpd/VPD_Chokurdakh.csv')

climate_C = pd.read_csv('../input/climate/real/daily/Daily_Chokurdakh.csv').drop(['Индекс ВМО',
'Общий признак качества температур', 'Минимальная температура воздуха', 'Максимальная температура воздуха'], axis=1)

grid_temp_C = pd.read_csv('../input/climate/grid/temperature/Grid_Temp_Chokurdakh.csv')
grid_prec_C = pd.read_csv('../input/climate/grid/precipitation/Grid_Prec_Chokurdakh.csv')
grid_vp_C = pd.read_csv('../input/climate/grid/vpd/Grid_VP_Chokurdakh.csv')

mean_rh_H = pd.read_csv('../input/climate/real/relative humidity/RH_Khatanga.csv')
mean_sol_H = pd.read_csv('../input/climate/real/sunshine duration/SD_Khatanga.csv')

mean_temp_H = pd.read_csv('../input/climate/real/temperature/Temp_Khatanga.csv').drop(['Индекс ВМО'], axis=1)
mean_prec_H = pd.read_csv('../input/climate/real/precipitation/Prec_Khatanga.csv').drop(['Индекс ВМО'], axis=1)
mean_vpd_H = pd.read_csv('../input/climate/real/vpd/VPD_Khatanga.csv')

climate_H = pd.read_csv('../input/climate/real/daily/Daily_Khatanga.csv').drop(['Индекс ВМО',
'Общий признак качества температур', 'Минимальная температура воздуха', 'Максимальная температура воздуха'], axis=1)

grid_temp_H = pd.read_csv('../input/climate/grid/temperature/Grid_Temp_Khatanga.csv')
grid_prec_H = pd.read_csv('../input/climate/grid/precipitation/Grid_Prec_Khatanga.csv')
grid_vp_H = pd.read_csv('../input/climate/grid/vpd/Grid_VP_Khatanga.csv')

mean_rh_I = pd.read_csv('../input/climate/real/relative humidity/RH_Inuvik.csv')

mean_temp_I = pd.read_csv('../input/climate/real/temperature/Temp_Inuvik.csv')
mean_prec_I = pd.read_csv('../input/climate/real/precipitation/Prec_Inuvik.csv')
mean_vpd_I = pd.read_csv('../input/climate/real/vpd/VPD_Inuvik.csv')

climate_I = pd.read_csv('../input/climate/real/daily/Daily_Inuvik.csv')

grid_temp_I = pd.read_csv('../input/climate/grid/temperature/Grid_Temp_Inuvik.csv')
grid_prec_I = pd.read_csv('../input/climate/grid/precipitation/Grid_Prec_Inuvik.csv')
grid_vp_I = pd.read_csv('../input/climate/grid/vpd/Grid_VP_Inuvik.csv')

d18O_yearly = pd.read_excel('../input/d18O.xlsx')

mean_temp_D = pd.read_csv('../input/climate/real/temperature/Temp_Deputatsky.csv')
mean_prec_D = pd.read_csv('../input/climate/real/precipitation/Prec_Deputatsky.csv')
mean_vpd_D = pd.read_csv('../input/climate/real/vpd/VPD_Deputatsky.csv')

climate_D = pd.read_csv('../input/climate/real/daily/Daily_Deputatsky.csv')

grid_temp_D = pd.read_csv('../input/climate/grid/temperature/Grid_Temp_Deputatsky.csv')
grid_prec_D = pd.read_csv('../input/climate/grid/precipitation/Grid_Prec_Deputatsky.csv')
grid_vp_D = pd.read_csv('../input/climate/grid/vpd/Grid_VP_Deputatsky.csv')
