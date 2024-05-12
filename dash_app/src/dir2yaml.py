#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import sys
import yaml

# find . -name ".DS_Store" -delete 

def dir_to_dict(path):

    directory = {}

    for dirname, dirnames, filenames in os.walk(path):
        dn = os.path.basename(dirname)
        directory[dn] = []

        if dirnames:
            for d in dirnames:
                directory[dn].append(dir_to_dict(path=os.path.join(path, d)))

            for f in filenames:
                directory[dn].append(f)
        else:
            directory[dn] = filenames

        return directory


def make_yaml_dir(dirpath):

    with open("{}.yaml".format(os.path.basename(dirpath)), "w") as f:
        
        yaml.dump(dir_to_dict(path=dirpath), f, default_flow_style=False)
        print("Dictionary written to {}.yaml".format(os.path.basename(p)))


# def make_yaml_dir():

#     if len(sys.argv) == 1:
#         p = os.getcwd()
#     elif len(sys.argv) == 2:
#         p = os.path.abspath(sys.argv[1])
#     else:
#         sys.stderr.write("Unexpected argument {}\n".format(sys.argv[2:]))

#     try:
#         with open("{}.yaml".format(os.path.basename(p)), "w") as f:
#             try:
#                 yaml.dump(dir_to_dict(path=p), f, default_flow_style=False)
#                 print("Dictionary written to {}.yaml".format(os.path.basename(p)))
#             except Exception as e:
#                 print(e)
#     except Exception as e:
#         print(e)
