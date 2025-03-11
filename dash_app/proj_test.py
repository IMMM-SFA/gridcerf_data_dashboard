#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import geopandas as gpd
import pydeck as pdk
import dash
from dash import html
import dash_deck
from pyproj import Transformer
import time

import rioxarray
import pandas as pd
import numpy as np

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

start = time.time()

def style_map_icons(df_coors_long):

    icon_data = {
        "url": "/assets/icons/map_icons/black_square.svg",
        "width": 242,
        "height": 242,
        "anchorY": 121, # set to 0 if want to position it at the bottom center of the icon
        "anchorX": 121, # center of X
    }

    df_coors_long["icon_data"] = np.where(df_coors_long.index >= 0, icon_data, None)
    
    return df_coors_long 

# ------------------------------------------------
# DeckGL Static Layers (i.e., Basemap)
# ------------------------------------------------

LAND_NORTHAMERICA = gpd.read_file("data/static_layer_data/land.geojson")
OCEANS = gpd.read_file("data/static_layer_data/oceans.geojson")
STATES = gpd.read_file("data/static_layer_data/states.geojson")
TRANSMISSION_LINES = gpd.read_file("data/static_layer_data/transmission_lines.geojson")

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

mid = time.time()
print(f"{mid - start} seconds for static layer making")

# ------------------------------------------------
# DeckGL Dynamic Feasibility Layer
# ------------------------------------------------

df_coors_long = pd.read_csv("data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv") # now instantaneous to read in
df_coors_long =  style_map_icons(df_coors_long=df_coors_long)

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

deck = pdk.Deck(
    initial_view_state=view_state,
    views=[view], 
    layers=[ocean_layer, land_layer, states_layer, trans_layer, feasibility_layer],
    parameters={"cull": False}, # does not work with OrthographicView if set to True
    map_style=None,
    map_provider=None,
    # tooltip={"text": "{name}"}  # config tooltips based on feature properties
)


end = time.time()
print(f"{end - mid} seconds to build the deck\n")

# ------------------------------------------------
# Dash App
# ------------------------------------------------

app = dash.Dash(__name__)

app.layout = html.Div(
    dash_deck.DeckGL(
        data=json.loads(deck.to_json()), # Pass the deck configuration as JSON
        id="deck-gl",
        style={"position": "relative", "width": "100%", "height": "100vh"}
    )
)

plott = time.time()
print(f"{plott - end} seconds to plot the deck")

print(f"TOTOAL:  {plott - start} seconds for everything")

if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 8070))
    app.run_server(port=PORT, debug=True)

    # dcc.Loading from GeoCLUSTER to "fake" new layer making ... that's the best idea I can come up with and will have to do




# --------------------------------------------------------------------------------
""" 
NOTES

By default, pydeck assumes your coordinates are in geographic coordinates.

Thus, when it encounters large meter values from an Albers projection, it 
interprets them as latitude/longitude degrees, which is why you see an 
"invalid latitude" error.

Next steps for non-Web Mercator projection:

Configure a Custom Coordinate System in deck.gl
If you really need to keep your data in Albers projection, 
you'll have to adjust pydeck's coordinate system settings. 
This can involve using a COORDINATE_SYSTEM like COORDINATE_SYSTEM.CARTESIAN 
and handling the transformations manually. Note that this is more 
advanced and often impractical if you're using standard basemaps 
(which are in Web Mercator).

Set the Layer’s Coordinate System:
Tell pydeck to treat your data as already “projected” by 
setting the layer’s coordinate system to Cartesian. 
This tells pydeck not to assume the data 
is in geographic coordinates (latitude/longitude).

Use an Appropriate View:
Instead of the default Web Mercator–based view, 
use a view like an OrthographicView so 
that the view state is defined in your 
projected (meter) coordinates rather than lat/lon.

Define a Custom View State:
Because your data is in meters, you need to 
calculate (or decide on) an appropriate 
center and zoom level in those same units.

"""

"""
DEBUGGING NOTES

parameters={"cull": True}

In deck.gl (and thus pydeck), the parameters dictionary 
lets you pass WebGL state settings to the underlying renderer.
 Setting parameters={"cull": True} tells the renderer to 
 enable face culling—that is, it will skip rendering 
 polygons (or faces) that aren’t facing the camera. 
 This can improve performance because fewer fragments 
 are drawn. However, if you need to see both sides of 
 your geometry (for example, if your polygons are meant 
 to be double-sided), you may need to disable culling.

"""

# --------------------------------------------------------------------------------
