#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adapted from: https://pydeck.gl/gallery/globe_view.html

This demos the experimental Glove View from deck.gl/pydeck by using the GeoJSON
and column layers. The data used contains global plant database and can be found here:
https://github.com/ajduberstein/geo_datasets

WebGL for Performance
WebGL is typically faster for rendering large datasets. Make sure you are leveraging this 
by using efficient layer types, such as ScatterplotLayer or HexagonLayer, which are 
optimized for large datasets.

Ensure your data is in an efficient format (like Parquet or GeoJSON) for faster loading 
and processing. Preprocess your data to reduce its size, if possible
"""
# standard libraries
import os
import json

# visualization, data manipulation, and framework libraries
import dash
from dash import html
import dash_deck
import pydeck
import numpy as np

# SOURCED SCRIPTS
from src.reader import open_as_raster
from layout import cache
from definitions import OUTDIR

@cache.memoize(timeout=7200)  # Cache for 2 hours 
def load_large_data(layer_name, COMPILED_DIR, fpaths, adjust_mode):

    if layer_name == "base-map-ocean":

        OCEANS = json.load(open('data/ne_50m_ocean.geojson', 'r', encoding='utf-8'))

        # #D4DADC and RBG is 212, 218, 220

        if adjust_mode:  # When the switch is "True"
            fill_color = [212, 218, 220] # light grey
        else:
            fill_color = [0, 31, 72] # dark blue
            
        return pydeck.Layer(
                    "GeoJsonLayer",
                    id="base-map-ocean",
                    data=OCEANS,
                    stroked=False,
                    filled=True, 
                    pickable=False, # False to remove tooltip over oceans
                    auto_highlight=True,
                    get_line_color=[60, 60, 60], # [134, 181, 209], [22, 36, 105],
                    get_fill_color=fill_color,                
                    opacity=0.5,                
                )
                

    if layer_name == "base-map":

        LAND = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"

        if adjust_mode:  # When the switch is "True"
            # fill_color = [250, 250, 248] # near white
            return pydeck.Layer(
                        "GeoJsonLayer",
                        id="base-map",
                        data=LAND,
                        stroked=False,
                        filled=True,
                        get_line_color=[60, 60, 60],
                        get_fill_color=[250, 250, 248] # near white
                    )
        else:
            return pydeck.Layer(
                        "GeoJsonLayer",
                        id="base-map",
                        data=LAND,
                        stroked=False,
                        filled=True,
                        get_line_color=[60, 60, 60],
                        get_fill_color=[66, 133, 55], # green [32, 145, 62], [200, 200, 200], [160, 160, 160]
                    )
    
    if layer_name == "feasibility-layer":

        TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
        data_df, array, source_crs, geo_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=True, is_convert_to_png=False)
        
        if adjust_mode:  # When the switch is "True"
            url_path = "/assets/icons/map_icons/im3_blue_square.svg"
        else:
            url_path = "/assets/icons/map_icons/fuchsia_square.svg"

        icon_data = {
            "url": "/assets/icons/map_icons/blue_square.svg", # svg repo
            "width": 242,
            "height": 242,
            "anchorY": 121, # set to 0 if want to position it at the bottom center of the icon
            "anchorX": 121, # center of X
        }

        df_coors_long["icon_data"] = np.where(df_coors_long.index >= 0, icon_data, None)
        df_coors_long["Angle"] = np.where(df_coors_long["LongitudeProj"] <= -121, 15,
                     np.where(df_coors_long["LongitudeProj"].between(-121, -118), 13,
                     np.where(df_coors_long["LongitudeProj"].between(-118, -112), 10,
                     np.where(df_coors_long["LongitudeProj"].between(-112, -107), 8,
                     np.where(df_coors_long["LongitudeProj"].between(-107, -103), 5,
                     np.where(df_coors_long["LongitudeProj"].between(-103, -100), 2,
                     np.where(df_coors_long["LongitudeProj"].between(-93, -91), -2,
                     np.where(df_coors_long["LongitudeProj"].between(-91, -82), -5,
                     np.where(df_coors_long["LongitudeProj"].between(-82, -76), -10,
                     np.where(df_coors_long["LongitudeProj"] > -76, -15, 0))))))))))

        return pydeck.Layer(
                    id="feasibility-layer",
                    type="IconLayer",
                    data=df_coors_long,
                    get_icon="icon_data",
                    get_size=1150, # or 120 if you want best coverage
                    size_units="meters",
                    # size_scale=1,
                    # iconAtlas: 'path/to/icon-atlas.png', ?
                    # icon_mapping=icon_mapping,
                    width_scale=20,
                    get_width=1000,
                    radius=500,
                    get_radius=500,
                    get_angle="Angle",
                    get_pixel_offset=[0,1],
                    get_position=["LongitudeProj", "LatitudeProj"],
                    pickable=True,
                    auto_highlight=True,
                    stroked=True,
                    transitions={
                            # transition with a duration of 3000ms
                            'get_position': 3000,  # Transition duration in milliseconds
                            'get_size': 3000,
                            # 'radius': 1000
                            # getRadius: {
                            #     duration: 3000,
                            #     easing: d3.easeBackInOut,
                            # },
                        },
                    # update_triggers={
                    #     # 'get_position': ['year'],
                    #     'get_icon': ['IsFeasible']
                    # }
                    # rgb(60, 220, 255)
                )


def plot_deckgl_map(COMPILED_DIR, fpaths, selected_layers, adjust_mode):

    view_state = pydeck.ViewState(latitude=39.8283, longitude=-98.5795, # center U.S.
                                  zoom=2,
                                  # pitch=30, # ?
                                  # bearing=0 # ?
                                  )
    view = pydeck.View(type="_GlobeView", controller=True, width="100%", height="100%") # width=1000, height=700

    deck_layers = []

    for layer in selected_layers:
        layer = load_large_data(layer, COMPILED_DIR, fpaths, adjust_mode)  # Load data, cached if previously loaded
        deck_layers.append(layer)

    r = pydeck.Deck(
        views=[view],
        initial_view_state=view_state,
        layers=deck_layers,
        # map_provider="mapbox", # removed
        parameters={"cull": True},
        # map_style=pydeck.map_styles.SATELLITE,
        # map_style="mapbox://styles/mapbox/light-v9",
        # Note that this must be set for the globe to be opaque
        # tooltip={"text": "{tags}"}
        # does NOT EXIST:
        # animation_config={
        #     'duration': 2000,  # Duration of the animation in milliseconds
        #     'easing': 'linear',  # Animation easing function
        #     'transition': True
        # }
    )

    # TODO: save/download the map feature can be added this way
    # r.to_html(os.path.join(OUTDIR, "icon_layer.html"))

    #######
    # Animate over the years
    # for year in range(2025, 2100):
    #     # Filter data for the current year
    #     year_data = data[data['year'] == year]

    #     # Update layer data
    #     r.update_layer(
    #         layer,
    #         data=year_data
    #     )
    # then connect to mapgl

    """
        Notice that here, we are explicitly convert the r.to_json() into a python dictionary.
        This is needed because the data contains NaN, which can't be parsed by the underlying
        JavaScript JSON parser, but it can be parsed by Python's JSON engine.
    """

    if adjust_mode:
        mapgl = html.Div(
        dash_deck.DeckGL(
            json.loads(r.to_json()),
            id="deck-gl",
            style={"background-color": "white"},
            # tooltip={"text": "{IsFeasible} feasible, {LatitudeProj}, {LongitudeProj}"},
            )
        )
    else:
        mapgl = html.Div(
        dash_deck.DeckGL(
            json.loads(r.to_json()),
            id="deck-gl",
            style={"background-color": "black"},
            # tooltip={"text": "{IsFeasible} feasible, {LatitudeProj}, {LongitudeProj}"},
            )
        )

    return mapgl
