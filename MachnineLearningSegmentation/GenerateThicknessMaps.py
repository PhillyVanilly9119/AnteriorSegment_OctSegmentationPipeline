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
import scipy
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Custom imports
import BackendFunctions as Backend

def calculate_thickness() :

def find_boundaries_in_mask(mask) : 
    """ 
    """ 
    width = np.shape(mask)[1]
# =============================================================================
#     crn_thickness = 320 # >>TBD<< 
#     # TODO: round values in mask to 255, 127 and 0 
#     crn_val = 255 
#     milk_val = 127 
#     milk = [] 
#     OVD_THICKNESS = [] # final return value 
# =============================================================================
    # Maybe process the 
    # 1) Find epithelium -> write to array
    epithelium = [] 
    endothelium = [] 
    for aScan in range(width) : 
        current_scans = mask[:,aScan]  
        current_spots = np.where(current_scans==crn_val) 
        if np.size(c_spots) > 1 :  
            epithelium.append(np.amin(c_spots)) 
            endothelium.append(np.amax(c_spots)) 
        else : 
            epithelium.append(0) 
            endothelium.append(0)                
    valid_endo = AutoSegmentation.check_for_continuity(endothelium) 
    if np.count_nonzero(valid_endo) == np.shape(mask)[1] : 
        interp_endo = np.add(epithelium, crn_thickness) 
    else : 
        interp_endo = np.add(AutoSegmentation.interpolate_curve(epithelium, valid_endo), 
                             crn_thickness) 
    averaged_endo = np.asarray(interp_endo, dtype=np.uint16) 
    # 3) Find OVD 
    for aScan in range(AScans) : 
        c_aScan = mask[:,aScan] 
        c_aScan[averaged_endo[aScan]:] 
        m_spots = np.where(c_aScan[averaged_endo[aScan]:]==milk_val) 
        if np.size(m_spots) > 1 : 
            milk.append(np.amin(m_spots)+averaged_endo[aScan]) 
        else : 
            milk.append(1023) 
        # 4) Evaluate thickness  
        OVD_THICKNESS.append(AutoSegmentation.calculate_thickness(averaged_endo[aScan],  
                                                                  milk[aScan])) 
    return np.asarray(OVD_THICKNESS) 

def generate_and_safe_thickness_maps() :
    """
    """
    main_path = Backend.clean_path_selection("Please select main path of data base")
    list_measurements = Backend.fast_scandir(main_path) 
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


if __name__ == '__main__' :
    generate_and_safe_thickness_maps()