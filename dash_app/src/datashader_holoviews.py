#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard
import os

# visualization and data manipulation
import holoviews as hv
from holoviews import opts
from holoviews.operation.datashader import datashade
from holoviews.element.tiles import EsriImagery, CartoDark, CartoLight, EsriStreet, EsriNatGeo, EsriUSATopo, EsriTerrain, OSM, OpenTopoMap, EsriReference

# sourced scripts
from src.reader import open_as_raster
from definitions import plotly_config, CMAP_BLACK


def plot_ds_holoviews_map(COMPILED_DIR, fpaths):


    TIFPATH = os.path.join(COMPILED_DIR, fpaths[0])
    data_df, array, source_crs, geo_crs, df_coors_long, boundingbox, img = open_as_raster(TIFPATH=TIFPATH, is_reproject=True, is_convert_to_png=False)

    # to use RAPIDS ... need to install drivers, but have no GPUs on Mac

    # ylat = np.arange(0, array.shape[0], 1).tolist()
    # xlon = np.arange(0, array.shape[1], 1).tolist()
    
    # data_xr = xr.DataArray(array, 
    # 	coords={'y': ylat,'x': xlon}, 
    # dims=["y", "x"])
    # df = data_xr.to_dataframe(name='value').reset_index()
    # print(df)

    # this works
    # fig = df_coors_long.hvplot.scatter(x='LongitudeProj', y='LatitudeProj', by='IsFeasible')
    # fig = df_coors_long.hvplot(x="LongitudeProj", y="LatitudeProj", kind='scatter', rasterize=True)
    plot_width = int(5460/1.32)
    plot_height = int((3229-250)/1.32)
    # print(int(5460/1.32), int((3229-250)/1.32))

    # map_tiles = gv.tile_sources.OSM() # gv not defined does not work
    # map_tiles = EsriImagery().opts(alpha=0.5, width=plot_width, height=plot_height, bgcolor='black')
    # map_tiles = hv.element.tiles.EsriImagery().opts(alpha=0.5, width=plot_width, height=plot_height, show_grid=False)
    # map_tiles = CartoDark()
    map_tiles = EsriStreet().opts(alpha=0.5, bgcolor='black', width=plot_width, height=plot_height)
    # map_tiles = hv.Tiles('https://tile.openstreetmap.org/{Z}/{X}/{Y}.png', name="OSM") #.opts(width=plot_width, height=plot_height)
    # all of the OSM maps here: https://xyzservices.readthedocs.io/en/stable/gallery.html
    # map_tiles = hv.Tiles('https://tiles.stadiamaps.com/tiles/stamen_toner_background/{z}/{x}/{y}{r}.{ext}', name="OSM")

    df_coors_long["easting"], df_coors_long["northing"] = hv.Tiles.lon_lat_to_easting_northing(
    df_coors_long["LongitudeProj"], df_coors_long["LatitudeProj"]
    )
    # points = hv.Points(df_coors_long, ['LongitudeProj', 'LatitudeProj'])
    df_coors_long["alpha"] = 1 # get an error if put 100
    df_coors_long["color"] = "black"
    # df_coors_long["marker"] = "circle"
    # df_coors_long["size"] = 1

    # fig.opts.defaults(opts.Points(size=1, line_color='black'))

    # SHOW
    # STREAMS****: https://holoviews.org/gallery/apps/bokeh/nytaxi_hover.html
    points = hv.Points(df_coors_long, ['easting', 'northing'], vdims=['alpha', 'color']).opts(
                            cmap=CMAP_BLACK, alpha="alpha", 
                            color="color",
                            # color='k'
                            # marker='marker', #size='size'
                            )
    # markers = points.opts(
    # 			opts.Points(
    # 				color='color',
    # 				size='size',
    # 				alpha='alpha',
    # 				# tools=['hover'],
    # 				cmap=CMAP_BLACK,  # Or any color map
    # 				size_index='size'
    # 			)
    # 		)
    # https://holoviews.org/_modules/holoviews/operation/datashader.html
    feasibility = datashade(points, cmap=CMAP_BLACK,
                            # color_key="#000000", 
                            alpha=155, 
                            min_alpha=255,
                            width=plot_width, height=plot_height)
    fig = map_tiles * feasibility * points

    # hv.extension('bokeh', logo=False)


    print(fig)
    print(map_tiles)

    fig.opts(xaxis=None,yaxis=None, title="")
    setattr(fig, 'plot_width', 1700)
    setattr(fig, 'plot_height', 900)

    print(opts)
    # plot_width  = int(750)
    # plot_height = int(plot_width*4)
    opts.defaults(
        opts.Points(size=1, color='blue'),
        # opts.Overlay(width=plot_width, height=plot_height, xaxis=None, yaxis=None),
        # opts.RGB(width=plot_width, height=plot_height),
        # opts.Histogram(responsive=True, min_height=250)
        )



    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # Display the plot
    # hv.save(fig, 'holoview_plot.html', fmt='html')

    # plot = df_coors_long.hvplot(
    # 					x='easting',
    # 					y='northing',
    # 					kind='scatter',
    # 					rasterize=True,
    # 					cmap=cc.fire,
    # 					cnorm='eq_hist',
    # 					width=length, 
    # 					height=length*2
    # 				)
    # fig2 = map_tiles * plot
    # hv.save(fig2, 'holoview_plot2.html', fmt='html')

    # scatter = create_datashaded_scatterplot(df)
    
    return fig
