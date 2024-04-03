#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------------------
# GRIDCERF, data tool and app that runs visuals on Closed-Loop Geothermal Data
# -------------------------------------------------------------------------------------

# standard libraries
import os
import sys
import time
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
import dash_leaflet as dl
# import matplotlib

# web app and interactive graphics libraries 
import dash
from dash.dependencies import Input, Output, State
from dash import Dash, dcc, html, ctx
from dash_svg import Svg, G, Path, Circle # Scalable Vector Graphics (SVG) maker
import dash_daq as daq                    # Adds more data acquisition (DAQ) and controls to dash callbacks 
import dash_bootstrap_components as dbc   # Adds bootstrap components for more web themes and templates
from dash.exceptions import PreventUpdate
from dash import dash_table

# sourced scripts
sys.path.append("src")
# from reader import read_data

# paths and global variables
REQUESETS_PATHNAME_PREFIX = "/"
DATA_DIR = "../../data/gridcerf/"
COMPILED_DIR = os.path.join(DATA_DIR, "compiled")
METADATA_DIR = "../../data/metadata"
OUTDIR = "tmp"

# central and queryable 
tech_pathways_df = pd.read_csv(os.path.join(METADATA_DIR, "tech_pathways_mapped.csv"))
src_meta = pd.read_csv(os.path.join(DATA_DIR, "metadata_ab_edits.csv"))
src_meta_df = src_meta[["plain_language_layer_name", "source_tag_id", "source_data_title"]]


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



# functions

def open_as_raster(TIFPATH):

	with rasterio.open(TIFPATH) as src: 
		array = src.read(1)
		crs = src.crs
		metadata = src.meta
		array_nodata = np.where(array == src.nodata, np.nan, 0)
		array = np.where(array==1, np.nan, array)

	return array


