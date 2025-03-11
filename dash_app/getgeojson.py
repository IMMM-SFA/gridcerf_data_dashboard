import geopandas as gpd

# shapefile_path = "data/shapefiles/conus_state_boundary_epsg4326/conus_state_boundary_epsg4326.shp"
# shapefile_path = "data/shapefiles/conus_transmission_epsg4326/conus_transmission_epsg4326.shp"
shapefile_path = "data/state_shp_albers/state_shp_albers.shp"

gdf = gpd.read_file(shapefile_path)

print(gdf)
# target_crs = "ESRI:102003"
# gdf_albers = gdf.to_crs(target_crs)
# print(gdf_albers)

gdf.to_file("data/states_polygons_albers.geojson", driver="GeoJSON")
