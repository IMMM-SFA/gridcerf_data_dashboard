#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------------
# GRIDCERF, data tool and app that runs visuals on Closed-Loop Geothermal Data
# -------------------------------------------------------------------------------------

# https://dash.gallery/dash-deck-explorer/globe-view

# THIS is what I want for a quick introduction to JavaScript
# https://github.com/Esri/quickstart-map-js


# https://blog.mapbox.com/visualizing-radar-data-with-vector-tiles-117bc5ee9a5a

# LIBRARIES

# standard libraries
import os
import sys
import yaml

# data manipulation
import pandas as pd
import numpy as np
import xarray as xr
from functools import reduce

# web visualization and interactive libraries
from dash.dependencies import Input, Output, State
from dash import Dash, html
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc
import holoviews as hv
hv.extension('bokeh')
from holoviews.plotting.plotly.dash import to_dash

# SOURCED SCRIPTS
from definitions import CONNECT_TO_LAMBDA, PORT, plotly_config, CMAP_BLACK, token
if CONNECT_TO_LAMBDA:
	from msdlive_utils import get_bytes
	from io import BytesIO

from src.reader import open_as_raster
from src.utilities import create_datashaded_scatterplot #, get_map_data
from src.imshow import plot_imshow_map
from src.datashader_mapbox import plot_ds_mapbox_map
from src.datashader_holoviews import plot_ds_holoviews_map
from src.leaflet_titiler import plot_leaflet_map
from src.mapbox_raster import plot_mapbox_map
from src.deckgl import plot_deckgl_map
from layout import app, tech_pathways_df, src_meta, all_options, OUTDIR, COMPILED_DIR

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
	# print(len(fpaths))

	# i = 0
	# for fpath in fpaths:

	# 	TIFPATH = os.path.join(COMPILED_DIR, fpath)
	# 	data_array, array, source_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=False, is_convert_to_png=False)
	# 	i += 1

	if maptool == "Plotly-datashader, mapbox": 

		fig_div = plot_ds_mapbox_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)

	if maptool == "Plotly-datashader, holoviews": 

		fig = plot_ds_holoviews_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)

		components = to_dash(app, [fig]) # breaks here, reset_button=True

		fig_div = html.Div(id="energy-map3", 
						children=components.children
						)
		print("HOLOVIEWS PLOTTED")

	if maptool == "Leaflet and TiTiler":

		fig_div = plot_leaflet_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)

	if maptool == "Mapbox":

		fig_div = plot_mapbox_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)

	if maptool == "Plotly-imshow":

		fig_div = plot_imshow_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)
	
	if maptool == "DeckGL":

		fig_div = plot_deckgl_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths)
		
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

