# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 08:52:56 2020

@author: Philipp
"""

import os 
import cv2
import glob 
import numpy as np
from PIL import Image
from tqdm import tqdm
from tkinter.filedialog import Tk, askdirectory, askopenfilename 

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
    return int(path.split('\\')[folder_idx].split(img_dtype)[0])

# =============================================================================
# ### Main Processing ###
# =============================================================================
def create_new_masks_autoSegmented(path, dims=(1024,1024)) :
    assert os.path.isdir(path), FileNotFoundError("[FILE NOT FOUND in >>create_new_masks_autoSegmented()<<]")
    dirs_vols = fast_scandir(path)
    for folder in dirs_vols :
        indices = []
        print(folder)
        for c_mask, mask in enumerate(folder) :
            break
            indices.append(get_img_idx(c_mask))
        print(indices)
        #curr_folder = sort_list_after_number(folder)

def create_new_masks_manuSegmented(path, dims=(1024,1024)) :
    pass

# =============================================================================
# ### MOVED ###
# =============================================================================
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