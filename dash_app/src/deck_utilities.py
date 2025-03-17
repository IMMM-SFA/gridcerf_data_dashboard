#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# import ujson # ultra fast JSON encoder and decoder written in pure C with bindings for Python 3.8+
import orjson

# JSON serialization (convert to bytes) of your deck configuration

special_mapping = {
    "autoHighlight": "autoHighlight",       # already camelCase
    "coordinateSystem": "coordinateSystem",   # already camelCase
    "_data": "data",
    "filled": "filled",
    "getFillColor": "getFillColor",
    "getLineColor": "getLineColor",
    "get_line_width": "getLineWidth",
    "id": "id",
    "pickable": "pickable",
    "stroked": "stroked",
    "@@type": "@@type",
    # For the feasibility layer:
    "get_icon": "getIcon",
    "icon_mapping": "iconMapping",
    "get_size": "getSize",
    "size_units": "sizeUnits",
    "get_pixel_offset": "getPixelOffset",
    "get_position": "getPosition",
    "icon_atlas": "iconAtlas"
}

def remove_none_and_internal(obj):
    """
    Recursively remove keys with None values and keys starting with an underscore,
    except for those explicitly handled in special_mapping or with custom rules.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for k, v in obj.items():
            if v is None:
                continue

            # First check if the key is explicitly defined in special_mapping.
            if k in special_mapping:
                new_key = special_mapping[k]
            # Otherwise, if the key is one of the known snake_case keys we want to convert,
            # apply the conversion.
            elif k == "coordinate_system":
                new_key = "coordinateSystem"
            elif k == "auto_highlight":
                new_key = "autoHighlight"
            elif k == "get_fill_color":
                new_key = "getFillColor"
            elif k == "get_line_color":
                new_key = "getLineColor"
            elif k == "get_line_width":
                new_key = "getLineWidth"
            elif k == "get_icon":
                new_key = "getIcon"
            elif k == "icon_mapping":
                new_key = "iconMapping"
            elif k == "get_size":
                new_key = "getSize"
            elif k == "get_pixel_offset":
                new_key = "getPixelOffset"
            elif k == "get_position":
                new_key = "getPosition"
            elif k == "icon_atlas":
                new_key = "iconAtlas"
            # Skip any other key starting with an underscore.
            elif k.startswith('_'):
                continue
            else:
                new_key = k

            new_obj[new_key] = remove_none_and_internal(v)
        return new_obj

    elif isinstance(obj, list):
        return [remove_none_and_internal(item) for item in obj if item is not None]
    else:
        return obj

# Example usage:
# Let's say deck_dict is your deck dictionary.
# cleaned_deck_dict = remove_none_and_internal(deck_dict)
# Then you can serialize with orjson:
# import orjson
# deck_json = orjson.dumps(cleaned_deck_dict, option=orjson.OPT_INDENT_2).decode("utf-8")
# print(deck_json)

def fast_deck_to_json(deck): 

    deck_dict = { "initialViewState": deck.initial_view_state.__dict__,
                #   "layers": deck.layers, 
                # "layers": [convert_layer(layer) for layer in deck.layers] if deck.layers else None,
                    "layers": [layer.__dict__ for layer in deck.layers] if deck.layers else None,
                    "parameters": deck.parameters,
                    "views": [view.__dict__ for view in deck.views] if deck.views else None
                #   "map_style": deck.map_style, 
                #   "map_provider": deck.map_provider, 
                #   "tooltip": deck.tooltip
                    }
    deck_dict["layers"][-1]["icon_atlas"] = str(deck_dict["layers"][-1]["icon_atlas"])
    cleaned_deck_dict = remove_none_and_internal(deck_dict)
    return cleaned_deck_dict
    






# def convert_layer(layer):
#     layer_dict = {}
#     for k, v in layer.__dict__.items():
#         if k == "image":
#             # Convert the image value into a serializable representation.
#             layer_dict[k] = convert_image(v)
#         else:
#             layer_dict[k] = v
#     return layer_dict

# def remove_none(obj):
#     if isinstance(obj, dict):
#         return {k: remove_none(v) for k, v in obj.items() if v is not None}
#     elif isinstance(obj, list):
#         return [remove_none(item) for item in obj if item is not None]
#     else:
#         return obj



# special_mapping = {
#     "autoHighlight": "autoHighlight",       # already camelCase
#     "coordinateSystem": "coordinateSystem",   # already camelCase
#     "_data": "data",
#     "filled": "filled",
#     "getFillColor": "getFillColor",
#     "getLineColor": "getLineColor",
#     "id": "id",
#     "pickable": "pickable",
#     "stroked": "stroked",
#     "@@type": "@@type"
# }


# def remove_none_and_internal(obj):
#     """
#     Recursively remove keys with None values and keys starting with an underscore,
#     except rename the key '_data' to 'data'.
#     """
#     if isinstance(obj, dict):
#         new_obj = {}
#         for k, v in obj.items():
#             if v is None:
#                 continue
#             # Rename '_data' to 'data'
#             if k == "_data":
#                 new_key = "data"
#             if k == "coordinate_system":
#                 new_key = "coordinateSystem"
#             if k == "auto_highlight":
#                 new_key = "autoHighlight"
#             if k == "get_fill_color":
#                 new_key = "getFillColor"
#             if k == "get_line_color":
#                 new_key = "getLineColor"
#             # Skip other keys that start with an underscore
#             if k.startswith('_k'):
#                 continue
#             else:
#                 new_key = k
#             new_obj[new_key] = remove_none_and_internal(v)
#         return new_obj
#     elif isinstance(obj, list):
#         return [remove_none_and_internal(item) for item in obj if item is not None]
#     else:
#         return obj

