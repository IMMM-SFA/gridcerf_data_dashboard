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
from dash import Dash, html, callback_context
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc

# SOURCED SCRIPTS
from definitions import CONNECT_TO_LAMBDA, PORT, COMPILED_DIR, OUTDIR
if CONNECT_TO_LAMBDA:
	from msdlive_utils import get_bytes
	from io import BytesIO

from src.reader import open_as_raster
from src.deckgl import plot_deckgl_globe, plot_deckgl_map
from layout import app, tech_pathways_df, src_meta, all_options
from layout import intro_text, section_headers, title_text, description_text, funding_text, data_text

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
    [Output(component_id="map", component_property="children"),
	 Output('last-btn-pressed', 'children')],
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
	Input('adjust-mode', 'value'),
	Input('button1', 'n_clicks'),
	Input('button2', 'n_clicks'),
	Input('last-btn-pressed', 'children'),
	# Input(component_id="opacity-btn", component_property="n_clicks"),
	Input(component_id="visibility-btn", component_property="n_clicks"),
	Input(component_id="tabnav", component_property="value"),
	Input('multi-layer-dropdown', 'value')
    ],
)

def map(year, ssp,
		tech, subtech, feature,
		is_ccs, coolingtype, capacity_factor, 
		# selected_layers, 
		adjust_mode, btn1, btn2, last_pressed,
		# opacity_clicks, 
		visible_clicks,
		tab_id,
		layer_catalogue
		):

    # -----------------------------------------------------------------------------
    # Creates and displays map by querying a "database" table of all pathways
    # to their filenames.
    # -----------------------------------------------------------------------------

	# print(" --------------------------------------------------------------- ")
	year = str(year)
	# print([ssp, year, tech, subtech, feature, is_ccs, coolingtype, capacity_factor])
	query_df = tech_pathways_df.query("ui_ssp in @ssp and \
									   ui_year in @year and \
									   ui_tech in @tech and \
									   ui_subtype in @subtech and \
									   ui_feature in @feature and \
									   ui_is_ccs in @is_ccs and \
									   ui_cooling_type in @coolingtype and \
									   ui_capacity_factor in @capacity_factor")

	fpaths = query_df["fpath"].values
	# print(fpaths) # ['ssp5/2025/biomass/gridcerf_biomass_conventional_no-ccs_dry.tif']
	# i = 0
	# for fpath in fpaths:
	# 	TIFPATH = os.path.join(COMPILED_DIR, fpath)
	# 	data_array, array, source_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=False, is_convert_to_png=False)
	# 	i += 1

	basemap_layers = ["base-map-ocean", "base-map"]

	if visible_clicks % 2 == 0:
		visibility_mode = True
		selected_layers = ["base-map-ocean", "base-map", "feasibility-layer"]
	else: 
		visibility_mode = False
		selected_layers = basemap_layers

	if tab_id == "insights-tab":
		is_compiled = True
	if tab_id == "layers-tab": 
		is_compiled = False
		selected_layers = basemap_layers + layer_catalogue
		fpaths = layer_catalogue
	
	# DeckGL
	ctx = callback_context # there are multiple callback contextes in this  

	if ctx.triggered:
		
		clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]

		# if adjust_mode:
		clicked_id_ = clicked_id + "-" + last_pressed
		# "button2-True"
		# "button2-False"
		# "adjust-mode-True"
		# "adjust-mode-False"

		# clicked_id == adjust-mode from light to dark then need go into button2
		if clicked_id == 'button1':
			fig_div = plot_deckgl_globe(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, 
										adjust_mode=adjust_mode, visibility_mode=visibility_mode, is_compiled=is_compiled)
			last_pressed = "button1"
		# elif clicked_id_ == 'adjust-mode-button1':
		# 	fig_div = plot_deckgl_globe(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, adjust_mode=adjust_mode)
		# 	last_pressed = "button1"
		elif clicked_id == 'button2':
			fig_div = plot_deckgl_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, 
										adjust_mode=adjust_mode, visibility_mode=visibility_mode, is_compiled=is_compiled)
			last_pressed = "button2"
		elif clicked_id_ == "adjust-mode-button2":
			fig_div = plot_deckgl_map(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, 
									adjust_mode=adjust_mode, visibility_mode=visibility_mode, is_compiled=is_compiled)
			last_pressed = "button2"
		else:
			# default (or if fails all other options it will become a globe) 
			fig_div = plot_deckgl_globe(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, 
									adjust_mode=adjust_mode, visibility_mode=visibility_mode, is_compiled=is_compiled)
			last_pressed = "button1"
	else:
		fig_div = plot_deckgl_globe(COMPILED_DIR=COMPILED_DIR, fpaths=fpaths, selected_layers=selected_layers, 
								adjust_mode=adjust_mode, visibility_mode=visibility_mode, is_compiled=is_compiled)
		last_pressed = "button1"

	return fig_div, last_pressed

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
	# Output('app-logo', 'style'),
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

		# KEEP
		# app_logo = {
		# 	"filter": "invert(108%) sepia(0%) saturate(3207%) hue-rotate(0deg) brightness(100%) contrast(100%)",
		# 	"transition": "filter 0.3s"
		# }

		page_body = {
			"background-color": "white",
			# "background-color": "rgba(255, 255, 255, 0.1)"
		}
		return header_banner, page_body
	
	else:  # When the switch is "False"
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
			"background-color": "black",
			# "background-color": "rgba(0, 0, 0, 0.1)" # rgba(0, 0, 0, 0.5)
		}
		return header_banner, page_body


@app.callback(
    [
     Output('button1', 'className'),
     Output('button2', 'className')
	 ],
    [Input('button1', 'n_clicks'),
     Input('button2', 'n_clicks')]
)
def update_output(n_clicks1, n_clicks2):

	ctx = callback_context

	if ctx.triggered:
			
		clicked_id = ctx.triggered[0]['prop_id'].split('.')[0]

		if clicked_id == 'button1':
			return 'button-selected', 'button'
		elif clicked_id == 'button2':
			return 'button', 'button-selected'
	else:
		return "button-selected", "button"

@app.callback(
    [Output(component_id="expandable-box", component_property="style"),
     Output(component_id="expandable-box", component_property="children"),
	],
   [Input(component_id="expandable-box", component_property="n_clicks"),
    Input(component_id="close-button", component_property="n_clicks"),
	]
)

def toggle_expand(expand_clicks, close_clicks):

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
		 						  	 src=app.get_asset_url("icons/nav_icons/info.svg"),
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

@app.callback(
    Output("visibility", "src"),
    Input("visibility-btn", "n_clicks"),
)
def toggle_eye_icon(n_clicks):

	if n_clicks % 2 == 0: # eye-open
		return app.get_asset_url("icons/map_icons/eye-open.svg")
	else: # eye-closed
		return app.get_asset_url("icons/map_icons/eye-slashed.svg")

# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

if CONNECT_TO_LAMBDA:
	print("Sending app to the get_wsgi_handler ... ")
else:
	if __name__ == "__main__":
		app.run_server(port=PORT, debug=True)