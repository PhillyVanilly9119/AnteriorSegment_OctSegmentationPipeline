# -*- coding: utf-8 -*-
"""
Created on Wed May 20 17:10:58 2020

@author: Philipp
"""

# =============================================================================
#     if flag_fromJSON:
# # =============================================================================
# #     TODO: Add logic to alternatively load model from .JSON file    
# # =============================================================================
#         pass
#     else:
#         if path is None:
#             path = askdirectory(title='Please a *.h5-file containing a network')
#             
#         # check if path contains images
#         h5_file = None
#         for f in os.listdir(path):
#             h5_file = f if f.endswith('.h5') else FileNotFoundError("Directory [DOES NOT CONTAIN A *.h5-file]!")
#             print(f"Loading network model from file << {h5_file} >>")
#             break
#         if h5_file is not None:
#             model = load_model(h5_file)
#             print("Loaded model from disk")
# =============================================================================