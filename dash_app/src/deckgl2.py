#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import dash_deck
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import numpy as np
from dash import html
from .deck_utilities import *

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

ICON_MAPPING = { "black_square": 
                { 
                # "url": "/assets/icons/map_icons/black_square.svg",
                 "width": 242, "height": 242, "anchorX": 121, "anchorY": 121 } 
                 }

LAND_NORTHAMERICA = gpd.read_file("dash_app/data/static_layer_data/land.geojson")
# OCEANS = gpd.read_file("data/static_layer_data/oceans.geojson")
STATES = gpd.read_file("dash_app/data/static_layer_data/states.geojson")
TRANSMISSION_LINES = gpd.read_file("dash_app/data/static_layer_data/transmission_lines.geojson")

def plot_static_layers(styling_dict):

    # ------------------------------------------------
    # DeckGL Static Layers (i.e., Basemap)
    # ------------------------------------------------

    hard_grey = [60, 60, 60]
    black = [0, 0, 0]

    land_layer = pdk.Layer(
                "GeoJsonLayer",
                id="land-layer",
                data=LAND_NORTHAMERICA,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=False,
                filled=True, 
                pickable=False, # False to remove tooltip over oceans
                auto_highlight=True,
                get_line_color=hard_grey,
                get_fill_color=styling_dict["land"],
                # opacity=0.5,
                # get_position="pos",
            )

    # ocean_layer = pdk.Layer(
    #             "GeoJsonLayer",
    #             id="ocean-layer",
    #             data=OCEANS,
    #             coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
    #             stroked=False,
    #             filled=True,
    #             pickable=False,
    #             auto_highlight=False,
    #             get_line_color=hard_grey,
    #             get_fill_color=styling_dict["ocean"],
    #         )

    states_layer = pdk.Layer(
                "GeoJsonLayer",
                id="states-layer",
                data=STATES,
                coordinate_system=COORDINATE_SYSTEM.CARTESIAN,
                stroked=True,
                filled=True,
                pickable=False,
                auto_highlight=False,
                get_line_color=black,
                get_fill_color=styling_dict["states"],
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
    
    return [land_layer, states_layer, trans_layer]


def plot_map(df_coors_long, fpaths, styling_dict):

    # ------------------------------------------------
    # DeckGL Static Layers
    # ------------------------------------------------
    layers = plot_static_layers(styling_dict=styling_dict)

    # ------------------------------------------------
    # DeckGL Dynamic Feasibility Layer
    # ------------------------------------------------
    df_coors_long["icon"] = "black_square"

    feasibility_layer = pdk.Layer(
                    id="feasibility-layer",
                    type="IconLayer",
                    data=df_coors_long,
                    get_icon="icon",
                    icon_mapping=ICON_MAPPING,
                    get_size=1000,
                    size_units="meters",
                    # get_angle="Angle",
                    get_pixel_offset=[0,1],
                    get_position=["Longitude", "Latitude"],
                    pickable=True,
                    auto_highlight=True,
                    stroked=False,
                    opacity=0.7,
                    # size_scale=1,
                    # icon_atlas="assets/icons/map_icons/black_square.png",
                    icon_atlas="http://127.0.0.1:8060/assets/icons/map_icons/black_square2.svg",
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
                data=orjson.dumps(fast_deck_to_json(deck)).decode("utf-8"),
                # data=deck.to_json(),
                id="deck-gl",
        )
    )
