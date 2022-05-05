# -*- coding: utf-8 -*-

import dash_bootstrap_components as dbc

from dash import (
    Dash,
    dash_table,
    dcc,
    html
)
from utils.functions import  flatten
from coh_app.dash_utils import get_highlight_conditions
from coh_app.callbacks import *


coh_app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


coh_app.layout = html.Div(children=[
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