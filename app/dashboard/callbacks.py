from dash import (
    Input,
    Output,
    callback
)
from app.trs_isotopes_analyser import TRSIsotopesAnalyser
from app.config import load_config
import pandas as pd
import plotly.express as px
from zhutils.approximators.polynomial import Polynomial
from zhutils.common import Months


config = load_config('config/config.24sites.yaml')
ia = TRSIsotopesAnalyser(
    config['sites_path'],
    config['isotopes_path'],
    config['climate_path']
)

# TODO: Добавить возможность отображения на карте станций ВМО и подсветка тех станций данные по которым использовались.

@callback(
    Output('isotope-selection', 'options'),
    Output('isotope-selection', 'placeholder'), 
    Output('climate-index-selection', 'placeholder'), 
    Input('site-selection', 'value')
)
def update_isotope_selection(site_code):
    if not site_code:
        return [], 'First select site code', 'First select site code'
    
    all_isotopes = ["13C", "18O", "2H"]
    result = []
    for isotope in all_isotopes:
        i = ia.__get_isotope_by_site_code__(isotope, site_code)
        if i:
            result.append(isotope)
    return result, 'Select isotope', 'Select climate index'


@callback(
    Output('climate-index-selection', 'options'),
    Output('label-demo', 'children'),
    Input('site-selection', 'value')
)
def update_climate_index_selection(site_code):
    if not site_code:
        return [], ''
    
    site = ia.__get_sites_by_pattern__({'code': site_code})[0]
    clim_data = ia.climate_data.get(site.station_name)

    if clim_data is None:
        return [], f'There is no climate data for {site_code}'
    
    result = [column for column in clim_data.columns if column not in {'Year', 'Month'}]

    wmo = "" if pd.isna(site.station_wmo_code) else f" (WMO: {site.station_wmo_code})"

    start_year, end_year = min(clim_data['Year']), max(clim_data['Year'])

    return result, f'Climate station: {site.station_name}{wmo} ({start_year}-{end_year})'


@callback(
    Output('sites-map', 'figure'),
    [
        Input('site-selection', 'value'),
        Input('sites-map', 'figure')
    ]
)
def update_sites_map(site_code, map_fig):

    if not site_code:
        return map_fig
    
    site = ia.__get_sites_by_pattern__({'code': site_code})[0]

    map_fig['layout']['mapbox']['center']['lat'] = site.lat
    map_fig['layout']['mapbox']['center']['lon'] = site.lon

    return map_fig


@callback(
    Output('climate-corr-table', 'data'),
    [
        Input('site-selection', 'value'),
        Input('isotope-selection', 'value'),
        Input('climate-index-selection', 'value'),
        Input('year-range-slider', 'value')
    ]
)
def update_climate_corr_table(site_code, isotope, clim_index, year_limits):

    if not all([site_code, isotope, clim_index, year_limits]):
        return []

    climate_corr = ia.compare_with_climate(
        isotope,
        clim_index,
        site_codes=[site_code],
        start_year=year_limits[0],
        end_year=year_limits[1]
    )
    climate_corr = climate_corr[climate_corr['Site Code'] == site_code]
    climate_corr = climate_corr.drop(columns=['Site Code'])
    climate_corr = climate_corr.set_index('Month').T.iloc[:,8:20]
    climate_corr_res = {}
    for column in climate_corr.columns:
        r = climate_corr[column][0]
        p = climate_corr[column][1]
        climate_corr_res[column] = f'{r:.2f}\n(p={p:.4f})'
    
    return [climate_corr_res]


@callback(
    Output('year-range-slider', 'min'),
    Output('year-range-slider', 'max'),
    Output('year-range-slider', 'marks'),
    Output('year-range-slider', 'value'),
    [
        Input('site-selection', 'value'),
        Input('climate-index-selection', 'value'),
        Input('year-range-slider', 'value')
    ]
)
def update_year_range_slider(site_code, clim_index, year_limits):

    if not (site_code and clim_index):
        return 1900, 2020, {i: str(i) for i in range(1900, 2021, 10)}, [1960, 2000]
    
    site = ia.__get_sites_by_pattern__({'code': site_code})[0]
    climate_data = ia.climate_data.get(site.station_name)

    if climate_data is None:
        return 1900, 2020, {i: str(i) for i in range(1900, 2021, 10)}, [1960, 2000]
    
    climate_data = climate_data[['Year', 'Month', clim_index]].dropna()
    start_year = climate_data['Year'].min()
    end_year = climate_data['Year'].max()

    return (
            start_year,
            end_year,
            {i: str(i) for i in range(start_year, end_year+1) if i % 10 == 0},
            [max(year_limits[0], start_year), min(year_limits[1], end_year)]
        )


