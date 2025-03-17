#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import s3fs

# source in credentials and connect to s3 bucket
script_dir = os.path.abspath("../../../") # "../../../git_repositories"
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from gridcerf_credentials import *

s3 = s3fs.S3FileSystem(
    anon=False,
    key=AWS_Access_Key_ID,
    secret=AWS_Secret_Access_Key
)

# local
local_path = "../../data/zarr_output"

# cloud 
bucket_name = "gridcerf-dashboard"
s3_dest = f"{bucket_name}/gridcerf_compiled_zarr"

# if folder exists, delete it recursively
if s3.exists(s3_dest):
    s3.rm(s3_dest, recursive=True)
    print(f"Emptied {s3_dest} from bucket {bucket_name}")

# copy to s3
s3.put(local_path, s3_dest, recursive=True)

print("Copied!")
