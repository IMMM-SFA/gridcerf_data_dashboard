#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import matplotlib.colors as mcolors

# client (browser) paths
PORT = int(os.environ.get("PORT", 8060))
REQUESETS_PATHNAME_PREFIX = "/"

CONNECT_TO_LAMBDA = False

if CONNECT_TO_LAMBDA:
    DATASET_ID = "1ffea-emt93" # MSD-LIVE added dataset id that goes to DEV

REMINDER = "It's coors = (lat, lon) and ... LON = COLS = X ... LAT = ROWS = Y"


CMAP_BLACK = mcolors.ListedColormap(['black'])
# CMAP_BLACK = mcolors.ListedColormap((0,0,0,0.8))

token = open("../../mapbox_token.py").read() # mapbox_api_token = os.getenv("MAPBOX_ACCESS_TOKEN")

plotly_config = {'displaylogo': False,
                'modeBarButtonsToRemove': ['autoScale', 'resetScale'], # High-level: zoom, pan, select, zoomIn, zoomOut, autoScale, resetScale
                'toImageButtonOptions': {
                    'format': 'png', # one of png, svg, jpeg, webp
                    'filename': 'custom_image',
                    'height': None,
                    'width': None,
                    'scale': 6 # Multiply title/legend/axis/canvas sizes by this factor
                        }
                  }


# https://medium.com/plotly/introducing-dash-holoviews-6a05c088ebe5
# https://examples.holoviz.org/gallery/nyc_taxi/nyc_taxi.html
# https://towardsdatascience.com/displaying-a-gridded-dataset-on-a-web-based-map-ad6bbe90247f
# https://holoviews.org/getting_started/Customization.html
# https://holoviews.org/reference/elements/matplotlib/Points.html
# https://stackoverflow.com/questions/57588857/matplotlib-listedcolormap-transparent-color
# https://datashader.org/getting_started/Pipeline.html
# https://holoviews.org/_modules/holoviews/operation/datashader.html
# https://discourse.holoviz.org/t/how-to-set-geoviews-map-extent-programmatically-in-panel-dashboard/1181
# https://geog-312.gishub.org/book/geospatial/leafmap.html
# https://leafmap.org/get-started/
# https://ai-incubator.pnnl.gov/chat/fy0s5mBnqiTK9YE6C4xB8YrmQv0YMnyLsjA7
# https://www.google.com/search?q=holoviews+albers+conic&rlz=1C5CHFA_enUS1091US1091&oq=holoviews+albers+conic&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIHCAEQIRigATIHCAIQIRigATIHCAMQIRigATIHCAQQIRigAdIBCDQ0NTdqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8
# https://geoviews.org/user_guide/Projections.html


# https://plotly.com/python/mapbox-layers/
# learn Mapbox GL JS: https://docs.mapbox.com/mapbox-gl-js/guides/migrate/
# layer building in holoviz: https://github.com/holoviz/holoviews/issues/3882
# remove frame around plot: https://discourse.holoviz.org/t/remove-frame-around-plot/4023/3
# LINKED SELECTIONS ** https://medium.com/plotly/introducing-dash-holoviews-6a05c088ebe5
# foreal example:
#	https://github.com/niowniow/foreal/blob/ea0cb314f3a408f7fd544528ce83e03ca2269b12/foreal/webportal/app.py#L48
# 	https://github.com/niowniow/foreal/blob/ea0cb314f3a408f7fd544528ce83e03ca2269b12/foreal/webportal/app.py#L48
#	https://github.com/niowniow/foreal/blob/ea0cb314f3a408f7fd544528ce83e03ca2269b12/foreal/webportal/__init__.py
#	https://github.com/niowniow/foreal/blob/ea0cb314f3a408f7fd544528ce83e03ca2269b12/foreal/webportal/shared.py

# stocknews example:
#	https://github.com/troyscribner/stocknews/tree/6565a854a3469c93b42f2a871301469aa6b9bd04
# of interest: mapboxgl dash python
# click event: does dash python support mapboxgl
#