app = dash.Dash(__name__, assets_folder="assets", 
				# Bootstrap stylesheets available on the web: https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/
				# Link to a stylesheet served over a content delivery network (CDN)
				# BOOTSTRAP links to the standard Bootstrap stylesheet
                external_stylesheets=[dbc.themes.BOOTSTRAP], 
                # url_base_pathname=URL_BASE_PATHNAME, # not needed
                requests_pathname_prefix=REQUESETS_PATHNAME_PREFIX,
                meta_tags=[
                		   {"charset": "UTF-8"},
                           {"http-equiv": "X-UA-Compatible", "content": "IE=9"},
                		   {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                           {"name": "description", "content": "Geospatial Raster Input Data for Capacity Expansion Regional Feasibility (GRIDCERF). A high-resolution energy mapper."}
                        ]
					)


app.title = "GRIDCERF | Geospatial Raster Input Data for Capacity Expansion Regional Feasibility"

# -----------------------------------------------
# HTML components.
# -----------------------------------------------

# no Alaska, Hawaii
state_names = ["Alabama", "Arkansas", "American Samoa", "Arizona", "California", 
				"Colorado", "Connecticut", "District ", "of Columbia", "Delaware", "Florida", 
				"Georgia", "Guam", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", 
				"Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", 
				"Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", 
				"North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", 
				"New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", 
				"South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", 
				"Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]


tabs = ["information-tab", "insights-tab", "layers-tab"]

section_headers = ["Overview", "Authors", "Funding"]

title_text = """Geospatial Raster Input Data for Capacity Expansion Regional Feasibility (GRIDCERF)"""

description_text = """A high-resolution energy mapper for exploring the siting viability of renewable 
					 and non-renewable power plants in the United States."""

overview_text = """The United States will likely need new utility-scale generation resources given that the 
				   growth of electricity demand cannot be subsided by energy efficiency initiatives alone. 
				   Climate change, energy system transitions, and socioeconomic shifts are also driving 
				   electricity demand and power plant siting."""
overview_text_cont = """To explore where new power plants can be built, GRIDCERF visualizes location- and technology-specific 
				   data comprised of 264 suitability layers across 56 power plant technologies. The data are fully 
				   compatible with integrated, multi-model approaches, so they can easily be re-ingested into 
				   geospatial modeling software."""

author_text = """GRIDCERF represents the extensive collection of data formatting, processing, and visualization 
				 created by the IM3 Group at the Pacific Northwest National Laboratory."""

funding_text = """This research was funded by the U.S. Department of Energy, Office of Science, as part of 
				  research in MultiSector Dynamics, Earth and Environmental Systems Modeling Program."""

select_headers = ["Select a visualization tool", 
				  "Select a state", 
				  "Select a year", 
				  "Select a technology",
				  "Select a technology sub-type",
				  "Select a Carbon Capture Sequestration (CCS) method",
				  "Select a Cooling Type", 
				  "Select a socioeconomic scenario"]
select_ids = ["map-select",
			  "state-select",
			  "year-select",
			  "tech-select",
			  "subtech-select",
			  "carbon-capture-select",
			  "cooling-type-select"
			  ]


def table_card():

	return html.Div(
			id="table-container",
			className="page",
			children=[dash_table.DataTable(
								id='table',
								row_selectable="multi",
							    data=src_meta_df.to_dict('records'),
							    sort_action='native',
							    filter_action="native",
							    columns=[{"name": i, "id": i} for i in src_meta_df.columns if i != "id"],
							    style_table={'height': '600px', 'width': '1700px', 'overflowY': 'auto'}

							)
					]
				)


def metadata_text_value(group_id, text_id, value_id, text):

	return html.Div(
					id=group_id,
					className="horizonal-text",
					children=[
						html.Div(id=text_id, children=text),
						html.Div(id=value_id, className="metatext")
						]
					)

def metadata_card():

	return html.Div(
					id="meta",
					className="meta-card",
					children=[
						html.Div(id="data_title", className="metatext"),
						metadata_text_value(group_id="meta-tag-text", text_id="tag_text", value_id="tag_id", text="TAG ID"),
						metadata_text_value(group_id="meta-src-type-text", text_id="srctype_text", value_id="source_type", text="SOURCE TYPE"),
						metadata_text_value(group_id="meta-desc-text", text_id="desc_text", value_id="description", text="DESCRIPTION"),
						metadata_text_value(group_id="meta-date-updated-text", text_id="updated_text", value_id="date_updated", text="DATE UPDATED"),
						metadata_text_value(group_id="meta-date-accessed-text", text_id="accessed_text", value_id="date_accessed", text="DATE ACCESSED"),

						metadata_text_value(group_id="meta-methods-text", text_id="methods_text", value_id="methodlogy", text="METHDOLOGY"),
						metadata_text_value(group_id="meta_citation-text", text_id="citation_text", value_id="citation", text="CITATION"),
						metadata_text_value(group_id="meta-link-text", text_id="data_link_text", value_id="data_link", text="DATA LINK"),
						# html.Div(id="tag_id", className="metatext"),
						# html.Div(id="source_type", className="metatext"),
						# html.Div(id="description", className="metatext"),
						# html.Div(id="date_updated", className="metatext"),
						# html.Div(id="date_accessed", className="metatext"),
						# html.Div(id="methodlogy", className="metatext"),
						# html.Div(id="citation", className="metatext"), # button
						# html.Div(id="data_link", className="metatext"), # button
					]
		)



def tabs_card():

    information_tab = dcc.Tab(label="Information",
		                         id=tabs[0],
		                         value=tabs[0],
		                         selected_className="active-tab",
		                         children=[
		                                   # html.Hr(className="tab-hr"),
		                                   html.Div(id='intro', 
                                                            children=[html.P(title_text, id='title', className="title-text"),
                                                                      html.P(description_text, id='description-text', className="page-text"), 
                                                                      html.P(section_headers[0], id='header0', className="header-text"),
                                                                      html.Hr(className="hr"),
                                                                      html.P(overview_text, id='overview-text', className="page-text"),
                                                                      html.P(overview_text_cont, id='overview-text-cont', className="page-text"),
                                                                      html.P(section_headers[1], id='header1', className="header-text"),
                                                                      html.Hr(className="hr"),
                                                                      html.P(author_text, id='author-text', className="page-text"), 
                                                                      html.P(section_headers[2], id='header2', className="header-text"),
                                                                      html.Hr(className="hr"),
                                                                      html.P(funding_text, id='funding-text', className="page-text"),
                                                                      # html.Label([html.P("Download the contributing", id="shorttext1"),
                                                                      #               html.A('papers', href='https://gdr.openei.org/submissions/1473', id='hyperlink1'),
                                                                      #               html.P("and", id="shorttext2"),
                                                                      #               html.A('code', href='https://github.com/pnnl/GeoCLUSTER', id='hyperlink2'),
                                                                      #               html.P(".", id="shorttext3"),
                                                                      #               ], id='ab-note4')
                                                    ]),
		                                   html.Button("Get Started", id="launch-btn", className="button"),
		                                   ]
	                                   )


    insights_tab = dcc.Tab(label="Insights",
                         id=tabs[1],
                         value=tabs[1],
                         selected_className="active-tab",
                         children=[

                         			# need to create a tree-like structure and/or datatable with cascading logic
                         			html.Br(),

                         			html.P(select_headers[0], id='select-header0', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="map-select",
                                        className="dropdown-select",
                                        options=["Plotly-imshow", "Plotly-datashader and RAPIDS", "Leaflet and TiTiler"],
                                        value="Plotly-imshow",
                                        clearable=False,
                                        searchable=False,
                                        multi=False
                                    ),

                                    html.P(select_headers[1], id='select-header1', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="state-select",
                                        className="dropdown-select",
                                        options=state_names,
                                        value=state_names[0],
                                        clearable=False,
                                        searchable=False,
                                        multi=False
                                    ),

									# make year a slider from 2025 - 2100 with 5 year increments
									# for the population
									
                                    # html.P(select_headers[2], id='select-header2', className="dropdown-header-text"),
									# dcc.Dropdown(
                                    #     id="year-select",
                                    #     className="dropdown-select",
                                    #     options=["2024"],
                                    #     value="2024",
                                    #     clearable=False,
                                    #     searchable=False,
                                    #     multi=True
                                    # ),

                                    html.P(select_headers[3], id='select-header3', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="tech-select",
                                        className="dropdown-select",
                                        options=["Biomass", "Coal", "Gas", "Nuclear", "Refined Liquids", "Solar", "Wind"],
                                        value="Biomass",
                                        clearable=False,
                                        searchable=False,
                                        multi=True
                                    ),

                                    html.P(select_headers[4], id='select-header4', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="subtech-select",
                                        className="dropdown-select",
                                        options=["Conventional", "Integrated Gasification Combined Cycle (IGCC)", "CC", "Gen3", "CT", "CSP", "PV", "Onshore"],
                                        value="Conventional",
                                        clearable=False,
                                        searchable=False,
                                        multi=True
                                    ),

                                    html.P(select_headers[5], id='select-header5', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="carbon-capture-select",
                                        className="dropdown-select",
                                        options=["CCS", "No-CCS"],
                                        value="CCS",
                                        clearable=False,
                                        searchable=False,
                                        multi=True
                                    ),

                                    html.P(select_headers[6], id='select-header6', className="dropdown-header-text"),
									dcc.Dropdown(
                                        id="cooling-type-select",
                                        className="dropdown-select",
                                        options=['Dry', 'Once-through', 'Recirculating','Recirculating-Seawater',
                                        		 'Pond', 'Centralized Enhanced Dry-Hybrid', 'Centralized Enhanced Recirculating'],
                                        value="Dry",
                                        clearable=False,
                                        searchable=False,
                                        multi=True
                                    ),
                         ]
                         )

    layers_tab = dcc.Tab(label="Layers",
						   id=tabs[2],
						   value=tabs[2],
						   selected_className="active-tab",
						   children=[
						   		html.Br(),
							    table_card(),
							    metadata_card()
						   ]
						   )

    tabnav = dcc.Tabs(id="tabnav", 
                    value=tabs[1], 
                    children=[information_tab,
                              insights_tab,
                              layers_tab
                              ])

    return tabnav



def banner_card():

	"""Builds the banner at the top of the page containing app name and logos. """

	return html.Header( # html.Header
			id="banner",
			className="bannerbar",
			children=[
				html.A(
	 				href="https://zenodo.org/records/6601790",
	 				target="_blank",
	 				children=[
	 						  html.Div(id="name-logo-container",
	 						  		children=[
	 						  				  html.H1("GRIDCERF", id="app-name"),
	 						  				  html.Img(id="app-logo", className="svg", 
	 						  				  		   src=app.get_asset_url("icons/logos_icons/model_kaleidoscope_world.svg")),
	 						  				  ]
	 						  			),
	 						  ]
	 				),
				html.A(
	 				href="https://www.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.Img(id="lab-logo", className="logo", alt="lab logo",
	 						  		   src=app.get_asset_url("icons/logos_icons/pnnl_abbreviated_logo.png")),
	 						  ]
	 					),

				html.A(
	 				href="https://im3.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.Img(id="group-logo", className="logo", alt="group logo",
	 						  		   src=app.get_asset_url("icons/logos_icons/IM3_final.png")),
	 						  ]
	 					),

			],
		)

