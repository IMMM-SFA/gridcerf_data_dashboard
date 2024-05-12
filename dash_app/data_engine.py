#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

sys.path.append("src")
from dir2yaml import make_yaml_dir
from yaml2csv import create_tech_pathways_csv


if __name__ == "__main__":

	# msdlive download the data dir locally

	# make YAML of the data dir
	# make_yaml_dir(dirpath="../../data/msdlive-grdcerf") 

	# convert YAML to CSV tech pathways 
	create_tech_pathways_csv(yaml_inpath="../../data/msdlive-gridcerf.yaml", 
							 outpath="../../data/msdlive_tech_paths.csv")
