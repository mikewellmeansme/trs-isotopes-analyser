# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash import (
    Dash,
    dash_table,
    dcc,
    html
)
#from utils.functions import  flatten
#from app.dashboard.dash_utils import get_highlight_conditions
#from app.dashboard.callbacks import *
from dash import (
    Input,
    Output,
    callback
)
from app.trs_isotopes_analyser import TRSIsotopesAnalyser
from app.config import load_config
import pandas as pd
import plotly.express as px


dashboard = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

config = load_config('config/config.24sites.yaml')
ia = TRSIsotopesAnalyser(
    config['sites_path'],
    config['isotopes_path'],
    config['climate_path']
)

# TODO: График коэффициентов корреляции по месяцам
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

    return result, f'Climate station: {site.station_name}{wmo}'



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

map = px.scatter_mapbox(pd.read_csv(config['sites_path']),
        lat="Latitude (degrees N)", lon="Longitude (degrees E)",
        hover_name="Site name", hover_data=["Site code", "Elevation"],
        zoom=3, height=600, width=1400
    )
map.update_layout(
    title='Sites map',
    mapbox_style='open-street-map',
    autosize=True,
    hovermode='closest'
)


dashboard.layout = html.Div(children=[
    dbc.Container([
        html.H1(children='Tree-ring stable isotope data'),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Dropdown(
                        id="site-selection",
                        placeholder='Select site code',
                        options = [ site.code for site in ia.sites ]
                    ),
                    width="4"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="isotope-selection",
                        placeholder='First select site code',
                        options = []
                    ),
                    width="4"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="climate-index-selection",
                        placeholder='First select site code',
                        options=[]
                    ),
                    width="4"
                )
            ],
            justify="center",
        ),

        dbc.Label('Click a cell in the table:', id="label-demo" ),
        dcc.Graph(id='sites-map', figure=map),
        dash_table.DataTable(
            #dendroclim_df.to_dict('records'),
            id='dendroclim',
            #style_data_conditional=flatten(get_highlight_conditions()) + flatten(get_highlight_conditions(negative=True)),
            style_cell={
                'whiteSpace': 'pre-line',
                'textAlign': 'center'
            }
        ),
        dbc.Alert(id='tbl_out', children=''),
        dbc.Row(
                [
                    dbc.Col(dcc.Graph(
                        id='scatter-graph',
                        figure={
                            'data': [],
                            'layout': {
                                'title': 'Scatter plot'
                            }
                        }
                    ), width=6),
                    dbc.Col(dcc.Graph(
                        id='simple-graph',
                        figure={
                            'data': [],
                            'layout': {
                                'title': 'Plot'
                            }
                        }
                    ), width=6)
                ]
        )
    ])
])
