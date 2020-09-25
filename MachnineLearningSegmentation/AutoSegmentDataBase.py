# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:36:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna
            Center for Medical Physics and Biomedical Engineering
                
"""
# Global imports
import os

# Custom imports 
import BackendFunctions as Backend
from Inference import AutoSegmentation

if __name__ == '__main__' :
    dims = (1024, 1024)
    path_data_base = Backend.clean_path_selection("Please select data base which contains all volume measurements")
    AS = AutoSegmentation(dims, dims, dims)
    # Add logic to go through whole data base and infer one vol. after another
    sub_dirs = Backend.get_subdirs_only(path_data_base)
    for root, dirs, files in os.walk(sub_dirs) :
        scans, path_vol_measurement = AS.load_data_from_folder(root)
        masks = AS.apply_trained_net(scans)
        AS.check_predicted_masks(scans, masks, path_vol_measurement)
        
    print(f"Done applying inference to all b-Scans of all volumes in {path_data_base")
    print(":) :) :)")