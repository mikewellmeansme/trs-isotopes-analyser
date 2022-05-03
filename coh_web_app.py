# -*- coding: utf-8 -*-
import pandas as pd
import dash_bootstrap_components as dbc

from dash import (
    Dash,
    Input,
    Output,
    callback,
    dash_table,
    dcc,
    html
)
from utils.functions import dropna_pearsonr, flatten, get_polynomial_fit, get_equation
from utils.dash_utils import get_coh_and_clim, get_highlight_conditions
from climate.data_preprocessing import load_data


climate_data = load_data()
dendroclim_df = pd.read_excel('output/dendroclim_COH_corr_FOR_WEB.xlsx')
df_COH = pd.read_excel("input/COH/13C_allsites.xlsx")


"""@callback(Output('soure_table', 'data'), Input('dendroclim', 'active_cell'))
def update_table(active_cell):
    result, _, _ = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)
    result = result.to_dict('records')
    return result if result else {'None':'None'}"""


@callback(Output('tbl_out', 'children'), Input('dendroclim', 'active_cell'))
def update_pearsonr(active_cell):
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)

    r, p = dropna_pearsonr(res[obs], res[clim])
    return  f'{r:.2f} (p={p:.4f})'


@callback(Output('simple-graph', 'figure'), Input('dendroclim', 'active_cell'))
def update_simple_graph(active_cell):
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)

    return  {
                'data': [
                    {'x': res['Year'], 'y': res[obs], 'name': obs},
                    {'x': res['Year'], 'y': res[clim], 'name': clim, 'yaxis': 'y2'},
                ],
                'layout': {
                    'title': f'{obs} and {clim} plot',
                    'xaxis': {'title' :'Year'},
                    'yaxis': {'title': obs},
                    'yaxis2': {'title': clim, 'overlaying':'y', 'side': 'right', 'showgrid': False, 'showline': True,}
                }
            }


@callback(Output('scatter-graph', 'figure'), Input('dendroclim', 'active_cell'))
def update_scatter_graph(active_cell):
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)
    _, p = get_polynomial_fit(res[clim], res[obs])

    return  {
                'data': [
                    {'x': res[clim], 'y': res[obs], 'type' :'scatter', 'mode':'markers', 'marker': {'color': 'grey'}, 'text': res['Year'], 'name': 'Scatterplot'},
                    {'x': res[clim], 'y': p(res[clim]), 'line': {'color':'black','width': 1,'dash':'dash'}, 'name': 'LS fit'},
                ],
                'layout': {
                    'title': f'{obs} {clim} trend',
                    'xaxis': {'title' : clim},
                    'yaxis': {'title' : obs},
                    'showlegend': False
                }
            }


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


app.layout = html.Div(children=[
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
        dbc.Alert(id='tbl_out'),
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
        #dash_table.DataTable(id='soure_table'),
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True)
