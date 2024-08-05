# import dash_leaflet as dl
# from dash import Dash

# # Cool, dark tiles by Stadia Maps.
# url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
# attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '
# # Create app.
# app = Dash()
# app.layout = dl.Map([
#     dl.TileLayer(url=url, maxZoom=20, attribution=attribution)
# ], center=[56, 10], zoom=6, style={'height': '50vh'})

# if __name__ == '__main__':
#     app.run_server(debug=True)


#Build Dash app (note: JupyterDash is being used here but will work in external dash app , to see this change last line to "mode=External")

from jupyter_dash import JupyterDash
from dash import Dash, html,dcc,Input, Output
import dash_leaflet as dl
import json
import httpx

# read data
S3_URL = open("Resource_Files\S3_URL.txt").read() # this is my S3 bucket URL saved in txt file for privacy 


# Extract min and max values of the COG , this is used to rescale the COG

titiler_endpoint = "http://localhost:8080"  # titiler docker image running on local .
url = S3_URL


r = httpx.get(
    f"{titiler_endpoint}/cog/statistics",
    params = {
        "url": url,
    }
).json()

minv = (r["1"]["min"])
maxv = (r["1"]["max"])


#get tile map from titiler endpoint and url , and scale to min and max values 

r = httpx.get(
    f"{titiler_endpoint}/cog/tilejson.json",
    params = {
        "url": url,
        "rescale": f"{minv},{maxv}",
        "colormap_name": "viridis"
    }
).json()



#create function which uses "get point" via titiler to get point value. This will be used in dash to get 
#point value and present this on the map 


def get_point_value(lat,lon):

    Point = httpx.get(
        f"{titiler_endpoint}/cog/point/{lon},{lat}",
        params = {
            "url": url,
            "resampling": "average"

        }
    ).json()


    return "{:.2f}".format(float(Point["values"][0]))



app = JupyterDash(__name__)

#create the info panel where our wind speed will be displayed 
info = html.Div( id="info", className="info",
                style={"position": "absolute", "bottom": "10px", "left": "10px", "z-index": "1000"})

#Create app layout 
#dash leaflet used to create map (https://dash-leaflet.herokuapp.com/)
#dl.LayersControl, dl.overlay & dl.LayerGroup used to add layer selection functionality 
app.layout = html.Div([
dl.Map(style={'width': '1000px', 'height': '500px'},
               center=[55, -4],
               zoom=5,
               id = "map",
               children=[
            dl.LayersControl([
                
                   dl.Overlay(dl.LayerGroup(dl.TileLayer(url="https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_nolabels/{z}/{x}/{y}.png",id="TileMap")),name="BaseMap",checked=True),
                   #COG fed into Tilelayer using TiTiler url (taken from r["tiles"][0])
                   dl.Overlay(dl.LayerGroup(dl.TileLayer(url=r["tiles"][0], opacity=0.8,id="WindSpeed@100m")),name="WS@100m",checked=True),
                   dl.LayerGroup(id="layer"),
                # set colorbar and location in app            
                   dl.Colorbar(colorscale="viridis", width=20, height=150, min=minv, max=maxv,unit='m/s',position="bottomright"),
                   info,
                   
])
])
])
# create callback which uses inbuilt "click_lat_lng" feature of Dash leaflet map, extract lat/lon and feed to get_point_value function , WS fed to output id = info (which is info html.div)
@app.callback(Output("info", "children"), [Input("map", "click_lat_lng")])
def map_click(click_lat_lng):

    lat= click_lat_lng[0]
    lon=click_lat_lng[1]
    
    return get_point_value(lat,lon)



app.run_server(debug=True,mode='inline')







# # Map layers
# keys = ["temp_new", "clouds_new", "precipitation_new", "pressure_new", "wind_new"]

# #Color scales
# map_colorscale = {'temp': ['rgba(130, 87, 219, 1)', 'rgba(32, 140, 236, 1)', 'rgba(32, 196, 232, 1)', 'rgba(35, 221, 221, 1)',
#                            'rgba(194, 255, 40, 1)', 'rgba(255, 240, 40, 1)', 'rgba(255, 194, 40,1)', 'rgba(252, 128, 20, 1)'],
#                   'clouds': ['rgba(255, 255, 255, 0.0)', 'rgba(253, 253, 255, 0.1)', 'rgba(252, 251, 255, 0.2)',
#                              'rgba(250, 250, 255, 0.3)', 'rgba(249, 248, 255, 0.4)', 'rgba(247, 247, 255, 0.5)',
#                              'rgba(246, 245, 255, 0.75)', 'rgba(244, 244, 255, 1)', 'rgba(243, 242, 255, 1)',
#                              'rgba(242, 241, 255, 1)', 'rgba(240, 240, 255, 1)']

# markers = [dl.Marker(position=[52.195573, 20.883528])]

# #Colorbars
# colorbar_temp = dl.Colorbar(colorscale=map_colorscale['temp'], id='temp_colorbar',
#                        position='bottomleft', width=200, height=10, min=-30, max=30,
#                         nTicks=8, opacity=0.9, tickValues=[-30, -20, -10, 0, 10, 20, 30])
# colorbar_clouds = dl.Colorbar(colorscale=map_colorscale['clouds'], id='clouds_colorbar',
#                               position='bottomleft', width=200, height=10, min=0, max=100,
#                               nTicks=11, opacity=0.9, tickValues=[0, 20, 40, 60, 80, 100])

# # -----------------

# html.Div(
#         dl.Map(children=[dl.TileLayer(),
#         dl.LayersControl(
#             [dl.BaseLayer(
#                           dl.TileLayer(url=url.format(key)), name=key, checked=key == "temp_new", id=key) for key in keys]
#             +
#             [dl.Overlay(dl.LayerGroup(markers), name="TEST", checked=True)]
#             )
#         ], center=[52.195573, 20.883528], zoom=12, id='map' )
#     , style={'width': '90%', 'height': '50vh', 'margin': "auto", "display": "block", "position": "relative"}),

# # -------------
# @app.callback(
#     Output('???', '???'),
#     Input('???', '???')
# )
# def update_colorbar(key):
#     if key == 'temp_new':
#          return dl.Overlay(colorbar_temp)
#     else:
#         return dl.Overlay(colorbar_clouds)