def footer_card():

	"""Builds the banner at the top of the page containing app name and logos. """

	return html.Footer( # html.Header
			id="footer",
			className="footerbar",
			children=[
				html.A(
	 				href="https://www.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.P("For informational purposes only.", id="disclaimer"),
	 						  ]
	 					),

				html.A(
	 				href="https://im3.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.Img(id="dot1", className="dot", alt="dot",
	 						  		   src=app.get_asset_url("icons/nav_icons/dot.svg")),
	 						  ]
	 					),

				html.A(
	 				href="https://www.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.P("Privacy Policy", id="privacy"),
	 						  ]
	 					),

				html.A(
	 				href="https://im3.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.Img(id="dot2", className="dot", alt="dot",
	 						  		   src=app.get_asset_url("icons/nav_icons/dot.svg")),
	 						  ]
	 					),

				html.A(
	 				href="https://www.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.P("Terms & conditions", id="terms"),
	 						  ]
	 					),

				html.A(
	 				href="https://im3.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.Img(id="dot3", className="dot", alt="dot",
	 						  		   src=app.get_asset_url("icons/nav_icons/dot.svg")),
	 						  ]
	 					),

				html.A(
	 				href="https://www.pnnl.gov/",
	 				target="_blank",
	 				children=[
	 						  html.P("Enabled and funded by the Office of Science", id="funder"),
	 						  ]
	 					),

			],
		)


