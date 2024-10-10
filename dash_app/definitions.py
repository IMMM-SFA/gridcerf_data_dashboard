#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

# CLIENT (BROWSER) PATHS
PORT = int(os.environ.get("PORT", 8060))
REQUESETS_PATHNAME_PREFIX = "/"

CONNECT_TO_LAMBDA = False

# FILE PATHS
if CONNECT_TO_LAMBDA:

    # https://gridcerf.dev.msdlive.org/

    DATASET_ID = "1ffea-emt93" # MSD-LIVE added dataset id that goes to DEV
    DATA_DIR = ""
    LAMBDA_TASK_ROOT = os.getenv('LAMBDA_TASK_ROOT')

    if LAMBDA_TASK_ROOT is None:
        METADATA_DIR = './metadata'
    else:
        METADATA_DIR = os.path.join(LAMBDA_TASK_ROOT, "dash_app", "metadata")

else:
	DATA_DIR = "../../data/msdlive-gridcerf"
	METADATA_DIR = "./metadata"


COMPILED_DIR = os.path.join(DATA_DIR, "gridcerf/compiled/compiled_technology_layers")
OUTDIR = "tmp"

# REMINDER = "It's coors = (lat, lon) and ... LON = COLS = X ... LAT = ROWS = Y"
