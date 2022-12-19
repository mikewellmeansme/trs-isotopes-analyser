import plotly.express as px
import pandas as pd
from dash import (
    Input,
    Output,
    callback
)

from app.utils.functions import dropna_pearsonr, get_polynomial_fit, get_equation
from app.dashboard.dash_utils import get_coh_and_clim, get_highlight_conditions



@callback(Output('tbl_out', 'children'), Input('dendroclim', 'active_cell'))
def update_pearsonr(active_cell):

    if not active_cell:
        return ''
    
    if active_cell['column_id'] in ['Observation', 'Char']:
        return ''
    
    res, obs, clim = get_coh_and_clim(active_cell, dendroclim_df, climate_data, df_COH)

    r, p = dropna_pearsonr(res[obs], res[clim])
    return  f'{r:.2f} (p={p:.4f})'



