#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Define dash app layout.
# -----------------------------------------------------------------------------

# LIBRARIES

## standard libraries
import os
import time

## data manipulation
import pandas as pd
import xarray as xr

## AWS libraries
from flask import Flask
from flask_compress import Compress

## web framework
import dash
from dash import html, dcc, html, callback_context, callback, get_asset_url, ctx, dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import dash_daq as daq
from flask_caching import Cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# SOURCED SCRIPTS
from .src.utilities import recur_dictify
from .definitions import CONNECT_TO_LAMBDA, ZARRPATH, s3, SERVE_LOCALLY, REQUESETS_PATHNAME_PREFIX, METADATA_DIR

from .src.deckgl2 import plot_map

# PATHS
tech_pathways_df = pd.read_csv("dash_app/metadata/msdlive_tech_paths.csv") 
src_meta = pd.read_csv("dash_app/metadata/metadata_ab_edits.csv") ## sourced
src_meta_df = src_meta[["plain_language_layer_name", "source_tag_id", "source_data_title"]]

tech_pathways_df = tech_pathways_df.fillna('--')
tech_pathways_df['ui_year'] = tech_pathways_df['ui_year'].astype(str) ## sourced

pathway = ["ui_tech", "ui_subtype", "ui_feature", "ui_is_ccs", "ui_cooling_type", "ui_capacity_factor"]
tech_pathways_dict = recur_dictify(df=tech_pathways_df[pathway])
all_options = tech_pathways_dict ## sourced

layer_catalogue = pd.read_csv("dash_app/metadata/layer_catalogue.csv")

layer_catalogue.rename(columns={'filename': 'label', 'filepath': 'value'}, inplace=True)
list_of_dicts = layer_catalogue[['label', 'value']].to_dict(orient='records')

# -----------------------------------------------------------------------------
# Dash app layout begins here.
# -----------------------------------------------------------------------------

section_headers = ["Overview", "Download Data",  "Funding"]

title_text = """Geospatial Raster Input Data for Capacity Expansion Regional Feasibility (GRIDCERF), Version 2.0"""

description_text = """This dashboard presents a high-resolution interface for exploring geospatial power plant siting
                     suitability of renewable and non-renewable power plants in the contiguous United States."""

intro_text = dcc.Markdown('''

        The GRIDCERF database offers hundreds of individual technological, socioeconomic, and natural 
        resource constraints as well as dozens of pre-compiled energy generation specific composite 
        suitability layers. Data is provided in a harmonized data format that can be easily ingested 
        by geospatially-enabled modeling software.

        GRIDCERF data can be directly used with the open-source power plant siting model [CERF](https://github.com/IMMM-SFA/cerf) 
        (Capacity Expansion Regional Feasibility) to site renewable and non-renewable power 
        plants at a 1 $\\text{km}^2$ resolution.

        ''', 
        className="page-text",
        link_target="_blank",
        mathjax=True
)

data_text = dcc.Markdown(
    '''
    GRIDCERF data is available for download [here](https://doi.org/10.57931/2281697).
    ''',
    className="page-text",
    link_target="_blank",
)

funding_text = """This research was funded by the U.S. Department of Energy, Office of Science, as part of 
                    research in MultiSector Dynamics, Earth and Environmental Systems Modeling Program."""

tabs = ["", "insights-tab", "layers-tab"]

