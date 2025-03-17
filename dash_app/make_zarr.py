#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import rioxarray
import pandas as pd
import numpy as np
import time
import zarr
import xarray as xr

def preprocess_data(TIF_path, is_albers=True):

    start = time.time()

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

    # print(f"{end-start} seconds to preprocess TIF")

    max_lat = df_melted_feasible["Latitude"].max()
    min_lat = df_melted_feasible["Latitude"].min()
    max_lon = df_melted_feasible["Longitude"].max()
    min_lon = df_melted_feasible["Longitude"].min()

    bbox = [[min_lat, min_lon],[max_lat, max_lon]]

    # dx = df_melted_feasible[["Latitude", "Longitude"]].astype(np.float32).to_xarray() # DO NOT recommend doing this.
    dx = df_melted_feasible[["Latitude", "Longitude"]].to_xarray()
    return dx

# --------------------------------------------------------------------
#  Make Zarr and remove an old store if it exists
# --------------------------------------------------------------------
zarr_dir = "../../data/zarr_output2"
if os.path.exists(zarr_dir): # remove an old store if it exists:
    import shutil
    shutil.rmtree(zarr_dir)

zarr_store = zarr.DirectoryStore(zarr_dir)
root = zarr.group(store=zarr_store)

# --------------------------------------------------------------------
#  Loop over metdata, run preprocess, attach metdata, and write out
# --------------------------------------------------------------------

root_dir = "../../data/msdlive-gridcerf/gridcerf/compiled/compiled_technology_layers"
metadata_df = pd.read_csv("metadata/msdlive_tech_paths.csv")

for idx, row in metadata_df.iterrows():
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

    # print(ds)

    # raise SystemExit

    ds.attrs["ssp"] = str(ssp)
    ds.attrs["tech"] = str(tech)
    ds.attrs["subtech"] = str(subtech)
    ds.attrs["tech_feature"] = str(tech_feature)
    ds.attrs["is_ccs"] = str(is_ccs)
    ds.attrs["cooling_type"] = str(cooling_type)
    ds.attrs["capacity_factor"] = str(capacity_factor)
    ds.attrs["year"] = str(year)

    print(idx, ds.attrs)
    # raise SystemExit

    # ----------------------------------------------------------------
    #  Append each file’s data and group metadata into a Zarr store
    # ----------------------------------------------------------------
    group_name = f"{ssp}_{year}_{tech}_{subtech}_{tech_feature}_{is_ccs}_{cooling_type}_{capacity_factor}"
    
    # TODO: Check what kind of float it is ... could probably be smaller
    
    ds.to_zarr(
        store=zarr_dir,
        group=group_name,
        mode="a"
    )

print("Zarr creation complete!")

# Example 
# base_dir = os.path.join(root_dir, "compiled_technology_layers/ssp2")
# year = "2020"
# technology = "biomass"
# TIF_path = os.path.join(base_dir, year, technology, "gridcerf_biomass_conventional_no-ccs_dry.tif")
# df_melted_feasible = preprocess_data(TIF_path=TIF_path)
# df_melted_feasible.to_csv('data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv', index=False)

# when reading the data 
# if CONNECT_TO_LAMBDA:
#     TIF_source = "S3"
#     TIF_content = get_bytes(DATASET_ID, TIFPATH)  # reading the retrieved file from the S3 bucket  
#     TIF_stream = BytesIO(TIF_content) # wrap the file content in a BytesIO object for use like a file


# Optional: Create an index for searching by energy type, year, etc.
# energy_index = root.create_dataset("energy_index", shape=(len(metadata_dict),), dtype='S100')
# for i, (energy_type, meta_list) in enumerate(metadata_dict.items()):
#     energy_index[i] = energy_type  # Store energy type as index

# print("Conversion to Zarr complete.")
