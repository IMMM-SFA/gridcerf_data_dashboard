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
import time

## data manipulation libraries 
import xarray as xr

## web visualization and interactive libraries
from dash.dependencies import Input, Output, State
from dash import Dash, html, callback_context, callback
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc

# SOURCED SCRIPTS
from definitions import CONNECT_TO_LAMBDA, PORT, ZARRPATH, s3
if CONNECT_TO_LAMBDA:
	from msdlive_utils import get_bytes
	from io import BytesIO

from src.reader import open_as_raster
from src.deckgl2 import plot_map
from layout import create_app, tech_pathways_df, src_meta, all_options
from layout import intro_text, section_headers, title_text, description_text, funding_text, data_text

# -----------------------------------------------------------------------------
# Define dash app callbacks.
# -----------------------------------------------------------------------------

# -------------------------------------------
# Right-hand panel.
# -------------------------------------------

@callback(
    Output('subtech-select', 'options'),
    Input('tech-select', 'value'))
def set_level2_options(tech):
    return [{'label': i, 'value': i} for i in all_options[tech]]

@callback(
    Output('subtech-select', 'value'),
    Input('subtech-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@callback(
    Output('feature-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'))
def set_level2_options(tech, subtech):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech]]


@callback(
    Output('feature-select', 'value'),
    Input('feature-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@callback(
    Output('carbon-capture-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'),
    Input('feature-select', 'value'))
def set_level2_options(tech, subtech, feature):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech][feature]]

