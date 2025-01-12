#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# DEV: https://gridcerf.dev.msdlive.org/
# PROD: https://gridcerf.msdlive.org/

# CLIENT (BROWSER) PATHS
PORT = int(os.environ.get("PORT", 8060))
REQUESETS_PATHNAME_PREFIX = "/"

CONNECT_TO_LAMBDA = True

# FILE PATHS
# MAPBOX_TOKEN = open("../../mapbox_token.py").read() # mapbox api token

if CONNECT_TO_LAMBDA:

    print("DEPLOYMENT 16")

    SERVE_LOCALLY = False
    DATASET_ID = "1ffea-emt93" # MSD-LIVE added dataset id that goes to DEV
    DATA_DIR = ""
    LAMBDA_TASK_ROOT = os.getenv('LAMBDA_TASK_ROOT')
    DIR = os.path.join(LAMBDA_TASK_ROOT, "dash_app")

    if LAMBDA_TASK_ROOT is None:
        print(" ********** ", "LAMBDA_TASK_ROOT is None")
        METADATA_DIR = "./metadata"
        DATA_DIR = "./data"
    else:
        print("********** LAMBDA_TASK_ROOT is ", os.getenv('LAMBDA_TASK_ROOT'))
        METADATA_DIR = os.path.join(DIR, "metadata")
        DATA_DIR = os.path.join(DIR, "data")

else:
    CERF_DATA_DIR = "../../data/msdlive-gridcerf"
    METADATA_DIR = "./metadata"
    DATA_DIR = "./data"
    LAMBDA_TASK_ROOT = ""
    SERVE_LOCALLY = True

print("SERVE_LOCALLY is ", SERVE_LOCALLY)

COMPILED_DIR = os.path.join(CERF_DATA_DIR, "gridcerf/compiled/compiled_technology_layers")
OUTDIR = "tmp"

# REMINDER = "It's coors = (lat, lon) and ... LON = COLS = X ... LAT = ROWS = Y"
