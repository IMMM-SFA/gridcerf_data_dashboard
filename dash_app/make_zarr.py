#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import rioxarray
import pandas as pd
import numpy as np
import time
import zarr
# from zarr.storage import S3Store
from zarr.storage import FSStore
import xarray as xr
import s3fs

# source in credentials
script_dir = os.path.abspath("../../../") # "../../../git_repositories"
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from gridcerf_credentials import *

s3 = s3fs.S3FileSystem(
    anon=False,
    key=AWS_Access_Key_ID,
    secret=AWS_Secret_Access_Key
)

bucket_name = "gridcerf-dashboard"

# list the contents of the bucket root
try:
    contents = s3.ls(bucket_name)
    print("Bucket contents:", contents)
except Exception as e:
    print("Error accessing bucket:", e)

run_spatial_metadata = False

def preprocess_data(TIF_path, is_albers=True):

    # Read the data, make xarray, reformat matrix as df, and melt the df
    xarray = rioxarray.open_rasterio(TIF_path, masked=True)
    matrix = xarray.isel(band=0).values 
    TIF_df = pd.DataFrame(matrix, columns=xarray.x, index=xarray.y)

    df_melted_feasible = ( ## This takes 93% of total time (total time is 0.5-1 sec though)
        TIF_df
        .reset_index()
        .rename(columns={'index': 'Latitude'})
        .melt(id_vars='Latitude', var_name='Longitude', value_name='IsFeasible')
        .query("IsFeasible != 1")
    )

    # Map styling by projection (so fast that it's not worth saving)
    if not is_albers: 
        df_melted_feasible["Angle"] = np.where(df_melted_feasible["Longitude"] <= -121, 15,
                        np.where(df_melted_feasible["Longitude"].between(-121, -118), 13,
                        np.where(df_melted_feasible["Longitude"].between(-118, -112), 10,
                        np.where(df_melted_feasible["Longitude"].between(-112, -107), 8,
                        np.where(df_melted_feasible["Longitude"].between(-107, -103), 5,
                        np.where(df_melted_feasible["Longitude"].between(-103, -100), 2,
                        np.where(df_melted_feasible["Longitude"].between(-93, -91), -2,
                        np.where(df_melted_feasible["Longitude"].between(-91, -82), -5,
                        np.where(df_melted_feasible["Longitude"].between(-82, -76), -10,
                        np.where(df_melted_feasible["Longitude"] > -76, -15, 0))))))))))
    if is_albers:
        df_melted_feasible["Angle"] = 0

    # Mirror the data over the x-axis (flip) 
    df_melted_feasible["Latitude"] = -df_melted_feasible["Latitude"]

    if run_spatial_metadata:

        # Spatial metadata
        crs = xarray.rio.crs 
        bbounds = xarray.rio.bounds()
        min_lon = bbounds[0]
        min_lat = bbounds[1]
        max_lon = bbounds[2]
        max_lat = bbounds[3]
        bbox = [[min_lat, min_lon],[max_lat, max_lon]]

        result = {
            "source_crs": crs,
            "units": "m",
            "bounds": bbounds,
            "min_lon": min_lon,
            "min_lat": min_lat,
            "max_lon": max_lon,
            "max_lat": max_lat,
            "bounding_box": bbox
        }

        max_lat = df_melted_feasible["Latitude"].max()
        min_lat = df_melted_feasible["Latitude"].min()
        max_lon = df_melted_feasible["Longitude"].max()
        min_lon = df_melted_feasible["Longitude"].min()

        bbox = [[min_lat, min_lon],[max_lat, max_lon]]

    # dx = df_melted_feasible[["Latitude", "Longitude"]].astype(np.float32).to_xarray() # DO NOT recommend doing this. B/c loose accuracy. 
    dx = df_melted_feasible[["Latitude", "Longitude"]].to_xarray()

    return dx

# --------------------------------------------------------------------
#  Make Zarr and remove an old store if it exists
# --------------------------------------------------------------------
zarr_dir = "../../data/gridcerf_compiled_zarr"
if os.path.exists(zarr_dir): # remove an old store if it exists:
    import shutil
    shutil.rmtree(zarr_dir)

# Local Run
# zarr_store = zarr.DirectoryStore(zarr_dir)
# root = zarr.group(store=zarr_store)

# Cloud Run
# s3_store = S3Store(f"{bucket_name}/gridcerf_compiled_zarr", s3=s3)
s3_mapper = s3.get_mapper(f"{bucket_name}/gridcerf_compiled_zarr")
# s3_store = FSStore(f"s3://{bucket_name}/gridcerf_compiled_zarr", s3=s3)
# s3_store = FSStore(
#     f"s3://{bucket_name}/gridcerf_compiled_zarr",
#     storage_options={"key": AWS_Access_Key_ID, "secret": AWS_Secret_Access_Key}
# )
# root = zarr.group(store=s3_store, overwrite=True)
root = zarr.group(store=s3_mapper, overwrite=True)


# --------------------------------------------------------------------
#  Loop over metdata, run preprocess, attach metdata, and write out
# --------------------------------------------------------------------

root_dir = "../../data/msdlive-gridcerf/gridcerf/compiled/compiled_technology_layers"
metadata_df = pd.read_csv("metadata/msdlive_tech_paths.csv")

for idx, row in metadata_df.iterrows():

    start = time.time()

    tif_path = row["fpath"]
    ssp = row["ssp"]
    tech = row["tech"]
    subtech = row["subtype"]
    tech_feature = row["feature"]
    is_ccs = row["is_ccs"]
    cooling_type = row["cooling_type"]
    capacity_factor = row["cap_factor"]
    year = row["ui_year"]

    TIF_path = os.path.join(root_dir, tif_path)
    ds = preprocess_data(TIF_path=TIF_path)

    ds.attrs["ssp"] = str(ssp)
    ds.attrs["tech"] = str(tech)
    ds.attrs["subtech"] = str(subtech)
    ds.attrs["tech_feature"] = str(tech_feature)
    ds.attrs["is_ccs"] = str(is_ccs)
    ds.attrs["cooling_type"] = str(cooling_type)
    ds.attrs["capacity_factor"] = str(capacity_factor)
    ds.attrs["year"] = str(year)

    # ----------------------------------------------------------------
    #  Append each file’s data and group metadata into a Zarr store
    # ----------------------------------------------------------------
    group_name = f"{ssp}_{year}_{tech}_{subtech}_{tech_feature}_{is_ccs}_{cooling_type}_{capacity_factor}"
        
    ds.to_zarr(
        # store=zarr_dir,
        # store=s3_store,
        store=s3_mapper,
        group=group_name,
        mode="a"
    )
    
    print(idx, time.time() - start) #, ds.attrs)

print("Zarr creation complete!")
