#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# data manipulation
import numpy as np
import pandas as pd
import rasterio
import rioxarray
import xarray as xr
from pyproj import Transformer
from pyproj import CRS

# sourced scripts
from definitions import CONNECT_TO_LAMBDA
if CONNECT_TO_LAMBDA:
    from definitions import DATASET_ID
    from msdlive_utils import get_bytes
    from io import BytesIO

def print_full(df):

    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')


def recur_dictify(df):

    # tech, subtype, feature, is_ccs, cooling_type, capacity factor

    if len(df.columns) == 1:

        if df.values.size == 1: 
            return df.values[0][0]

        return df.values.squeeze()

    grouped = df.groupby(df.columns[0])

    d = {k: recur_dictify(g.iloc[:,1:].drop_duplicates()) for k,g in grouped}

    return d


# if CONNECT_TO_LAMBDA:

#     def open_as_raster(TIFPATH):

#         # reading the retrieved file from the S3 bucket  
#         file_content = get_bytes(DATASET_ID, TIFPATH)
        
#         # wrap the file content in a BytesIO object for use like a file
#         file_stream = BytesIO(file_content)

#         with rasterio.open(file_stream) as src: 
#             array = src.read(1)
#             metadata = src.meta
#             array_nodata = np.where(array == src.nodata, np.nan, 0)
#             array = np.where(array==1, np.nan, array)

#         data_array = pd.DataFrame(array, columns=data_array.x, index=data_array.y) 

#         return data_array, array, metadata


# else:
    
def open_as_raster(TIFPATH):

    """This should work with any file that rasterio can open 
    (most often: geoTIFF). The x and y coordinates are generated 
    automatically from the file’s geoinformation, shifted to the 
    center of each pixel (see “PixelIsArea” Raster Space for more 
    information)."""

    TIF_source = "Local"
    TIF_stream = TIFPATH

    if CONNECT_TO_LAMBDA:

        TIF_source = "S3"
        TIF_content = get_bytes(DATASET_ID, TIFPATH)  # reading the retrieved file from the S3 bucket  
        TIF_stream = BytesIO(TIF_content) # wrap the file content in a BytesIO object for use like a file

    # use rioxarray to get lat and long of 
    og_proj_array = rioxarray.open_rasterio(TIF_stream, masked=True) # returns xarray.DataArray
    data_2d = og_proj_array.isel(band=0).values
    og_lons = og_proj_array.x
    og_lats = og_proj_array.y
    data_df = pd.DataFrame(data_2d, columns=og_proj_array.x, index=og_proj_array.y) 
    print(data_df)

    # TODO
    # just need to reproject the row and column names ... !!!!!!!!!!!!!
    # and then need to pivot the data so it's value | lat | lon



    # the BELOW reprojects EVERYTHING EVEN THE CELLS ...
    # proj_4326_array = og_proj_array.rio.reproject("EPSG:4326")
    # proj_lons = proj_4326_array.x #np.array(proj_4326_array.x)
    # proj_lats = proj_4326_array.y # np.array(proj_4326_array.y)
    # data_2d = proj_4326_array.isel(band=0).values
    # data_df = pd.DataFrame(data_2d, columns=proj_lons, index=proj_lats) 

    # data_df = pd.DataFrame(array, columns=data_array.x, index=data_array.y) 


    with rasterio.open(TIF_stream) as src: # returns rasterio.DatasetReader
        
        array = src.read(1)
        metadata = src.meta

        # orginal projected coordinates (albers_conic_crs) to geographic coordinates (geo_crs)
        conic_crs = src.crs # Albers Equal Area Conic CRS (ESRI:102003)
        geo_crs = CRS("EPSG:4326")  # WGS84 (aka.  Albers Equal)
        pyproj_crs = CRS(conic_crs.to_proj4())
        proj_units = pyproj_crs.axis_info[0].unit_name
        transform = src.transform # affine transform from map pixel coors to geo coors
        transformer = Transformer.from_crs(conic_crs, geo_crs, always_xy=True)
        print("\tCRS: ", conic_crs)
        print("\tProjection Units: ", proj_units)
        print("\n")

        
        albers_lon, albers_lat = src.xy(2654, 2891) # row value, column value
        geo_lon, geo_lat = transformer.transform(albers_lon, albers_lat)
        coors = [geo_lat, geo_lon]
        
        cols, rows = np.meshgrid(np.arange(src.width), np.arange(src.height)) 
        xs, ys = rasterio.transform.xy(transform, rows, cols)
        # print(xs)
        # print(transform)
        # print(crs)
        # print(f"LONGITUDE: {lon} \tLATITUDE: {lat}")
        # lon_transformed, lat_transformed = transformer.transform(lon, lat)
        array_nodata = np.where(array == src.nodata, np.nan, 0)
        array = np.where(array==1, np.nan, array)


    print(f"{TIF_source}: {TIF_stream}\n")
    # print(data_df)
    # print(data_array)

    return data_df, array, metadata





    # def get_map_data():

    #     geo_data  = df_location.apply(lambda x: [dict(lat=x.latitude, lon=x.longitude)]*x.Count, axis = 1)
    #     geo_data = reduce(lambda x, y: x + y, geo_data)

    #     return geo_data


    #     print(data_array)

    #     file_content = get_bytes(DATASET_ID, TIFPATH)

    #     with rasterio.open(TIFPATH) as src: 
    #         array = src.read(1)
    #         metadata = src.meta
    #         array_nodata = np.where(array == src.nodata, np.nan, 0)
    #         array = np.where(array==1, np.nan, array)

    #     return data_array, array, metadata # ['driver', 'dtype', 'nodata', 'width', 'height', 'count', 'crs', 'transform']


    # def open_as_raster(TIFPATH):


        # data_array = xr.DataArray.to_dataframe(name='data_array',
        #                                        data=data_array,
        #                                        # coords={

        #                                        # }
        #                                        )
        # print(data_array)



        # rioxarray.Coordinates(data_array.coords)

        #  It combines xarray and rasterio similar to how geopandas 
        # combines functionality from pandas and fiona.


        # with rasterio.open(file_stream) as src: 
        #     array = src.read(1)
        #     crs = src.crs
        #     metadata = src.meta
        #     # full_array = src.values
        #     # lat = src.latitude.values #.max() or .min() or .mean()
        #     # lon = src.longitude.values 
        #     # print(lat)
        #     # print(lon)
        #     array_nodata = np.where(array == src.nodata, np.nan, 0)
        #     array = np.where(array==1, np.nan, array)


        # # use rioxarray to get lat and long of 
        # data_array = rioxarray.open_rasterio(file_stream, masked=True)
        # lon = data_array.x
        # lat = data_array.y


    # def get_map_data():

    #     geo_data  = df_location.apply(lambda x: [dict(lat=x.latitude, lon=x.longitude)]*x.Count, axis = 1)
    #     geo_data = reduce(lambda x, y: x + y, geo_data)

    #     return geo_data

def create_datashaded_scatterplot(df):

    dataset = hv.Dataset(df)
    scatter = datashade(
        hv.Scatter(dataset, kdims=["x"], vdims=["y"])
    ).opts(width=800, height=800)

    return scatter



def update_plot(df):
    
    scatter = create_datashaded_scatterplot(df)
    components = to_dash(app, [scatter])

    return components.children

