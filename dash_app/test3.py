import dash_leaflet as dl
from dash import Dash

# Custom icon as per official docs https://leafletjs.com/examples/custom-icons/
custom_icon = dict(
    iconUrl='https://leafletjs.com/examples/custom-icons/leaf-green.png',
    shadowUrl='https://leafletjs.com/examples/custom-icons/leaf-shadow.png',
    iconSize=[38, 95],
    shadowSize=[50, 64],
    iconAnchor=[22, 94],
    shadowAnchor=[4, 62],
    popupAnchor=[-3, -76]
)
# Small example app.
app = Dash()
app.layout = dl.Map([
    dl.TileLayer(),
    dl.Marker(position=[55, 10]),
    dl.Marker(position=[57, 10], icon=custom_icon),
], center=[56, 10], zoom=6, style={'height': '50vh'})

if __name__ == '__main__':
    app.run_server()


# import dash
# from dash import dcc, html
# import dash_leaflet as dl

# app = dash.Dash(__name__)

# # Sample data
# markers = [
#     {"position": [37.7749, -122.4194], "label": "San Francisco"},
#     {"position": [34.0522, -118.2437], "label": "Los Angeles"},
#     {"position": [40.7128, -74.0060], "label": "New York"}
# ]

# # Create markers for the map
# marker_components = [
#     dl.Marker(position=marker['position'], children=[
#         dl.Tooltip(marker['label'])
#     ]) for marker in markers
# ]

# app.layout = html.Div([
#     dcc.Store(id='map-config', data={
#         'initial_zoom': 13,
#         'initial_center': [37.7749, -122.4194]  # San Francisco coordinates
#     }),
#     dl.Map(id='map', center=[37.7749, -122.4194], zoom=13, children=[
#         dl.TileLayer(),
#         *marker_components
#     ]),
#     html.Script('''
#     document.addEventListener('DOMContentLoaded', function() {
#         var map = document.querySelector('#map')._leaflet_map;
#         var markers = map._layers;

#         function updateMarkerSizes() {
#             var zoom = map.getZoom();
#             var sizeInPixels = 10; // Desired constant size in pixels
            
#             for (var id in markers) {
#                 var marker = markers[id];
#                 if (marker instanceof L.Marker) {
#                     // Update marker icon size based on the zoom level
#                     marker.setIcon(L.divIcon({
#                         className: 'custom-marker',
#                         html: '<div style="width: '+sizeInPixels+'px; height: '+sizeInPixels+'px; background: red; border-radius: 50%;"></div>'
#                     }));
#                 }
#             }
#         }

#         // Update marker size when zoom changes
#         map.on('zoomend', updateMarkerSizes);
#         updateMarkerSizes(); // Initial call to set sizes
#     });
#     '''),
#     # html.Style('''
#     # .custom-marker {
#     #     width: 10px; /* Change this to your desired size */
#     #     height: 10px; /* Change this to your desired size */
#     #     background: red;
#     #     border-radius: 50%;
#     #     text-align: center;
#     #     line-height: 10px; /* Change this to your desired size */
#     #     color: white;
#     # }
#     # ''')
# ])

# if __name__ == '__main__':
#     app.run_server(debug=True)