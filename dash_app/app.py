#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------------
# GRIDCERF, data tool and app that runs visuals on Closed-Loop Geothermal Data
# -------------------------------------------------------------------------------------

# LIBRARIES

# standard libraries
import os
import sys
import yaml

# data manipulation
import pandas as pd
import xarray as xr
from functools import reduce
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from PIL import Image

# visualization and data manipulation
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# web app and interactive graphics libraries 
from dash.dependencies import Input, Output, State
from dash import Dash, html
from dash import ctx
from dash.exceptions import PreventUpdate
from dash import dcc
import dash_leaflet as dl
import dash_leaflet.express as dlx

# SOURCED SCRIPTS
from definitions import CONNECT_TO_LAMBDA
if CONNECT_TO_LAMBDA:
	from msdlive_utils import get_bytes
	from io import BytesIO

# sourced scripts
from src.utilities import open_as_raster, create_datashaded_scatterplot #, get_map_data
from layout import app, tech_pathways_df, src_meta, all_options, OUTDIR, COMPILED_DIR

# app = create_app()

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
		data_array, array, metadata = open_as_raster(TIFPATH=TIFPATH) # save metadata['crs'] and metadata['']
		i += 1
		# print(array)

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
		
		def tif_to_png(tif_path):
			with rasterio.open(tif_path) as src:
				array = src.read(1)  # read the first (and only) band
				array = np.interp(array, (array.min(), array.max()), (0, 255)) #  255 is white and 0 is black
				img = Image.fromarray(array.astype(np.uint8)).resize((src.width, src.height))

				# print(src)
				print(src.bounds)
				# metadata = src.meta # dict_keys(['driver', 'dtype', 'nodata', 'width', 'height', 'count', 'crs', 'transform'])
				# print(metadata['transform']) 
				# print('\n')
				# print(metadata['crs'])
				# crs = src.crs
				# print()
				# lat_max = src.latitude.values.max()
				# lat_min = src.latitude.values.min()
				# lon_max = src.longitude.values.max()
				# lon_min = src.longitude.values.min()
				
				# print(lat_max, lat_min, lon_max, lon_min)
				return img, src.bounds, [src.width, src.height], [-171.791110603, 18.91619, -66.96466, 71.3577635769]

		# TIFPATH = os.path.join(COMPILED_DIR, fpath)
		# print(TIFPATH)
		# data_array, array, metadata = open_as_raster(TIFPATH=TIFPATH) 

		PNG, bounds, width_height, bbox = tif_to_png(tif_path=TIFPATH)
		
		# PNG = array
		print(array.shape)
				
		""" 
		Convert Raster to Web-Compatible Format:

Leaflet does not directly support .TIF files, so you’ll need to convert your .TIF file to a format that Leaflet can display, like PNG or JPEG. You can use a tool like rasterio to handle this conversion.
Create a Web Tile Layer:

Convert the raster data into tiles (e.g., using Mapbox or a tile server).
Set Up Your Dash App:

Create a Dash app with Dash Leaflet to display the map and raster tiles.

"""
		# dlx.dicts_to_geojson(geo_data)

		# ## Map Update 
		# if len(location)>0:
		# 	df_loc = pd.DataFrame({"state_lower":location})
		# 	df_loc = df_loc.groupby('state_lower').size().reset_index(name='doc_count')
		# 	df_loc['state_lower'] = df_loc.state_lower.str.lower()
		# 	df_loc = df_loc.merge(df_location, on='state_lower', how = 'inner')
		# 	geo_data  = df_loc.apply(lambda x: [dict(lat=x.latitude, lon=x.longitude)]*x.doc_count, axis = 1)
		# 	geo_data = reduce(lambda x, y: x + y, geo_data)
		# else: geo_data=[]


		# Paths.
		GEOTIFF_DIR = "data"
		DATA_DIR = "data"
		DRIVER_PATH = "data/db.sqlite"
		# Server config.
		TC_PORT = 5000
		TC_HOST = "localhost"
		TC_URL = f"http://{TC_HOST}:{TC_PORT}"
		# Data stuff.
		GFS_YEAR, GFS_MONTH, GFS_DAY, GFS_HOUR, GFS_FCST_HOUR = "2020", "01", "01", "000", "0000"
		GFS_KEY = f"gfs_4_{GFS_YEAR}{GFS_MONTH}{GFS_DAY}_{GFS_FCST_HOUR}_{GFS_HOUR}"
		PARAMS = ["wspd", "temp"]
		PARAMS_GFS = ["VGRD:100 m above ground", "UGRD:100 m above ground", "TMP:2 m above ground"]
		PARAM_MAPPINGS = dict(
		wspd=lambda ds: (ds['UGRD_100maboveground'][:][0]**2 + ds['VGRD_100maboveground'][:][0]**2)**0.5,
		temp=lambda ds: ds['TMP_2maboveground'][:][0]
		)

		cmaps = ["Viridis", "Spectral", "Greys"]
		lbl_map = dict(wspd="Wind speed", temp="Temperature")
		unit_map = dict(wspd="m/s", temp="°K")
		srng_map = dict(wspd=[0, 10], temp=[250, 300])
		param0 = "temp"
		cmap0 = "Viridis"
		srng0 = srng_map[param0]


		fig_div = html.Div(children=[
    # Create the map itself.
    dl.Map(id="map", center=[39.8283, -98.5795], zoom=4, children=[
        dl.TileLayer(),
        # dl.TileLayer(id="tc", opacity=0.5),
		# WMSTileLayer
		# dl.WMSTileLayer(url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
        #             layers="nexrad-n0r-900913", format="image/png", transparent=True),
		dl.ImageOverlay(url=PNG, opacity=0.5, bounds=[[24.9493, -125.00165], [49.59037, -66.93457]]
		#tileSize=912 #width_height
		#  bounds={"getEast": -66.945392, "getNorth": 49.382808, "getSouth": 24.521208, "getWest": -124.736342}
		), #bounds [bounds[0], bounds[1], bounds[2], bounds[3]]
		# url=TIFPATH
        # dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
    ], style={"width": "100%", "height": "100%"}
	),
    # Create controller.
    # html.Div(children=[
    #     html.Div("Parameter"),
    #     dcc.Dropdown(id="dd_param", options=[dict(value=p, label=lbl_map[p]) for p in PARAMS], value=param0),
    #     html.Br(),
    #     html.Div("Colorscale"),
    #     dcc.Dropdown(id="dd_cmap", options=[dict(value=c, label=c) for c in cmaps], value=cmap0),
    #     html.Br(),
    #     html.Div("Opacity"),
    #     dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
    #     html.Br(),
    #     html.Div("Stretch range"),
    #     dcc.RangeSlider(id="srng", min=srng0[0], max=srng0[1], value=srng0,
    #                     marks={v: "{:.1f}".format(v) for v in srng0}),
    #     html.Br(),
    #     html.Div("Value @ click position"),
    #     html.P(children="-", id="label"),
    # ], 
	# className="info")

], style={"display": "grid", "width": "100%", "height": "100vh"})

		# fig_div = html.Div(id="plotly-map", 
		# 				   children=[dl.Map(
		# 				   				# dl.BaseLayer(id="baselayer"),
		# 				   				# dl.TileLayer(url=TIFPATH), center=[56,10], zoom=6, style={'height': '80vh', 'width': '80vh'}
		# 								dl.LayersControl(
		# 									[
		# 										dl.Overlay(
		# 											[
		# 												# dl.ImageOverlay(url=png_path, bounds=bounds_png)
		# 												dl.GeoTIFFOverlay(
		# 													url=TIFPATH) #, bounds=bounds_tiff)
		# 											],
		# 											name="Map", checked=True)
		# 									],
		# 									position="topleft"
		# 								),
		# 								),
		# 				   				# dl.GeoJSON(data=dlx.dicts_to_geojson(
		# 				   				# 							get_map_data()
		# 				   				# 							), 
		# 				   				# 			cluster=True, 
		# 						  		# 	 		superClusterOptions={"radius": 100}, id='map-geojson'),
										

		# 				   ],
		# 				   )

		# fig_div = html.Div(id="plotly-map",
		# 				   children=dl.Map(
		# 				   				children=[
		# 				   						  dl.TileLayer(),
		# 				   						  dl.LayersControl([dl.BaseLayer(
		# 				   						  						dl.TileLayer(url=TIFPATH)) #, name=key, checked=key == "temp_new", id=key) for key in keys
		# 				   						  						]
		# 				   						  					+
		# 				   						  					[dl.Overlay(dl.LayerGroup(markers), name="TEST", checked=True)]
		# 				   						  					)
		# 				   						  ],
		# 				   				center=[52.195573, 20.883528], zoom=12, id='map'), 
		# 				   			    style={'width': '80vh', 'height': '80vh'}), 
		# 				   			    # 'margin': "auto", "display": "block", "position": "relative"


		print("Leaflet and TiTiler")


	if maptool == "Mapbox":
		
		# fig.update_layout(mapbox_style="open-street-map")

		# df = px.data.gapminder().query("year == 2007")
		# fig = px.scatter_geo(df, locations="iso_alpha",
		# 					color="continent", # which column to use to set the color of markers
		# 					hover_name="country", # column added to hover information
		# 					size="pop", # size of markers
		# 					projection="natural earth")
							
		## IF USING MAPBOX THIS IS GREAT BUT IT DOESN'W WORK FOR IMSHOW
		# Add a basemap layer (a custom image or plotly mapbox style) - optional
		# fig.update_layout(
		# 		mapbox_style="open-street-map",  # Choose a basemap style (e.g., 'open-street-map', 'carto-positron', 'white-bg')
		# 		mapbox=dict(
		# 				center=dict(lat=37.0902, lon=-95.7129),  # Center of the US (latitude and longitude)
		# 				zoom=3  # Adjust the zoom level as needed
		# 		),
		# 		autosize=True
		# )
		# Add a trace in order for the base map to appear
		# fig.add_trace(go.Scattermapbox(
		# 	mode='markers',
		# 	lon=[-95.7129],  # Longitude of center (for example)
		# 	lat=[37.0902],  # Latitude of center (for example)
		# 	marker=dict(
		# 				size=10, # Fixed size?
		# 				color='red'
		# 				)
		# ))

		# Update layout with geo projection and center -- this did nothing ... 
		# fig.update_layout(
		# 	geo=dict(
		# 		scope='usa',
		# 		center=dict(lat=39.0902, lon=-95.7129),  # Center of the US
		# 		projection_scale=5  # Adjust this as needed
		# 	)
		# )
		# fig.add_trace(px.imshow(array))






		# print(data_array)

		# fig_div = html.Div(id="plotly-map", 
		# 				   children=[
		# 				   px.scatter_mapbox(data_array), # lon=data_array.x, lat=data_array.y
		# 				   ]
		# 				   )
		# fig_div.update_layout(
		# 			title='Raster Overlay on Map',
		# 			geo=dict(
		# 				scope='usa',
		# 				projection=dict(type='mercator'),
		# 				showland=True,
		# 				landcolor='rgb(243, 243, 243)'
		# 			)
		# 		)


		# Convert to Plotly-compatible format
		img_trace = px.imshow(data_array)

		# Create map with base layer and raster overlay
		fig = px.scatter_mapbox(
			lat=[37.7749],
			lon=[-95.7129],
			color_discrete_sequence=['blue'],
			zoom=4,
			mapbox_style='open-street-map'
		)

		print(img_trace.data[0])
		fig.add_trace(img_trace.data[0])

		fig.update_layout(
			title='Raster Overlay on Map',
			mapbox=dict(
				style='open-street-map',
				center=dict(lat=37.7749, lon=-95.7129),
				zoom=4
			)
		)

		fig_div = html.Div(id="plotly-map", 
						   children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config)]
						   )

		print("Mapbox")


	if maptool == "Plotly-imshow":
		
		# This is custom and NOT spatially driven ... what makes this technology non spatial?
		# v.s. other spatial technology?

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
