#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Define dash app layout.
# -----------------------------------------------------------------------------

# standard libraries
import os
import sys

# data manipulation
import pandas as pd

# web app and interactive graphics libraries 
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc     # Adds bootstrap components for more web themes and templates
# import dash_daq as daq                    # Adds more data acquisition (DAQ) and controls to dash callbacks 
# from dash_svg import Svg, G, Path, Circle # Scalable Vector Graphics (SVG) maker
import dash_leaflet as dl
from dash import dash_table
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle

# MSD-LIVE added imports:
# from msdlive_utils import get_bytes
# from io import BytesIO
from flask import Flask
from flask_compress import Compress

# MSD-LIVE added dataset id that goes to DEV
DATASET_ID = "1ffea-emt93"


# sourced scripts
sys.path.append("src")
from utilities import recur_dictify

# MSD-LIVE added logic to support app running locally and in lambda:
LAMBDA_TASK_ROOT = os.getenv('LAMBDA_TASK_ROOT')
# If 'LAMBDA_TASK_ROOT' is not set, METADATA_DIR will be './metadata'
# If 'LAMBDA_TASK_ROOT' is set, METADATA_DIR will be the absolute path
METADATA_DIR = './metadata' if LAMBDA_TASK_ROOT is None else os.path.join(LAMBDA_TASK_ROOT, "dash_app", "metadata")

# client (browser) paths
REQUESETS_PATHNAME_PREFIX = "/"

# file paths and global variables
# DATA_DIR = "../../data/msdlive-gridcerf"
DATA_DIR = ""
# METADATA_DIR = os.path.join(DATA_DIR, "metadata")
COMPILED_DIR = os.path.join(DATA_DIR, "gridcerf/compiled/compiled_technology_layers")
OUTDIR = "tmp"

# central and queryable 
tech_pathways_df = pd.read_csv(os.path.join(METADATA_DIR, "msdlive_tech_paths.csv")) # tech_pathways_mapped.csv
src_meta = pd.read_csv(os.path.join(METADATA_DIR, "metadata_ab_edits.csv"))
src_meta_df = src_meta[["plain_language_layer_name", "source_tag_id", "source_data_title"]]

tech_pathways_df = tech_pathways_df.fillna('--')
tech_pathways_df['ui_year'] = tech_pathways_df['ui_year'].astype(str)
pathway = ["ui_tech", "ui_subtype", "ui_feature", "ui_is_ccs", "ui_cooling_type", "ui_capacity_factor"]
tech_pathways_dict = recur_dictify(df=tech_pathways_df[pathway])
all_options = tech_pathways_dict


# -----------------------------------------------------------------------------
# Dash app layout begins here.
# -----------------------------------------------------------------------------

