#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 7 seconds to load the map ... 

import time
import json
import dash_deck
import pydeck as pdk
import geopandas as gpd
import pandas as pd
import numpy as np
from dash import html
import ujson # ultra fast JSON encoder and decoder written in pure C with bindings for Python 3.8+
import orjson

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

LAND_NORTHAMERICA = gpd.read_file("data/static_layer_data/land.geojson")
# OCEANS = gpd.read_file("data/static_layer_data/oceans.geojson")
STATES = gpd.read_file("data/static_layer_data/states.geojson")
TRANSMISSION_LINES = gpd.read_file("data/static_layer_data/transmission_lines.geojson")

from functools import lru_cache

# def styling_dict_to_hashable(styling_dict): 
#     print(styling_dict.items())
#     return frozenset(styling_dict.items())

# @lru_cache(maxsize=32) 
# def cached_plot_static_layers(styling_hashable): 
#     styling_dict = dict(styling_hashable) 
#     hard_grey = [60, 60, 60] 
#     black = [0, 0, 0]
#     print("HERE")

# @lru_cache(maxsize=1) 
# def cached_dynamic_data(): 
#     df = pd.read_csv("data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv") 
#     return style_map_icons2(df)

# @lru_cache(maxsize=32) 
# def plot_static_layers_cached(styling_hashable): 
#     # Convert back to a dictionary 
#     styling_dict = dict(styling_hashable)

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


def plot_map(index, fpaths, styling_dict):

    # Get cached static layers 
    # styling_hashable = styling_dict_to_hashable(styling_dict)
    # layers = plot_static_layers_cached(styling_hashable=styling_hashable)

    start = time.time()
    layers = plot_static_layers(styling_dict=styling_dict)
    end = time.time()
    print("Statics: ", end-start)

    # ------------------------------------------------
    # DeckGL Dynamic Feasibility Layer
    # ------------------------------------------------

    start = time.time()
    df_coors_long = pd.read_csv("data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv") # now instantaneous to read in
    # df_coors_long =  style_map_icons2(df_coors_long=df_coors_long)
    df_coors_long = df_coors_long.drop(columns=['Angle', 'IsFeasible'])
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

    end = time.time()
    print("Dynamics: ", end-start)

    # print(deck.layers)
    # def fast_deck_to_json(deck): 
    #     # Build a simplified dict from the deck configuration. 
    #     # Adjust the keys if necessary to match what dash_deck expects. 
    #     deck_dict = { "initialViewState": deck.initial_view_state, 
    #     "views": deck.views, "layers": [layer.dict for layer in deck.layers], 
    #     "parameters": deck.parameters, "map_style": deck.map_style, 
    #     "map_provider": deck.map_provider, "tooltip": deck.tooltip, } 
        
    #     return orjson.dumps(deck_dict).decode("utf-8")

    # deck.to_json = lambda: fast_deck_to_json(deck)

    # start=time.time()
    # deck_json = deck.to_json() 
    # # end=time.time()
    # with open("deck_config.json", "w") as f: 
    #     f.write(deck_json)
    
    # print("JSON: ", end-start)
    # deck_json_str = deck.to_json()
    # deck_config = deck.to_dict() # Get the deck configuration as a dictionary 
    # deck_json = ujson.dumps(deck_config) # Use ujson for faster serialization

    # print(json.loads(deck.to_json()))

    return html.Div(
            dash_deck.DeckGL(
                # data=deck.to_json,
                data=json.loads(deck.to_json()), # Pass the deck configuration as JSON
                # data=ujson.dumps(deck_json_str), # JSON serialization (convert to bytes) of your deck configuration; this takes 3 seconds 
                id="deck-gl",
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

