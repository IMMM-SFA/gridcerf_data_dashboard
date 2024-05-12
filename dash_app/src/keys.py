#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ssp_d = {
	"ssp2": "SSP2 - 'Middle of the Road'",
	"ssp3": "SSP3 - 'A Rocky Road'",
	"ssp5": "SSP5 - 'Taking the Highway'",
}

tech_d = {
		"coal": "Coal",
		"nuclear": "Nuclear",
		"gas": "Natural Gas",
		"biomass": "Biomass",
		"solar": "Solar",
		"refinedliquids": "Refined Liquids",
		"wind": "Wind",
		"geothermal": "Geothermal"
		  }

subtech_d = {
    "conventional": "Conventional",
    "gen3": "Generation 3 Reactor", # or could be Gen 3 Small Modular Reactor
    "gen2": "Generation 2 Reactor",
    "igcc": "Integrated Gasification Combined Cycle (IGCC)",
    "cc": "Combined Cycle (CC)",
    "ct": "Combustion Turbine (CT)",
    "csp": "Concentrating Solar Power (CSP)",
    "pv": "Photovoltaic (PV)",
    "turbine": "Combustion Turbine (CT)",
    "onshore": "Onshore",
    "offshore": "Offshore",

    "centralized": "Centralized",
    "enhanced": "Enhanced",

    "smr": "Small Modular Reactor (SMR)",
    "ap1000": "AP1000",
    "lwr": "Light Water Reactor (LWR)"
}

is_ccs_d = { # "Carbon Capture Sequestration (CCS)"
    "ccs": "Yes", # carbon_capture_sequestration
    "with-ccs": "Yes",
    "no-ccs": "No"
}

cooling_d = {
	"dry": "Dry",
	"dry-hybrid": "Dry-Hybrid",
	"oncethrough": "Once-through",
	"recirculating": "Recirculating",
	"recirculating-seawater": "Recirculating-Seawater",
	"pond": "Pond",
	"no-cooling": "No Cooling",
	# "centralized enhanced dry-hybrid": "Centralized Enhanced Dry-Hybrid",
	# "centralized enhanced recirculating": "Centralized Enhanced Recirculating"
}

feature_d = {
	"hubheight80": "Hub Height 80 meters (m)",
	"hubheight100": "Hub Height 100 meters (m)",
	"hubheight110": "Hub Height 110 meters (m)",
	"hubheight120": "Hub Height 120 meters (m)",
	"hubheight140": "Hub Height 140 meters (m)",
	"hubheight160": "Hub Height 160 meters (m)",
}

keys_d = {
	"ssp": ssp_d,
	"tech": tech_d,
	"subtech": subtech_d,
	"is_ccs": is_ccs_d,
	"cooling_type": cooling_d,
	"feature": feature_d
}



