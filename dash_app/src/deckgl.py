#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adapted from: https://pydeck.gl/gallery/globe_view.html

This demos the experimental Glove View from deck.gl/pydeck by using the GeoJSON
and column layers. The data used contains global plant database and can be found here:
https://github.com/ajduberstein/geo_datasets

Notice that here, we are explicitly convert the r.to_json() into a python dictionary.
This is needed because the data contains NaN, which can't be parsed by the underlying
JavaScript JSON parser, but it can be parsed by Python's JSON engine.

"""
import os
import json

import dash
import dash_deck
import dash_html_components as html
import pydeck
import pandas as pd

# sourced scripts
from src.reader import open_as_raster
from definitions import token as mapbox_api_token


COLOR_BREWER_BLUE_SCALE = [
    [240, 249, 232],
    [204, 235, 197],
    [168, 221, 181],
    [123, 204, 196],
    [67, 162, 202],
    [8, 104, 172],
]

def plot_deckgl_map(COMPILED_DIR, fpaths):
        
    COUNTRIES = "https://d2ad6b4ur7yvpq.cloudfront.net/naturalearth-3.3.0/ne_50m_admin_0_scale_rank.geojson"
    # POWER_PLANTS = "https://raw.githubusercontent.com/ajduberstein/geo_datasets/master/global_power_plant_database.csv"
    OCEANS = json.load(open('data/ne_50m_ocean.geojson', 'r', encoding='utf-8'))

    # df = pd.read_csv(POWER_PLANTS)

    # easy to create a left and right orientation to rotate as needed, this can be loose but will be great

    # def is_green(fuel_type):
    #     if fuel_type.lower() in (
    #         "nuclear",
    #         "water",
    #         "wind",
    #         "hydro",
    #         "biomass",
    #         "solar",
    #         "geothermal",
    #     ):
    #         return [10, 230, 120]
    #     return [230, 158, 10]


    # df["color"] = df["primary_fuel"].apply(is_green)

    # view_state = pydeck.ViewState(latitude=51.47, longitude=0.45, zoom=2)
    view_state = pydeck.ViewState(latitude=39.8283, 
                                  longitude=-98.5795, 
                                  zoom=2,
                                  # pitch=30, # ?
                                  # bearing=0 # ?
                                  )


    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, geo_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=True, is_convert_to_png=False)
    
    icon_data = {
    # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
    # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
    "url": "/assets/icons/map_icons/blue_square.svg",
    "width": 242,
    "height": 242,
    "anchorY": 121, # set to 0 if wnat to position it at the bottom center of the icon
    "anchorX": 121, # center of X
    }

    # icon_mapping = {
    #     "myIcon": {
    #         # x: 0,
    #         # y: 0,
    #         # width: 128,
    #         # height: 128,
    #         "anchor": [0.5, 0.5], #// Position the anchor at the bottom center of the icon
    #         # offset: [0, -10]  // Offset the icon by 10 pixels upwards
    #     }
    #     }

    df_coors_long["icon_data"] = None
    for i in df_coors_long.index:
        df_coors_long["icon_data"][i] = icon_data

    layers = []
    # Set height and width variables
    # view = pydeck.View(type="_GlobeView", controller=True, width=1000, height=700)
    view = pydeck.View(type="_GlobeView", controller=True, width="100%", height="100%")

    # print(df_coors_long.columns)

    df_coors_long["Angle"] = 0
    for i in df_coors_long.index:

        # left
        if df_coors_long["LongitudeProj"][i] <= -121:
            df_coors_long["Angle"][i] = 15
        if df_coors_long["LongitudeProj"][i] > -121 and df_coors_long["LongitudeProj"][i] <= -118: 
            df_coors_long["Angle"][i] = 13
        if df_coors_long["LongitudeProj"][i] > -118 and df_coors_long["LongitudeProj"][i] <= -112: 
            df_coors_long["Angle"][i] = 10
        if df_coors_long["LongitudeProj"][i] > -112 and df_coors_long["LongitudeProj"][i] <= -107: 
            df_coors_long["Angle"][i] = 8
        if df_coors_long["LongitudeProj"][i] > -107 and df_coors_long["LongitudeProj"][i] <= -103: 
            df_coors_long["Angle"][i] = 5
        if df_coors_long["LongitudeProj"][i] > -103 and df_coors_long["LongitudeProj"][i] <= -100: 
            df_coors_long["Angle"][i] = 2

        # right
        if df_coors_long["LongitudeProj"][i] > -93 and df_coors_long["LongitudeProj"][i] <= -91: 
            df_coors_long["Angle"][i] = -2
        if df_coors_long["LongitudeProj"][i] > -91 and df_coors_long["LongitudeProj"][i] <= -82: 
            df_coors_long["Angle"][i] = -5
        if df_coors_long["LongitudeProj"][i] > -82 and df_coors_long["LongitudeProj"][i] <= -76: 
            df_coors_long["Angle"][i] = -10
        if df_coors_long["LongitudeProj"][i] > -76:
            df_coors_long["Angle"][i] = -15

    layers = [
        pydeck.Layer(
            "GeoJsonLayer",
            id="base-map-ocean",
            data=OCEANS,
            stroked=False,
            filled=True, 
            pickable=False, #Key difference in this layer as we don't want tooltips when hovering over the ocean
            auto_highlight=True,
            get_line_color=[60, 60, 60],
            # get_fill_color=[134, 181, 209],
            # get_fill_color=[22, 36, 105],
            get_fill_color=[0, 31, 72],                
            opacity=0.5,                
        ),
        pydeck.Layer(
            "GeoJsonLayer",
            id="base-map",
            data=COUNTRIES,
            stroked=False,
            filled=True,
            get_line_color=[60, 60, 60],
            get_fill_color=[66, 133, 55], # green
            # get_fill_color=[32, 145, 62],
            # get_fill_color=[200, 200, 200],
            # get_fill_color=[160, 160, 160]
        ),
        pydeck.Layer(
            type="IconLayer",
            data=df_coors_long,
            get_icon="icon_data",
            get_size=1150, # or 120 if you want best coverage
            size_units="meters", #need to get rid of border 
            # size_scale=1,
            #   iconAtlas: 'path/to/icon-atlas.png', ?
            # icon_mapping=icon_mapping,
            width_scale=20,
            get_width=1000,
            radius=500,
            get_radius=500,
            get_angle="Angle",
            # (The rotating angle of each object, in degrees, default is 0)
            get_pixel_offset=[0,1],
            # get_width=1000,
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
        ),
        # pydeck.Layer(
        # does't work
        #     type="HeatmapLayer",
        #     data=df_coors_long,
        #     get_position=["LongitudeProj", "LatitudeProj"],
        #     aggregation=pydeck.types.String("MEAN"),
        #     pickable=True,
        #     get_weight="IsFeasible",
        #     threshold=1,
        #     color_range=COLOR_BREWER_BLUE_SCALE,
        #     opacity=0.9
        # ),
        # pydeck.Layer(
        #     type="GridCellLayer", # ColumnLayer, HexagonLayer, ScatterplotLayer
        #     id="feasibility-raster",
        #     # offset Disk offset from the position, relative to the radius. By default, the disk is centered at each position.
        #     # angle Disk rotation, counter-clockwise in degrees.
        #     # vertices
        #     data=df_coors_long,
        #     get_elevation="IsFeasible",
        #     elevation_scale=100,
        #     get_position=["LongitudeProj", "LatitudeProj"],
        #     width_scale=20,
        #     get_width=1000,  # Set the width of the column
        #     pickable=True,
        #     stroked=False, # Whether to draw an outline around the disks, Only applies if extruded: false.
        #     auto_highlight=True,
        #     # wireframe=True,
        #     extruded=False,
        #     radius=500,
        #     get_radius=500, # Radius is given in meters
        #     get_fill_color=[180, 0, 200, 140],  # Set an RGBA value for fill
        #     # get_fill_color="color",
        #     opacity=0.5,
        # ),
    ]

    """
    
    3) Try an animation ! 
        A) Need to have a df that has all years in it (need to experiment with this pipeline)

            data = pd.DataFrame({
                'year': years,
                'latitude': latitudes,
                'longitude': longitudes
            })

    4) Figure out layer controller and other controller panels
    5) Verify offset and accuracy! 


    
    """
    
    """ The GridCellLayer can render a grid-based heatmap. 
    It is a variation of the ColumnLayer. It takes 
    the constant width / height of all cells and bottom-left 
    coordinate of each cell. This is the primitive layer 
    rendered by CPUGridLayer after aggregation. 
    Unlike the CPUGridLayer, it renders one column for 
    each data object."""

    r = pydeck.Deck(
        views=[view],
        initial_view_state=view_state,
        layers=layers,
        map_provider="mapbox",
        # map_style=pydeck.map_styles.SATELLITE,
        # map_style="mapbox://styles/mapbox/light-v9",
        # Note that this must be set for the globe to be opaque
        parameters={"cull": True},
        # tooltip={"text": "{tags}"}

        # does NOT EXIST:
        # animation_config={
        #     'duration': 2000,  # Duration of the animation in milliseconds
        #     'easing': 'linear',  # Animation easing function
        #     'transition': True
        # }
    )

    # r.to_html("icon_layer.html")

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

    # how does it connect to the below??

    mapgl = html.Div(
        dash_deck.DeckGL(
            json.loads(r.to_json()),
            id="deck-gl",
            style={"background-color": "black"},
            tooltip={"text": "{IsFeasible} feasible, {LatitudeProj}, {LongitudeProj}"},
        )
    )

    fig_div = html.Div(id="plotly-map", 
                        children=[mapgl]
                        ) # does not work 

    return mapgl

    # app = dash.Dash(__name__)

    # app.layout = html.Div(
    #     dash_deck.DeckGL(
    #         json.loads(r.to_json()),
    #         id="deck-gl",
    #         style={"background-color": "black"},
    #         tooltip={"text": "{name}, {primary_fuel} plant, {country}"},
    #     )
    # )


    # if __name__ == "__main__":
    #     app.run_server(debug=True)