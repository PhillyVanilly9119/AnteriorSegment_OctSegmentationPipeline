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
from tkinter.filedialog import Tk, askdirectory

def fast_scandir(dirname):
    sub_folders = []
    folders = [f.path for f in os.scandir(dirname) if f.is_dir()]
    for subdir in folders :
        for f in os.scandir(subdir) :
            if f.is_dir() :
                sub_folders.append(f.path)
    return sub_folders   

def create_dir(directory) :
    if not os.path.isdir(directory) :
            os.mkdir(directory)
            
def clean_path_selection(text) :
    root = Tk()
    root.withdraw()
    path = askdirectory(title=text, mustexist=True)
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
    assert os.path.isfile(path), "Input path is not a path to an image!"
    h, w = dims[0], dims[1]
    image = Image.open(path).resize((h,w))
    return np.asarray(image, dtype=np.uint8)

def save_single_image(file_name, img, c_map='gray') :
    plt.imsave(file_name, img, cmap=c_map)
    
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
    for image in range(np.shape(images)[0]) :
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
  
### FOR NETWORK ###
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
            print("[WARNING:] Stumbled upon invalid cornea segmentation in A-Scan \#{ascan}...")
            pass 
        # Create Masks for 3-channel segmentation
        masks = []
        masks.append(cornea) # Mask No.1
        masks.append(ovd) # Mask No.2
        tmp = np.add(cornea, ovd)
        _, background = cv2.threshold(tmp, 127, 255, cv2.THRESH_BINARY_INV)
        masks.append(background) # Mask No.3
        
    return masks, tripple_mask

def create_tripple_masks_for_training(path, dtype='.bmp', dims=(1024,1024), 
                                      is_save_newly_calced_masks=True):
    """
    >>> prepares data array for passing and training to network
    
    return dimensions:  (n_img, height, width, n_masks)
    
    """
    print("Prepocessing masks [GROUND TROUTH] for training...")
    list_mask_files = ['mask_cornea',
                       'mask_ovd', 
                       'mask_background']    
    trip_masks = [] 
    files = os.listdir(path)
    for c, f in enumerate(tqdm(files)) :
        # Check if the single masks already exist and load them, else create them from the combined mask
        crn_file = os.path.join(path, f, str(list_mask_files[0] + dtype))
        ovd_file = os.path.join(path, f, str(list_mask_files[1] + dtype))
        bg_file = os.path.join(path, f, str(list_mask_files[2] + dtype))
        if not os.path.isfile(crn_file) or not os.path.isfile(ovd_file) or not os.path.isfile(bg_file):
            # Load line-segmented mask
            if os.path.isfile(os.path.join(path, f, 'mask.bmp')) :
                raw_mask = np.asarray(Image.open(os.path.join(path, f, 'mask.bmp')).resize(dims))
            elif os.path.isfile(os.path.join(path, f, 'mask.png')) :
                raw_mask = np.asarray(Image.open(os.path.join(path, f, 'mask.png')).resize(dims))
            else :
                print(f"No valid mask file found in {os.path.join(path, f)}")
            # create and add all three masks in order
            masks, _ = create_output_channel_masks(raw_mask)
            trip_masks.append(np.moveaxis(masks, 0, -1))
            masks = np.asarray(masks)

            def safe_singular_mask(mask, file_path) :
                assert np.size(dims) == 2, "[DIMENSION ERROR] - please enter image height and width"
                plt.imsave(file_path, mask, cmap='gray', format='bmp')
 
            if is_save_newly_calced_masks :
                safe_singular_mask(masks[0,:,:], crn_file)
                safe_singular_mask(masks[1,:,:], ovd_file)
                safe_singular_mask(masks[2,:,:], bg_file)
                print(f"\nSaved calculated masks from folder/ iteration No. {c}!")
        else :
            cornea = np.asarray(Image.open(os.path.join(path, f, str(list_mask_files[0] + dtype))).resize(dims))
            ovd = np.asarray(Image.open(os.path.join(path, f, str(list_mask_files[1] + dtype))).resize(dims))
            background = np.asarray(Image.open(os.path.join(path, f, str(list_mask_files[2] + dtype))).resize(dims))
            new_masks = np.dstack((cornea[:,:,0], ovd[:,:,0], background[:,:,0]))
            trip_masks.append(new_masks)
              
    print("Done [LOADING] and/or creating [MASKS]!")
    # return dimensions are (n_img, height, width, n_masks)        
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
        stack = np.concatenate((images,
                                create_flipped_img_4d_tensor(images),
                                create_flipped_img_4d_tensor(images, axis=0),
                                create_flipped_img_4d_tensor(images, axis=1)
                                ))
    elif x_flip and not y_flip : 
        stack = np.concatenate((images,
                                create_flipped_img_4d_tensor(images, axis=0),
                                ))
    elif not x_flip and y_flip :
        stack = np.concatenate((images,
                                create_flipped_img_4d_tensor(images, axis=1)
                                ))
    else :
        print("You have chosen to not add any flipped images")        

    print(f"Added {np.shape(stack)[0]-sizes[0]} images [THROUGH FLIPPING] to original data!")
    return stack
    
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
    path_source = askdirectory(title='Please select folder from which you want to add data') 
    assert os.path.isdir(path_source), "Directory from which I am supposed to load data does not exist!"
    path_target = askdirectory(title='Please select folder to which you want to add data') 
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
    ### TODO: Test!!!!
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
        
def sanity_check_training_data(scans, masks, update_rate_Hz=2):
    """
    >>> Quick run-through of overlayed images (scans+masks) 
    to see if the scans and masks order matches in data stacks
    REMARK: June 26th image dimensions in pre-processing := (n_img, h, w)
    """       
    print("Displaying images...")
    if scans.shape[2] != masks.shape[2]:
        print("Dimensions of data stacks do not match!")
    for im in tqdm(range(scans.shape[0])):
        plt.ion()
        plt.imshow(scans[im,:,:], 'gray', interpolation='none')
        plt.imshow(masks[im,:,:], 'jet', interpolation='none', alpha=0.7)
        plt.show()
        plt.pause(1/update_rate_Hz)
        plt.clf()    
    print("Done displaying images!")