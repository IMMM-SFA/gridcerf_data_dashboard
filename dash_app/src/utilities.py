#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# data manipulation
import numpy as np
import pandas as pd

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



# def rasterio_open():
   
#     with rasterio.open(TIF_stream) as src: # returns rasterio.DatasetReader
        
#         array = src.read(1)
#         metadata = src.meta

#         # orginal projected coordinates (albers_conic_crs) to geographic coordinates (geo_crs)
#         # conic_crs = src.crs # Albers Equal Area Conic CRS (ESRI:102003)
#         geo_crs = CRS("EPSG:4326")  # WGS84 (aka.  Albers Equal)
#         pyproj_crs = CRS(source_crs.to_proj4())
#         proj_units = pyproj_crs.axis_info[0].unit_name
#         transform = src.transform # affine transform from map pixel coors to geo coors
#         transformer = Transformer.from_crs(source_crs, geo_crs, always_xy=True)
#         print("\tCRS: ", source_crs)
#         print("\tProjection Units: ", proj_units)
#         print("\n")

        
#         albers_lon, albers_lat = src.xy(2654, 2891) # row value, column value
#         geo_lon, geo_lat = transformer.transform(albers_lon, albers_lat)
#         coors = [geo_lat, geo_lon]
        
#         cols, rows = np.meshgrid(np.arange(src.width), np.arange(src.height)) 
#         xs, ys = rasterio.transform.xy(transform, rows, cols)
#         # print(xs)
#         # print(transform)
#         # print(crs)
#         # print(f"LONGITUDE: {lon} \tLATITUDE: {lat}")
#         # lon_transformed, lat_transformed = transformer.transform(lon, lat)
#         array_nodata = np.where(array == src.nodata, np.nan, 0)
#         array = np.where(array==1, np.nan, array)


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








		# def tif_to_png(tif_path):
		# 	with rasterio.open(tif_path) as src:
		# 		array = src.read(1)  # read the first (and only) band
		# 		array = np.interp(array, (array.min(), array.max()), (0, 255)) #  255 is white and 0 is black
		# 		img = Image.fromarray(array.astype(np.uint8)).resize((src.width, src.height))

		# 		# print(src)
		# 		print(src.bounds)
		# 		# metadata = src.meta # dict_keys(['driver', 'dtype', 'nodata', 'width', 'height', 'count', 'crs', 'transform'])
		# 		# print(metadata['transform']) 
		# 		# print('\n')
		# 		# print(metadata['crs'])
		# 		# crs = src.crs
		# 		# print()
		# 		# lat_max = src.latitude.values.max()
		# 		# lat_min = src.latitude.values.min()
		# 		# lon_max = src.longitude.values.max()
		# 		# lon_min = src.longitude.values.min()
				
		# 		# print(lat_max, lat_min, lon_max, lon_min)
		# 		return img, src.bounds, [src.width, src.height], [-171.791110603, 18.91619, -66.96466, 71.3577635769]

		# # TIFPATH = os.path.join(COMPILED_DIR, fpath)
		# # print(TIFPATH)
		# # data_array, array, metadata = open_as_raster(TIFPATH=TIFPATH) 

		# PNG, bounds, width_height, bbox = tif_to_png(tif_path=TIFPATH)
		
		# # PNG = array
		# print(array.shape)