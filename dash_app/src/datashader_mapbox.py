#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard
import os

# visualization and data manipulation
import numpy as np
import plotly.express as px
from dash import html, dcc
import datashader as ds
import holoviews as hv
import datashader.transfer_functions as tf

# sourced scripts
from src.reader import open_as_raster
from definitions import plotly_config, CMAP_BLACK


def plot_ds_mapbox_map(COMPILED_DIR, fpaths):

    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, geo_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=True, is_convert_to_png=False)

    df_coors_long["easting"], df_coors_long["northing"] = hv.Tiles.lon_lat_to_easting_northing(
    df_coors_long["LongitudeProj"], df_coors_long["LatitudeProj"]
    )

    # points = hv.Points(df_coors_long, ['easting', 'northing'])
    # feasibility = datashade(points, cmap=cc.fire, width=plot_width, height=plot_height)
    # fig = map_tiles * feasibility

    # cvs = ds.Canvas(plot_width=int(6858/1.5), plot_height=int(3033/1.5)) # 3033, 6858
    # 3229, 5460

    # just feed the new data 

    # bigger over all number, smaller fraction number, more holes
    cvs = ds.Canvas(plot_width=int(5460/1.32), plot_height=int((3229-250)/1.32))
    agg = cvs.points(df_coors_long, x='LongitudeProj', y='LatitudeProj')
    coords_lat, coords_lon = agg.coords['LatitudeProj'].values, agg.coords['LongitudeProj'].values

    print(int(5460/1.32), int((3229-250)/1.32)) # wow I was able to guess the length(LongitudeProj) and the length(LatitudeProj) is 
    # what the plot_width and plot_heights should be respectively!
    print(agg)
    # WALKTHROUGH: https://towardsdatascience.com/big-data-visualization-using-datashader-in-python-c3fd00b9b6fc

    # x_range:  (-124.4600091773715, -67.0847028164778)
    # y_range:  (26.648993778952498, 48.99927661906988)
    # Corners of the image, which need to be passed to mapbox (xarray)
    coordinates = [[coords_lon[0], coords_lat[0]],
                    [coords_lon[-1], coords_lat[0]],
                    [coords_lon[-1], coords_lat[-1]],
                    [coords_lon[0], coords_lat[-1]]] 

    print(coordinates)

    # print(df_coors_long[:1])


    img = tf.shade(agg, cmap=CMAP_BLACK)[::-1].to_pil() #gray, kbc (blue)_    cc.kg
    fig = px.scatter_mapbox(df_coors_long, lat='LatitudeProj', lon='LongitudeProj', 
                        color_discrete_sequence=["#48f542"], 
                        # size="IsFeasible",
                        # size=1,
                        zoom=3)


    fig.update_layout(mapbox_style="open-street-map", # "carto-darkmatter",
                mapbox_layers = [
            {
                "sourcetype": "image",
                "source": img,
                "coordinates": coordinates
            }]
        ) # could separate basemap here

    # https://plotly.com/python/datashader/



    # https://developer.nvidia.com/blog/making-a-plotly-dash-census-viz-powered-by-rapids/

    # 'data': [{
    #            'type': 'scattermapbox',
    #            'lat': lat, 'lon': lon,
    #        }],
    # 'layout': {
    #            'mapbox': {
    # 		   …
    #                'layers': [{
    #                "sourcetype": "image",
    #                "source": datashader_output_img,
    #       	}],
    # }

    fig_div = html.Div(id="plotly-map", 
                        children=[dcc.Graph(id="energy-map", figure=fig, config=plotly_config)]
                        )

    print("DATASHADER + MAPBOX PLOTTED")

    return fig_div