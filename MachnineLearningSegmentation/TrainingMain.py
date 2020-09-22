# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing functionality to train Network for 
                        
            TRAINING OF NETWORK FOR AUTO SEGMENTATION

"""

# global imports
import os
import cv2
import time
import numpy as np
from PIL import Image
from tqdm import tqdm

# local imports 
import BackendFunctions as Backend
    
# =============================================================================
# DATA PRE-PROCESSING - Training
# =============================================================================     
def prepare_data_for_network(dims, is_user_select_data_path=False, 
                             is_add_flipped_data=False, is_check_for_matching_data=False) :
    """
    Loads, pre-processes and displays data (optional) for training with CNN (UNet)
    """
    # Load and preprocess
    if is_user_select_data_path :
        path = Backend.clean_path_selection("Please select folder with training data")
    else :
        path = r"D:\PhilippData\MedicalUniversity\Data\AntSeg_SegPipeline\training"
    print("[STARTING PREPROCESSING] data for training...")
    # rewrite image loading function to be able to load either '*.bmp' and '*.png'
    t1 = time.time()
    sub_dirs = Backend.get_subdirs_only(path)
    x, y = zip(*[load_and_process_scans_and_masks(d, dims) for d in tqdm(sub_dirs)])
    x = np.dstack(x)
    y = np.concatenate(y)                    
    x = x[np.newaxis]
    x = np.swapaxes(x, 0, 3)
    # Add flipped versions of the all b-Scans to the training data
    if is_add_flipped_data:
        x = add_flipped_data(x)
        y = add_flipped_data(y)
    # Sanity check if inconsistencies in the data were observed
    # -> displays overlay of background and b-Scan           
    if is_check_for_matching_data:
        Backend.sanity_check_training_data(x[:,:,:,0], y[:,:,:,0], y[:,:,:,1], update_rate_Hz=1) 
    t2 = time.time()
    print(f"[DONE PREPROCESSING] data for training \nDuration: {t2-t1} secs")
    return x, y

# =============================================================================
# MASK CREATION - FOR NETWORK 
# =============================================================================
def load_and_process_scans_and_masks(path, dims, scan_name='raw_bScan') :
    """
    -> Loads data for training and handles differences in files and their
    configurations, that derive from different stages in the segementation project
    Go through all subdirs and load pairs of Scan(s) and (tripple)-mask(s)
    """
    scans = []
    masks = []
    for root, dirs, files in os.walk(path) :
        # returns 3D-tensor with b-Scans (h, w, n_imgs)
        scans = load_bScans_for_training(root, scan_name, dims)
        # returns 4D-tensor with masks (n_img, h, w, n_mask)
        masks = create_tripple_masks_for_training(root, dims=dims)
        # delete all non-relevant files
        delete_invalid_images(root)
    return scans, masks             

def delete_invalid_images(path) :
    valid_scans = [
            'mask.bmp',
            'mask.png',
            'raw_bScan.png',
            'raw_bScan.bmp',
            'mask_ovd.bmp',
            'mask_cornea.bmp',
            'mask_background.bmp'
            ]
    img_list = os.listdir(path)
    invalid_list = [file for file in img_list if file not in valid_scans]
    # Delete *.PNGs of SCAN and MASK if *.BMPs exist
# =============================================================================
#     # TODO: Rethink! Neither statement should ever be true
#     if os.path.isfile(os.path.join(path, 'mask.bmp')) :
#         invalid_list.append(os.path.join(path, 'mask.png'))
#     if os.path.isfile(os.path.join('raw_bScan.bmp')) :
#         invalid_list.append(os.path.join(path, 'raw_bScan.png'))
#     # delete all non-relevant files 
# =============================================================================
    for file in invalid_list :
        c_file = os.path.join(path, file)
        if os.path.isfile(c_file) :
            os.remove(c_file)

def load_bScans_for_training(root, scan_name, dims) :
    if os.path.isfile(os.path.join(root, scan_name + '.bmp')) :
        scan = Backend.load_single_image(os.path.join(root, scan_name + '.bmp'), dims)
        scan = scan[:,:,0]
    elif os.path.isfile(os.path.join(root, scan_name + '.png')) :
        scan = Backend.load_single_image(os.path.join(root, scan_name + '.png'), dims)
    else :
        raise FileNotFoundError(f"Couldn't find either *.BMP or *.PNG files of {scan_name} in {root}")         
    return np.asarray(scan, dtype=np.uint8) 


def create_three_masks_from_tripple_mask(mask) :
    mask = np.asarray(Backend.convert_mask_vals_to_trips(mask))
    masks = []
    cornea = np.zeros_like(mask, dtype=np.uint8)
    milk = np.zeros_like(mask, dtype=np.uint8)
    background = np.zeros_like(mask, dtype=np.uint8)

    background[mask==0] = 255
    cornea[mask==127] = 255
    milk[mask==255] = 255
    
    masks.append(cornea) # Mask No.1
    masks.append(milk) # Mask No.2
    masks.append(background) # Mask No.3
    return np.asarray(masks, dtype=np.uint8)
    
def create_output_channel_masks(mask) :
    """
    >>> created the 3 kinds of masks for passing into the network and
    the overlayed combined (tripple) mask
    
    return dimensions:  masks = (n_mask, height, width) and 
                        tripple_masks = (height, width)    
    """
    dims = np.shape(mask) 
    cornea = np.zeros((dims))
    ovd = np.zeros_like(mask, dtype=np.uint8)
    background = np.zeros_like(mask, dtype=np.uint8)
    tripple_mask = np.zeros_like(mask, dtype=np.uint8)
    
    for ascan in range(dims[1]) : # iterate through A-Scans
        bndry_spots = np.squeeze(np.where(mask[:,ascan]==np.amax(mask)))
        if np.size(bndry_spots) == 2 : # case: only Cornea visible
            start_crn = np.amin(bndry_spots)
            end_crn = np.amax(bndry_spots)
            # cornea = 1
            tripple_mask[start_crn:end_crn, ascan] = 255
            cornea[start_crn:end_crn, ascan] = 255
        elif np.size(bndry_spots) == 3 :
            tripple_mask[bndry_spots[0]:bndry_spots[1], ascan] = 255
            cornea[bndry_spots[0]:bndry_spots[1], ascan] = 255
            tripple_mask[bndry_spots[2]:, ascan] = 127
            ovd[bndry_spots[2]:, ascan] = 255
        else :
            print(f"[WARNING:] Stumbled upon invalid cornea segmentation in A-Scan \#{ascan}...")
            pass 
        # Create Masks for 3-channel segmentation
        tmp = np.add(cornea, ovd)
        _, background = cv2.threshold(tmp, 127, 255, cv2.THRESH_BINARY_INV)

        masks = []
        masks.append(ovd)
        masks.append(cornea) 
        masks.append(background)
        
        # tripple_mask is an additional return variable
    return masks
               
def create_tripple_masks_for_training(path, dims=(1024,1024), dtype='.bmp',
                                      is_save_newly_calced_masks=True):
    """
    >>> prepares data array for passing and training to network
    return dimensions:  (n_img, height, width, n_masks)
    """
    list_mask_files = ['mask_cornea',
                       'mask_ovd', 
                       'mask_background']    
    trip_masks = []
    # Check if the single masks already exist and load them, else create them from the combined mask
    crn_file = os.path.join(path, str(list_mask_files[0] + dtype))
    ovd_file = os.path.join(path, str(list_mask_files[1] + dtype))
    bg_file = os.path.join(path, str(list_mask_files[2] + dtype))
    ### IF three single DONT masks already EXIST -> Calculate
    if not os.path.isfile(crn_file) or not os.path.isfile(ovd_file) or not os.path.isfile(bg_file) :
        # Load line-segmented mask
        if os.path.isfile(os.path.join(path, 'mask.bmp')) :
            raw_mask = Backend.load_single_image(os.path.join(path, 'mask.bmp'), dims)
            masks = create_three_masks_from_tripple_mask(raw_mask)
        elif os.path.isfile(os.path.join(path, 'mask.png')) :
            raw_mask = Backend.load_single_image(os.path.join(path, 'mask.png'), dims)
            # create and add all three masks in order
            masks = create_output_channel_masks(raw_mask)
            trip_masks.append(masks)
            masks = np.asarray(masks)
        else :
            print(f"No valid mask file found in {path}")
        # save masks if flag is True
        if is_save_newly_calced_masks :
            Backend.save_single_grey_img(masks[0,:,:], ovd_file)
            Backend.save_single_grey_img(masks[1,:,:], crn_file)
            Backend.save_single_grey_img(masks[2,:,:], bg_file)
            print(f"\nSaved generated single masks for training in {path}")
    ### IF they EXIST -> load them
    else :
        cornea = np.asarray(Image.open(os.path.join(path, str(list_mask_files[0] + dtype))).resize(dims))
        ovd = np.asarray(Image.open(os.path.join(path, str(list_mask_files[1] + dtype))).resize(dims))
        background = np.asarray(Image.open(os.path.join(path, str(list_mask_files[2] + dtype))).resize(dims))
        new_masks = np.dstack((cornea[:,:,0], ovd[:,:,0], background[:,:,0]))
        trip_masks.append(new_masks)
    return np.asarray(trip_masks, dtype=np.uint8)

def add_flipped_data(images, x_flip=True, y_flip=True) :
    """
    >>> Adds flipped versions of the input data to the training data stack
    --> image stack dimensions: [n_img, h, w, channels]; 
        channels = 1 for B-Scans
    >> Change flag combination to add certain configuration of flipped images
    """
    print("Adding flipped images to training data stack... ")
    stack = images # return at least input image stack
    sizes = np.shape(images)
    dims = np.size(sizes)      
    assert dims == 4, "Images are expected to be 4D-array with dims=[n,h,w,c]!"
    #(n,h,w,c)
    if x_flip and y_flip :
        print("Adding flipped versions along both axis and point mirrored image...")
        stack = np.concatenate((images,
                                Backend.create_flipped_img_4d_tensor(images),
                                Backend.create_flipped_img_4d_tensor(images, axis=0),
                                Backend.create_flipped_img_4d_tensor(images, axis=1)
                                ))
    elif x_flip and not y_flip :
        print("Adding flipped versions along horizontal axis...")
        stack = np.concatenate((images,
                                Backend.create_flipped_img_4d_tensor(images, axis=0),
                                ))
    elif not x_flip and y_flip :
        print("Adding flipped versions along vertical axis...")
        stack = np.concatenate((images,
                                Backend.create_flipped_img_4d_tensor(images, axis=1)
                                ))
    else :
        print("You have chosen to not add any flipped images")        

    print(f"Added {np.shape(stack)[0]-sizes[0]} images [THROUGH FLIPPING] to original data!")
    return stack
