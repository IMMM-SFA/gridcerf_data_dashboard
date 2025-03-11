#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ------------------------------------------------
# Static Layer Preprocessing
# ------------------------------------------------

import os
import geopandas as gpd
import shapely.ops as ops

# DATA PATHS
DATA_DIR = "data"
CERF_DATA_DIR = "../../data/msdlive-gridcerf"
COMPILED_DIR = os.path.join(CERF_DATA_DIR, "gridcerf/compiled/compiled_technology_layers")

STATES_PATH = os.path.join(DATA_DIR, "states_polygons_albers.geojson") # polygons
TRANS_PATH = os.path.join(DATA_DIR, "conus_transmission_epsg4326_albers.geojson")
LAND_PATH = os.path.join(DATA_DIR, "ne_50m_admin_0_scale_rank_albers.geojson")
OCEANS_PATH = os.path.join(DATA_DIR, "ne_50m_ocean_albers.geojson")

north_america = [
    "United States",
    "Alaska",
    "Hawaii",
    "Puerto Rico",
    "United States Virgin Islands",
    "Cayman Islands",
    "Bermuda",
    "British Virgin Islands",
    "Turks and Caicos Islands",
    "Montserrat",
    "Canada",
    "Mexico",
    "Jamaica",
    "Cuba",
    "Dominican Republic",
    "Haiti",
    "Belize",
    "Guatemala",
    "Honduras",
    "El Salvador",
    "Nicaragua",
    "Costa Rica",
    "Panama",
    "Saint Pierre and Miquelon",
    "Greenland",
    "The Bahamas",
    "Anguilla",
    "Aruba",
    "Curaçao",
    "Guadeloupe",
    "Martinique",
    "Saint Martin",
    "Saint Barthelemy",
    "Saint Kitts and Nevis",
    "Saint Lucia",
    "Saint Vincent and the Grenadines"
]

# ------------------------------------------------
# Functions
# ------------------------------------------------

def reproject2albers(fname, ftype):

    inpath = os.path.join(DATA_DIR, fname) # geojson, json, shapefile
    gdf = gpd.read_file(inpath)

    target_crs = "ESRI:102003"
    gdf_albers = gdf.to_crs(target_crs)

    gdf_albers.to_file(inpath.replace(f".{ftype}", f"_albers.{ftype}"))

def mirror_geometry(geom, axis='x'):
    """
    Reflects the geometry across an axis.
    If axis='x': mirror vertically (flip y).
    If axis='y': mirror horizontally (flip x).
    """
    if axis == 'x':
        # Mirror vertically: flip y coordinate.
        return ops.transform(lambda x, y, z=None: (x, -y) if z is None else (x, -y, z), geom)
    elif axis == 'y':
        # Mirror horizontally: flip x coordinate.
        return ops.transform(lambda x, y, z=None: (-x, y) if z is None else (-x, y, z), geom)
    else:
        raise ValueError("Axis must be 'x' or 'y'")

# ------------------------------------------------
# Preprocessing Static Layers
# ------------------------------------------------

LAND = gpd.read_file(LAND_PATH)
LAND_NORTHAMERICA = LAND[LAND["sr_subunit"].isin(north_america)]
LAND_NORTHAMERICA["geometry"] = LAND_NORTHAMERICA["geometry"].apply(lambda geom: mirror_geometry(geom, axis='x'))

OCEANS = gpd.read_file(OCEANS_PATH)
OCEANS["geometry"] = OCEANS["geometry"].apply(lambda geom: mirror_geometry(geom, axis='x'))

STATES = gpd.read_file(STATES_PATH)
STATES["geometry"] = STATES["geometry"].apply(lambda geom: mirror_geometry(geom, axis='x'))

TRANSMISSION_LINES = gpd.read_file(TRANS_PATH)
TRANSMISSION_LINES["geometry"] = TRANSMISSION_LINES["geometry"].apply(lambda geom: mirror_geometry(geom, axis='x'))

LAND_NORTHAMERICA.to_file("data/static_layer_data/land.geojson", driver="GeoJSON")
OCEANS.to_file("data/static_layer_data/oceans.geojson", driver="GeoJSON")
STATES.to_file("data/static_layer_data/states.geojson", driver="GeoJSON")
TRANSMISSION_LINES.to_file("data/static_layer_data/transmission_lines.geojson", driver="GeoJSON")

# OCEANS = json.loads(OCEANS_NORTHAMERICA.to_json())