select_headers = ["Select a visualization tool", 
                    "Select a state", 
                    "Select a year", 
                    "Select a technology type",
                    "Select a technology sub-type",
                    "Carbon Capture Sequestration (CCS)",
                    "Select a thermoelectric cooling type", 
                    "Select a Shared Socioeconomic Pathway (SSP)", #  Select a socioeconomic scenario
                    "Select a feature",
                    "Select a Class" # Capacity Factor (CF)
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


def create_app():
    server = Flask(__name__)
    Compress(server)

    if CONNECT_TO_LAMBDA:

        app = dash.Dash(__name__, assets_folder="assets", 
                        external_stylesheets=[dbc.themes.BOOTSTRAP], 
                        requests_pathname_prefix=REQUESETS_PATHNAME_PREFIX,
                        meta_tags=[
                                   {"charset": "UTF-8"},
                                   {"http-equiv": "X-UA-Compatible", "content": "IE=9"},
                                   {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                                   {"name": "description", "content": "Geospatial Raster Input Data for Capacity Expansion Regional Feasibility (GRIDCERF). A high-resolution energy mapper."}
                                ],
                        serve_locally = SERVE_LOCALLY, # must be False for app deployment on AWS lambda
                        server=server,
                        )

    else:

        app = dash.Dash(__name__, assets_folder="assets",
                    external_stylesheets=[dbc.themes.BOOTSTRAP], 
                    requests_pathname_prefix=REQUESETS_PATHNAME_PREFIX,
                    meta_tags=[
                               {"charset": "UTF-8"},
                               {"http-equiv": "X-UA-Compatible", "content": "IE=9"},
                               {"name": "viewport", "content": "width=device-width, initial-scale=1"},
                               {"name": "description", "content": "Geospatial Raster Input Data for Capacity Expansion Regional Feasibility (GRIDCERF). A high-resolution energy mapper."}
                            ],
                        )
    
    cache.init_app(app.server)
    
    app.title = "GRIDCERF | Geospatial Raster Input Data for Capacity Expansion Regional Feasibility"

    # -----------------------------------------------
    # HTML components.
    # -----------------------------------------------

    def mode_switch():
        
        return daq.ToggleSwitch(
                    id='adjust-mode',
                    className="daq-toggle-switch",
                    value=False,
                    )
    
    def mode_switch2():
        return html.Div([
                    html.Div('button1', id='btn-text', style={'display': 'none'}),
                    # html.Div('button1', id='last-btn-pressed', style={'display': 'none'}),
                    html.Div(id='map-selector',
                             children=[
                                html.Button(
                                    children=[
                                        html.Img(id="sun_preview", src=app.get_asset_url("icons/map_icons/sun2.svg")),
                                    ],
                                    id='button1',
                                    className='button-selected',  # Initially selected
                                    n_clicks=1
                                ),
                        html.Button(
                            children=[
                                # html.Img(id="flat_preview", src=app.get_asset_url("previews/2d_preview.png")),
                                html.Img(id="moon_preview", src=app.get_asset_url("icons/map_icons/moon2.svg")),
                                # html.P('2D Map', className="button-text")
                            ],
                            id='button2',
                            className='button',
                            n_clicks=0
                        )
                    ], 
                    ),
                ])


    def table_card():

        return html.Div(
                id="table-container",
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

    def layer_metadata_card():

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
                        ]
            )



    def tabs_card():

        insights_tab = dcc.Tab(label="Technology Suitability",
                             id=tabs[1],
                             value=tabs[1],
                             selected_className="active-tab",
                             children=[
                                         html.Br(),
                                        html.P("Explore composite siting suitability layers for different technologies:",
                                                className="guidance-text"), 
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

                                        html.Div(id="subtech-select-container",
                                                  className="select-container",
                                                  children=[
                                                     html.P(select_headers[4], id='select-header4', className="dropdown-header-text"),
                                                    dcc.Dropdown(
                                                        id="subtech-select",
                                                        className="dropdown-select",
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
                                        
                             ]
                             )
        
        layers_tab = dcc.Tab(label="Layer Catalogue",
                               id=tabs[2],
                               value=tabs[2],
                               selected_className="active-tab",
                               disabled=True,
                               children=[
                                       html.Br(),
                                    html.P("Explore individual layers in the database", className="guidance-text"), 
                                    html.Br(),
                                    html.Div(id="dropdown-container",
                                             children=[
                                                dcc.Dropdown(
                                                        id='multi-layer-dropdown',
                                                        className="dropdown-select",
                                                        options=list_of_dicts,
                                                        value=[], 
                                                        multi=True,
                                                        searchable=True
                                                    )]
                                            )
                                    # table_card(),
                                    # layer_metadata_card()
                               ]
                               )

        tabnav = dcc.Tabs(id="tabnav", 
                        value=tabs[1], 
                        children=[insights_tab,
                                  layers_tab
                                  ])

        return tabnav



    def header_card():

        """Builds the banner at the top of the page containing app name and logos. """

        return html.Header(
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
                                                  # KEEP
                                                     # html.Img(id="app-logo", className="svg", 
                                                     #		   src=app.get_asset_url("icons/logos_icons/model_kaleidoscope_world.svg")),
                                                     ]
                                               ),
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

    def map_selector():
        return html.Div([
                    html.Div('button1', id='last-btn-pressed', style={'display': 'none'}),
                    html.Div(id='map-selector',
                             children=[
                                html.Button(
                                    children=[
                                        html.Img(id="globe_preview", src=app.get_asset_url("icons/map_icons/globe-thicker.svg")),
                                    ],
                                    id='button1',
                                    className='button-selected',  # Initially selected
                                    n_clicks=1
                                ),
                        html.Button(
                            children=[
                                # html.Img(id="flat_preview", src=app.get_asset_url("previews/2d_preview.png")),
                                html.Img(id="flat_preview", src=app.get_asset_url("icons/map_icons/map-final.svg")),
                                # html.P('2D Map', className="button-text")
                            ],
                            id='button2',
                            className='button',
                            n_clicks=0
                        )
                    ], 
                    ),
                ])

    def map():

        return html.Div(
                        children=[
                            dcc.Loading(
                                    parent_className="loader-wrapper",
                                    id="loading",
                                    type="circle",
                                    # style={"backgroundColor": "transparent"},
                                    children=[
                                        html.Div(
                                        id="map",
                                        className="map-column",
                                        children=[
                                            ]
                                        )
                                    ]
                            ),
                            about(),
                            nav(),
                            # mode_switch(),
                            # map_selector(),
                            mode_switch2(),
                            html.Div(id="layer-container",
                                     children=[
                                            # html.Button("X", id="close-layer-button", className="close-btn"),
                                            html.P("Layers", id='header0', className="header-text"),
                                            html.Hr(className="hr2"),
                                            # html.Div(id="basemap-layer",
                                            # 		children=[
                                            # 			html.P("Basemap"),
                                            # 		]
                                            # ),
                                            html.Div(id="layer-funcs-container", # TODO: Fix duplicate
                                                    children=[
                                                        html.Div("Technology Layer", className="layer-concept"),
                                                        html.Div(id="layer-funcs", className="layer-funcs",
                                                                children=[
                                                                    # html.Button(
                                                                    # 	id="opacity-btn",
                                                                    # 	children=[
                                                                    # 		html.Img(id="opacity", src=app.get_asset_url("icons/map_icons/opacity.svg")),
                                                                    # 	],
                                                                    # 	# className='button-selected',  # Initially selected
                                                                    # 	n_clicks=1
                                                                    # ),
                                                                    # html.Button(
                                                                    # 	id="visibility-btn",
                                                                    # 	children=[
                                                                    # 		html.Img(id="visibility", src=app.get_asset_url("icons/map_icons/eye-open.svg")),
                                                                    # 	],
                                                                    # 	# className='button-selected',  # Initially selected
                                                                    # 	n_clicks=2
                                                                    # ),
                                                                ])
                                                        
                                                    ]
                                            ),
                                            html.Div(className="layer-name-container",
                                                    children=[
                                                        html.Div(id="hex-box1", className="hex-box"),
                                                        html.Div("SUITABLE SITING AREA", className="layer-name"),
                                                        # html.Div("FEASIBILITY", id="layer-name", className="layer-name"),
                                                        # Suitable Siting Area
                                                    ]
                                            ),
                                            html.Hr(className="hr3"),
                                            html.Div(id="layer-funcs-container2",
                                                    children=[
                                                        html.Div("Electricity Grid", className="layer-concept"),
                                                        
                                                    ]
                                            ),
                                            html.Div(className="layer-name-container",
                                                    children=[
                                                        html.Div(id="hex-box2", className="hex-box"),
                                                        html.Div("TRANSMISSION LINES", className="layer-name"),
                                                        # html.Div("FEASIBILITY", id="layer-name", className="layer-name"),
                                                        # Suitable Siting Area
                                                    ]
                                            ),
                                            html.Hr(className="hr3"),
                                            # dcc.Checklist(
                                            # 	id='layer-selector',
                                            # 	options=[
                                            # 		{'label': 'Basemap Ocean', 'value': 'base-map-ocean'}, # AB: need to predfine the database 
                                            # 		{'label': 'Basemap Land', 'value': 'base-map'}, 
                                            # 		{'label': 'Feasibility Layer', 'value': 'feasibility-layer'}, 
                                            # 	],
                                            # 	value=["base-map-ocean", "base-map", "feasibility-layer"],  # Default selected layers
                                            # 	inline=True,
                                            # 	# style={'display': 'none'}
                                            # ),
                            ])
                        ]
        )

    def about():

        return html.Div(
                        id="expandable-box",
                        className="about",
                        children=[
                            html.Button("X", id="close-button", className="close-btn"),
                            # intro
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

                        #    about(),
                           map(),
                        #    nav(),
                        ]
                    )


    app.layout = html.Div(
                          id="app-container",
                          children=[
                                    header_card(),
                                    page_card(),
                                    # footer_card(),
                                    dcc.Store(id="visibility-click-store", data=0), 
                            ],
                        )

    return app


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
		 						  	 src=get_asset_url("icons/nav_icons/info.svg"),
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