# # def remove_none_and_internal(obj):
# #     """
# #     Recursively remove keys with None values and keys starting with an underscore.
# #     """
# #     if isinstance(obj, dict):
# #         # Build a new dictionary excluding None values and keys starting with '_'
# #         return {
# #             k: remove_none_and_internal(v)
# #             for k, v in obj.items()
# #             if v is not None and not k.startswith('_k')
# #         }
# #     elif isinstance(obj, list):
# #         # Process each item in the list.
# #         return [remove_none_and_internal(item) for item in obj if item is not None]
# #     else:
# #         return obj


    print('\n')
    # deck_dict = deck.to_json()
    # d = json.loads(deck_dict)
    # print(d["layers"][0].keys())
    # print(d["layers"][1].keys())
    # print(d["layers"][2].keys())
    # print(d["layers"][-1].keys())
    # print(len(deck.layers))
    # print(layers[0].keys())
    # print(layers[1].keys())
    # print(layers[2].keys())
    # print(layers[3].keys())
    print('\n')   
    # deck_dict = fast_deck_to_json(deck)
    # deck_json = orjson.dumps(deck_dict).decode("utf-8")
    # print(len(deck_dict["layers"]))
    # print(deck_dict["layers"][0]["pickable"])
    # print(deck_dict["layers"][0].keys())
    # print(deck_dict["layers"][1].keys())
    # print(deck_dict["layers"][-1].keys())
    # print(deck_dict["layers"][-1]["iconAtlas"])
    # print(type(deck_dict["layers"][-1]["iconAtlas"]))
    # print(deck_dict["layers"][3].keys())
    # print(deck_dict["layers"][-1].keys())
    # deck_json = orjson.dumps(deck_dict, default=default).decode("utf-8")
    # deck_json = orjson.dumps(deck_dict).decode("utf-8")



    # def remove_none(obj):
    #     if isinstance(obj, dict):
    #         return {k: remove_none(v) for k, v in obj.items() if v is not None}
    #     elif isinstance(obj, list):
    #         return [remove_none(item) for item in obj if item is not None]
    #     else:
    #         return obj

    # def convert_image(image_obj):
    #     # If the image is an SVG or has a specific method to return its data,
    #     # you can use that method. For now, we'll just use its string representation.
    #     return str(image_obj)



    # def to_serializable(obj):
    #     if isinstance(obj, (str, int, float, bool)) or obj is None:
    #         return obj
    #     if isinstance(obj, list):
    #         return [to_serializable(item) for item in obj if item is not None]
    #     if isinstance(obj, dict):
    #         return {k: to_serializable(v) for k, v in obj.items() if v is not None}
    #     if hasattr(obj, '__dict__'):
    #         print(obj)
    #         return to_serializable(vars(obj))
    #     type_name = str(type(obj)).lower()
    #     if 'svg' in type_name or 'image' in type_name:
    #         print(type_name)
    #         return str(obj)
    #     return str(obj)

    # def default(obj):
    #     if obj is None:
    #         return []  # or some default coordinate, e.g. [0, 0]
    #     if hasattr(obj, '__dict__'):
    #         return obj.__dict__
    #     raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    # deck_dict = fast_deck_to_json(deck)
    # print(deck_dict["layers"][0].keys())
    # print(deck_dict["layers"][-1].keys())
    # deck_json = orjson.dumps(deck_dict, default=default).decode("utf-8")
    # deck_json = orjson.dumps(deck_dict).decode("utf-8")
    
    # deck_json = deck.to_json() 
    # d = json.loads(deck_json)