# MSD-LIVE TODO need to wrap in a function to support lambda
def create_app(): #-> Dash:
	server = Flask(__name__)
	Compress(server)


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
	                        ],

					# MSD-LIVE compressing the response via flask-compress, can do both locally and for lambda
					# MSD-LIVE add logic to set serve_locally to support lambda
					# You must set serve_locally=False or the app will not work when deployed remotely			 
					serve_locally = False if LAMBDA_TASK_ROOT is not None else True,
					server=server
						)


	app.title = "GRIDCERF | Geospatial Raster Input Data for Capacity Expansion Regional Feasibility"



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

	# overview_text = """The United States will likely need new utility-scale generation resources because rising
	# 				   electricity demand cannot be met by energy efficiency initiatives alone. 
	# 				   Climate change, energy system transitions, and socioeconomic shifts are also driving 
	# 				   electricity demand and power plant siting."""
	# overview_text_cont = """To explore where new power plants can be built, GRIDCERF geovisualizes technology-specific 
	# 				   data comprised of 264 suitability layers across 56 power plant technologies. The data are fully 
	# 				   compatible with integrated, multi-model approaches, so they can easily be re-ingested into 
	# 				   geospatial modeling software."""

	overview_text = """The United States will likely need new utility-scale generation resources because rising
					   electricity demand cannot be met by energy efficiency initiatives alone. To explore 
					   where new power plants can be built, GRIDCERF geovisualizes technology-specific 
					   data comprised of 264 suitability layers across 56 power plant technologies. The data are fully 
					   compatible with integrated, multi-model approaches, so they can easily be re-ingested into 
					   geospatial modeling software."""

	author_text = """GRIDCERF represents the extensive collection of data formatting, processing, and visualization 
					 created by the IM3 Group.""" # at the Pacific Northwest National Laboratory."""

	funding_text = """This research was funded by the U.S. Department of Energy, Office of Science, as part of 
					  research in MultiSector Dynamics, Earth and Environmental Systems Modeling Program."""

	select_headers = ["Select a visualization tool", 
					  "Select a state", 
					  "Select a year", 
					  "Select a technology",
					  "Select a technology sub-type",
					  "Select a Carbon Capture Sequestration (CCS) method",
					  "Select a Cooling Type", 
					  "Select a Shared Socioeconomic Pathway (SSP)", #  Select a socioeconomic scenario
					  "Select a feature",
					  "Select a Capacity Factor (CF)"

					  ]
	select_ids = ["map-select",
				  "state-select",
				  "year-select",
				  "tech-select",
				  "subtech-select",
				  "carbon-capture-select",
				  "cooling-type-select",
				  "feature-select"
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

	    # information_tab = dcc.Tab(label="Information",
		# 	                         id=tabs[0],
		# 	                         value=tabs[0],
		# 	                         selected_className="active-tab",
		# 	                         children=[
		# 	                                   # html.Hr(className="tab-hr"),
		# 	                                   html.Div(id='intro', 
	    #                                                         children=[html.P(title_text, id='title', className="title-text"),
	    #                                                                   html.P(description_text, id='description-text', className="page-text"), 
	    #                                                                   html.P(section_headers[0], id='header0', className="header-text"),
	    #                                                                   html.Hr(className="hr"),
	    #                                                                   html.P(overview_text, id='overview-text', className="page-text"),
	    #                                                                   html.P(overview_text_cont, id='overview-text-cont', className="page-text"),
	    #                                                                   html.P(section_headers[1], id='header1', className="header-text"),
	    #                                                                   html.Hr(className="hr"),
	    #                                                                   html.P(author_text, id='author-text', className="page-text"), 
	    #                                                                   html.P(section_headers[2], id='header2', className="header-text"),
	    #                                                                   html.Hr(className="hr"),
	    #                                                                   html.P(funding_text, id='funding-text', className="page-text"),
	    #                                                                   # html.Label([html.P("Download the contributing", id="shorttext1"),
	    #                                                                   #               html.A('papers', href='https://gdr.openei.org/submissions/1473', id='hyperlink1'),
	    #                                                                   #               html.P("and", id="shorttext2"),
	    #                                                                   #               html.A('code', href='https://github.com/pnnl/GeoCLUSTER', id='hyperlink2'),
	    #                                                                   #               html.P(".", id="shorttext3"),
	    #                                                                   #               ], id='ab-note4')
	    #                                                 ]),
		# 	                                   # html.Button("Get Started", id="launch-btn", className="button"),
		# 	                                   ]
		#                                    )


	    insights_tab = dcc.Tab(label="Technology Suitability",
	                         id=tabs[1],
	                         value=tabs[1],
	                         selected_className="active-tab",
	                         children=[

	                         			html.Br(),

	                         			html.Div(id="map-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[0], id='select-header0', className="dropdown-header-text"),
													dcc.Dropdown(
				                                        id="map-select",
				                                        className="dropdown-select",
				                                        options=["Plotly-imshow", "Plotly-datashader, holoviews", "Leaflet and TiTiler"],
				                                        value="Leaflet and TiTiler",
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),

	                         					 ]
	                         					 ),
	                         			
	                                    # html.P(select_headers[1], id='select-header1', className="dropdown-header-text"),
										# dcc.Dropdown(
	                                    #     id="state-select",
	                                    #     className="dropdown-select",
	                                    #     options=state_names,
	                                    #     value=state_names[0],
	                                    #     clearable=False,
	                                    #     searchable=False,
	                                    #     multi=False
	                                    # ),

										# can also make year a slider from 2025 - 2100 with 5 year increments, 
										# OR make it an animation
										
										html.Div(id="tech-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[3], id='select-header3', className="dropdown-header-text"),
				                                    dcc.Dropdown(
				                                    	id="tech-select",
				                                    	className="dropdown-select",
				                                    	options=list(all_options.keys()), # where the chain starts **
				                                    	value="Biomass",
				                                    	clearable=False,
				                                    	searchable=False,
				                                    	multi=False
				                                    	),
	                         					 ]
	                         					 ),

										html.Div(id="year-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[2], id='select-header2', className="dropdown-header-text"),
													dcc.Dropdown(
				                                        id="year-select",
				                                        className="dropdown-select",
				                                        options=list(range(2025, 2105, 5)),
				                                        value=2025,
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),

	                         					 ]
	                         					 ),
	                                    
	                                    html.Div(id="ssp-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[7], id='select-header7', className="dropdown-header-text"),
													dcc.Dropdown(
				                                        id="ssp-select",
				                                        className="dropdown-select",
				                                        options=tech_pathways_df["ui_ssp"].unique(), 
				                                        value=list(tech_pathways_df["ui_ssp"].unique())[0],
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),
	                         					 ]
	                         					 ),

	                                    html.Div(id="subtech-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[4], id='select-header4', className="dropdown-header-text"),
				                                    dcc.Dropdown(
				                                        id="subtech-select",
				                                        className="dropdown-select",
				                                        # options=tech_pathways_df["subtype"].dropna().unique(), # NOT THE SAME 
				                                        # options=["Conventional", "Integrated Gasification Combined Cycle (IGCC)", "CC", "Gen3", "CT", "CSP", "PV", "Onshore"],
				                                        # value="Conventional",
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),
			                 					 ]
			                 					 ),
	                                    
	                                    html.Div(id="feature-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[8], id='select-header8', className="dropdown-header-text"),
				                                    dcc.Dropdown(
				                                        id="feature-select",
				                                        className="dropdown-select",
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),
	                         					 ]
	                         					 ),

	                                    html.Div(id="carbon-capture-select-container",
	                         					 className="select-container",
	                         					 children=[
			                     					html.P(select_headers[5], id='select-header5', className="dropdown-header-text"),
					                                dcc.Dropdown(
					                                    id="carbon-capture-select",
					                                    className="dropdown-select",
					                                    # options=["CCS", "No-CCS"],
					                                    # value="CCS",
					                                    clearable=False,
					                                    searchable=False,
					                                    multi=False
					                                ),
	                         					 ]
	                         					 ),

	                                    html.Div(id="cooling-type-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[6], id='select-header6', className="dropdown-header-text"),
				                                    dcc.Dropdown(
				                                        id="cooling-type-select",
				                                        className="dropdown-select",
				                                        # options=['Dry', 'Once-through', 'Recirculating','Recirculating-Seawater',
				                                        # 		 'Pond', 'Centralized Enhanced Dry-Hybrid', 'Centralized Enhanced Recirculating'],
				                                        # value="Dry",
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),
	                         					 ]
	                         					 ),
	                                    
	                                    html.Div(id="capacity-factor-select-container",
	                         					 className="select-container",
	                         					 children=[
		                         					html.P(select_headers[9], id='select-header9', className="dropdown-header-text"),
				                                    dcc.Dropdown(
				                                        id="capacity-factor-select",
				                                        className="dropdown-select",
				                                        clearable=False,
				                                        searchable=False,
				                                        multi=False
				                                    ),
	                         					 ]
	                         					 ),
	                                    
	                         ]
	                         )

	    layers_tab = dcc.Tab(label="Layer Catalogue",
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
	                    children=[#information_tab,
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
					# html.A(
		 			# 	href="https://www.pnnl.gov/",
		 			# 	target="_blank",
		 			# 	children=[
		 			# 			  html.Img(id="lab-logo", className="logo", alt="lab logo",
		 			# 			  		   src=app.get_asset_url("icons/logos_icons/pnnl_abbreviated_logo.png")),
		 			# 			  ]
		 			# 		),

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
								  # dcc.Graph(id="energy-map", config=plotly_config),
								  # dl.Map(dl.TileLayer(), center=[56,10], zoom=6, style={'height': '50vh'})

						]
			)


	def about():

		return html.Div(
						id="about",
						className="about-column",
						children=[

						html.Div(id='intro', 
	                            children=[html.P(title_text, id='title', className="title-text"),
	                                      html.P(description_text, id='description-text', className="page-text"), 
	                                      html.P(section_headers[0], id='header0', className="header-text"),
	                                      html.Hr(className="hr"),
	                                      html.P(overview_text, id='overview-text', className="page-text"),
	                                      # html.P(overview_text_cont, id='overview-text-cont', className="page-text"),
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


						# html.Div(
						#     [
						#         html.H2("Sidebar", className="display-4"),
						#         html.Hr(),
						#         html.P(
						#             "A simple sidebar layout with navigation links", className="lead"
						#         ),
						#     ])

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

					# html.Div([
					#     PanelGroup(
					#         id='panel-group',
					#         children=[
					#             Panel(
					#                 id='panel-1',
					#                 children=[
					#                     about(),
					#                 ],
					#             ),
					#             PanelResizeHandle(
					#             	html.Div(
					#             		style={"backgroundColor": "grey", "height": "100%", "width": "5px"})
					#             	),
					#             Panel(
					#                 id='panel-2',
					#                 children=[
					#                     map()
					#                 ],
					#                 # style={"backgroundColor": "black", "color": "white"}
					#             ),
					#             PanelResizeHandle(
					#             	html.Div(
					#             		style={"backgroundColor": "grey", "height": "100%", "width": "5px"})
					#             	),
					#             Panel(
					#                 id='panel-3',
					#                 children=[
					#                     nav()
					#                 ],
					#                 # style={"backgroundColor": "black", "color": "white"}
					#             )
					#         ], direction='horizontal'
					#     )
					# ], style={"height": "100vh"})



						   about(),
						   map(),
						   nav(),
						]
					)


	app.layout = html.Div(
					      id="app-container",
					      children=[
									# dcc.Store(id='results'),
									banner_card(),
									page_card(),
									footer_card(),
							],
						)

	return app

app = create_app()