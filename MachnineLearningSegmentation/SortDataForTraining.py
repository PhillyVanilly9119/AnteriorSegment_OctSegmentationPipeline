# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:59:03 2020

@author: Philipp
"""

import os
import glob
import numpy as np
from PIL import Image

def sortAndAddTrainingData(main_path, train_dt_folder):
# =============================================================================
#     TODO: write logic to seamlessly add images to training data if numbers already exist
#     TODO: Add user input sanity check of overlayed images -> call sanityCheckData()
# =============================================================================
    bScan_path = main_path
    png_extension = '.png'
    bmp_extension = '.bmp'
    
    # folders for training data
    train_main_path = os.path.join(train_dt_folder, 'Set1') 
    train_bScan_path = os.path.join(train_main_path, 'image')
    if not os.path.exists(train_bScan_path):
        os.makedirs(train_bScan_path)
    train_mask_path = os.path.join(train_main_path, 'mask')
    if not os.path.exists(train_mask_path):
        os.makedirs(train_mask_path)

    # Load b-Scans
    if os.path.isdir(bScan_path) is True:
        bScan_list = glob.glob(os.path.join(bScan_path, "*.bmp"))
        # sort list after b-Scan #'s
        bScan_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        for infile in bScan_list:
            number = infile.split('\\')[-1].split(bmp_extension)[0]
            im = Image.open(infile)
            if np.array(im).shape == (1024, 512): 
                im.save(os.path.join(train_bScan_path, number + png_extension)) 
    else:
        print("The mask folder: \"{}\" does not exist".format(bScan_path))
    
    # Load Masks
    folder = bScan_path.split('\\')[-1] # get last folder in "SELECETED" dir
    mask_path = os.path.join(bScan_path, 'Segmented_Data', 'masks_' + folder)
    if os.path.isdir(mask_path) is True:
        mask_list = glob.glob(os.path.join(mask_path, "*.png"))
        # sort list after masks #'s
        mask_list.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
        for infile in mask_list: 
            number = infile.split('\\')[-1].split('No')[1].split(png_extension)[0]
            if infile.endswith(png_extension):
                im = Image.open(infile)
                if np.array(im).shape == (1024, 1024): 
                    im.save(os.path.join(train_mask_path, str(f'{int(number):03}') + png_extension)) 
    else:
        print("The mask folder: \"{}\" does not exist".format(mask_path))


data_path = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\SegmentierteVolumen\VISCOAT_1_1_OD-2020-04-24_091514"
training_path = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\Training"
sortAndAddTrainingData(data_path, training_path)
