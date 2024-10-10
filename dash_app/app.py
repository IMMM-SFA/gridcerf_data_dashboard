#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------------
# GRIDCERF, U.S energy feasibility mapper and database explorer
# -------------------------------------------------------------------------------------

# LIBRARIES

## standard libraries
import os
import sys
import yaml

## web visualization and interactive libraries
from dash.dependencies import Input, Output, State
from dash import Dash, html
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc

# SOURCED SCRIPTS
from definitions import CONNECT_TO_LAMBDA, PORT, COMPILED_DIR, OUTDIR
if CONNECT_TO_LAMBDA:
	from msdlive_utils import get_bytes
	from io import BytesIO

from src.reader import open_as_raster
from src.deckgl import plot_deckgl_map
from layout import app, tech_pathways_df, src_meta, all_options

# -----------------------------------------------------------------------------
# Define dash app callbacks.
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
	Input(component_id="year-select", component_property="value"),
	Input(component_id="ssp-select", component_property="value"),
	Input(component_id="tech-select", component_property="value"),
	Input(component_id="subtech-select", component_property="value"),
	Input(component_id="feature-select", component_property="value"),
	Input(component_id="carbon-capture-select", component_property="value"),
	Input(component_id="cooling-type-select", component_property="value"), 
	Input(component_id="capacity-factor-select", component_property="value"),
	Input(component_id="layer-selector", component_property="value"),
	Input('adjust-mode', 'value')
    ],
)

def map(year, ssp,
		tech, subtech, feature,
		is_ccs, coolingtype, capacity_factor, selected_layers, adjust_mode):

    # -----------------------------------------------------------------------------
    # Creates and displays map by querying a "database" table of all pathways
    # to their filenames.
    # -----------------------------------------------------------------------------

	print(" --------------------------------------------------------------- ")
	year = str(year)
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

	# i = 0
	# for fpath in fpaths:
	# 	TIFPATH = os.path.join(COMPILED_DIR, fpath)
	# 	data_array, array, source_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=False, is_convert_to_png=False)
	# 	i += 1

	# DeckGL
	fig_div = plot_deckgl_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, adjust_mode=adjust_mode)
		
	return fig_div


# @app.callback(
# 	[
# 	Output(component_id='data_title', component_property='children'),
# 	Output(component_id='tag_id', component_property='children'),
# 	Output(component_id='source_type', component_property='children'),
# 	Output(component_id='description', component_property='children'),
# 	Output(component_id='date_updated', component_property='children'),
# 	Output(component_id='date_accessed', component_property='children'),
# 	Output(component_id='methodlogy', component_property='children'),
# 	Output(component_id='citation', component_property='children'),
# 	Output(component_id='data_link', component_property='children')
# 	],
# 	[Input(component_id='table', component_property='active_cell')]
# 	)

# def output_string(active_cell):

# 	if active_cell is None:
# 		return "", "", "", "", "", "", "", "", ""

# 	data_row = active_cell['row']
# 	data_col_id = active_cell['column_id']
	
# 	title = src_meta.loc[data_row, "plain_language_layer_name"]
# 	tag_id = src_meta.loc[data_row, "source_tag_id"]
# 	src_type = src_meta.loc[data_row, "source_type"]
# 	desc = src_meta.loc[data_row, "source_data_description"]
# 	date_updated = src_meta.loc[data_row, "source_data_updated"]
# 	data_accessed = src_meta.loc[data_row, "source_data_accessed"]
# 	layer_methodology = src_meta.loc[data_row, "layer_methodology"]
# 	citation = src_meta.loc[data_row, "source_data_citation"]
# 	data_link = src_meta.loc[data_row, "source_data_link"]
	
# 	return str(title), str(tag_id), str(src_type), str(desc), str(date_updated), str(data_accessed), str(layer_methodology), str(citation), str(data_link)

# @app.callback(
#     Output('adjust-mode', 'style'),
#     Input('adjust-mode', 'value')
# )
# def update_toggle_style(value):
#     if value:  # When the switch is "true"
#         return {
#             'backgroundColor': '#ffdd57',  # Sunny color
#             'border': '1px solid #f39c12',  # Optional border color
#         }
#     else:  # When the switch is "false"
#         return {
#             'backgroundColor': 'transparent',  # Keep transparent
#             'border': '1px solid #ccc',  # Optional border color
#         }

# @app.callback(
#     Output('adjust-mode', 'style'),
#     Output('toggle-icon', 'style'),
#     Output('moon-icon', 'style'),
#     Output('sun-icon', 'style'),
#     Input('adjust-mode', 'n_clicks'),
# )
# def update_switch(n_clicks):
#     if n_clicks % 2 == 1:  # Odd clicks mean switch is "on"
#         return (
#             {'backgroundColor': '#ffdd57'},  # Sunny color when "on"
#             {'transform': 'translateX(30px)'},  # Move the icon to the right
#             {'display': 'none'},  # Hide moon icon
#             {'display': 'block'}  # Show sun icon
#         )
#     else:  # Even clicks mean switch is "off"
#         return (
#             {'backgroundColor': '#ccc'},  # Default color when "off"
#             {'transform': 'translateX(0)'},  # Move the icon to the left
#             {'display': 'block'},  # Show moon icon
#             {'display': 'none'}  # Hide sun icon
#         )

@app.callback(
    Output('adjust-mode', 'color'),
    # Output('output', 'children'),
    Input('adjust-mode', 'value')
)
def update_switch(value):
    if value:  # When the switch is "True"
        return "#fce17c"
    else:  # When the switch is "False"
        return 'blue'

@app.callback(
	Output('banner', 'style'),
	Output('app-logo', 'style'),
	Output('page-body', 'style'),
    Input('adjust-mode', 'value')
)
def update_mode(value):
	if value:  # When the switch is "True"
		header_banner =  {
			"width": "100%",
			"background-color": "#2C7E9E",
			"display": "inline-block",
			"grid-area": "header",
			"transition": "background-color 0.3s"
			}
		app_logo = {
			"filter": "invert(108%) sepia(0%) saturate(3207%) hue-rotate(0deg) brightness(100%) contrast(100%)",
			"transition": "filter 0.3s"
		}
		page_body = {
			"background-color": "white",
			# "background-color": "rgba(255, 255, 255, 0.1)"
		}
		return header_banner, app_logo, page_body
	
	else:  # When the switch is "False"
		header_banner =  {
		"width": "100%",
		"background-color": "#1F244D", 
		"display": "inline-block",
		"grid-area": "header",
		"transition": "background-color 0.3s"
		}

		app_logo = {
			"filter": "invert(38%) sepia(13%) saturate(3207%) hue-rotate(0deg) brightness(100%) contrast(80%)",
			"transition": "filter 0.3s"
		}
		page_body = {
			"background-color": "black",
			# "background-color": "rgba(0, 0, 0, 0.1)" # rgba(0, 0, 0, 0.5)
		}
		return header_banner, app_logo, page_body

# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

if CONNECT_TO_LAMBDA:
	print("Sending app to the get_wsgi_handler ... ")
else:
	if __name__ == "__main__":
		app.run_server(port=PORT, debug=True)