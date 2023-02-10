# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash import (
    Dash,
    dash_table,
    dcc,
    html
)
from app.utils.functions import  flatten
from app.dashboard.dash_utils import get_highlight_conditions
from app.dashboard.callbacks import *


dashboard = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


dashboard.layout = html.Div(children=[
    dbc.Container([
        html.H1(children='Tree-ring stable isotope exploratory dashboard'),
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
                        options = [],
                        searchable=False
                    ),
                    width="4"
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id="climate-index-selection",
                        placeholder='First select site code',
                        options=[],
                        searchable=False
                    ),
                    width="4"
                )
            ],
            justify="center",
        ),

        dbc.Label('Click a cell in the table:', id="label-demo" ),
        dcc.Graph(id='sites-map', figure=map),
        dash_table.DataTable(
            id='climate-corr-table',
            style_data_conditional=flatten(get_highlight_conditions()) + flatten(get_highlight_conditions(negative=True)),
            style_cell={
                'whiteSpace': 'pre-line',
                'textAlign': 'center'
            }
        ),
        # TODO: границы по-умолчанию из конфига
        dcc.RangeSlider(
            1900, 2020,
            id='year-range-slider',
            allowCross=False,
            marks = {i: str(i) for i in range(1900, 2021, 10)},
            value=[1960, 2000],
            tooltip={
                    "placement": "bottom",
                    "always_visible": True
                }
        ),
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
