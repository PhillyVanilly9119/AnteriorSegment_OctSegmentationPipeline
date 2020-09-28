# -*- coding: utf-8 -*-
"""
Created on Tue Sep 15 08:52:56 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at
"""

"""
TODO:
    > Add function description and make it more abstract
"""

# Global imports
import os 
import cv2
import uuid
import glob 
import shutil
import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt
from tkinter.filedialog import Tk, askdirectory, askopenfilename

def fast_scandir(dirname):
    sub_folders = []
    folders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for subdir in folders :
        for f in os.scandir(subdir) :
            if f.is_dir() :
                sub_folders.append(f.path)
    return sub_folders   

def get_subdirs_only(path) :
    sub_dirs = [x[0] for x in os.walk(path)]
    return sub_dirs[1:] 
    
def create_dir(directory) :
    if not os.path.isdir(directory) :
            os.mkdir(directory)
            
def clean_path_selection(text) :
    root = Tk()
    root.withdraw()
    path = askdirectory(title=text, mustexist=True)
    root.destroy()
    return path

def clean_file_selection(text) :
    root = Tk()
    root.withdraw()
    path = askopenfilename(title=text)
    root.destroy()
    return path

def sort_list_after_number(in_list) :
    in_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
    return in_list
 
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
# IMAGE PROCESSING FUNCTIONS
# =============================================================================
def get_img_idx(path, folder_idx=-1, img_dtype='.bmp') :
    img_num = path.split('\\')[folder_idx].split(img_dtype)[0]
    return int(img_num)

def get_img_dirs(path) :
    f = []
    for (dirpath, dirnames, filenames) in os.walk(path):
        f.extend(filenames)
    return f
    
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
    assert os.path.isfile(path), f"Path {path} is not an image file!"
    h, w = dims[0], dims[1]
    image = Image.open(path).resize((h,w))
    return np.asarray(image, dtype=np.uint8)
    
def save_single_grey_img(img, file_path, file_type='bmp') :
    #assert np.shape(np.size((img))) == 2, "[DIMENSION ERROR] of input image"
    plt.imsave(file_path, img, cmap='gray', format=file_type)

def convert_mask_vals_to_trips(mask) :
    qrt = round(255/4)
    new_mask = np.zeros_like(mask)
    new_mask[(mask < qrt)] = 0
    new_mask[(mask > qrt) & (mask < 3*qrt)] = 127
    new_mask[(mask > 3*qrt)] = 255
    return np.asarray(new_mask, dtype=np.uint8)
    
def overlay_transparent(background_img, img_to_overlay_t, x=0, y=0, overlay_size=None):
	bg_img = background_img.copy()
	if overlay_size is not None:
		img_to_overlay_t = cv2.resize(img_to_overlay_t.copy(), overlay_size)
	# Extract the alpha mask of the RGBA image, convert to RGB 
	b,g,r,a = cv2.split(img_to_overlay_t)
	overlay_color = cv2.merge((b,g,r))
	# Apply some simple filtering to remove edge noise
	mask = cv2.medianBlur(a,5)
	h, w, _ = overlay_color.shape
	roi = bg_img[y:y+h, x:x+w]
	# Black-out the area behind the logo in our original ROI
	img1_bg = cv2.bitwise_and(roi.copy(),roi.copy(),mask = cv2.bitwise_not(mask))	
	# Mask out the logo from the logo image.
	img2_fg = cv2.bitwise_and(overlay_color,overlay_color,mask = mask)
	# Update the original image with our new ROI
	bg_img[y:y+h, x:x+w] = cv2.add(img1_bg, img2_fg)
	return bg_img

# =============================================================================
# IMAGE PRE-PROCESSING 
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
        
def create_flipped_img_4d_tensor(images, axis=None) :
    stack = np.zeros_like(images)
    # GO THROUGH ALL IMAGES
    for image in tqdm(range(np.shape(images)[0])) :
        # GO THROUGH ALL CHANNELS
        for channel in range(np.shape(images)[-1]) :
            stack[image,:,:,channel] = np.flip(images[image,:,:,channel], axis)
    return stack       

# =============================================================================
# IMAGE POST-PROCESSING
# =============================================================================
### FILTER-OPERATIONS ###
def open_and_close(image, kernel_size=3) :
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.morphologyEx(cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel), 
                            cv2.MORPH_CLOSE, 
                            kernel)

# =============================================================================
# MASK CREATION - TEMP-FCNTs
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
            new_mask = recalculate_auto_mask_boundaries(curr_mask)
            # Save mask and scan to folder
            save_single_grey_img(curr_scan, os.path.join(curr_dir, 'raw_bScan.bmp'))
            save_single_grey_img(new_mask, os.path.join(curr_dir, 'mask.bmp'))
            
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
        new_mask = recalculate_manu_mask_boundaries(curr_mask)
        # Save mask and scan to folder
        save_single_grey_img(curr_scan, os.path.join(target_dir_curr_file, 'raw_bScan.bmp'))
        save_single_grey_img(new_mask, os.path.join(target_dir_curr_file, 'mask.bmp'))

def recalculate_auto_mask_boundaries(mask) : 
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

