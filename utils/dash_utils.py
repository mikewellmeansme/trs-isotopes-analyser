import pandas as pd

months = ['September', 'October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August']

def get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH):
    row = dendroclim_df.loc[[active_cell['row']]]
    char = row['Char'].item()
    observ, station = row['Observation'].item().split()
    climate_key = f'{char}_{station}'
    month = active_cell['column_id']
    clim_result = climate_data[climate_key][['Year', month]].rename(columns={month: f'{climate_key} {month}'})

    if month in ['September', 'October', 'November', 'December']:
        clim_result['Year'] = clim_result['Year'] + 1
    
    coh_result = df_COH[['Year', observ]]

    result = pd.merge(clim_result, coh_result, how='outer', on = 'Year')

    return result, observ, f'{climate_key} {month}'



def get_highlight_conditions(negative=False):
    return [
                [
                    {
                        'if': {
                            'column_id': f'{month}',
                            'filter_query': f'{{{month}}} contains "p=0.0{i}" && {{{month}}} contains "-"' if negative else f'{{{month}}} contains "p=0.0{i}"'
                        },
                        'backgroundColor': 'red' if negative else 'green',
                        'color': 'white'
                    } 
                for i in range(5)] 
            for month in months]
