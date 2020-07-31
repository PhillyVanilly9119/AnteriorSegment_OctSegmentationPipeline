# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

"""

import os
import sys
import cv2
import glob 
import numpy as np
import scipy
import matplotlib.pyplot as plt
from PIL import Image  
from tqdm import tqdm
from pathlib import Path
from tensorflow import keras
from main_Training import DataPreprocessing as DP
from tkinter.filedialog import Tk, askdirectory, askopenfilename 

# =============================================================================
# I/O Functions
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
        
# =============================================================================
# Functions for inference, i.e. apply prediction on raw scans
# =============================================================================
class AutoSegmentation() :
    
    def __init__(self, net_dims, raw_dims, output_dims) :
        self.net_dims = net_dims
        self.raw_dims = raw_dims
        self.output_dims = output_dims  
    
    #AUXILIARY   
    @staticmethod
    def fast_scandir(dirname):
        sub_folders = []
        folders = [f.path for f in os.scandir(dirname) if f.is_dir()]
        for subdir in folders :
            for f in os.scandir(subdir) :
                if f.is_dir() :
                    sub_folders.append(f.path)
        return sub_folders   
    
    #IMAGE FILTER 
    @staticmethod
    def open_and_close(image, kernel_size=3) :
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        return cv2.morphologyEx(cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel), cv2.MORPH_CLOSE, kernel)
    
    def set_img_tripple_vals(image) : 
        assert image.dtype==np.uint8, "Image has wrong data type"
        # TODO: Set values to 0, 127 or 255
        return image
    
    @staticmethod
    def scale_value_range(X, x_min=0, x_max=1):
        nom = (X-X.min(axis=0))*(x_max-x_min)
        denom = X.max(axis=0) - X.min(axis=0)
        return np.asarray(x_min + nom/denom, dtype=np.uint8)
    
    @staticmethod
    def interpolate_curve(vector, valid) :
        vector = np.array(vector, dtype=np.uint16)
        valid = np.array(valid, dtype=bool)
        assert np.size(vector) == np.size(valid), "Dimensional mismatch of vectors"
        valid_x = np.squeeze(valid.nonzero())
        valid_y = vector[valid_x]
        poly = np.polyval(np.polyfit(valid_x, valid_y, 2), np.linspace(0, 1023, 1024))
        return np.array(poly, dtype=np.uint16)
    
    @staticmethod
    def check_for_continuity(vector, delta=5) :
        vector = np.asarray(vector, dtype=np.uint16)
        bool_curve = np.zeros(shape=(np.shape(vector)))
        bool_curve[0] = True
        for pix in range(1, np.shape(vector)[0]) :
            if ( (vector[pix]<vector[pix-1]+delta) & (vector[pix]>vector[pix-1]-delta) ) :
                if vector[pix] < 5 :
                    bool_curve[pix] = False
                else :
                    bool_curve[pix] = True
            else :
                bool_curve[pix] = False
        return np.array(bool_curve, dtype=bool)

    @staticmethod
    def calculate_thickness(boundary1, boundary2) :
        if boundary2 == 1023 :
            return 1000
        else :
            return boundary2-boundary1
    
    @staticmethod    
    def find_boundaries_in_mask(mask, AScans=None) :
        """
        CONDITION 1:
        CONDITION 2:
        1) Find Epithelium
        2) Find Endothelium -> with fixed thickness for interpolation
        3) Find OVD Start (with a different continuity condition?)
        4) calculate thickness  -> I) set to max, if y(1023) == 0, i.e. no OVD in path in lower boundary
                                -> II) calc thickness in pxls
                                -> III) -1 if no pixel in aScan    
        # if no OVD or ovd @1023 -> write max  value
        
        """
        crn_thickness = 320 # >>TBD<<
        # TODO: round values in mask to 255, 127 and 0
        crn_val = 255
        milk_val = 127
        epithelium = []
        endothelium = []
        milk = []
        OVD_THICKNESS = [] # final return value
        if AScans is None :
            AScans = np.shape(mask)[1]

        # 1) FIND Epithelium and 
        # 2) Epithelium
        for aScan in range(AScans) :
            c_aScan = mask[:,aScan] 
            # Find positions, where cornea pixels are
            c_spots = np.where(c_aScan==crn_val) # Find positions, where milk area is
            # If there is a cornea value in the current A-Scan
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
    
    def load_data_from_folder(self) :
        """
        Primitive to load *.bmp-files of OCT b-Scans generated by ZEISS RESCAN
        """                
        path = self.clean_path_selection('Please select data for segmentation')
        # check if path contains images
        assert any(fname.endswith('.bmp') for fname in os.listdir(path)), "Directory [DOES NOT CONTAIN ANY IMAGES] / *.BMP-files!"
        scan_list = glob.glob(os.path.join(path, "*.bmp"))
        # sort list after b-Scan #'s in image file names
        scan_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        # Load (ONLY) b-Scans (with size = IMG_HEIGHT x IMG_WIDTH)
        scans = [np.asarray(Image.open(infile)) for infile in scan_list if np.shape(np.asarray(Image.open(infile))) == (self.raw_dims[0],self.raw_dims[1])]
        return np.dstack(scans), path
        
    def resize_img_stack(self, images, out_dims) :
        """
        Primitive to reshape image data stack and return as a 3D numpy-array
        """
        assert images.ndim == 3, "[IMAGE RESIZING ERROR] Wrong dimensionality of image data!"
        in_dims = np.shape(images)
        #print(f"Reshaping images from {in_dims} to {out_dims}...")
        images = [cv2.resize(images[:,:,i], 
                             (out_dims[0], out_dims[1]), 
                             interpolation = cv2.INTER_AREA) for i in range(in_dims[2])]
        return np.dstack(images)
        
    def apply_trained_net(self, scans, is_fixed_path_to_network=True) :
        """
        Predict and display segmented b-Scans -> Display to user
        """
        assert scans.ndim == 3, "[PREDICTION ERROR - IMAGE SIZE] - please check image data!"
        scans = self.resize_img_stack(scans, (self.net_dims[0], self.net_dims[1], scans.shape[2]))
        if is_fixed_path_to_network :
            path = r'C:\Users\Philipp\Desktop\Network_Melli\current_best_model_version9_30602020_1413_acc9984'
        else :
            path = askopenfilename(title='Please select file with trained net for [AUTO-SEGMENTATION]')          
        model = keras.models.load_model(path)
        predictions = np.squeeze(model.predict(np.expand_dims(np.rollaxis(scans, 2), axis=-1), verbose=1))
                
        #Threshold the masks for area-prediction
        masks = (predictions > 0.5).astype(np.uint8)
        masks = np.moveaxis(masks, 0, -1)
        
        return masks
      
    @staticmethod
    def clean_path_selection(text) :
        root = Tk()
        root.withdraw()
        path = askdirectory(title=text, mustexist=True)
        root.destroy()
        return path
    
    @staticmethod    
    def check_for_duplicates(path_one, path_two) : 
        """
        Returns BOOL for if the file exists in both dirs
        """ 
        if os.path.isfile(path_one) and os.path.isfile(path_two) : 
            return True
        else :
            return False    

    @staticmethod
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
    
    def check_predicted_masks(self, scans, masks, path, flag_apply_filter) :
        """
        Sort and check if automatically segmented b-Scans were segmented correctly
        --> Input images dimensionality = [h,w,ch,num] (reshaping in function)        
        """
        masks = np.moveaxis(masks, 2, -1)
        path_good = os.path.join(path, 'CorrectScans')
        Path(path_good).mkdir(parents=True, exist_ok=True)
        path_bad = os.path.join(path, 'IncorrectScans')
        Path(path_bad).mkdir(parents=True, exist_ok=True)
        idx = self.find_max_idx(path_good, path_bad)
        print("Created paths for sorting!")
        print("Please review automatically segmented images...")
        scans = self.resize_img_stack(scans, self.output_dims)
        cornea = self.resize_img_stack(masks[:,:,:,0], self.output_dims)
        ovd = self.resize_img_stack(masks[:,:,:,1], self.output_dims)
        background = self.resize_img_stack(masks[:,:,:,2], self.output_dims)
        for im in range(idx, np.shape(scans)[2]) :            
            good_img_file = os.path.join(path_good, f'{im:03}' + '.bmp')
            bad_img_file = os.path.join(path_bad, f'{im:03}' + '.bmp')
            current_img = np.add(cornea[:,:,im],ovd[:,:,im])*255
            disp_img = np.concatenate((current_img, background[:,:,im]*255), axis=1)
            cv2.imshow(f"Predicted BACKGROUND-mask on original B-Scan No.{im} - left hand side = overlayed Cornea and OVD boundary - right hand side = background",
                       cv2.resize(disp_img, (1920,1080), interpolation = cv2.INTER_AREA))
            key = cv2.waitKey(0)
            if key == ord('y') or key == ord('Y') :
                if not self.check_for_duplicates(good_img_file, bad_img_file) :
                    # Create and save mask from which thickness determination should take place
                    cv2.imwrite(good_img_file, (np.add((cornea[:,:,im]*255),(ovd[:,:,im])*127))) 
                else :
                    print("[WARNING:] image with same number in both folders")  
                    continue
            elif key == ord('n') or key == ord('N') :
                if not self.check_for_duplicates(good_img_file, bad_img_file) :
                    plt.imsave(bad_img_file, scans[:,:,im], cmap='gray')
                else :
                    print("[WARNING:] image with same number in both folders")
                    continue
            else :
                print("You have pressed an invalid key... [EXITING LOOP]")
                cv2.destroyAllWindows()
                sys.exit(0)
            cv2.destroyAllWindows()
        
        print("Done displaying images!")
        
if __name__ == '__main__' :
    determine_thickness_for_database()
     
# =============================================================================
# TBD if deprecated - functions based on 1-channel UNet segmenation
# ============================================================================= 