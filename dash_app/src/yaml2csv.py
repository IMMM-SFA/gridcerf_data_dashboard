#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# standard libraries
import os
import csv
import sys
import yaml
import pprint

# data manipulation libraries
import pandas as pd
from pandas import json_normalize

# sourced scripts
from keys import keys_d


def create_tech_pathways_csv(yaml_inpath, outpath):

	with open(yaml_inpath, "r") as f:
		data = yaml.full_load(f)
		data_target = data["msdlive-gridcerf"][0]["gridcerf"][1]['compiled'][1]["compiled_technology_layers"]

	# to pretty print all data
	# pprint.pprint(data, depth=6)

	data_list = []

	for i in range(len(data_target)):

		# row = {}
		
		for ssp_key, value in data_target[i].items():
			year_data = data_target[i][ssp_key]

			for i in range(len(year_data)):

				for year_key, value in year_data[i].items():
					tech_data = year_data[i][year_key]

					for i in range(len(tech_data)):

						for tech_key, value in tech_data[i].items():
							file_data = tech_data[i][tech_key]

						for file in file_data:

							path_list = file.replace(".tif", "").replace("gridcerf_", "").split("_")
							path_list.append(file)
							path = os.path.join(ssp_key, year_key, tech_key, file)
							fname = file

							# remap
							og_tech = path_list[0]
							path_list[0] = keys_d["tech"][path_list[0]]
							tech = path_list[0]

							og_subtech = path_list[1]
							path_list[1] = keys_d["subtech"][path_list[1]]

							if len(path_list) < 6:
								subtech = path_list[1]
								feature = "--"
								og_feature = feature
								ccs = path_list[2]
								cooling = path_list[3]
								cf = "--"

							if path_list[0] == keys_d["tech"]["nuclear"]: #6
								og_subtech = og_subtech + " " + path_list[2]
								subtech = path_list[1] + " " + keys_d["subtech"][path_list[2]]
								ccs = "--"

							if path_list[0] == keys_d["tech"]["geothermal"]: #6
								og_subtech = og_subtech + " " + path_list[2]
								subtech = path_list[1] + " " + keys_d["subtech"][path_list[2]] 
								# Centralized Enhanced Dry-Hybrid
								feature = "--"
								og_feature = feature
								ccs = "--"
								cooling = path_list[3]
								cf = path_list[4]

							if path_list[0] == keys_d["tech"]["wind"]: #6
								subtech = path_list[1]
								feature = keys_d["feature"][path_list[2]]
								og_feature = path_list[2]
								ccs = "--"
								cooling = path_list[3]
								cf = path_list[4]
							
							if path_list[0] == keys_d["tech"]["solar"]: #6
								og_subtech = og_subtech + " " + path_list[2]
								subtech = path_list[1] + " " + keys_d["subtech"][path_list[2]]
								feature = "--"
								og_feature = feature
								ccs = "--"
								cooling = path_list[3]

								cf = path_list[4]

							ccs_og = ccs
							if ccs != "--":
								ccs = keys_d["is_ccs"][ccs]

							cooling_og = cooling
							try:
								if cooling != "--":
									cooling = keys_d["cooling_type"][cooling]
							except Exception:
								print(cooling)


							if ssp_key.startswith("ssp"):
								ssp = keys_d["ssp"][ssp_key]


							path_list = [ssp_key, year_key, tech, subtech, feature, ccs, cooling, cf, fname, path]

							# ssp_key = keys_d["ssp"][ssp_key]

							uid_key = path.replace("/", "_").replace("gridcerf_", "").replace(".tif", "")
							
							row_dict = {

										"ui_ssp": ssp, 
										"ui_year": year_key,
										"ui_tech": tech, 
										"ui_subtype": subtech, 
										"ui_feature": feature, 
										"ui_is_ccs": ccs, 
										"ui_cooling_type": cooling, 
										"ui_capacity_factor": cf, 

										"fname": fname, 
										"fpath": path,

										# "uid_key": uid_key,

										"ssp": ssp_key,
										"tech": og_tech, 
										"subtype": og_subtech, 
										"feature": og_feature, 
										"is_ccs": ccs_og, 
										"cooling_type": cooling_og, 
										"cap_factor": cf

										}
										# key = fname **
							
							data_list.append(row_dict)


	print(data_list[0])

	keys = data_list[0].keys()
	with open(outpath, 'w', newline='') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(data_list)

	# df = pd.json_normalize(data_target)




