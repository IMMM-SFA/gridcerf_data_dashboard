#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Define dash app layout.
# -----------------------------------------------------------------------------

# LIBRARIES

## standard libraries
import os
import sys

## data manipulation
import pandas as pd

## AWS libraries
from flask import Flask
from flask_compress import Compress

## web framework
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash import dash_table
from flask_caching import Cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

# SOURCED SCRIPTS
from src.utilities import recur_dictify
from definitions import LAMBDA_TASK_ROOT, CONNECT_TO_LAMBDA, SERVE_LOCALLY, REQUESETS_PATHNAME_PREFIX, METADATA_DIR

print("Layout file")

# PATHS
tech_pathways_df = pd.read_csv(os.path.join(METADATA_DIR, "msdlive_tech_paths.csv")) 
src_meta = pd.read_csv(os.path.join(METADATA_DIR, "metadata_ab_edits.csv")) ## sourced
src_meta_df = src_meta[["plain_language_layer_name", "source_tag_id", "source_data_title"]]

tech_pathways_df = tech_pathways_df.fillna('--')
tech_pathways_df['ui_year'] = tech_pathways_df['ui_year'].astype(str) ## sourced

pathway = ["ui_tech", "ui_subtype", "ui_feature", "ui_is_ccs", "ui_cooling_type", "ui_capacity_factor"]
tech_pathways_dict = recur_dictify(df=tech_pathways_df[pathway])
all_options = tech_pathways_dict ## sourced

layer_catalogue = pd.read_csv(os.path.join(METADATA_DIR, "layer_catalogue.csv"))

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
