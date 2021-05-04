# -*- coding: utf-8 -*-
"""

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna,
            Center for Medical Physics and Biomedical Engineering
                
"""

# proprietary imports 
import os
import cv2
import glob
import numpy as np
import matplotlib.pyplot as plt

from tqdm import tqdm
from PIL import Image
from scipy.io import savemat
from scipy.ndimage import median_filter
from scipy.interpolate import interp1d

# # custom imports
# import GenerateThicknessMaps as thickness


# ToDo: Fix import of pre_check_measurement_folder() and  from GenerateThicknessMaps.py module
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


def load_scans_and_overlaying_masks(main_path, match_dims=(512,512), is_filter_masks=True) :
    """
    Loads all b-Scans and corresponding masks in <<<main_path>>>
    """  
    # MAIN LOOP for thickness calcs 
    folder = main_path
    SCAN_LIST_VALID, list_valid_bScans, list_invalid_bScans = pre_check_measurement_folder(folder)  
    counter_invalid = 0 
    counter_valid = 0 
    masks = []
    scans = []
    # Calculate thickness vector for every b-Scan
    for scan in range(128): 
        if scan not in SCAN_LIST_VALID: 
            print("[WARNING!] - Algo not tested for this option!!!")
            mask_file = os.path.join(list_invalid_bScans[counter_invalid], 'binary_mask.png')         
            # Load b-Scan -> rethink, not yet tested
            if os.path.join(main_path, f'{scan:03}.bmp'):
                scans.append(np.asarray(Image.open(os.path.join(main_path, f'{scan:03}.bmp')).convert('L').resize(match_dims)))
            else:
                FileExistsError(f'{scan:03}.bmp doesn\'t exist')
            if os.path.isfile(mask_file):
                print(f"Scan No.{scan} was [MANUALLY] re-segmented (should't have happend") # debug
                try :
                    mask = np.asarray(Image.open(mask_file).convert('L'))
                    masks.append(create_trips_out_masks_from_binary(mask))
                except FileExistsError:
                    FileExistsError(f'{mask_file} doesn\'t exist')
                counter_invalid += 1 
            else: 
                FileExistsError(f"{mask_file} doesn\'t exist")                
        else: 
            if os.path.isfile(list_valid_bScans[counter_valid]):
                masks.append(np.asarray(Image.open(list_valid_bScans[counter_valid]).convert('L')))
            if os.path.join(main_path, f'{scan:03}.bmp'):
                scans.append(np.asarray(Image.open(os.path.join(main_path, f'{scan:03}.bmp')).convert('L').resize(match_dims)))
            counter_valid += 1
    
    # prepare data stacks for a reasonable representation
    masks = np.swapaxes(np.asarray(masks), 0, 2)
    scans = np.swapaxes(np.asarray(scans), 0, 2)
    masks = np.swapaxes(np.asarray(masks), 0, 1)
    scans = np.swapaxes(np.asarray(scans), 0, 1)

    assert scans.shape == masks.shape

    just_ovds = np.zeros_like(masks)
    if is_filter_masks: # apply "coarse" median filter
        for i in range(masks.shape[-1]):
            masks[:,:,i] = median_filter(masks[:,:,i], size=9) # remain only tripple-values due to props of MF
            for j in range(masks.shape[1]):
                spots = np.squeeze(np.where(masks[:,j,i]==255))
                bndry = np.amin(spots)
                just_ovds[0:bndry+1,j,i] = 1
    
    scans_structures = np.copy(scans) # NON-NOISE OCT structures
    scans_structures[masks == 0] = 0 # set noise pxls to 0
    
    scans_ovd = np.copy(scans) # just OVD
    scans_ovd[just_ovds > 0] = 0 # set values above cornea to 0
    scans_ovd[masks > 0] = 0 # set noise pxls to 0
    # scans_ovd[masks == 255] = 0 # set values cornea to 0
    
    # reshape scans
    raw_scans_only = []
    structures_only = []
    ovd_only = []
    
    for i in tqdm(range(scans.shape[1])):
        raw_scans_only.append(cv2.resize(scans[i,:,:], dsize=match_dims, interpolation=cv2.INTER_CUBIC))
        structures_only.append(cv2.resize(scans_structures[i,:,:], dsize=match_dims, interpolation=cv2.INTER_CUBIC))
        ovd_only.append(cv2.resize(scans_ovd[i,:,:], dsize=match_dims, interpolation=cv2.INTER_CUBIC))

    return np.asarray(raw_scans_only), np.asarray(structures_only), np.asarray(ovd_only)

if __name__ == '__main__' :
    
    path = r'E:\TachyBackupOfFolders\OVID_segmentedDataForPaper\03_AMVISCPLUS\AMVISCPLUS_5_1_Size6_OD-2020-05-15_102414'
    scans, structures, ovds = load_scans_and_overlaying_masks(path)
    # plt.figure()
    # plt.imshow(scans[:,:,255]) 
    # plt.show()
    # plt.figure()
    # plt.imshow(structures[:,:,255]) 
    # plt.show()
    # plt.figure()
    # plt.imshow(ovds[:,:,255]) 
    # plt.show()

    print("Saving file...")
    scans.astype('uint8').tofile(r'C:\Users\Philipp\Desktop\AmviscPlus51_512x512x512_raw.bin')
    structures.astype('uint8').tofile(r'C:\Users\Philipp\Desktop\AmviscPlus51_512x512x512_structures.bin')
    ovds.astype('uint8').tofile(r'C:\Users\Philipp\Desktop\AmviscPlus51_512x512x512_ovd.bin') 
    print("Done saving!")