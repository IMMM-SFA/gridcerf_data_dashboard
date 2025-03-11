#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 7 seconds to load the map ... 

import json
import dash_deck
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import numpy as np
from dash import html

try:
    from pydeck.core.constants import COORDINATE_SYSTEM
    from pydeck import OrthographicView
    from pydeck.data_utils import compute_matrix
except ImportError:
    # Fallback definition: deck.gl uses the following convention:
    class COORDINATE_SYSTEM:
        DEFAULT = -1
        LNGLAT = 1
        METER_OFFSETS = 2
        LNGLAT_OFFSETS = 3
        CARTESIAN = 0

LAND_NORTHAMERICA = gpd.read_file("data/static_layer_data/land.geojson")
OCEANS = gpd.read_file("data/static_layer_data/oceans.geojson")
STATES = gpd.read_file("data/static_layer_data/states.geojson")
TRANSMISSION_LINES = gpd.read_file("data/static_layer_data/transmission_lines.geojson")


def plot_static_layers():

    # ------------------------------------------------
    # DeckGL Static Layers (i.e., Basemap)
    # ------------------------------------------------

    land_layer = pdk.Layer(
                "GeoJsonLayer",
                id="land-layer",
                data=LAND_NORTHAMERICA,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=False,
                filled=True, 
                pickable=False, # False to remove tooltip over oceans
                auto_highlight=True,
                get_line_color=[60, 60, 60],
                get_fill_color=[48, 105, 59], #  # 66, 133, 55
                # opacity=0.5,
                # get_position="pos",
            )

    ocean_layer = pdk.Layer(
                "GeoJsonLayer",
                id="ocean-layer",
                data=OCEANS,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=False,
                filled=True,
                pickable=False,
                auto_highlight=False,
                get_line_color=[60, 60, 60],
                get_fill_color=[0, 31, 72], # [0, 31, 72],      
            )

    states_layer = pdk.Layer(
                "GeoJsonLayer",
                id="states-layer",
                data=STATES,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=True,
                filled=True,
                pickable=False,
                auto_highlight=False,
                get_line_color=[0, 0, 0],
                get_fill_color=[66, 133, 55],
                get_line_width=1000,
                # get_fill_color=[0, 0, 0, 0] # [66, 133, 55],
            )

    trans_layer = pdk.Layer(
                "GeoJsonLayer",
                id="transmission-layer",
                data=TRANSMISSION_LINES,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=False,
                filled=False,
                pickable=False,
                auto_highlight=False,
                get_line_color=[255, 0, 225], # [255, 200, 0], # 255, 200, 0
                get_line_width=1000,
            )
    
    return [ocean_layer, land_layer, states_layer, trans_layer]


def plot_map(index, fpaths):

    layers = plot_static_layers()

    # ------------------------------------------------
    # DeckGL Dynamic Feasibility Layer
    # ------------------------------------------------

    df_coors_long = pd.read_csv("data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv") # now instantaneous to read in
    df_coors_long =  style_map_icons2(df_coors_long=df_coors_long)

    feasibility_layer = pdk.Layer(
                    id="feasibility-layer",
                    type="IconLayer",
                    data=df_coors_long,
                    get_icon="icon_data",
                    get_size=1145,
                    size_units="meters",
                    get_angle="Angle",
                    get_pixel_offset=[0,1],
                    get_position=["Longitude", "Latitude"],
                    pickable=True,
                    auto_highlight=True,
                    stroked=False,
                    opacity=0.7,
                    # size_scale=1,
                    # iconAtlas: 'path/to/icon-atlas.png', ?
                    # icon_mapping=icon_mapping,
                    # width_scale=20,
                    # get_width=1000,
                    # radius=500,
                )

    view_state = pdk.ViewState(
                            target=[-100, -40, 0], # define the exact point (x, y, z) around which the camera rotates
                            zoom=-12, # Arguments like y=, x=, latitude=, longitude=, pitch=, bearing= do not work for OrthographicView
                            )

    view = pdk.View(
        type="OrthographicView", # pydeck defaults to using a MapView
        controller={"minZoom": -12.5, "maxZoom": 0, # "maxBounds": bbox, # bbox does not work for OrthographicView
                    "dragPan": True, "scrollZoom": True,
                    "dragRotate": True, "doubleClickZoom": True,
                    "touchZoom": True, "touchRotate": False
                    }
    )

    layers.append(feasibility_layer)

    deck = pdk.Deck(
        initial_view_state=view_state,
        views=[view], 
        layers=layers,
        parameters={"cull": False}, # does not work with OrthographicView if set to True
        map_style=None,
        map_provider=None,
        # tooltip={"text": "{name}"}  # config tooltips based on feature properties
    )


    return html.Div(
            dash_deck.DeckGL(
                data=json.loads(deck.to_json()), # Pass the deck configuration as JSON
                id="deck-gl",
                style={"position": "relative", "width": "100%", "height": "100vh"}
        )
    )




def style_map_icons2(df_coors_long):

    icon_data = {
        "url": "/assets/icons/map_icons/black_square.svg",
        "width": 242,
        "height": 242,
        "anchorY": 121, # set to 0 if want to position it at the bottom center of the icon
        "anchorX": 121, # center of X
    }

    df_coors_long["icon_data"] = np.where(df_coors_long.index >= 0, icon_data, None)
    
    return df_coors_long 

