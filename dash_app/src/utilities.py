#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# data manipulation
import pandas as pd

def print_full(df):

    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')


def recur_dictify(df):

    # tech, subtype, feature, is_ccs, cooling_type, capacity factor

    if len(df.columns) == 1:

        if df.values.size == 1: 
            return df.values[0][0]

        return df.values.squeeze()

    grouped = df.groupby(df.columns[0])

    d = {k: recur_dictify(g.iloc[:,1:].drop_duplicates()) for k,g in grouped}

    return d