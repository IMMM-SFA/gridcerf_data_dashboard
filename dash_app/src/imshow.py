#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard
import os

# visualization and data manipulation
import numpy as np
import plotly.express as px
from dash import html, dcc

# sourced scripts
from src.reader import open_as_raster
from definitions import plotly_config

def plot_imshow_map(COMPILED_DIR, fpaths):

    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, df_coors_long, boundingbox, boundingbox_proj, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=False, is_convert_to_png=False)

    # TODO
    # 1) get the bounding box of the data
    # 2) set that to basemap
    # 3) extract the basemap(s)
    # 3) place that first into px.imshow() and then add array trace with fig.add_trace()
    # 4) change X and Y hovers into lon and lat 
    # 5) hover also tells you the geographical location  
    # 6) and then a mini-view can show a leaflet zoom in to that area
    
    # US vector and raster tiles (and more) here: https://data.maptiler.com/downloads/north-america/us/ 

    R_mask = np.where(np.isnan(array), 176, array) 
    G_mask = np.where(np.isnan(array), 233, array)
    B_mask = np.where(np.isnan(array), 235, array)

    R_mask = np.where(array==0, 0, R_mask) 
    G_mask = np.where(array==0, 0, G_mask)
    B_mask = np.where(array==0, 0, B_mask)  

    rgb_stack = np.stack((R_mask, G_mask, B_mask), axis=-1)
    fig = px.imshow(rgb_stack)

    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    fig.update(layout_coloraxis_showscale=False)
    # fig.update_traces(showlegend=False)
    # fig.update_traces(marker_showscale=False)
    # fig.write_html(os.path.join(OUTDIR, "map-layer.html"))
    print("IMSHOW PLOTTED")
    print("\n\n")

    fig_div = html.Div(id="plotly-map", 
                        children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config)]
                        )

    return fig_div
