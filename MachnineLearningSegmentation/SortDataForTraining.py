# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

"""

# Lib imports
import os
import uuid
import shutil
import numpy as np
from PIL import Image
from tqdm import tqdm
from tkinter.filedialog import askdirectory

# Local imports
 

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