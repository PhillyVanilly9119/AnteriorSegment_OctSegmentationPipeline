# -*- coding: utf-8 -*-
"""
Created on Wed May 20 17:10:58 2020

@author: Philipp
"""
# Lib imports
import os
import cv2
import glob
import numpy as np
import scipy
from tqdm import tqdm
from PIL import Image
import matplotlib.pyplot as plt

# Local imports
from ApplyNetwork4AutoSegmentation import AutoSegmentation

# =============================================================================
                        ### I/O data handling ###
# =============================================================================
def open_and_close(image, kernel_size=3) :
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)

# ============================================================================= 
                            ### image processing and handling ###
# =============================================================================
def resize_no_interpol(image, dims) :
    assert np.size(dims) == 2, "[DIMENSION ERROR] please enter 2-D tuple as output-dimensions"
    return cv2.resize(image,
                      (dims[0], dims[1]), 
                      fx = 0, fy = 0,
                      interpolation=cv2.INTER_NEAREST)

def load_images(path, name, dims, img_dtype='.png') :
    print(f"Loading all images >>{name+img_dtype}<< from >>{path}<<...")
    assert np.size(dims)==2, f"[RESHAPING DIMENSIONS MISMATCH] Please enter tuple containing (height, width)"
    h, w = dims[0], dims[1]
    files = os.listdir(path)
    try :
        if any([os.path.isfile(os.path.join(path, f, name + img_dtype)) for f in files]) :
            img_stack = [np.asarray(Image.open(os.path.join(path, f, name + img_dtype)).resize((h,w))) for f in tqdm(files)]
    except FileNotFoundError :
        print(f"There were no images named >>{name}<< found in any sub-directory of >>{path}<<")
    
    print("Done loading images!") 
    return np.dstack(img_stack)

# ============================================================================= 
                        ### Process data (sets) ###
# =============================================================================
def determine_thickness_for_database() :        
    """
    TODOs/ necessary functions:
        -> 
        "segment entire volume"
        "write map into path"
    """        
    main_path = AutoSegmentation.clean_path_selection("Select main path of data to evaluate") 
    # 1) List with all folders containing volume measurements
    list_measurements = AutoSegmentation.fast_scandir(main_path)
    SAVE_PATHS_MAPS = os.path.join(main_path, 'EvaluatedData')
    if not os.path.exists(SAVE_PATHS_MAPS):
        os.makedirs(SAVE_PATHS_MAPS)
    # MAIN LOOP for thickness calcs
    for c_folder, folder in tqdm(enumerate(list_measurements)) :
        SCAN_LIST = []
        # 1: Find and sort all B-Scans in order
        list_valid_bScans = glob.glob(os.path.join(folder, 'CorrectScans', "*.bmp"))
        if list_valid_bScans :
            list_valid_bScans.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
            for path in list_valid_bScans :
                string = path.split('\\')[-1].split('.bmp')[0]
                SCAN_LIST.append(int(string))
        list_invalid_bScans = []
        # ERROR HANDLE if ML-data-dir does not exist
        folder_ml_data = os.path.join(folder, 'IncorrectScans', 'Data_Machine_Learning')
        if not os.path.exists(folder_ml_data) :
            os.mkdir(folder_ml_data)
        manual_folders = [f.path for f in os.scandir(os.path.join(folder,
                                                                  'IncorrectScans',
                                                                  'Data_Machine_Learning')) if f.is_dir()]
        if manual_folders :
            for ml_folder in manual_folders:
                list_invalid_bScans.append(ml_folder)
            list_invalid_bScans.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))    
        
        THICKNESS_MAP = []
        # Process every B-Scan in volume
        counter_invalid = 0
        counter_valid = 0
        print(f"\nCalculating thickness for Volume No.{c_folder+1} in a total of {len(list_measurements)} measurements...")
        for scan in tqdm(range(128)) :
            if scan not in SCAN_LIST :
                # Load mask
                mask_file = os.path.join(list_invalid_bScans[counter_invalid], 'mask.png')
                if os.path.isfile(mask_file) :
                    mask = np.asarray(Image.open(mask_file))
                    _, mask = DP.create_tripple_mask(mask)
                    save_name = os.path.join(folder, 'CorrectScans')
                    plt.imsave(os.path.join(save_name, f'{int(scan):03}.bmp'), 
                               mask, cmap='gray', format='bmp')
                    THICKNESS_MAP.append(AutoSegmentation.find_boundaries_in_mask(mask))   
                    counter_invalid += 1
                else :
                    print(f"Could not load scan No.{scan} from mask No.{counter_invalid}")                
            else :
                mask = np.asarray(Image.open(list_valid_bScans[counter_valid]).convert('L'))
                THICKNESS_MAP.append(AutoSegmentation.find_boundaries_in_mask(mask))
                counter_valid += 1
                
        THICKNESS_MAP = np.asarray(THICKNESS_MAP, dtype=np.uint16)
        # Interpolate to square
        x = np.arange(0, THICKNESS_MAP.shape[0])
        fit = scipy.interpolate.interp1d(x, THICKNESS_MAP, axis=0)
        INTERPOL_THICKNESS_MAP = fit(np.linspace(0, THICKNESS_MAP.shape[0]-1, 1024))
        INTERPOL_THICKNESS_MAP_SMOOTH = scipy.ndimage.median_filter(INTERPOL_THICKNESS_MAP, 
                                                             size=round(INTERPOL_THICKNESS_MAP.shape[0]/75))
        # Save all kinds of created thickness-data
        name_measurement = folder.split('\\')[-1]
        # Plots
        plt.imsave(os.path.join(SAVE_PATHS_MAPS, ('InterpolatedThicknessmap_' + name_measurement + '.bmp')), 
                               np.asarray(INTERPOL_THICKNESS_MAP,dtype=np.uint16), cmap='gray', format='bmp')
        plt.imsave(os.path.join(SAVE_PATHS_MAPS, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.bmp')), 
                               np.asarray(INTERPOL_THICKNESS_MAP_SMOOTH,dtype=np.uint16), cmap='gray', format='bmp')
        # Binaries
        INTERPOL_THICKNESS_MAP.astype(np.uint16).tofile(os.path.join(SAVE_PATHS_MAPS, ('InterpolatedThicknessmap_' + name_measurement + '.bin')))
        INTERPOL_THICKNESS_MAP_SMOOTH.astype(np.uint16).tofile(os.path.join(SAVE_PATHS_MAPS, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.bin')))
        # *.MAT Files
        scipy.io.savemat(os.path.join(SAVE_PATHS_MAPS, ('InterpolatedThicknessmap_' + name_measurement + '.mat')), 
                         {'INTERPOL_THICKNESS_MAP': INTERPOL_THICKNESS_MAP.astype(np.uint16)})
        scipy.io.savemat(os.path.join(SAVE_PATHS_MAPS, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.mat')), 
                         {'INTERPOL_THICKNESS_MAP_SMOOTH': INTERPOL_THICKNESS_MAP_SMOOTH.astype(np.uint16)})
    
    print("Done Processing data base! :) :) <3")