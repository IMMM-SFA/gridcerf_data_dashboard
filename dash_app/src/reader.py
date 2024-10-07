#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard libraries
import os

# data manipulation
import numpy as np
import pandas as pd
import rasterio
import rioxarray
import xarray as xr
from pyproj import Transformer, Proj, transform
from pyproj import CRS
from PIL import Image
# import rasterio
# from rasterio.warp import calculate_default_transform, reproject, Resampling

# sourced scripts
from definitions import CONNECT_TO_LAMBDA
if CONNECT_TO_LAMBDA:
    from definitions import DATASET_ID
    from msdlive_utils import get_bytes
    from io import BytesIO

WEB_CRS = "EPSG:4326" # WGS 84
# WEB_CRS = "EPSG:3857" # WEB MERCATOR

def read_TIF_metadata(TIF_stream):

	# rioxarray
	og_proj_array = rioxarray.open_rasterio(TIF_stream, masked=True) # returns xarray.DataArray

	# xds_lonlat = og_proj_array.rio.reproject(WEB_CRS)
	# print("HERE")
	# print(xds_lonlat)
	# print('\n\n\n')

	data_2d = og_proj_array.isel(band=0).values
	data_df = pd.DataFrame(data_2d, columns=og_proj_array.x, index=og_proj_array.y) 
	# og_lons = og_proj_array.x
	# og_lats = og_proj_array.y

	# Metadata
	# metadata = og_proj_array.rio.meta()

	# Transform
	transform = og_proj_array.rio.transform()

	# Albers Equal Area Conic CRS (ESRI:102003)
	source_crs = og_proj_array.rio.crs 
	pyproj_crs = CRS(source_crs.to_proj4())
	units_crs = pyproj_crs.axis_info[0].unit_name

	# Bounding Box
	source_bounds = og_proj_array.rio.bounds()
	min_lon = source_bounds[0]  # minx
	min_lat = source_bounds[1]   # miny
	max_lon = source_bounds[2]  # maxx
	max_lat = source_bounds[3]   # maxy

	source_bbox = [[min_lat, min_lon],[max_lat, max_lon]]

	return og_proj_array, data_df, transform, source_crs, units_crs, source_bbox

    
def melt_and_reproject(array, TIF_df, source_crs, geo_crs):

	df_reset = TIF_df.reset_index()
	df_reset = df_reset.rename(columns={'index': 'Latitude'})
	df_melted = pd.melt(df_reset, id_vars='Latitude', var_name='Longitude', value_name='IsFeasible')

	# Transform 
	transformer = Transformer.from_crs(source_crs, geo_crs, always_xy=True)
	df_melted["LongitudeProj"], df_melted["LatitudeProj"] = transformer.transform(df_melted.Longitude, df_melted.Latitude)

	# Bounding Box
	min_lat = df_melted['LatitudeProj'].min()
	max_lat = df_melted['LatitudeProj'].max()
	min_lon = df_melted['LongitudeProj'].min()
	max_lon = df_melted['LongitudeProj'].max()

	bbox_proj = [[min_lat, min_lon],[max_lat, max_lon]]

	# Remove NonFeasible
	df_melted_feasible = df_melted[df_melted["IsFeasible"] != 1] # (216165, 5)

	# the BELOW reprojects EVERYTHING EVEN THE BINARY (BOOLEAN, is feasible?) CELLS ...
	proj_array = array.rio.reproject(geo_crs)
	proj_lons = proj_array.x #np.array(proj_array.x)
	proj_lats = proj_array.y # np.array(proj_array.y)
	data_2d = proj_array.isel(band=0).values
	data_df_proj = pd.DataFrame(data_2d, columns=proj_lons, index=proj_lats)

	unique_values = pd.unique(data_df_proj.values.flatten())
	# print(unique_values)

	return proj_array, df_melted_feasible, bbox_proj, data_df_proj
    
def open_as_raster(TIFPATH, is_reproject=False, is_convert_to_png=False):

	"""This should work with any file that rasterio can open 
	(most often: geoTIFF). The x and y coordinates are generated 
	automatically from the file's geoinformation, shifted to the 
	center of each pixel (see “PixelIsArea” Raster Space for more 
	information)."""

	TIF_source = "Local"
	TIF_stream = TIFPATH

	if CONNECT_TO_LAMBDA:

		TIF_source = "S3"
		TIF_content = get_bytes(DATASET_ID, TIFPATH)  # reading the retrieved file from the S3 bucket  
		TIF_stream = BytesIO(TIF_content) # wrap the file content in a BytesIO object for use like a file
	
	print(f"{TIF_source}: {TIF_stream}\n")

	array, data_df, transform, source_crs, units_crs, source_bbox = read_TIF_metadata(TIF_stream=TIF_stream)
	source_bbox = [[24.9493, -125.00165], [49.59037, -66.93457]] # bounds of the United States, not considering off shore
	# source_bbox = [[19.94822477183972, -134.3417298122159], [52.7538229058337, -60.14850035217076]]

	print(f"Data is in {source_crs} and its shape is {array.shape}")

	# WGS84 (aka.  Albers Equal) || destination_proj
	geo_crs = CRS(WEB_CRS)
	""" 
	dash-leaflet itself primarily supports EPSG:3857 (Web Mercator) and EPSG:4326 (WGS 84) out of the box
	"""
	if is_reproject:
		array, df_coors_long, proj_bbox, data_df = melt_and_reproject(array=array, # og projected array
																	  TIF_df=data_df, 
																	  source_crs=source_crs, 
																	  geo_crs=geo_crs
																	)
		print(f"Data is now in {geo_crs} and its shape is {array.shape}")
		bbox = proj_bbox
	else: 
		df_coors_long = []
		bbox = source_bbox
	
	array = array.values
	array = array.reshape(-1, array.shape[-1])

	if is_convert_to_png:
		# TIF to IMG (i.e., PNG)
		array_blackwhite = np.interp(array, (array.min(), array.max()), (0, 255)) #  255 is white and 0 is black
		img = Image.fromarray(array_blackwhite.astype(np.uint8)).resize((array_blackwhite.shape[0], array_blackwhite.shape[1]))
	else:
		img = []
	
	array[array == 1] = np.nan

	print(f"Bounding Box: {bbox}")

	with rasterio.open(TIF_stream) as src:
		transform = src.transform
		transformer = Transformer.from_crs(source_crs, geo_crs, always_xy=True)
		width = src.width
		height = src.height
		
		cols, rows = np.meshgrid(np.arange(width), np.arange(height))
		cols = cols.flatten()
		rows = rows.flatten()
		xs, ys = transform * (cols, rows)
		geo_lons, geo_lats = transformer.transform(xs, ys)
		geo_lons = geo_lons.reshape((height, width))
		geo_lats = geo_lats.reshape((height, width))
		# print(geo_lons)
		# print(geo_lats)

		# 1D, 2D, 3D values 
		# print(geo_lats.shape)

	return data_df, array, source_crs, geo_crs, df_coors_long, bbox, img
