import plotly.express as px
import pandas as pd
from dash import (
    Input,
    Output,
    callback
)
from climate.data_preprocessing import load_data
from utils.functions import dropna_pearsonr, get_polynomial_fit, get_equation
from coh_app.dash_utils import get_coh_and_clim, get_highlight_conditions


climate_data = load_data()
dendroclim_df = pd.read_excel('output/dendroclim_COH_corr_FOR_WEB.xlsx')
df_COH = pd.read_excel('input/COH/13C_allsites.xlsx')
sites = pd.read_csv('input/Sites.csv')


"""@callback(Output('soure_table', 'data'), Input('dendroclim', 'active_cell'))
def update_table(active_cell):
    result, _, _ = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)
    result = result.to_dict('records')
    return result if result else {'None':'None'}"""


@callback(Output('tbl_out', 'children'), Input('dendroclim', 'active_cell'))
def update_pearsonr(active_cell):

    if not active_cell:
        return ''
    
    if active_cell['column_id'] in ['Observation', 'Char']:
        return ''
    
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)

    r, p = dropna_pearsonr(res[obs], res[clim])
    return  f'{r:.2f} (p={p:.4f})'


@callback(Output('simple-graph', 'figure'), Input('dendroclim', 'active_cell'))
def update_simple_graph(active_cell):

    if not active_cell:
        return dict()
    
    if active_cell['column_id'] in ['Observation', 'Char']:
        return dict()
    
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

    if not active_cell:
        return dict()
    
    if active_cell['column_id'] in ['Observation', 'Char']:
        return dict()
    
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)
    _, p = get_polynomial_fit(res[clim], res[obs])
    eq = get_equation(res[clim], res[obs])

    annotation_x = res[clim].max() - (res[clim].max() - res[clim].min())/2
    annotation_y = res[obs].max()

    return  {
                'data': [
                    {'x': res[clim], 'y': res[obs], 'type' :'scatter', 'mode':'markers', 'marker': {'color': 'grey', 'size':9}, 'text': res['Year'], 'name': 'Scatterplot'},
                    {'x': res[clim], 'y': p(res[clim]), 'line': {'color':'black','width': 2}, 'name': 'LS fit'},
                ],
                'layout': {
                    'title': f'{obs} {clim} trend',
                    'xaxis': {'title' : clim},
                    'yaxis': {'title' : obs},
                    'showlegend': False,
                    'annotations': [{'x': annotation_x, 'y':annotation_y, 'text':eq, 'showarrow': False, 'font': {'size': 16}}]
                }
            }


@callback(Output('sites-map', 'figure'), Input('dendroclim', 'active_cell'))
def update_sites_map(active_cell):

    if not active_cell:
        return dict()
    
    active_cell['row']
    
    fig = px.scatter_mapbox(sites, lat="Latitude (degrees N)", lon="Longitude (degrees E)",
                            hover_name="Site name", hover_data=["Site code", "Elevation"],
                            zoom=3, height=800, width=1000)
    fig.update_layout(title='Sites map', mapbox_style='open-street-map')

    return fig