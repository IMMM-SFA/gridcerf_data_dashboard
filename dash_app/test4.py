import httpx
import dash_leaflet as dl
from dash import Dash, html

# Convert raster to Cloud-optimized GeoTiff 
# gdal_translate input.tif output_cog.tif -of COG -co COMPRESS=LZW


# Set up titiler endpoint and url to COG 
titiler_endpoint = "https://titiler.xyz"
url = "https://storage.googleapis.com/landcover_classes/agb_cog.tif"

# Fetch File Metadata to get min/max rescaling values
r = httpx.get(
    f"{titiler_endpoint}/cog/statistics",
    params = {
        "url": url,
    }
).json()

# Get minimum and maximum raster values
minv = (r["b1"]["min"]) # b1:  band 1
maxv = (r["b1"]["max"])

# Get tile map from titiler endpoint and url, and scale to min and max values 
r = httpx.get(
    f"{titiler_endpoint}/cog/tilejson.json",
    params = {
        "url": url,
        "rescale": f"{minv},{maxv}",
        "colormap_name": "magma"
    }
).json()

# print(r)
print(r["tiles"][0])



app = Dash(__name__)

# colorscale = ['#000004', '#3b0f70', '#8c2981', '#de4968', '#fe9f6d', '#fcfdbf']
colorscale = ["#000000"]

# Create app layout
app.layout = html.Div([
                      dl.Map(
                          style = 
                             {'height': '700px',
                                       'width': '1500px'},
                                    center = [5.814379, 0.843645],
                                    zoom = 12,
                                    id = "leaflet-map",
                                    children = [
                                              dl.LayersControl([
                                                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                                    # url = "https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png",
                                                                    url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                                                    id = "TileMap")),
                                                                name = "Carto DB", checked=False),
                                                             dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                                # url = 'https://api.mapbox.com/styles/v1/mapbox/dark-v10/tiles/{z}/{x}/{y}?access_token=ACCESS TOKEN'
                                                                url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                                                )), 
                                                                name = "Map Box", checked=True),
                                                            # COG fed into Tilelayer using TiTiler url (taken from r["tiles"][0])
                                                            dl.Overlay(dl.LayerGroup(dl.TileLayer(
                                                                                    url = r["tiles"][0], 
                                                                                    opacity = 0.8, 
                                                                                    id = "carbon_2000")), 
                                                                            name = "Carbon_Stock_2000", checked = True),
                                                            dl.LayerGroup(id = "layer"),
                                                            # Set colorbar and location in app
                                                            # dl.Colorbar(colorscale = colorscale, width = 20, height = 150, min = minv, max = maxv, position = "bottomright"),
                                                            # info,
                                                              ])
                                                ]
                             )
])
if __name__ == '__main__':
    app.run_server(debug=True)