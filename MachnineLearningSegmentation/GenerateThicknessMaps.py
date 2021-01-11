# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna
            Center for Medical Physics and Biomedical Engineering
                
"""

# Global imports 
import os
import tqdm
import glob

# Scipy imports are based on version 1.4.1 
# -> TODO: Fix for any version!
from scipy.io import savemat
from scipy.ndimage import median_filter
from scipy.interpolate import interp1d

import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt

# Custom imports
import BackendFunctions as Backend
import TrainingMain as Train

## Local Funcs  
def calculate_thickness(boundary_one, boundary_two) :
    if boundary_one is not None and boundary_two is not None :
        return np.asarray( np.absolute( np.subtract(boundary_two, boundary_one) ), np.uint16 )
    else :
        print("[WARNING] encountered empty array for thickness calculation")
        return None
    
def check_cornea_thickness(epi, endo) :
    assert epi is not None, "Epithelium boundary data is empty"
    assert endo is not None, "Endothelium boundary data is empty"
    thickness = calculate_thickness(epi, endo)
    average_thickness = np.average(thickness)
    deviation = np.std(thickness)
    spot_validity = []
    for spot in range(np.size(thickness)) :
        if ( thickness[spot] < (average_thickness - deviation) ) :
            spot_validity.append(0)
        elif ( thickness[spot] > (average_thickness + deviation) ) :
            spot_validity.append(0)
        else :
            spot_validity.append(1)
    return np.asarray(spot_validity, np.bool)
                 
def find_boundaries_and_calc_thickness_in_mask(mask, mask_idx) : 
    """ 
    >>> returns thickness-vector of the OVD layer per b-Scan 
    """ 
    width = np.shape(mask)[1]
    height = np.shape(mask)[0]
    OVD_THICKNESS = []
    mask = Backend.convert_mask_vals_to_trips(mask)
    val_crn = int(np.amax(mask)) # 255
    val_milk = int(round(val_crn/2)-1) # 127
    endo_offset = 3
    
    # 1) Find epithelium -> write to array
    epithelium = [] 
    endothelium = []
    for aScan in range(width) : 
        curr_aScan = mask[:,aScan]  
        crn_spots = np.where(curr_aScan==val_crn) 
        if np.size(crn_spots) > 1 :  
            epithelium.append(np.amin(crn_spots)) 
            endothelium.append(np.amax(crn_spots)) 
        else : 
            epithelium.append(0) 
            endothelium.append(0)
        curr_endo = endothelium[aScan] 
        # Set false positives north of the endothelium to val_crn and south to val_milk
        curr_aScan = curr_aScan.copy()
        curr_aScan[(np.where((curr_aScan[:curr_endo] > 0) & (curr_aScan[:curr_endo] <= val_crn)))] = val_crn
        curr_aScan[(np.where((curr_aScan[curr_endo:] > 0) & (curr_aScan[curr_endo:] >= val_milk)))] = val_milk
    
    # 2) Check for i) Continuity of the boundary layers & ii) Thickness of Cornea
    ## TODO: Re-check, since it pops up with almost all scans...
    if not check_cornea_thickness(epithelium, endothelium).all() :
        pass
        #print(f"[WARNING:] Deviation in corneal thickness in [MASK INDEX NO.{mask_idx}]") 
    if not Backend.check_for_boundary_continuity(epithelium) :
        pass
        #print(f"[WARNING:] Epithelium could not be identified as a continuous layer in [MASK INDEX NO.{mask_idx}]")
    if not Backend.check_for_boundary_continuity(endothelium) :    
        pass
        #print(f"[WARNING:] Endothelium could not be identified as a continuous layer in [MASK INDEX NO.{mask_idx}]")
    
    # 3) Find beginning of milk layer
    milk = [] 
    for aScan in range(width) : 
        curr_aScan = mask[:,aScan]
        curr_endo = endothelium[aScan]
        m_spots = np.where(curr_aScan[(curr_endo + endo_offset):] == val_milk) # look for milk-vals from endothelium on plus offset 
        if np.size(m_spots) > 1 : 
            milk.append(np.amin(m_spots) + endothelium[aScan] + endo_offset) # add start of milk layer  
        else : 
            milk.append(int(height-1)) 
        # 4) Evaluate thickness  
        OVD_THICKNESS.append(calculate_thickness( endothelium[aScan], milk[aScan] ))
    return np.asarray(OVD_THICKNESS, np.uint16) 

def check_for_bScan_list_completeness(return_list) :
    """
    check for consecutive combined numbers in both lists
    """
    sorted_list_diffs = sum(np.diff(sorted(return_list)))
    if sorted_list_diffs == (len(return_list) - 1):
        return True
    else:
        return False 

def pre_check_measurement_folder(folder) :
    SCAN_LIST_VALID = []
    SCAN_LIST_INVALID = [] 
    # 1. Find and sort all [CORRECT SEGMENTED] b-Scans in order 
    list_valid_bScans = glob.glob(os.path.join(folder, 'CorrectScans', "*.bmp")) 
    if list_valid_bScans : 
        list_valid_bScans.sort(key=lambda f: int(''.join(filter(str.isdigit, f)))) 
        for path in list_valid_bScans : 
            string = path.split('\\')[-1].split('.bmp')[0] 
            SCAN_LIST_VALID.append(int(string))              
    list_invalid_bScans = [] 
    # 2. Find and sort all [MANUALLY RE-SEGMENTED] b-Scans in order 
    folder_ml_data = os.path.join(folder, 'IncorrectScans', 'Data_Machine_Learning') 
    if not os.path.exists(folder_ml_data) : # ERROR HANDLE if ML-data-dir does not exist
        os.mkdir(folder_ml_data) 
    manual_folders = [f.path for f in os.scandir(os.path.join(folder, 'IncorrectScans', 
                                                'Data_Machine_Learning')) if f.is_dir()] 
    if manual_folders : 
        for ml_folder in manual_folders: 
            list_invalid_bScans.append(ml_folder)
        list_invalid_bScans.sort(key=lambda f: int(''.join(filter(str.isdigit, f)))) 
        for path in list_invalid_bScans : 
            string = path.split('\\')[-1].split('.bmp')[0].split('.')[-1]
            SCAN_LIST_INVALID.append(int(string))       
    # 3. Check if every index [0-127] exists in either of the lists only once!
    if len(SCAN_LIST_VALID) == 128 :
        SCAN_LIST = SCAN_LIST_VALID
    else : 
        SCAN_LIST = SCAN_LIST_VALID + SCAN_LIST_INVALID
        SCAN_LIST.sort()
        if not check_for_bScan_list_completeness(SCAN_LIST) :
            raise ValueError(f"Folder {folder} does not contain all (consecutive) scans")
    return SCAN_LIST_VALID, list_valid_bScans, list_invalid_bScans

def generate_and_safe_thickness_maps() :
    """
    Function to automatically crawl through the data base of segmented volume scans 
    and generate thickness maps
    """  
    ## TODO: Add flag as param to delete/handle data in 'EvaluatedData'
    main_path = Backend.clean_path_selection("Please select main path of data base")
    list_measurements = Backend.fast_scandir(main_path) 
    SAVE_PATHS_MAPS = os.path.join(main_path, 'EvaluatedData') 
    if not os.path.exists(SAVE_PATHS_MAPS): 
        os.makedirs(SAVE_PATHS_MAPS) 

    # MAIN LOOP for thickness calcs 
    for c_folder, folder in tqdm(enumerate(list_measurements)) :
        SCAN_LIST_VALID, list_valid_bScans, list_invalid_bScans = pre_check_measurement_folder(folder)  
        ## Process every B-Scan in volume 
        THICKNESS_MAP = [] 
        counter_invalid = 0 
        counter_valid = 0 
        print(f"\nCalculating thickness for Volume No.{c_folder+1} in a total of {len(list_measurements)} measurements...") 
        # Calculate thickness vector for every b-Scan
        for scan in tqdm(range(128)) : 
            if scan not in SCAN_LIST_VALID : 
                # Load mask 
                mask_file = os.path.join(list_invalid_bScans[counter_invalid], 'mask.png') 
                if os.path.isfile(mask_file) :
                    # debug
                    # print(f"Scan No.{scan} was [MANUALLY] re-segmented") 
                    mask = np.asarray(Image.open(mask_file).resize((1024, 1024))) 
                    _, trips_mask = Train.create_output_channel_masks(mask)
                    plt.imsave(os.path.join(os.path.join(folder, 'CorrectScans'),
                               f'{int(scan):03}.bmp'), trips_mask, cmap='gray', format='bmp') 
                    THICKNESS_MAP.append(find_boundaries_and_calc_thickness_in_mask(trips_mask, scan))
                    counter_invalid += 1 
                else : 
                    print(f"Could not load scan No.{scan} from mask No.{counter_invalid}")                 
            else : 
                # debug
                # print(f"Scan No.{scan} was [AUTOMATICALLY] segmented") 
                mask = np.asarray(Image.open(list_valid_bScans[counter_valid]).convert('L').resize((1024, 1024)))
                # Append b-Scan as row in heat map
                THICKNESS_MAP.append(find_boundaries_and_calc_thickness_in_mask(mask, scan)) 
                counter_valid += 1

        THICKNESS_MAP = np.squeeze(np.asarray(np.dstack(THICKNESS_MAP), dtype=np.uint16))

        # Interpolate to square 
        x = np.arange(0, THICKNESS_MAP.shape[0]) 
        fit = interp1d(x, THICKNESS_MAP, axis=0) 
        INTERPOL_THICKNESS_MAP = fit(np.linspace(0, THICKNESS_MAP.shape[0]-1, 1024))
        INTERPOL_THICKNESS_MAP_SMOOTH = median_filter(INTERPOL_THICKNESS_MAP, 
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
        savemat(os.path.join(SAVE_PATHS_MAPS, ('InterpolatedThicknessmap_' + name_measurement + '.mat')),  
                         {'INTERPOL_THICKNESS_MAP': INTERPOL_THICKNESS_MAP.astype(np.uint16)}) 
        savemat(os.path.join(SAVE_PATHS_MAPS, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.mat')),  
                         {'INTERPOL_THICKNESS_MAP_SMOOTH': INTERPOL_THICKNESS_MAP_SMOOTH.astype(np.uint16)}) 
     
    print("Done Processing data base! :) :) <3")


if __name__ == '__main__' :
    
    generate_and_safe_thickness_maps()
