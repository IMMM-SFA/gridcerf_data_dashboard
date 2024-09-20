#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard
import os

# visualization and data manipulation
from dash import html, dcc
import dash_leaflet as dl
import dash_leaflet.express as dlx

# sourced scripts
from src.reader import open_as_raster
from definitions import plotly_config, CMAP_BLACK


def plot_leaflet_map(COMPILED_DIR, fpaths):

    """ 
    Convert Raster to Web-Compatible Format:
        Leaflet does not directly support .TIF files, so you’ll need to convert your .TIF file to a format that Leaflet can display, 
        like PNG or JPEG. You can use a tool like rasterio to handle this conversion.
    
    Create a Web Tile Layer: 
        Convert the raster data into tiles (e.g., using Mapbox or a tile server).
        Set Up Your Dash App:
    
    Create a Dash app with Dash Leaflet to display the map and raster tiles.
    
    """
    USA_CENTER = [39.8283, -98.5795]

    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, geo_crs, df_coors_long, bounds, PNG = open_as_raster(TIFPATH=TIFPATH, is_reproject=False, is_convert_to_png=True)

    # TODO: 
    # see if can change CRS of the basemap (experiment with different basemap options)
    # see if can plot the df_coors_long as an alternative with leaflet where you set the size of the point.
    
    # dlx.dicts_to_geojson(geo_data)

    # ## Map Update 
    # if len(location)>0:
    # 	df_loc = pd.DataFrame({"state_lower":location})
    # 	df_loc = df_loc.groupby('state_lower').size().reset_index(name='doc_count')
    # 	df_loc['state_lower'] = df_loc.state_lower.str.lower()
    # 	df_loc = df_loc.merge(df_location, on='state_lower', how = 'inner')
    # 	geo_data  = df_loc.apply(lambda x: [dict(lat=x.latitude, lon=x.longitude)]*x.doc_count, axis = 1)
    # 	geo_data = reduce(lambda x, y: x + y, geo_data)
    # else: geo_data=[]

    # MAP CONTROLLER (I.E., LEGEND)
    # cmaps = ["Viridis", "Spectral", "Greys"]
    # lbl_map = dict(wspd="Wind speed", temp="Temperature")
    # unit_map = dict(wspd="m/s", temp="°K")
    # srng_map = dict(wspd=[0, 10], temp=[250, 300])
    # param0 = "temp"
    # cmap0 = "Viridis"
    # srng0 = srng_map[param0]

    map_fig = dl.Map(
                        style = 
                            {'height': '700px',
                                    'width': '1500px'},
                                center = USA_CENTER,
                                zoom = 4,
                                id = "leaflet-map",
                                children = [
                                            dl.LayersControl([
                                                        dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                                # url = "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png",
                                                                url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                                                id = "TileMap")),
                                                            name = "Carto DB", checked=False),
                                                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                            # url = 'https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=ACCESS TOKEN'
                                                            url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                                            )), 
                                                            name = "Map Box", checked=True),
                                                        # COG fed into Tilelayer using TiTiler url (taken from r["tiles"][0])
                                                        dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                                                url = PNG, 
                                                                                opacity = 0.8, 
                                                                                id = "carbon_2000")), 
                                                                        name = "Carbon_Stock_2000", checked = True),
                                                        dl.LayerGroup(id = "layer"),
                                                        # Set colorbar and location in app
                                                        # dl.Colorbar(colorscale = colorscale, width = 20, height = 150, min = minv, max = maxv, position = "bottomright"),
                                                        # info,
                                                            ])
                                            ]
                            )
    
    # map_fig = dl.Map(id="map",
    # 				   center=USA_CENTER, 
    # 				   zoom=4, 
    # 				   style={"width": "100%", "height": "100%"},
    # 				#    crs=str(geo_crs).replace(":", ""),
    # 				   children=[
    # 						# dl.TileLayer(),
    # 						dl.TileLayer(
    # 							id="tile-layer",
    # 							url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    # 							# https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}
    # 							attribution='Map data © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    # 							# opacity=0.5
    # 							),
    # 						dl.ImageOverlay(url=PNG, opacity=0.5, bounds=bounds), #tileSize=912 #width_height
    # 						# WMSTileLayer
    # 						# dl.WMSTileLayer(url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi",
    # 						#             layers="nexrad-n0r-900913", format="image/png", transparent=True),
    # 						# dl.Colorbar(id="cbar", width=150, height=20, style={"margin-left": "40px"}, position="bottomleft"),
    # 			])

    fig_div = html.Div(children=[
                # Create the map itself.
                map_fig
                ,
                # Create controller.
                # html.Div(children=[
                #     html.Div("Parameter"),
                #     dcc.Dropdown(id="dd_param", options=[dict(value=p, label=lbl_map[p]) for p in PARAMS], value=param0),
                #     html.Br(),
                #     html.Div("Colorscale"),
                #     dcc.Dropdown(id="dd_cmap", options=[dict(value=c, label=c) for c in cmaps], value=cmap0),
                #     html.Br(),
                #     html.Div("Opacity"),
                #     dcc.Slider(id="opacity", min=0, max=1, value=0.5, step=0.1, marks={0: "0", 0.5: "0.5", 1: "1"}),
                #     html.Br(),
                #     html.Div("Stretch range"),
                #     dcc.RangeSlider(id="srng", min=srng0[0], max=srng0[1], value=srng0,
                #                     marks={v: "{:.1f}".format(v) for v in srng0}),
                #     html.Br(),
                #     html.Div("Value @ click position"),
                #     html.P(children="-", id="label"),
                # ], 
                # className="info")

        ], 
        
        style={"display": "grid", "width": "100%", "height": "100vh"}
    )

    # fig_div = html.Div(id="plotly-map", 
    # 				   children=[dl.Map(
    # 				   				# dl.BaseLayer(id="baselayer"),
    # 				   				# dl.TileLayer(url=TIFPATH), center=[56,10], zoom=6, style={'height': '80vh', 'width': '80vh'}
    # 								dl.LayersControl(
    # 									[
    # 										dl.Overlay(
    # 											[
    # 												# dl.ImageOverlay(url=png_path, bounds=bounds_png)
    # 												dl.GeoTIFFOverlay(
    # 													url=TIFPATH) #, bounds=bounds_tiff)
    # 											],
    # 											name="Map", checked=True)
    # 									],
    # 									position="topleft"
    # 								),
    # 								),
    # 				   				# dl.GeoJSON(data=dlx.dicts_to_geojson(
    # 				   				# 							get_map_data()
    # 				   				# 							), 
    # 				   				# 			cluster=True, 
    # 						  		# 	 		superClusterOptions={"radius": 100}, id='map-geojson'),
                                    

    # 				   ],
    # 				   )

    # fig_div = html.Div(id="plotly-map",
    # 				   children=dl.Map(
    # 				   				children=[
    # 				   						  dl.TileLayer(),
    # 				   						  dl.LayersControl([dl.BaseLayer(
    # 				   						  						dl.TileLayer(url=TIFPATH)) #, name=key, checked=key == "temp_new", id=key) for key in keys
    # 				   						  						]
    # 				   						  					+
    # 				   						  					[dl.Overlay(dl.LayerGroup(markers), name="TEST", checked=True)]
    # 				   						  					)
    # 				   						  ],
    # 				   				center=[52.195573, 20.883528], zoom=12, id='map'), 
    # 				   			    style={'width': '80vh', 'height': '80vh'}), 
    # 				   			    # 'margin': "auto", "display": "block", "position": "relative"


    print("Leaflet and TiTiler")

    return fig_div
