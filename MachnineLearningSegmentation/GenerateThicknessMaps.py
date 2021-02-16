# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna,
            Center for Medical Physics and Biomedical Engineering
                
"""

# Global imports 
import os
import cv2
import tqdm
import glob
import shutil

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
        # Note: Absolute of difference to take into account inaccuracies of manual segmentation
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

def create_trips_out_masks_from_binary(mask) :
    """
    >>> created the 3 kinds of masks for passing into the network and
    the overlayed combined (tripple) mask from binary mask "binary_mask.png"
    
    return dimensions: tripple_masks nDim = 2 (height, width)    
    """
    tmp_mask = np.zeros_like(mask, dtype=np.uint8) 
    tripple_mask = np.zeros_like(mask, dtype=np.uint8)
    
    dims = np.shape(mask)
    tmp_mask[mask > 0] = np.amax(mask)
    mask = tmp_mask

    for ascan in range(dims[1]) : # iterate through A-Scans
        # find important spots in the a-Scan
        filled_area_spots = np.squeeze(np.where(mask[:,ascan]==np.amax(mask)))
        crn_start = np.amin(filled_area_spots)
        is_ovd_in_aScan = np.squeeze(np.where(np.diff(filled_area_spots) > 1))
        # find endothelium based on what can be seen in current a-Scan
        if (is_ovd_in_aScan.size > 0) : # case: cornea and OVD areas visible
            crn_end = np.squeeze(crn_start + is_ovd_in_aScan)
            ovd_start = np.squeeze(crn_end + np.amax(np.diff(filled_area_spots)))
            tripple_mask[crn_start:crn_end, ascan] = 255
            tripple_mask[ovd_start:, ascan] = 127
        else : # case: cornea but no OVD
            crn_end = np.amax(filled_area_spots)
            tripple_mask[crn_start:crn_end, ascan] = 255
        # TODO: Rethink if third condition is neccessary
    return tripple_mask

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
    
    # # 2) Check for i) Continuity of the boundary layers & ii) Thickness of Cornea
    # ## TODO: Re-check, since it pops up with almost all scans...
    # if not check_cornea_thickness(epithelium, endothelium).all() :
    #     pass
    #     #print(f"[WARNING:] Deviation in corneal thickness in [MASK INDEX NO.{mask_idx}]") 
    # if not Backend.check_for_boundary_continuity(epithelium) :
    #     pass
    #     #print(f"[WARNING:] Epithelium could not be identified as a continuous layer in [MASK INDEX NO.{mask_idx}]")
    # if not Backend.check_for_boundary_continuity(endothelium) :    
    #     pass
    #     #print(f"[WARNING:] Endothelium could not be identified as a continuous layer in [MASK INDEX NO.{mask_idx}]")
    
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
        SCAN_LIST = list(set(SCAN_LIST)) # recast as set to only have unique scan indicies incl. re-recast
        if not check_for_bScan_list_completeness(SCAN_LIST) :
            print(f"Missing scan indices are :{list(set(range(128)).symmetric_difference(set(SCAN_LIST)))}")
            raise ValueError(f"Folder {folder} does not contain all (consecutive) scans")
    return SCAN_LIST_VALID, list_valid_bScans, list_invalid_bScans

def save_and_overwrite_images(folder, mask, scan, dims=(512,512)) :
    """
    Function to resize and save and/or overwrite the masks
    """
    mask = cv2.resize(mask, dsize=dims, interpolation=cv2.INTER_NEAREST)
    plt.imsave(os.path.join(os.path.join(folder, 'CorrectScans'), 
                            f'{int(scan):03}.bmp'), mask, cmap='gray', format='bmp') 
    return mask

def resize_heatmaps_to_square(map, filter_size=9, side_length=512) :
    """
    Function to return square interpolated heat map
    TODO: Rethink if this could be ported to the backend functions
    """
    x = np.arange(0, map.shape[0]) 
    fit = interp1d(x, map, axis=0) 
    interpolated_map = fit(np.linspace(0, map.shape[0]-1, side_length))
    filtered_map = median_filter(interpolated_map, size=filter_size)    
    return interpolated_map, filtered_map

# TODO: Continue here
def filter_outlier_and_interpol_maps(map_in, name_measurement, kernel_size=5) :
    """
    Applies filtering and gets rid of outliers in already sqaure-interpolated thichness maps
    """
    map_out = np.zeros_like(map_in)
    # return map_out
    pass

def save_evaluated_data_in_subfolders(main_path, original_map, interpol_map, filtered_map, 
                                      dims=(512, 512), flag_save_images_additionally_combined=True) :
    """
    Save evaluated thickness maps in specified sub folders
    """
    name_measurement = main_path.split('\\')[-1]
    path = os.path.dirname(os.path.dirname(main_path))
    # create sub folder if it doesn't already exist
    current_measurement_path = os.path.join(path, 'EvaluatedData', name_measurement) 
    print(main_path)
    if not os.path.exists(current_measurement_path): 
        os.makedirs(current_measurement_path) 
    # reshape to square -> cubic interpolation 
    interpol_map = np.asarray( np.floor( cv2.resize(interpol_map, dsize=dims, interpolation=cv2.INTER_CUBIC) ) )
    filtered_map = np.asarray( np.floor( cv2.resize(filtered_map, dsize=dims, interpolation=cv2.INTER_CUBIC) ) )
    # save data do dedicated paths
    try : 
        # save plots of heat maps 
        plt.imsave(os.path.join(current_measurement_path, ('SquareInterpolatedThicknessmap_' + name_measurement + '.bmp')),  
                                np.asarray(interpol_map, dtype=np.uint8), cmap='gray', format='bmp') 
        plt.imsave(os.path.join(current_measurement_path, ('SmoothFilteredThicknessmap_' + name_measurement + '.bmp')),  
                                np.asarray(filtered_map, dtype=np.uint8), cmap='gray', format='bmp') 
        # if wanted store all images additionally in a seperate measurement folder
        if flag_save_images_additionally_combined :
            path_combined_images = os.path.join(path, 'EvaluatedData', '00_ImagesHeatMaps')
            if not os.path.exists(path_combined_images): 
                os.makedirs(path_combined_images) 
            plt.imsave(os.path.join(path_combined_images, ('SquareInterpolatedThicknessmap_' + name_measurement + '.bmp')),  
                                    np.asarray(interpol_map, dtype=np.uint8), cmap='gray', format='bmp') 
            plt.imsave(os.path.join(path_combined_images, ('SmoothFilteredThicknessmap_' + name_measurement + '.bmp')),  
                                    np.asarray(filtered_map, dtype=np.uint8), cmap='gray', format='bmp') 
        # save data in binaries 
        interpol_map.astype(np.uint16).tofile(os.path.join(current_measurement_path, ('InterpolatedThicknessmap_' + name_measurement + '.bin'))) 
        filtered_map.astype(np.uint16).tofile(os.path.join(current_measurement_path, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.bin'))) 
        # save data in *.MAT files for later evaluation
        
        # TODO: save the uninterpolated heat maps
        savemat(os.path.join(current_measurement_path, ('Thicknessmap_' + name_measurement + '.mat')),  
                            {'INTERPOL_THICKNESS_MAP': original_map.astype(np.uint16)})
        savemat(os.path.join(current_measurement_path, ('InterpolatedThicknessmap_' + name_measurement + '.mat')),  
                            {'INTERPOL_THICKNESS_MAP': interpol_map.astype(np.uint16)}) 
        savemat(os.path.join(current_measurement_path, ('SmoothInterpolatedThicknessmap_' + name_measurement + '.mat')),  
                            {'INTERPOL_THICKNESS_MAP_SMOOTH': filtered_map.astype(np.uint16)}) 
    except FileExistsError :
        FileExistsError(f"Could not safe data of {name_measurement} to file, because the path doesn't exist")
    finally :
        pass
        #print(f"Could not save data from {main_path} to file... ")

def generate_and_safe_thickness_maps(flag_delete_existing_eval_data_path=True) :
    """
    +++ MAIN DATA EVALUATION ROUTINE +++ 
    Automatically crawl through the data base of segmented volume scans and generate thickness maps
    """  
    main_path = Backend.clean_path_selection("Please select main path of data base")
    SAVE_PATHS_MAPS = os.path.join(main_path, 'EvaluatedData') 
    # delete previously evaluated data to avoid sub-tree conflicts
    if flag_delete_existing_eval_data_path and os.path.isdir(SAVE_PATHS_MAPS) :
        print(f"Deleting existing data in {SAVE_PATHS_MAPS}")
        shutil.rmtree(SAVE_PATHS_MAPS)
    else :
        print(f"[CAUTION]: Keeping folder with existing evaluated data in {os.path.join(main_path, 'EvaluatedData')}!")
    list_measurements = Backend.fast_scandir(main_path)
    if not os.path.exists(SAVE_PATHS_MAPS): 
        os.makedirs(SAVE_PATHS_MAPS) 
        print(f"Created folder {SAVE_PATHS_MAPS} to store evaluated data...")
    # MAIN LOOP for thickness calcs 
    for c_folder, folder in tqdm(enumerate(list_measurements)) :
        SCAN_LIST_VALID, list_valid_bScans, list_invalid_bScans = pre_check_measurement_folder(folder)  
        ## Process every B-Scan in volume 
        THICKNESS_MAP = [] 
        counter_invalid = 0 
        counter_valid = 0 
        # Update display prints
        print(f"\nCalculating thickness for volume No.{c_folder+1}/{len(list_measurements)} in \"{folder}\" ...") 
        if 128 > int(len(list_valid_bScans)) :
            print(f"\nRecalculating {int(128-len(list_valid_bScans))} scans in this folder... ")
        # Calculate thickness vector for every b-Scan
        for scan in tqdm(range(128)) : 
            if scan not in SCAN_LIST_VALID : 
                # Load mask 
                mask_file = os.path.join(list_invalid_bScans[counter_invalid], 'binary_mask.png') 
                if os.path.isfile(mask_file) :
                    # print(f"Scan No.{scan} was [MANUALLY] re-segmented") # debug
                    try :
                        mask = np.asarray(Image.open(mask_file), dtype=np.uint8)
                    except FileExistsError :
                        FileExistsError(f"Could not load {mask_file} - path does not exist")
                    trips_mask = create_trips_out_masks_from_binary(mask)
                    trips_mask = save_and_overwrite_images(folder, trips_mask, scan)
                    # Append b-Scan thickness of current b-Scan in heat map
                    THICKNESS_MAP.append(find_boundaries_and_calc_thickness_in_mask(trips_mask, scan)) 
                    counter_invalid += 1 
                else : 
                    print(f"Could not load scan No.{scan} from mask No.{counter_invalid}")                 
            else : 
                # print(f"Scan No.{scan} was [AUTOMATICALLY] segmented") # debug
                mask = np.asarray(Image.open(list_valid_bScans[counter_valid]).convert('L'))
                mask = save_and_overwrite_images(folder, mask, scan)
                # Append b-Scan thickness of current b-Scan in heat map
                THICKNESS_MAP.append(find_boundaries_and_calc_thickness_in_mask(mask, scan)) 
                counter_valid += 1

        THICKNESS_MAP = np.squeeze(np.asarray(np.dstack(THICKNESS_MAP), dtype=np.uint16)) 
        # interpolate data to square shape 
        INTERPOL_THICKNESS_MAP, INTERPOL_THICKNESS_MAP_SMOOTH = resize_heatmaps_to_square(THICKNESS_MAP)
        # save all kinds of created thickness-data 
        save_evaluated_data_in_subfolders(folder, THICKNESS_MAP, INTERPOL_THICKNESS_MAP, INTERPOL_THICKNESS_MAP_SMOOTH)
     
    print("Done Processing data base! :) :) <3")


if __name__ == '__main__' :
    
    generate_and_safe_thickness_maps()
