# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 08:52:56 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at
"""

import os 
import cv2
import uuid
import glob 
import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
from tkinter.filedialog import Tk, askdirectory

def open_and_close(image, kernel_size=3) :
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel), 
                            cv2.MORPH_CLOSE, 
                            kernel)
    
def load_images(path, name, dims, img_dtype='.png') :
    print(f"Loading all images {name+img_dtype} from {path}...")
    assert np.size(dims) == 2, f"[RESHAPING DIMENSION MISMATCH] Please enter valid tuple dimensions!"
    h, w = dims[0], dims[1]
    files = os.listdir(path)
    try :
        if any([os.path.isfile(os.path.join(path, f, name + img_dtype)) for f in files]):
            img_stack = [np.asarray(Image.open(os.path.join(path, f, name + img_dtype)).resize((h,w))) for f in tqdm(files)]
    except FileNotFoundError :
        print(f"There were no files named {name} in any (sub-)directory of {path}")
    
    print("Done loading images!")
    return np.dstack(img_stack)

def load_single_image(path, dims) :
    assert os.path.isfile(path), "Input path is not a path to an image!"
    h, w = dims[0], dims[1]
    image = Image.open(path).resize((h,w))
    return np.asarray(image, dtype=np.uint8)

def save_single_image(file_name, img, c_map='gray') :
    plt.imsave(file_name, img, cmap=c_map)

def sort_list_after_number(in_list) :
    in_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    return in_list

def fast_scandir(dirname):
    sub_folders = []
    folders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for subdir in folders :
        for f in os.scandir(subdir) :
            if f.is_dir() :
                sub_folders.append(f.path)
    return sub_folders   

def get_img_idx(path, folder_idx=-1, img_dtype='.bmp') :
    img_num = path.split('\\')[folder_idx].split(img_dtype)[0]
    return int(img_num)

def get_img_dirs(path) :
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(filenames)
    return f

def create_dir(directory) :
    if not os.path.isdir(directory) :
            os.mkdir(directory)
            
def resize_img_stack(images, out_dims, is_print_func_call=False) :
    assert images.ndim == 3, "[IMAGE RESIZING ERROR >>resize_img_stack()<<]"
    in_dims = np.shape(images)
    n_imgs = np.shape(images)[2]
    if is_print_func_call :
        print(f"Reshaping images from {in_dims} to {out_dims}...")
    images = [cv2.resize(images[:,:,i], 
                         (out_dims[0], out_dims[1]), 
                         interpolation = cv2.INTER_AREA) for i in range(n_imgs)]
        
def clean_path_selection(text) :
    root = Tk()
    root.withdraw()
    path = askdirectory(title=text, mustexist=True)
    root.destroy()
    return path
 
def check_for_duplicates(path_one, path_two) : 
    """
    Returns BOOL for if the file exists in both dirs
    """ 
    if os.path.isfile(path_one) and os.path.isfile(path_two) : 
        return True
    else :
        return False   
    
def find_max_idx(path_one, path_two) :
    """
    Primitive to find highest numbered scan in sorted directories
    """
    if os.path.isdir(path_one) :
        first_list = glob.glob(os.path.join(path_one, "*.bmp"))
        first_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    if os.path.isdir(path_one) :
        second_list = glob.glob(os.path.join(path_two, "*.bmp"))
        second_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f)))) 
    if not first_list and not second_list :
        index = 0
    elif first_list and not second_list :
        first_idx = first_list[-1]
        index = int(first_idx.split('\\')[-1].split('.bmp')[0])
        index += 1
    elif not first_list and second_list :
        second_idx = second_list[-1]
        index = int(second_idx.split('\\')[-1].split('.bmp')[0])
        index += 1
    elif first_list and second_list :
        first_idx = first_list[-1]
        second_idx = second_list[-1]
        first_idx = int(first_idx.split('\\')[-1].split('.bmp')[0])
        second_idx = int(second_idx.split('\\')[-1].split('.bmp')[0])
        index = max(first_idx, second_idx)
        index += 1
    else :
        return ValueError("No Index could be found")
    print(f"Found start index to be No.{index}")
    return index

# =============================================================================
# MASK CREATION
# =============================================================================
def create_new_masks_auto_segmented(path, dims=(1024,1024), is_select_target_dir=True) :
    assert os.path.isdir(path), FileNotFoundError("[FILE NOT FOUND in >>create_new_masks_autoSegmented()<<]")
    dirs_vols = fast_scandir(path)
    if is_select_target_dir :
        target_dir = clean_path_selection("Please select target folder for new masks")
        create_dir(target_dir)
    else :
        target_dir = path
    # Loop through volume measurements        
    for folder in tqdm(dirs_vols) :
        mask_files = get_img_dirs(folder)
        for mask_file in tqdm(mask_files) :
            curr_dir = os.path.join(target_dir, str(uuid.uuid4().hex))
            create_dir(curr_dir)
            curr_file = os.path.join(folder, mask_file)
            curr_mask = load_single_image(curr_file, dims=dims)
            curr_scan = load_single_image(os.path.join(os.path.dirname(folder), mask_file), dims)
            # Create new mask
            new_mask = recalcualte_auto_mask_boundaries(curr_mask)
            # Save mask and scan to folder
            save_single_image(os.path.join(curr_dir, 'raw_bScan.bmp'), curr_scan)
            save_single_image(os.path.join(curr_dir, 'mask.bmp'), new_mask)
            
def create_new_masks_manu_segmented(path, dims=(1024,1024), is_select_target_dir=True) :
    assert os.path.isdir(path), FileNotFoundError("[FILE NOT FOUND in >>create_new_masks_autoSegmented()<<]")
    dirs_data = fast_scandir(path)
    if is_select_target_dir :
        target_dir = clean_path_selection("Please select target folder for new masks")
        create_dir(target_dir)
    else :
        target_dir = path
    # Loop through volume measurements   
    for folder in tqdm(dirs_data) :
        mask_files = get_img_dirs(folder)
        mask_path = os.path.join(folder, mask_files[3])
        scan_path = os.path.join(folder, mask_files[-2])
        target_dir_curr_file = os.path.join(target_dir, str(uuid.uuid4().hex))
        create_dir(target_dir_curr_file)
        curr_mask = load_single_image(mask_path, dims=dims)
        curr_scan = load_single_image(scan_path, dims)
        # Create new mask
        new_mask = recalcualte_manu_mask_boundaries(curr_mask)
        # Save mask and scan to folder
        save_single_image(os.path.join(target_dir_curr_file, 'raw_bScan.bmp'), curr_scan)
        save_single_image(os.path.join(target_dir_curr_file, 'mask.bmp'), new_mask)

def recalcualte_auto_mask_boundaries(mask) : 
    crn_pix_val = np.amax(mask)
    milk_pix_val = int(np.floor(np.amax(mask)/2))
    out_mask = np.zeros_like(mask)
    for aScan in range(np.shape(mask)[1]) :
        c_aScan = mask[:,aScan] 
        epi = np.amin(np.where(c_aScan==crn_pix_val))
        crn_spot = np.amax(np.where(c_aScan==crn_pix_val)) # Find positions, where milk area is
        milk_spots = np.where(c_aScan==milk_pix_val)[0]
        if milk_spots[milk_spots > crn_spot] is None :
            milk_spots = np.amin(np.where(c_aScan==milk_pix_val)[0])
        else :
            milk_spot = np.amin(milk_spots[milk_spots > crn_spot])
        out_mask[epi:milk_spot, aScan] = crn_pix_val
        out_mask[milk_spot:, aScan] = milk_pix_val
    return out_mask

def recalcualte_manu_mask_boundaries(mask) : 
    out_mask = np.zeros_like(mask, dtype=np.uint8)
    for a_scan in range(np.shape(mask)[1]) : 
        c_ascan = mask[:,a_scan]
        bounds = np.where(c_ascan==np.amax(c_ascan))[0]
        if np.size(bounds) == 3 :
            border = int(bounds[1] + round(abs(bounds[-1]-bounds[-2])/2) + 2)
        elif np.size(bounds) == 2 :
            border = int(bounds[1] + round(bounds[-1]/2) + 2)
        else :
            print(f"encountered error while paring a-Scan No.{a_scan}")
        out_mask[bounds[0]:border, a_scan] = 255
        out_mask[border:, a_scan] = 127
    return out_mask   
