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
import rasterio
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

# sourced scripts
from layout import app, tech_pathways_df, src_meta, all_options, OUTDIR, COMPILED_DIR

# functions

def open_as_raster(TIFPATH):

	with rasterio.open(TIFPATH) as src: 
		array = src.read(1)
		crs = src.crs
		metadata = src.meta
		array_nodata = np.where(array == src.nodata, np.nan, 0)
		array = np.where(array==1, np.nan, array)

	return array

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
    Output(component_id="energy-map", component_property="figure"),
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
		array = open_as_raster(TIFPATH=TIFPATH)
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

	if maptool == "Plotly-datashader and RAPIDS": # holoviews & RAPIDS ... somewhat go together
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

	if maptool == "Leaflet and TiTiler":
		print("test")

	return fig


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
