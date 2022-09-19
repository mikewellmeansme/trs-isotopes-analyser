# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash import (
    Dash,
    dash_table,
    dcc,
    html
)
from utils.functions import  flatten
from app.dashboard.dash_utils import get_highlight_conditions
from app.dashboard.callbacks import *


dashboard = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# TODO: Центрирование карты на выбранной станции
# TODO: График коэффициентов корреляции по месяцам
# TODO: Добавить возможность отображения на карте станций ВМО и подсветка тех станций данные по которым использовались.

dashboard.layout = html.Div(children=[
    dbc.Container([
        html.H1(children='COH climate correlation'),
        dbc.Label('Click a cell in the table:'),
        dash_table.DataTable(
            dendroclim_df.to_dict('records'),
            id='dendroclim',
            style_data_conditional=flatten(get_highlight_conditions()) + flatten(get_highlight_conditions(negative=True)),
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
        ),
        dcc.Graph(id='sites-map')
        #dash_table.DataTable(id='soure_table'),
    ])
])