def map():

	return html.Div(
					id="map",
					className="map-column",
					children=[
							  dcc.Graph(id="energy-map", config=plotly_config),
							  dl.Map(dl.TileLayer(), center=[56,10], zoom=6, style={'height': '50vh'})

					]
		)


def nav():

	return html.Div(
					id="nav",
					className="nav-column",
					children=[tabs_card(),
					]
		)



def page_card():

	return html.Div(
			id="page-body",
			className="page",
			children=[
					   map(),
				# 	   html.Div(
				# 			id="map",
				# 			className="map-column",
				# 			children=[
				# 					  html.Div(id="energy-map2")
				# 			]
				# ),

					   nav(),
					]
				)

# -----------------------------------------------------------------------------
# Define dash app layout here.
# -----------------------------------------------------------------------------

app.layout = html.Div(
				      id="app-container",
				      children=[
								# dcc.Store(id='results'),
								banner_card(),
								page_card(),
								footer_card(),
						],
					)



# -----------------------------------------------------------------------------
# Define dash app plotting callbacks.
# -----------------------------------------------------------------------------

@app.callback(
    Output(component_id="energy-map", component_property="figure"),
    [
     Input(component_id="map-select", component_property="value"),
     Input(component_id="state-select", component_property="value"),
     # Input(component_id="year-select", component_property="value"),
     Input(component_id="tech-select", component_property="value"),
     Input(component_id="subtech-select", component_property="value"),
     Input(component_id="carbon-capture-select", component_property="value"),
     Input(component_id="cooling-type-select", component_property="value"),

     # Map Tool
     # State
     # Technology
     # Year
     # Socioeconomic scenario
     # Input vs. Compiled 
     # pull from filename
     # subcategories of technology (IGCC, CCS (had carbon capture technology));
     # subselect 
     # e.g., communications perspective: Land Management/Native Habitats
    ],
)

def map(maptool, state, 
			# year, 
			tech, subtech, carboncap, coolingtype):

    # -----------------------------------------------------------------------------
    # Creates and displays map by querying a "database" table of all pathways
    # to their filenames.
    # -----------------------------------------------------------------------------

	if isinstance(tech, str):
		tech = [tech]
	if isinstance(subtech, str):
		subtech = [subtech]
	if isinstance(carboncap, str):
		carboncap = [carboncap]
	if isinstance(coolingtype, str):
		coolingtype = [coolingtype]

	print(" --------------------------------------------------------------- ")
	query_df = tech_pathways_df.query("technology in @tech and \
									   subtype in @subtech and \
									   is_carbon_capture_sequestration in @carboncap and \
									   cooling_type in @coolingtype")
	print(tech, subtech, carboncap, coolingtype)
	print(query_df)
	fnames = query_df["fname"].unique()
	for fname in fnames:
		print(fname)
		TIFPATH = os.path.join(COMPILED_DIR, fname)
		array = open_as_raster(TIFPATH=TIFPATH)

		# *** files need to put into one dataframe that can be acessed by the map tool
		# otherwise will need to find a way to append continuously

	# TIFPATH = os.path.join(COMPILED_DIR, "gridcerf_biomass_conventional_ccs_dry.tif")


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

	data_row= active_cell['row']
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



# -----------------------------------------------------------------------------
# App runs here. Define configurations, proxies, etc.
# -----------------------------------------------------------------------------

server = app.server 
# from app import server as application # in the wsgi.py file -- this targets the Flask server of Dash app


if __name__ == '__main__':
	app.run_server(port=8060, debug=True) 









	# query_df = tech_pathways_df[ (tech_pathways_df["technology"] == tech) & \
	# 					  (tech_pathways_df["subtype"] == subtech) & \
	# 					  (tech_pathways_df["is_carbon_capture_sequestration"] == carboncap) & \
	# 					  (tech_pathways_df["cooling_type"] == coolingtype)
	# 		]
