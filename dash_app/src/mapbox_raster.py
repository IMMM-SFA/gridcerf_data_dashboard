#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard
import os

# visualization and data manipulation
from dash import html, dcc
import plotly.express as px
import geopandas as gpd
import shapely.geometry

# sourced scripts
from src.reader import open_as_raster
from definitions import plotly_config, CMAP_BLACK


def plot_mapbox_map(COMPILED_DIR, fpaths):

    # NOT GOING TO WORK

    # map box icons: https://labs.mapbox.com/maki-icons/

    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, geo_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=True, is_convert_to_png=False)

    fig = px.scatter_mapbox(df_coors_long, lat="LatitudeProj", lon="LongitudeProj", hover_name="IsFeasible", #hover_data=["State", "Population"],
                        size="IsFeasible",
                        size_max=1,  # This sets the maximum size of points
                        # size_max_scale=10,  # Controls how much the size scales relative to size_max
                        color_discrete_sequence=["fuchsia"], 
                        zoom=3, 
                        # height=300
                        )
    
    

    # fig = go.Figure(go.Scattermapbox(
    # 	lat=df_coors_long['LatitudeProj'],
    # 	lon=df_coors_long['LongitudeProj'],
    # 	# text=data['label'],
    # 	mode='markers',
    # 	marker=dict(
    # 		color='red',
    # 		symbol="bus",
    # 		opacity=0.7,
    # 		size=10  # Initial placeholder value
    # 	)
    # ))
    # fig.update_layout(
    # 	mapbox = dict(
    # 		accesstoken=token,
    # 		# style="outdoors", zoom=0.7),
    # 	# showlegend = False,
    # 	)
    # )

    fig.update_layout(mapbox_style="open-street-map") # Allowed values which do not require a token are 'open-street-map', 'white-bg', 'carto- positron', 'carto-darkmatter'. 
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_traces(marker=dict(size=4))

    fig.update_mapboxes(layers=[
        {	"symbol": {"icon": "square"},
            "sourcetype": "geojson",
            "type": "symbol", # Type: enumerated , one of ( "circle" | "line" | "fill" | "symbol" | "raster" )
            # "circle": {"radius": 13}
        }
    ])
    custom_javascript = html.Script('''
document.addEventListener('DOMContentLoaded', function() {
    var mapElement = document.querySelector('#map');
    if (mapElement) {
        var map = mapElement._plotly_js._fullData[0].mapboxMap;

        function updatePointSize() {
            var zoom = map.getZoom();
            // Calculate circle radius to cover approximately 1 km
            // Size in pixels = 1 km / (meters per pixel at current zoom level)
            var metersPerPixel = 156543.03392 * Math.cos(map.getCenter().lat * Math.PI / 180) / Math.pow(2, zoom);
            var radiusInPixels = 1000 / metersPerPixel; // 1000 meters (1 km)

            map.setPaintProperty('my-layer', 'circle-radius', radiusInPixels);
        }

        map.on('zoom', updatePointSize);
        updatePointSize(); // Initial call to set size
    }
});
''')


    # fig.update_layout(
    # 	mapbox_style="mapbox://styles/mapbox/streets-v11",
    # 	mapbox_layers=[
    # 		{
    # 			'sourcetype': 'geojson',
    # 			'source': {
    # 				'type': 'FeatureCollection',
    # 				'features': [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [lon, lat]}} for lon, lat in zip(df_coors_long['LongitudeProj'], df_coors_long['LatitudeProj'])]
    # 			},
    # 			'type': 'circle',
    # 			'point': {
    # 				'circle-radius': ['case', ['==', ['zoom'], 0], 10, 10],  # Static radius
    # 				'circle-color': '#FF0000',
    # 				'circle-opacity': 0.7
    # 			}
    # 		}
    # 	]
    # )

    # fig = px.density_mapbox(
    # 			df_coors_long,
    # 			lat="LatitudeProj",
    # 			lon="LongitudeProj",
    # 			z="IsFeasible",
    # 			radius=1,
    # 			zoom=3,
    # 			# color_continuous_scale=["#121212", "#121212"],
    # 			# opacity=0.9
    # 			# mapbox_style="open-street-map"
    # 		)
            # fig = go.Figure(go.Scattermapbox())
    # fig.update_layout(
    # 			mapbox_layers=[
    # 				{
    # 					# "below": "traces",
    # 					"circle": {"radius": 3},
    # 					"color":"red",
    # 					"minzoom": 6,
    # 					"source": gpd.GeoSeries(
    # 						df_coors_long.loc[:, ["LongitudeProj", "LatitudeProj"]].apply(
    # 							shapely.geometry.Point, axis=1
    # 						)
    # 					).__geo_interface__,
    # 				},
    # 			],
    # 			mapbox_style="carto-positron",
    # 		)
    fig.update_layout(
                mapbox_layers=[
                    {
                        # "below": "traces",
                        "circle": {"radius": 10},
                        "color":"red",
                        "minzoom": 10,
                        "source": gpd.GeoSeries(
                            df_coors_long.loc[:, ["LongitudeProj", "LatitudeProj"]].apply(
                                shapely.geometry.Point, axis=1
                            )
                        ).__geo_interface__,
                    },
                ],
                mapbox_style="open-street-map",
            )

    # Create a scatter mapbox plot
    # fig = go.Figure(go.Scattermapbox(
    # 	lat=df_coors_long['LatitudeProj'],
    # 	lon=df_coors_long['LongitudeProj'],
    # 	mode='markers',
    # 	marker=dict(
        
    # 		size=3,  # Fixed size for all points
    # 		color=df_coors_long['IsFeasible'],  # Optional: Color by a value
    # 		colorscale='Viridis',  # Optional: Color scale
    # 		# symbol="circle",
    # 		showscale=True  # Optional: Show color scale
    # 	),
    # 	# text=df_coors_long['IsFeasible'],  # Optional: Tooltip text
    # ))

    # # Update layout with Mapbox style
    # fig.update_layout(
    # 	mapbox=dict(
    # 		style='carto-positron',  # Choose a Mapbox style
    # 		# center=dict(lat=41, lon=-75),  # Center map on your data
    # 		# zoom=10  # Initial zoom level
    # 	),
    # 	# title='Map with Fixed Point Size'
    # )

    fig_div = html.Div(id="plotly-map", 
                        children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config),
                                custom_javascript]
                        )

    # fig.update_layout(mapbox_style="open-street-map")

    # df = px.data.gapminder().query("year == 2007")
    # fig = px.scatter_geo(df, locations="iso_alpha",
    # 					color="continent", # which column to use to set the color of markers
    # 					hover_name="country", # column added to hover information
    # 					size="pop", # size of markers
    # 					projection="natural earth")
                        
    ## IF USING MAPBOX THIS IS GREAT BUT IT DOESN'W WORK FOR IMSHOW
    # Add a basemap layer (a custom image or plotly mapbox style) - optional
    # fig.update_layout(
    # 		mapbox_style="open-street-map",  # Choose a basemap style (e.g., 'open-street-map', 'carto-positron', 'white-bg')
    # 		mapbox=dict(
    # 				center=dict(lat=37.0902, lon=-95.7129),  # Center of the US (latitude and longitude)
    # 				zoom=3  # Adjust the zoom level as needed
    # 		),
    # 		autosize=True
    # )
    # Add a trace in order for the base map to appear
    # fig.add_trace(go.Scattermapbox(
    # 	mode='markers',
    # 	lon=[-95.7129],  # Longitude of center (for example)
    # 	lat=[37.0902],  # Latitude of center (for example)
    # 	marker=dict(
    # 				size=10, # Fixed size?
    # 				color='red'
    # 				)
    # ))

    # Update layout with geo projection and center -- this did nothing ... 
    # fig.update_layout(
    # 	geo=dict(
    # 		scope='usa',
    # 		center=dict(lat=39.0902, lon=-95.7129),  # Center of the US
    # 		projection_scale=5  # Adjust this as needed
    # 	)
    # )
    # fig.add_trace(px.imshow(array))






    # print(data_array)

    # fig_div = html.Div(id="plotly-map", 
    # 				   children=[
    # 				   px.scatter_mapbox(data_array), # lon=data_array.x, lat=data_array.y
    # 				   ]
    # 				   )
    # fig_div.update_layout(
    # 			title='Raster Overlay on Map',
    # 			geo=dict(
    # 				scope='usa',
    # 				projection=dict(type='mercator'),
    # 				showland=True,
    # 				landcolor='rgb(243, 243, 243)'
    # 			)
    # 		)


    # Convert to Plotly-compatible format
    # img_trace = px.imshow(data_array)

    # # Create map with base layer and raster overlay
    # fig = px.scatter_mapbox(
    # 	lat=[37.7749],
    # 	lon=[-95.7129],
    # 	color_discrete_sequence=['blue'],
    # 	zoom=4,
    # 	mapbox_style='open-street-map'
    # )

    # print(img_trace.data[0])
    # fig.add_trace(img_trace.data[0])

    # fig.update_layout(
    # 	title='Raster Overlay on Map',
    # 	mapbox=dict(
    # 		style='open-street-map',
    # 		center=dict(lat=37.7749, lon=-95.7129),
    # 		zoom=4
    # 	)
    # )

    # fig_div = html.Div(id="plotly-map", 
    # 				   children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config)]
    # 				   )

    print("Mapbox")

    return fig_div
