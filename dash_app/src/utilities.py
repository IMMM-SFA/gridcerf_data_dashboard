#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import rasterio
import rioxarray
import numpy as np
import pandas as pd

# MSD-LIVE added imports:
from msdlive_utils import get_bytes
from io import BytesIO

# MSD-LIVE added dataset id that goes to DEV
DATASET_ID = "1ffea-emt93"

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


def open_as_raster(TIFPATH):



    """This should work with any file that rasterio can open 
    (most often: geoTIFF). The x and y coordinates are generated 
    automatically from the file’s geoinformation, shifted to the 
    center of each pixel (see “PixelIsArea” Raster Space for more 
    information)."""

#     print(data_array)

#     file_content = get_bytes(DATASET_ID, TIFPATH)

#     with rasterio.open(TIFPATH) as src: 
#         array = src.read(1)
#         metadata = src.meta
#         array_nodata = np.where(array == src.nodata, np.nan, 0)
#         array = np.where(array==1, np.nan, array)

#     return data_array, array, metadata # ['driver', 'dtype', 'nodata', 'width', 'height', 'count', 'crs', 'transform']


# def open_as_raster(TIFPATH):
    file_content = get_bytes(DATASET_ID, TIFPATH)
  # wrap the file content in a BytesIO object for use like a file
    file_stream = BytesIO(file_content)

    # data_array = rioxarray.open_rasterio(file_stream, masked=True)
    # data_array
    data_array = None

    with rasterio.open(file_stream) as src: 
        array = src.read(1)
        crs = src.crs
        metadata = src.meta
        array_nodata = np.where(array == src.nodata, np.nan, 0)
        array = np.where(array==1, np.nan, array)

    return data_array, array, metadata
