#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------------
# GRIDCERF, data tool and app that runs visuals on Closed-Loop Geothermal Data
# -------------------------------------------------------------------------------------

# standard libraries
import os
import sys
import yaml
# import time
# import pydoc

# data manipulation
import pandas as pd
import xarray as xr

# visualization and data manipulation
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from bokeh.sampledata.penguins import data as dftest
import hvplot.xarray
import hvplot.pandas
from holoviews.plotting.plotly.dash import to_dash

# web app and interactive graphics libraries 
from dash.dependencies import Input, Output, State
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc
import dash_leaflet as dl

# MSD-LIVE added imports:
from msdlive_utils import get_bytes
from io import BytesIO

# MSD-LIVE added dataset id that goes to DEV
DATASET_ID = "1ffea-emt93"

# sourced scripts
sys.path.append("src")
from utilities import open_as_raster
from layout import app, tech_pathways_df, src_meta, all_options, OUTDIR, COMPILED_DIR

# app = create_app()

from dash import Dash, html
import holoviews as hv
from holoviews.plotting.plotly.dash import to_dash
from holoviews.operation.datashader import datashade
import pandas as pd
import numpy as np
from plotly.data import carshare
from plotly.colors import sequential
import pandas as pd
import numpy as np

import holoviews as hv
from holoviews.operation.datashader import datashade
from holoviews.plotting.plotly.dash import to_dash

hv.extension("plotly")

plotly_config = {'displaylogo': False,
                'modeBarButtonsToRemove': ['autoScale', 'resetScale'], # High-level: zoom, pan, select, zoomIn, zoomOut, autoScale, resetScale
                'toImageButtonOptions': {
                    'format': 'png', # one of png, svg, jpeg, webp
                    'filename': 'custom_image',
                    'height': None,
                    'width': None,
                    'scale': 6 # Multiply title/legend/axis/canvas sizes by this factor
                        }
                  }


def generate_data():
    data = np.random.random((1000000, 2))

    return pd.DataFrame(data, columns=["x", "y"])


def create_datashaded_scatterplot(df):
    dataset = hv.Dataset(df)
    scatter = datashade(
        hv.Scatter(dataset, kdims=["x"], vdims=["y"])
    ).opts(width=800, height=800)

    return scatter


def update_plot(df):
    scatter = create_datashaded_scatterplot(df)
    components = to_dash(app, [scatter])
    return components.children


# @app.callback(
#     Output("plot-div", "children"),
#     Input("update-data-button", "n_clicks"),
#     prevent_initial_call=True
# )
# def update_plot_callback(n_clicks):
#     df = generate_data()
#     return update_plot(df)

# -----------------------------------------------------------------------------
# Define dash app plotting callbacks.
# -----------------------------------------------------------------------------

@app.callback(
    Output('subtech-select', 'options'),
    Input('tech-select', 'value'))
def set_level2_options(tech):
    return [{'label': i, 'value': i} for i in all_options[tech]]


@app.callback(
    Output('subtech-select', 'value'),
    Input('subtech-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('feature-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'))
def set_level2_options(tech, subtech):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech]]


@app.callback(
    Output('feature-select', 'value'),
    Input('feature-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('carbon-capture-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'),
    Input('feature-select', 'value'))
def set_level2_options(tech, subtech, feature):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech][feature]]

@app.callback(
    Output('carbon-capture-select', 'value'),
    Input('carbon-capture-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('cooling-type-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'),
    Input('feature-select', 'value'),
    Input('carbon-capture-select', 'value'),
    )
def set_level2_options(tech, subtech, feature, is_ccs):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech][feature][is_ccs]]