# TODO: починить латех в уравнении
@callback(
    Output('simple-graph', 'figure'),
    Output('scatter-graph', 'figure'),
    [
        Input('site-selection', 'value'),
        Input('isotope-selection', 'value'),
        Input('climate-index-selection', 'value'),
        Input('year-range-slider', 'value'),
        Input('climate-corr-table', 'active_cell')
    ]
)
def update_graphs(site_code, isotope, clim_index, year_limits, active_cell):

    if not site_code:
        return {}, {}
    
    if not isotope:
        return {}, {}
    
    isotope_data = ia.__get_isotope_by_site_code__(isotope, site_code)
    
    if not isotope_data:
        return {}, {}
    
    isotope_data = isotope_data.data

    site = ia.__get_sites_by_pattern__({'code': site_code})[0]

    climate_data = ia.climate_data.get(site.station_name)

    if not clim_index or climate_data is None or clim_index not in climate_data.columns:
        return {
            'data': [
                    {'x': isotope_data['Year'], 'y': isotope_data['Value'], 'name': f'{isotope} {site_code}'},
                ],
                'layout': {
                    'title': f'{isotope} {site_code} plot',
                    'xaxis': {'title' :'Year'},
                    'yaxis': {'title': isotope},
                }
        }, {}

    # TODO: РЕФАКТОРИТЬ ЭТУ ЖЕСТЬ

    month = 1
    shift = 0
    month_name = Months(1).name

    if active_cell:
        if 'prev' in active_cell['column_id']:
            month_name = active_cell['column_id'].split(' ')[0]
            shift = 1
        else:
            month_name = active_cell['column_id']
    
    month = Months[month_name].value
    
    climate_data = climate_data[
        (climate_data['Month'] == month) &
        (climate_data['Year'] >= year_limits[0]) &
        (climate_data['Year'] <= year_limits[1])
    ]
    climate_data[clim_index] = climate_data[clim_index].shift(shift)

    data = pd.merge(isotope_data, climate_data, on='Year', how='inner')
    p = Polynomial()
    p.fit(data[clim_index], data['Value'], deg=1)
    annotation_x = data[clim_index].max() - (data[clim_index].max() - data[clim_index].min())/2
    annotation_y = data['Value'].max()

    return  {
                'data': [
                    {'x': isotope_data['Year'], 'y': isotope_data['Value'], 'name': f'{isotope} {site_code}'},
                    {'x': climate_data['Year'], 'y': climate_data[clim_index], 'name': clim_index, 'yaxis': 'y2'},
                ],
                'layout': {
                    'title': f'{isotope} {site_code} and {clim_index} {month_name} {"prev " if shift else ""}plot',
                    'xaxis': {'title' :'Year'},
                    'yaxis': {'title': isotope},
                    'yaxis2': {'title': clim_index, 'overlaying':'y', 'side': 'right', 'showgrid': False, 'showline': True,}
                }
            }, {
                'data': [
                    {'x': data[clim_index], 'y': data['Value'], 'type' :'scatter', 'mode':'markers', 'marker': {'color': 'grey', 'size':9}, 'text': data['Year'], 'name': 'Scatterplot'},
                    {'x': data[clim_index], 'y': p.predict(data[clim_index]), 'line': {'color':'black','width': 2}, 'name': 'LS fit'},
                ],
                'layout': {
                    'title': f'{isotope} {site_code} and {clim_index} {month_name} {"prev " if shift else ""}trend',
                    'xaxis': {'title' : clim_index},
                    'yaxis': {'title' : isotope},
                    'showlegend': False,
                    'annotations': [{'x': annotation_x, 'y':annotation_y, 'text':p.get_equation(), 'showarrow': False, 'font': {'size': 16}}]
                }
            }


sites = pd.read_csv(config['sites_path'])
sites['size'] = 1
map = px.scatter_mapbox(
        sites,
        lat="Latitude (degrees N)", lon="Longitude (degrees E)",
        hover_name="Site name", hover_data=["Site code", "Elevation"],
        zoom=3, height=600, width=1400,
        size="size", size_max=20,
    )
map.update_layout(
    title='Sites map',
    mapbox_style='carto-positron',
    autosize=True,
    hovermode='closest'
)
