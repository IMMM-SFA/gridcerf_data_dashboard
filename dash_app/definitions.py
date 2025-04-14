#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import s3fs

# CLIENT (BROWSER) PATHS
# DEV: https://gridcerf.dev.msdlive.org/
# PROD: https://gridcerf.msdlive.org/
CONNECT_TO_LAMBDA = True
# CONNECT_TO_LAMBDA = False
PORT = int(os.environ.get("PORT", 8060))
REQUESETS_PATHNAME_PREFIX = "/"

# CONNECT TO PATHS IN REPO
METADATA_DIR = "./metadata" # in the repo

# CONNECT TO AWS S3
script_dir = os.path.abspath("../../../") 
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# from gridcerf_credentials import *

s3 = s3fs.S3FileSystem(
    anon=True,
    # key=AWS_Access_Key_ID, 
    # secret=AWS_Secret_Access_Key
)

BUCKET_NAME = "gridcerf-dashboard"
ZARRPATH = os.path.join(BUCKET_NAME, "gridcerf_compiled_zarr") #"../../data/zarr_output" # zarr connection
LAMBDA_TASK_ROOT = ""
SERVE_LOCALLY = False

if CONNECT_TO_LAMBDA:

    print("DEPLOYMENT 30")

    SERVE_LOCALLY = False

    # AWS lambda 
    METADATA_DIR = "./dash_app/metadata" # in the repo
    LAMBDA_TASK_ROOT = os.getenv('LAMBDA_TASK_ROOT', "")
    DIR = os.path.join(LAMBDA_TASK_ROOT, "dash_app")
    DATASET_ID = "w85m1-f5148" # prod # 1ffea-emt93: MSD-LIVE added dataset id that goes to DEV
    if LAMBDA_TASK_ROOT is None:
        print(" ********** ", "LAMBDA_TASK_ROOT is None")
        raise SystemExit
    else:
        print("********** LAMBDA_TASK_ROOT is ", os.getenv('LAMBDA_TASK_ROOT'))

print("SERVE_LOCALLY is ", SERVE_LOCALLY)
# REMINDER = "It's coors = (lat, lon) and ... LON = COLS = X ... LAT = ROWS = Y"
# FILE PATHS
# MAPBOX_TOKEN = open("../../mapbox_token.py").read() # mapbox api token