#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

def print_full(df):

    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')
    

def sum_rasters(raster_list) -> np.ndarray:
    """Sum all rasters in the input list and return a reclassified array having
    values of 0 == suitable and 1 == unsuitable.
    
    :param raster_list:                 List of full path with file name and extensions to the input raster files
    :type raster_list:                  list 
    
    :return:                            A 2D array of 0, 1 suitablity designation
    
    """
    
    for idx, raster in enumerate(raster_list):

        if idx == 0:
            final_array = raster_to_array(raster).astype(np.float32)

        else:

            this_array = raster_to_array(raster)
            final_array += this_array
                
    # reclassify array back to 0 == suitable, 1 == unsuitable
    return np.where(final_array == 0, 0, 1)
    

def raster_to_array(raster_file) -> np.ndarray:
    """Read in a raster file and return a 2D NumPy array.
    
    :param raster_file:                 Full path with file name and extension to the input raster file 
    :type raster_file:                  str 
    
    :return:                            A 2D array
    
    """
    
    with rasterio.open(raster_file) as src:
        return src.read(1)

    
def plot_raster(arr, title):

    fig, ax = plt.subplots(figsize=(10, 5))

    # Define the colors you want
    cmap = ListedColormap(["grey", "navy"])

    # Define a normalization from values -> colors
    norm = colors.BoundaryNorm([0, 1], 2)

    raster_plot = ax.imshow(arr, cmap=cmap)

    # Add a legend for labels
    legend_labels = {"grey": "0", "navy": "1"}

    patches = [Patch(color=color, label=label)
               for color, label in legend_labels.items()]

    ax.legend(handles=patches,
              bbox_to_anchor=(1.15, 1),
              facecolor="white")

    ax.set_title(title)

    ax.set_axis_off()
    
    return ax


    