# def style_map_icons2(df_coors_long):

#     icon_data = {
#         "url": "/assets/icons/map_icons/black_square.svg",
#         "width": 242,
#         "height": 242,
#         "anchorY": 121, # set to 0 if want to position it at the bottom center of the icon
#         "anchorX": 121, # center of X
#     }
    
#     df_coors_long["icon_data"] = np.where(df_coors_long.index >= 0, icon_data, None)
    
#     return df_coors_long 



    # def default(obj):
    #     if hasattr(obj, '__dict__'):
    #         return obj.__dict__
    #     raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


    # def remove_nulls(obj):
    #     # If it's a dictionary, create a new dictionary without keys that have None as value.
    #     if isinstance(obj, dict):
    #         return {k: remove_nulls(v) for k, v in obj.items() if v is not None}
    #     # If it's a list, apply the function to each element.
    #     elif isinstance(obj, list):
    #         return [remove_nulls(item) for item in obj]
    #     # Otherwise, return the object as is.
    #     else:
    #         return obj

    # data_no_null = remove_nulls(deck_json)

    # with open("deck_config2.json", "w") as f:
    #     f.write(deck_json)

    # print(deck_dict.keys())
    # deck.to_json = lambda: fast_deck_to_json(deck)
    # print('go')
    # orjson.dumps(deck_dict).decode("utf-8")

    # JSON → Python: json.loads(json_string)
    # Python → JSON: json.dumps(python_object, indent=2)


    # print(deck_dict["views"])
    # print(d["views"]) 

    # with open("deck_config2.json", "w") as f: 
    #     # json.dump(deck_dict, f, indent=4)
    #     f.write(deck_json)

    # print("Dictionaries are equal: ", deck_dict["views"] == d["views"])
    # diff_keys1 = set(d.keys()) - set(deck_dict.keys())
    # print("Keys in dict1 but not in dict2:", diff_keys1)



    # print("JSON: ", end-start)
    # deck_json_str = deck.to_json()
    # deck_config = deck.to_dict() # Get the deck configuration as a dictionary 
    # deck_json = ujson.dumps(deck_config) # Use ujson for faster serialization

    # print(json.loads(deck.to_json()))
    # list('initialViewState', 'layers', 'parameters', 'views')
    # print(d['initialViewState'])
    # print(d)




# from functools import lru_cache

# def styling_dict_to_hashable(styling_dict): 
#     print(styling_dict.items())
#     return frozenset(styling_dict.items())

# @lru_cache(maxsize=32) 
# def cached_plot_static_layers(styling_hashable): 
#     styling_dict = dict(styling_hashable) 
#     hard_grey = [60, 60, 60] 
#     black = [0, 0, 0]
#     print("HERE")

# @lru_cache(maxsize=1) 
# def cached_dynamic_data(): 
#     df = pd.read_csv("data/dynamic_layer_data/gridcerf_biomass_conventional_no-ccs_dry.csv") 
#     return style_map_icons2(df)

# @lru_cache(maxsize=32) 
# def plot_static_layers_cached(styling_hashable): 
#     # Convert back to a dictionary 
#     styling_dict = dict(styling_hashable)
