#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

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