@app.callback(
    Output('cooling-type-select', 'value'),
    Input('cooling-type-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@app.callback(
    Output('capacity-factor-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'),
    Input('feature-select', 'value'),
    Input('carbon-capture-select', 'value'),
    Input('cooling-type-select', 'value'),
    )
def set_level2_options(tech, subtech, feature, is_ccs, cooling_type):
    options = all_options[tech][subtech][feature][is_ccs][cooling_type]
    if isinstance(options, str): 
        options = [options]
    return [{'label': i, 'value': i} for i in options]

@app.callback(
    Output('capacity-factor-select', 'value'),
    Input('capacity-factor-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@app.callback(
	[
	Output(component_id='feature-select-container', component_property='style'),
	Output(component_id='carbon-capture-select-container', component_property='style'),
	Output(component_id='cooling-type-select-container', component_property='style'),
	Output(component_id='capacity-factor-select-container', component_property='style'),
	],
	[
	Input(component_id='feature-select', component_property='value'),
	Input(component_id='carbon-capture-select', component_property='value'),
	Input(component_id='cooling-type-select', component_property='value'),
	Input(component_id='capacity-factor-select', component_property='value'),
	]
	)

def show_hide_element(feature, is_ccs, cooling, capacity_factor):

	# eventually integrate this into the above callbacks

	feature_show = {'display': 'block'}
	is_css_show = {'display': 'block'}
	cooling_show = {'display': 'block'}
	cf_show = {'display': 'block'}

	if feature == '--':
		feature_show = {'display': 'none'}
	
	if is_ccs == '--':
		is_css_show = {'display': 'none'}

	if cooling == '--':
		cooling_show = {'display': 'none'}

	if capacity_factor == '--':
		cf_show = {'display': 'none'}

	return feature_show, is_css_show, cooling_show, cf_show


@app.callback(
    Output(component_id="map", component_property="children"),
    [
	Input(component_id="map-select", component_property="value"),
	# Input(component_id="state-select", component_property="value"),
	Input(component_id="year-select", component_property="value"),
	Input(component_id="ssp-select", component_property="value"), # Socioeconomic scenario (SSP)
	Input(component_id="tech-select", component_property="value"),
	Input(component_id="subtech-select", component_property="value"),
	Input(component_id="feature-select", component_property="value"),
	Input(component_id="carbon-capture-select", component_property="value"),
	Input(component_id="cooling-type-select", component_property="value"), 
	Input(component_id="capacity-factor-select", component_property="value"),
	# e.g., communications perspective: Land Management/Native Habitats
	# Input vs. Compiled (will always be compiled)
    ],
)

def map(maptool, #state, 
			year, ssp,
			tech, subtech, feature,
			is_ccs, coolingtype, capacity_factor):

    # -----------------------------------------------------------------------------
    # Creates and displays map by querying a "database" table of all pathways
    # to their filenames.
    # -----------------------------------------------------------------------------

	year = str(year)

	print(" --------------------------------------------------------------- ")
	print([ssp, year, tech, subtech, feature, is_ccs, coolingtype, capacity_factor])
	query_df = tech_pathways_df.query("ui_ssp in @ssp and \
									   ui_year in @year and \
									   ui_tech in @tech and \
									   ui_subtype in @subtech and \
									   ui_feature in @feature and \
									   ui_is_ccs in @is_ccs and \
									   ui_cooling_type in @coolingtype and \
									   ui_capacity_factor in @capacity_factor")

	fpaths = query_df["fpath"].values

	i = 0
	for fpath in fpaths:

		TIFPATH = os.path.join(COMPILED_DIR, fpath)
		print(TIFPATH)
		data_array, array, metadata = open_as_raster(TIFPATH=TIFPATH) # save metadata['crs'] and metadata['']
		i += 1
		print(array)

	if maptool == "Plotly-imshow":
		
		fig = px.imshow(array)
		fig.update_layout(mapbox_style="open-street-map")
		fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
		fig.update_xaxes(showticklabels=False)
		fig.update_yaxes(showticklabels=False)
		# fig.update_traces(showlegend=False)
		fig.update(layout_coloraxis_showscale=False)
		# fig.update_traces(marker_showscale=False)
		# fig.write_html(os.path.join(OUTDIR, "map-layer.html"))

		print("IMSHOW PLOTTED")
		print("\n\n")

		fig_div = html.Div(id="plotly-map", 
						   children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config)]
						   )

	if maptool == "Plotly-datashader, holoviews": 

		# to use RAPIDS ... need to install drivers, but have no GPUs on Mac

		ylat = np.arange(0, array.shape[0], 1).tolist()
		xlon = np.arange(0, array.shape[1], 1).tolist()
		
		data_xr = xr.DataArray(array, 
			coords={'y': ylat,'x': xlon}, 
		dims=["y", "x"])
		df = data_xr.to_dataframe(name='value').reset_index()
		print(df)

		# test
		fig = dftest.hvplot.scatter(x='bill_length_mm', y='bill_depth_mm', by='species')
		# fig = df.hvplot(x="x", y="y", kind='scatter', rasterize=True)
		print("HOLOVIEWS PLOTTED")
		print("\n\n")

		# scatter = create_datashaded_scatterplot(df)
		components = to_dash(app, [fig])

		fig_div = html.Div(id="plotly-map", 
						   children=components
						   )



	if maptool == "Leaflet and TiTiler":
		
		fig_div = html.Div(id="plotly-map", 
						   children=[dl.Map(dl.TileLayer(), center=[56,10], zoom=6, style={'height': '80vh'})]
						   )

		print("Leaflet and TiTiler")

		


	return fig_div


@app.callback(
	[
	Output(component_id='data_title', component_property='children'),
	Output(component_id='tag_id', component_property='children'),
	Output(component_id='source_type', component_property='children'),
	Output(component_id='description', component_property='children'),
	Output(component_id='date_updated', component_property='children'),
	Output(component_id='date_accessed', component_property='children'),
	Output(component_id='methodlogy', component_property='children'),
	Output(component_id='citation', component_property='children'),
	Output(component_id='data_link', component_property='children')
	],
	[Input(component_id='table', component_property='active_cell')]
	)

def output_string(active_cell):

	if active_cell is None:
		return "", "", "", "", "", "", "", "", ""

	data_row = active_cell['row']
	data_col_id = active_cell['column_id']
	
	title = src_meta.loc[data_row, "plain_language_layer_name"]
	tag_id = src_meta.loc[data_row, "source_tag_id"]
	src_type = src_meta.loc[data_row, "source_type"]
	desc = src_meta.loc[data_row, "source_data_description"]
	date_updated = src_meta.loc[data_row, "source_data_updated"]
	data_accessed = src_meta.loc[data_row, "source_data_accessed"]
	layer_methodology = src_meta.loc[data_row, "layer_methodology"]
	citation = src_meta.loc[data_row, "source_data_citation"]
	data_link = src_meta.loc[data_row, "source_data_link"]

	# tag_id = "TAG ID: " + str(tag_id)
	
	return str(title), str(tag_id), str(src_type), str(desc), str(date_updated), str(data_accessed), str(layer_methodology), str(citation), str(data_link)


server = app.server 