@callback(
    Output('carbon-capture-select', 'value'),
    Input('carbon-capture-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@callback(
    Output('cooling-type-select', 'options'),
    Input('tech-select', 'value'),
    Input('subtech-select', 'value'),
    Input('feature-select', 'value'),
    Input('carbon-capture-select', 'value'),
    )
def set_level2_options(tech, subtech, feature, is_ccs):
    return [{'label': i, 'value': i} for i in all_options[tech][subtech][feature][is_ccs]]

@callback(
    Output('cooling-type-select', 'value'),
    Input('cooling-type-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@callback(
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

@callback(
    Output('capacity-factor-select', 'value'),
    Input('capacity-factor-select', 'options'))
def set_level2_value(available_options):
    return available_options[0]['value']


@callback(
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


# -------------------------------------------
# DeckGL Mapping.
# -------------------------------------------

@callback(
    # [,
	# #  Output('last-btn-pressed', 'children')
	#  ],
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
	# Input(component_id="layer-selector", component_property="value"),
	# Input('adjust-mode', 'value'),
	# Input('button1', 'n_clicks'),
	# Input('button2', 'n_clicks'),
	# Input('last-btn-pressed', 'children'),
	# Input(component_id="opacity-btn", component_property="n_clicks"),
	# Input(component_id="visibility-btn", component_property="n_clicks"),
	Input(component_id='btn-text', component_property='children'),
	Input(component_id="tabnav", component_property="value"),
	Input(component_id='multi-layer-dropdown', component_property='value')
    ],
)

def map(year, ssp, tech, subtech, feature, is_ccs, coolingtype, capacity_factor, 
		# btn1, btn2, 
		btn_text,
		tab_id, layer_catalogue
		):

	start = time.time()
	year = str(year)
	query_df = tech_pathways_df.query("ui_ssp in @ssp and \
									   ui_year in @year and \
									   ui_tech in @tech and \
									   ui_subtype in @subtech and \
									   ui_feature in @feature and \
									   ui_is_ccs in @is_ccs and \
									   ui_cooling_type in @coolingtype and \
									   ui_capacity_factor in @capacity_factor")
	fpaths = query_df["fpath"].values # ['ssp5/2025/biomass/gridcerf_biomass_conventional_no-ccs_dry.tif']
	# index = f"{ssp}_{year}_{tech}_{subtech}_{feature}_{is_ccs}_{coolingtype}_{capacity_factor}"
	row = query_df.iloc[0]
	cols = ['ssp', 'ui_year', 'tech', 'subtype', 'feature', 'is_ccs', 'cooling_type', 'cap_factor']
	result_string = "_".join(str(row[col]) for col in cols)

	print(f"{ZARRPATH}/{result_string}")
	store = s3.get_mapper(f"{ZARRPATH}/{result_string}") # reading from the cloud adds two seconds (hopefully this speeds up)
	ds = xr.open_zarr(store) # had to remove consolidated=True, but otherwise works 
	# folder_path = f"{ZARRPATH}/{result_string}"
	# ds = xr.open_zarr(folder_path)
	df = ds.to_dataframe() 
	end = time.time()
	print(end-start)

	if btn_text == "button2": # dark 
		styling_dict = {"land": [48, 105, 59],
						"ocean": [0, 31, 72],
						"states": [66, 133, 55]
						}
	elif btn_text == "button1": # light
		styling_dict = {"land": [228, 235, 194],
						"ocean": [116, 206, 240],
						"states": [223, 234, 172],
						}
	else:
		print('no btn!')

	if ctx.triggered:
		fig_div = plot_map(df_coors_long=df, fpaths=fpaths, styling_dict=styling_dict) # takes 2.6 seconds
		mapped_time = time.time()
		print("Plot Map: ", mapped_time-start)

		return fig_div

	else:
		print("don't update!")
		raise PreventUpdate
	
# -------------------------------------------
# Map settings and tools.
# -------------------------------------------

@callback(
	Output('banner', 'style'),
	Output('page-body', 'style'),
    Input('btn-text', 'children')
)
def update_mode(value):

	time.sleep(1.3)

	if value == "button1":  # When the switch is "True" || LIGHT
		header_banner =  { # LIGHT
			"width": "100%",
			"background-color": "#2C7E9E",
			"display": "inline-block",
			"grid-area": "header",
			"transition": "background-color 0.3s"
			}

		# KEEP
		# app_logo = {
		# 	"filter": "invert(108%) sepia(0%) saturate(3207%) hue-rotate(0deg) brightness(100%) contrast(100%)",
		# 	"transition": "filter 0.3s"
		# }

		page_body = {
			"background-color": "#74cff0", #"white", # "rgba(255, 255, 255, 0.1)"
		}
		return header_banner, page_body
	
	elif value == "button2":  # When the switch is "False" || DARK
		header_banner =  { 
		"width": "100%",
		"background-color": "#1F244D", 
		"display": "inline-block",
		"grid-area": "header",
		"transition": "background-color 0.3s"
		}

		# KEEP
		# app_logo = {
		# 	"filter": "invert(38%) sepia(13%) saturate(3207%) hue-rotate(0deg) brightness(100%) contrast(80%)",
		# 	"transition": "filter 0.3s"
		# }

		page_body = {
			"background-color": "#001f48", #"black", # rgba(0, 0, 0, 0.5)
		}
		return header_banner, page_body


@callback(
    [
     Output('button1', 'className'),
     Output('button2', 'className'),
	 Output('btn-text', 'children')
	 ],
    [Input('button1', 'n_clicks'),
     Input('button2', 'n_clicks')]
)
def update_output(n_clicks1, n_clicks2):

	ctx = callback_context

	if ctx.triggered:
			
		clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]

		if clicked_id == 'button1':
			return 'button-selected', 'button', "button1"
		elif clicked_id == 'button2':
			return 'button', 'button-selected', "button2"
	else:
		return "button-selected", "button", "button1" # initialize on the sun (check if only falls into here for this case, b/c otherwise could be this 'button', 'button-selected' )

@callback(
    [Output(component_id="expandable-box", component_property="style"),
     Output(component_id="expandable-box", component_property="children"),
	],
   [Input(component_id="expandable-box", component_property="n_clicks"),
    Input(component_id="close-button", component_property="n_clicks"),
	]
)

def expand_box(expand_clicks, close_clicks):

	expanded_box_css = {"display": "block"}
	# expanded_btn_css = {"display": "block"}
	expanded_btn_css = [html.Button("X", id="close-button", className="close-btn", style={"display": "block" }),
	html.Div(id='intro', 
				children=[
						html.P(title_text, id='title', className="title-text"),
						html.P(description_text, id='description-text', className="page-text"), 
						html.P(section_headers[0], id='header0', className="header-text"),
						html.Hr(className="hr"),
						intro_text,
						html.P(section_headers[1], id='header3', className="header-text"),
						html.Hr(className="hr"),
						data_text,
						html.P(section_headers[2], id='header2', className="header-text"),
						html.Hr(className="hr"),
						html.P(funding_text, id='funding-text', className="page-text"),
		]
		)
	] 

	closed_box_css = {
				# "overflow-y": "hidden",
				"width": "40px",
				"height": "40px",
				"border-radius": "10px",
				"transition": "width 0.3s, height 0.3s",
			}
	# closed_btn_css ={"display": "none"}
	closed_btn_css = [
						html.Img(id="info-logo", className="svg", 
		 						  	 src=create_app().get_asset_url("icons/nav_icons/info.svg"),
									 style={"width": "30px", 
									 	    "height": "30px",
											"margin-left": "5px",
											"margin-top": "5px"
											}
									 ),
						html.Button(
							"X", 
							id="close-button", 
							className="close-btn", 
							style={"display": "none"})] 

	if close_clicks:
		return closed_box_css, closed_btn_css

	if expand_clicks:
		return expanded_box_css, expanded_btn_css

	return expanded_box_css, expanded_btn_css # Default state: expanded

# -----------------------------------------------------------------------------
# Older callbacks.
# -----------------------------------------------------------------------------

# @callback(
#     Output('adjust-mode', 'color'),
#     # Output('output', 'children'),
#     Input('adjust-mode', 'value')
# )
# def update_switch(value):
#     if value:  # When the switch is "True"
#         return "#fce17c"
#     else:  # When the switch is "False"
#         return 'blue'


# @callback(
#     Output("visibility", "src"),
#     Input("visibility-btn", "n_clicks"),
# )
# def toggle_eye_icon(n_clicks):

# 	if n_clicks % 2 == 0: # eye-open
# 		return app.get_asset_url("icons/map_icons/eye-open.svg")
# 	else: # eye-closed
# 		return app.get_asset_url("icons/map_icons/eye-slashed.svg")

# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

if CONNECT_TO_LAMBDA:
	print("Sending app to the get_wsgi_handler ... ")
else:
	if __name__ == "__main__":
		create_app().run(debug=False)
		# app.run_server(port=PORT, debug=False#, use_reloader=True, dev_tools_ui=True,
		# 				# dev_tools_props_check=True, 
		# 				# dev_tools_hot_reload=False,
		# 				) # disabling hot reloading