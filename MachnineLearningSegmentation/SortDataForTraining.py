# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 14:59:03 2020

@author: Philipp
"""

import os
import uuid
import glob
import shutil
import numpy as np
from PIL import Image
from tqdm import tqdm
from tkinter.filedialog import askdirectory


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

add_data_to_main_folder(flag_renameFilesTargetDir=False)


### DEPRECTAED ###
def sortAndAddTrainingData(main_path, train_dt_folder):
# =============================================================================
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


# =============================================================================
# data_path = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\SegmentierteVolumen\VISCOAT_1_1_OD-2020-04-24_091514"
# training_path = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\Training"
# sortAndAddTrainingData(data_path, training_path)
# =============================================================================