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










	# with rasterio.open(TIF_stream) as src:

	# 	array = src.read(1)
	# 	boundingbox = src.bounds

	# 	if is_convert_to_png:
	# 		# TIF to IMG (i.e., PNG)
	# 		array_blackwhite = np.interp(array, (array.min(), array.max()), (0, 255)) #  255 is white and 0 is black
	# 		img = Image.fromarray(array_blackwhite.astype(np.uint8)).resize((src.width, src.height))
	# 	else:
	# 		img = []
		
	# 	print('here')
	# 	print(array)

		# metadata = src.meta




def read_data():

	# get the parent directory path to where this notebook is currently stored
	root_dir = os.path.dirname(os.getcwd())

	# data directory in repository
	# data_dir = os.path.join(root_dir, "data")
	data_dir = os.path.join(root_dir, "../data")

	# GRIDCERF data directory from downloaded archive
	gridcerf_dir = os.path.join(data_dir, "gridcerf")

	# GRIDCERF reference data directory
	reference_dir = os.path.join(gridcerf_dir, "reference")



	# validation directory
	validation_dir = os.path.join(gridcerf_dir, 'validation')

	# common exclusion layers
	raster_dir = os.path.join(gridcerf_dir, 'common')

	# directory containing technology specific layers
	tech_dir = os.path.join(gridcerf_dir, 'technology_specific')

	# template land mask raster
	template_raster = os.path.join(reference_dir, "gridcerf_landmask.tif")

	# additional layers needed
	slope_raster = os.path.join(tech_dir, 'gridcerf_srtm_slope_20pct_or_less.tif')
	potential_raster = os.path.join(tech_dir, 'gridcerf_nrel_wind_development_potential_hubheight080m_cf35.tif')
	population_raster = os.path.join(tech_dir, 'gridcerf_densely_populated_ssp2_2020.tif')

	# EIA power plant spatialdata
	power_plant_file = os.path.join(validation_dir, 'eia', 'accessed_2021-06-09', 'PowerPlants_US_EIA', 'PowerPlants_US_202004.shp')

	# eia generator inventory file downloaded from:  https://www.eia.gov/electricity/data/eia860m/xls/april_generator2021.xlsx
	eia_generator_inventory_file = os.path.join(validation_dir, 'eia', 'april_generator2021.xlsx')

	# eia 923 generation data downloaded from: https://www.eia.gov/electricity/data/eia923/archive/xls/f923_2021.zip
	eia_generation_file = os.path.join(validation_dir, "eia", "EIA923_Schedules_2_3_4_5_M_12_2021_Final_Revision.xlsx")

	# administrative data
	cerf_conus_file = os.path.join(reference_dir, 'gridcerf_conus_boundary.shp')
	cerf_states_file = os.path.join(reference_dir, 'Promod_20121028_fips.shp')

	# output combined suitability layer without land mask
	cerf_suitability_file = os.path.join(validation_dir, 'temp', 'gridcerf_wind_suitability_nomask.tif')

	# combined suitability with land mask
	cerf_suitability_masked_file = os.path.join(validation_dir, 'temp', 'gridcerf_wind_suitability_landmask.tif')

	# validation outputs
	suitable_power_plants_file = os.path.join(validation_dir, 'results', 'suitable_power_plants_wind.shp')
	unsuitable_power_plants_file = os.path.join(validation_dir, 'results', 'unsuitable_power_plants_wind.shp')

	paths_dict = {"validation_dir": validation_dir,
				  "raster_dir": raster_dir,
				  "tech_dir": tech_dir,
				  "template_raster": template_raster,
				  "slope_raster": slope_raster,
				  "potential_raster": potential_raster,
				  "population_raster": population_raster,
				  "power_plant_file": power_plant_file,
				  "eia_generator_inventory_file": eia_generator_inventory_file,
				  "eia_generation_file": eia_generation_file,
				  "cerf_conus_file": cerf_conus_file,
				  "cerf_states_file": cerf_states_file,
				  "cerf_suitability_file": cerf_suitability_file,
				  "cerf_suitability_masked_file": cerf_suitability_masked_file,
				  "suitable_power_plants_file": suitable_power_plants_file,
				  "unsuitable_power_plants_file": unsuitable_power_plants_file}


	return paths_dict