def recalculate_manu_mask_boundaries(mask) : 
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
    
# =============================================================================
# FILE SORTING 
# =============================================================================
def copy_folders_to_new_dir(source, target):
    for files in os.listdir(source):
        shutil.move(os.path.join(source, files), os.path.join(target, files))
        
def rename_folders_in_dir(path):  
    for file in os.listdir(path):
        if os.path.isdir(os.path.join(path, file)):
            rand_name = uuid.uuid4().hex # create random hex 32-digit hex-num
            os.rename(os.path.join(path, file), os.path.join(path, rand_name)) # replace folder name with random hex name

def add_data_to_main_folder(flag_renameFilesTargetDir=False):
    """
    Add new data to training data, indepently of existing folders
    >> path_source = directory to existing training data
    >> path_target = directory to data that is supposed to be added
    # TODO: implement more efficient check of unique folders 
    """
    path_source = clean_path_selection('Please select folder from which you want to add data') 
    assert os.path.isdir(path_source), "Directory from which I am supposed to load data does not exist!"
    path_target = clean_path_selection('Please select folder to which you want to add data') 
    assert os.path.isdir(path_target), "Directory to were I am supposed to add data does not exist!"
    assert path_source is not path_target, "You have selected the same directory twice..."

    print("Renaming folders to ensure uniqueness in folder names...")
    rename_folders_in_dir(path_target) # rename data-folders that you want to add
    if flag_renameFilesTargetDir:
        rename_folders_in_dir(path_source)
    # check for any duplicates after renaming new data-folders
    print("Checking if target and source files are all unique...")
    for name1 in tqdm(path_target):
        for name2 in path_source:
            if name1 == name2:
                rename_folders_in_dir(path_source)
            else:
                pass
    
    print("Adding selected folders to data base...")
    copy_folders_to_new_dir(path_source, path_target)
    path_updated_training_data = os.listdir(path_source)
    print("Done adding new data for machine learning")   
    
    return path_updated_training_data

# =============================================================================
#  VISUALISATION
# =============================================================================   
def show_images_in_subplots(images, num=None) :
        sizes = np.shape(images)
        if num == None:
            num = sizes[2] # number is images in stack
        else:
            num = num
        assert num <= 25, "You are trying to [DISPLAY TOO MANY IMAGES]"
        frame = int(np.ceil(np.sqrt(num)))
        fig, ax = plt.subplots(frame, frame)
        for f1 in range(frame) :
            for f2 in range(frame) :
                idx = ((f2+1)+(f1*frame))-1
                if idx < num :
                    ax[f1,f2].imshow(images[:,:,idx], cmap='gray')
                    ax[f1,f2].title.set_text(f'Scan No. {idx} (from stack)')
                else :
                    ax[f1,f2].imshow(images[:,:,0], cmap='gray')
                    ax[f1,f2].title.set_text(f'[CAUTION!] index out of bounds - displaying Scan No. {0} instead')
                    
def predict_and_show_segmentation(model, X_test, Y_test, num_img=9):
    """
    Display up to 16 predicted bScan-overlay
    ### TODO: Test!!!!
    """
    preds_test = model.predict(X_test, verbose=1) # predict 
    preds_test_t = (preds_test > 0.5).astype(np.uint8) # apply threshold
    preds_test_t = preds_test_t[:,:,:,0] # delete image-channel-dimension
    assert num_img < 17, "Number of images to display of too large too appreciate sufficient resolution..."
    page_length = int(np.ceil(np.sqrt(num_img)))
    fig, ax = plt.subplots(page_length, page_length)
    for f1 in range(page_length) :
        for f2 in range(page_length) :
            idx = ((f2+1)+(f1*page_length))-1
            # Check shape of tensors
            overlay = overlay_transparent(X_test[idx,:,:], preds_test_t[idx,:,:])
            # precautionary measure if user input of num_img is too big
            if idx < num_img :
                ax[f1,f2].imshow(overlay, cmap='gray')
                ax[f1,f2].title.set_text(f'Overlayed b-Scan ans Mask No. {idx}')
            else :
                ax[f1,f2].imshow(overlay, cmap='gray')
                ax[f1,f2].title.set_text(f'[CAUTION!] index out of bounds - displaying overlay No. {0} instead')
        
def sanity_check_training_data(scans, cornea, milk, update_rate_Hz=2):
    """
    >>> Quick run-through of overlayed images (scans+masks) 
    to see if the scans and masks order matches in data stacks
    REMARK: June 26th image dimensions in pre-processing := (n_img, h, w)
    """       
    print("Displaying images...")
    if (scans.shape[2] != cornea.shape[2]) or (scans.shape[2] != milk.shape[2]):
        print("Dimensions of data stacks do not match!")
    for im in tqdm(range(scans.shape[0])):
        plt.ion()
        plt.imshow(scans[im,:,:], 'gray', interpolation='none')
        plt.imshow(cornea[im,:,:], 'jet', interpolation='none', alpha=0.6)
        plt.imshow(milk[im,:,:], 'jet', interpolation='none', alpha=0.6)
        plt.show()
        plt.pause(1/update_rate_Hz)
        plt.clf()    
    print("Done displaying images!")