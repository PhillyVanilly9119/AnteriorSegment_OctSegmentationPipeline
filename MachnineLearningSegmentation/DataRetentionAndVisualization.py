"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna,
            Center for Medical Physics and Biomedical Engineering
              
                                    **************
              
    Script containing functions to calculate thickness maps and perform analysis in them
                
                                    **************
"""

# Global imports 
import os
import cv2
import tqdm
import math
import random

import scipy.io
from scipy.stats import kruskal
from scipy.io import savemat

import numpy as np
import pandas as pd
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# Custom imports
import BackendFunctions as Backend
# import TrainingMain as Train

# OVD optical index list (empirially found by M. Wuest - wuest.melanie96@gmail.com)
index_dict = {
    "provisc": 1.357, # from here on: cohesive
    "zhyalinplus": 1.364,
    "amviscplus": 1.356, 
    "discovisc": 1.337, # from here on: diperse
    "healonendocoat": 1.357,
    "viscoat": 1.356,
    "zhyalcoat": 1.343,
    "combivisc": 1.353, # from here on: combi-systems
    "duovisc": 1.356,
    "twinvisc": 1.353,
}

#### TODO: Starting to clean up and rewrite some functions in OOP

class HandleThicknessMaps():
    def __init__(self):
        pass
    
    def get_loading_path(self, flag):
        pass


#########################################
### I/O AND MEASUREMENT NAME HANDLING ###
#########################################
def get_ovd_name(path_full, dtype='.mat') :
    """
    >>> get the name of the ovd and the file name from the full file path
    -> assuming file name structure: "<mapName>_<ovdName>_<measurement>_<repetition>_<DateTime>"
    """
    file_parts = os.path.split(path_full)
    file_name = file_parts[-1]
    ovd_name = file_name.split('_')[1]
    return ovd_name

def get_repetition_number(path_full, delim='_', dtype='.mat') :
    """
    >>> returns the number  the full file path
    -> assuming file name structure: "<mapName>_<ovdName>_<measurement>_<repetition>_<DateTime>"
    """
    repetition = path_full.split(delim)[-4]
    if int(repetition) == 1 or int(repetition) == 2 :
        return int(repetition)
    else :
        print("Extracted repetiton number is [INVALID]")

def return_matching_ovd_index(opt_ind_dict, ovd_name) : 
    """
    >>> return the OVDs' opical index from dict 
    """
    for name, index in opt_ind_dict.items() :
        ovd_name = ovd_name.lower()
        if ovd_name == name : 
            return index
        
def load_heat_map_from_current_sub_dir(path_file, mat_var_name) :
    """
    >>> loads heat map from path parameter and returns 
    i)      heat map as 2D-array and
    ii)     measurement name from file name
    iii)    name of the OVD
    -> assuming file name structure: "<mapName>_<ovdName>_<measurement>_<repetition>_<DateTime>"
    -> assuming all *.mat files are in one directory
    """
    heat_map = Backend.load_mat_file( path_file, mat_var_name, dtype=np.uint16 )
    return heat_map


#############################
### Loading specific maps ###
#############################
""" Processing evaluated heat maps according to the sorting 
(all, same name, same name and measurement rep)"""
def stack_all_heat_maps_in_dir(main_path, mat_var_name='INTERPOL_THICKNESS_MAP', is_manual_path_selection=True) :
    """
    >>> creates a 3D data tensor, containing the stacked thickness maps
    """
    if is_manual_path_selection :
        main_path = Backend.clean_path_selection("Please select path with thickness maps")  
    stacked_map_array = []
    for file in os.listdir(main_path) :
        c_full_file_path = os.path.join(main_path, file)
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) :
            stacked_map_array.append( load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name) )
    return np.dstack( np.asarray(stacked_map_array) )
            
def stack_all_heat_maps_same_ovd(main_path, ovd_name, mat_var_name='INTERPOL_THICKNESS_MAP', is_manual_path_selection=True) :
    """
    >>> returns 3D data tensor, containing the stacked thickness maps of the same OVDs
    """
    if is_manual_path_selection :
        main_path = Backend.clean_path_selection("Please select path with thickness maps")  
    stacked_map_array = []
    for file in os.listdir(main_path) :
        c_full_file_path = os.path.join(main_path, file)
        c_ovd_name = get_ovd_name(c_full_file_path) 
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) and c_ovd_name.lower()==ovd_name.lower() :
            stacked_map_array.append( load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name) )
    return np.dstack( np.asarray(stacked_map_array) )

def stack_all_heat_maps_same_ovd_and_rep(main_path, ovd_name, index, meas_rep_num, 
                                         mat_var_name='INTERPOL_THICKNESS_MAP', 
                                         is_manual_path_selection=True,
                                         is_resize_to_square_map=True) :
    """
    >>> returns 3D data tensor, containing the stacked thickness maps of the same OVDs from the same measurement repetition
    """
    
    if meas_rep_num != 1 or meas_rep_num != 2:
        ValueError("num_rep argument invalid... Please check if 3rd parameter is either 1 or 2")
    
    if is_manual_path_selection :
        main_path = Backend.clean_path_selection("Please select path with thickness maps")  
    stacked_map_array = []
    # print(os.listdir(main_path))
    for file in os.listdir(main_path) :
        c_full_file_path = os.path.join(main_path, file)
        c_ovd_name = get_ovd_name(c_full_file_path)
        c_rep = get_repetition_number(c_full_file_path)
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) and \
            c_ovd_name.lower()==ovd_name.lower() and c_rep==meas_rep_num:
            index = index_dict[c_ovd_name.lower()]
            data_stack_um = convert_ovd_map_to_um( load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name), 
                                                  index)  
            if is_resize_to_square_map :
                data_stack_um = cv2.resize(data_stack_um, (512,512))
            stacked_map_array.append(data_stack_um)  
    return np.asarray(stacked_map_array)

######################
### MAP PROCESSING ###
######################
def convert_ovd_map_to_um(heat_map, index, scan_depth_um=2900, aLen_plxs=512, dtype_return=np.uint16) :
    """
    >>> converts the values of the ovd thickness map from realtive a-Scan samples/pixels to µm
    """
    conversion_factor = (scan_depth_um * 1.34) / (index * aLen_plxs) # convert from pixels to µm acc. to opt. idx of OVD 
    return np.asarray( conversion_factor * heat_map, dtype=dtype_return )

def save_mat_file_as_xls(mat_file, file_name, path='', is_manual_path_selection=True) :
    """
    >>> Saves an existing thickness map (*.MAT-file) to a *.XLS-file
    """
    shape_dims = (2048, 128)
    assert np.shape(mat_file)[0] == np.shape(mat_file)[1], "Mat-File does not contain square shaped thickness map"
    mat_file = mat_file.reshape(shape_dims) # Stack values so that they fit into excel sheet
    df = pd.DataFrame(mat_file)
    # if manual saving path selection
    if is_manual_path_selection :
        path = Backend.clean_path_selection("Please select the path from which you want to save the data")
    filepath = os.path.join(path, file_name.split('.mat')[0] + '.xls')
    df.to_excel(filepath, index=False)
    return True # rethink return type and check all funcs that use this one

def convert_all_mat2xls_files(path_saving, path_loading, mat_var_name) :
    """
    >>> Converts all *.MAT-files (thickness maps = mat-var-name) to *.XLS-files and saves them 
    """ 
    print(f'Converting and saving *.MAT-files from \n>>{path_loading}<< \nas *.XLS-files to \n>>{path_saving}<<')   
    for file in tqdm(os.listdir(path_loading)) :
        c_full_file_path = os.path.join(path_loading, file)
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) :
            c_map = load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name)
            if not save_mat_file_as_xls(c_map, file, path_saving, is_manual_path_selection=False) :
                print(f'Error with file {file}')

def calc_value_ratio_for_threshold(thickness_map, thickness_threshold_um) :
    """
    >>> Finds and returns percentages of values in thickness maps
        above (1st return value) and below (2nd return value) a threshold
        CAUTION: Assumes all values in map and threshold are in µm !!!
    """
    c_map = np.asarray(thickness_map).flatten()
    greater = np.sum(c_map > thickness_threshold_um) / np.size(c_map)
    less = 1 - greater
    return np.round(100*greater, 2), np.round(100*less, 2) 

def find_values_in_inner_circle(c_map, radius_pxls) :
    """
    >>> Finds and returns values of the inner circle in a thickness map
    """
    inner_pnts = []
    inner_pnts_spots = []
    x_length, y_length = np.shape(c_map)[0], np.shape(c_map)[1]
    x_center, y_center = int(x_length/2), int(y_length/2)
    assert x_center > radius_pxls, "Selected radius is too big for image size in x-direction"
    assert y_center > radius_pxls, "Selected radius is too big for image size in y-direction"
    for i in range(x_length) :
        for j in range(y_length) :
            if int(np.round(np.sqrt((i-x_center)**2 + (j-y_center)**2))) <= radius_pxls :
                inner_pnts.append(c_map[i,j])
                inner_pnts_spots.append([i,j])
    return np.asarray(inner_pnts), np.asarray(inner_pnts_spots)


def grab_inner_circle_vals_only(stack_in, num_ovds: int=10, radius_pxls: int=128):
    assert stack_in.ndim == 3 # expecting 3D data cube 
    return np.asarray([find_values_in_inner_circle(stack_in[i,:,:], radius_pxls)[0] for i in range(num_ovds)])


def load_all_ovd_data_after_meas_rep(index_dict, path_files_loading, path_files_saving, rep_num,
                      is_save_files=False, is_process_inner_circle=False) :
    """
    returns data stack with all OVDs from one measurement repetition
    data_stack = [name_ovd, measurement, length, width]
    """
    return_list = []
    for name, index in index_dict.items() :
        data_stack = stack_all_heat_maps_same_ovd_and_rep(path_files_loading, name, index, rep_num, 
                                                          mat_var_name='ORIGINAL_THICKNESS_MAP',
                                                          is_manual_path_selection=False)
        # grab only values from inner 3mm diameter 
        if is_process_inner_circle :
            new_stack = []
            for img in range(data_stack.shape[0]):
                new_stack.append(cv2.resize(data_stack[img,:,:], (512,512)))
            new_stack = np.asarray(new_stack)
            data_inner_dia = grab_inner_circle_vals_only(new_stack) # asserting [x, y, n] cube (n = number of measurement repetitions)
            data_stack = data_inner_dia
            
            if is_save_files :
                savemat(os.path.join(path_files_saving, 'CombinedMapsInner3mm' + name + 'mat'), 
                        {'ALL_COMBINED_GROUP_THICKNESS_MAPs': data_stack.astype(np.uint16)})
        return_list.append(data_stack)

    return np.asarray(np.squeeze(return_list))    


def return_n_random_choices(data, samples) :
    return np.asarray(random.choices(data.flatten(), k=samples))


def create_pandas_data_frame(data, index_dict: dict, num_rep: int) :
    """ Returns input data (numpy-array) as a pandas data frame """
    assert data.ndim == 3
    # assert that data stack contains as much different OVDs as the name dict contains entries
    assert data.shape[-1] == len(index_dict) 
    
    key1 = "Thickness values in [µm]"
    key2 = "Type of measurement"
    key3 = "OVD name"
    if num_rep == 1:
        rep_key = "after I/A"
    elif num_rep == 2:
        rep_key = "after I/A & Phaco"
    else :
        ValueError("num_rep argument invalid... Please check if 3rd parameter is either 1 or 2")
    
    frame_list = []
    for i, ovd in enumerate(index_dict.items()) : 
        df = pd.DataFrame( {key1:data[:,:,i].flatten(), key2:rep_key, key3:index_dict[ovd[0]]} )
        frame_list.append(df)

    return pd.concat(frame_list, ignore_index=True)


################
### PLOTTING ###
################   
  
def dummy_thickness_map_creation() :
    """
    >>> Create and save thickness maps
    """
    path_loading = r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm'
    path_saving = r'C:\Users\Philipp\Desktop\OVID Results\NewHeatMaps'
    mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM'
    x_label='Slow Scanning Axis [6mm]' 
    y_label='Fast Scanning Axis [6mm]'
    my_dpi = 300
    
    for i, file in tqdm(enumerate(os.listdir(path_loading))) :
        c_full_file_path = os.path.join(path_loading, file)
        just_file = file.split('.mat')[0].split('_')
        if int(just_file[3]) == 1 :
            suffix = ', after I/A (1)'
        elif int(just_file[3]) == 2 :
            suffix = ', after phaco (2)'
        else :
            raise SystemError("Error while parsing measurement repetition number")
        title = 'Thickness map of ' + just_file[1] + ', Measurement No.' + just_file[2] + suffix
        plt.ion()
        _, ax = plt.subplots(figsize=(3*1250/my_dpi, 3*1000/my_dpi))
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) :
            data_stack = load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name)
            plt.imshow(data_stack)
            cbar = plt.colorbar()
            cbar.set_label('OVD thickness in [µm]', fontsize=15)
            plt.clim(0, 2250)
            plt.title(title, y=1.025)
            ax.set_title(title, fontsize=15)
            ax.set_xlabel(x_label, fontsize=14)
            ax.set_ylabel(y_label, fontsize=14)
            ax.set_yticklabels([])
            ax.set_xticklabels([])
            plt.savefig(os.path.join( path_saving, (file.split('.mat')[0] + '.pdf') ), format='pdf')
        plt.clf()


def create_data_stack_and_pdFrame() :
    path_files_loading = r'C:\Users\Philipp\Desktop\OVID Results\DATA\OriginalSampling\Original Data'
    path_files_saving = r'C:\Users\Philipp\Desktop\plotvalues200um_one.mat'

    data = []    
    for name, index in index_dict.items():
        for i in range(1,3): # measurement repetiton number
            # data = first half of all valuesare 1st rep, se
            data.append(stack_all_heat_maps_same_ovd_and_rep(path_files_loading, name, index, i,
                                                 mat_var_name='ORIGINAL_THICKNESS_MAP',
                                                 is_manual_path_selection=(False)).flatten())        
    data = np.asarray(data)
    
    key1 = "Thickness values in [µm]"
    key2 = "Type of measurement"
    key3 = "OVD name"
    ovd = list(index_dict.keys())
    frame_list = []
    for i in range(data.shape[0]) : # interate through OVDs
        if i % 2 == 0 :
            rep_key = "after I/A"
        else :
            rep_key = "after I/A & Phaco"
        df = pd.DataFrame( {key1:data[i,:].flatten(), key2:rep_key, key3:ovd[i//2]} )
        frame_list.append(df)

    return data, pd.concat(frame_list, ignore_index=True)


def main() : 
    
    data, df =  create_data_stack_and_pdFrame()
    key1 = "Thickness values in [µm]"
    key2 = "Type of measurement"
    key3 = "OVD name"
    
    fig, ax = plt.subplots(figsize=(32, 18))
    ax = sns.violinplot(ax=ax, data = df, x = key3, y = key1, linewidth=2.5, 
                        inner='quartile', cut=0, fontsize=12, legend=False, 
                        hue=key2, split=True, palette='Blues')

    ax.set_xlabel(key3, fontsize=30)
    ax.set_ylabel(key1, fontsize=25)
    ax.set_title('Thickness value distribution per OVD', fontsize=36)
    ax.set_yticklabels(ax.get_yticks(), size=20)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize = 20)

    # plt.legend(title=key2, size=24, loc=1, bbox_to_anchor=(0.6,1))
    plt.setp(ax.get_legend().get_texts(), fontsize=20) # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize=24) # for legend title
    # ax._legend.set_title(key2, size=50) 

    plt.show()
    
    data.to_csv(r"C:\Users\Philipp\Desktop\OVID Results\DATA\allThicknessValues.csv")
    
    

if __name__ == '__main__' :
    main()
    
 