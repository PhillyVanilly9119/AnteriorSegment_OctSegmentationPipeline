"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna,
            Center for Medical Physics and Biomedical Engineering
                
"""

# Global imports 
import os
import tqdm
import math
import glob
import time
import scipy.io
import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
import matplotlib as mpl
import matplotlib.pyplot as plt

# Custom imports
import BackendFunctions as Backend
import TrainingMain as Train

# OVD optical index list (empirially found by M. Wuest - wuest.melanie96@gmail.com)
index_dict = {
    "provisc": 1.357,
    "zhyalinplus": 1.364,
    "amviscplus": 1.356,
    "discovisc": 1.337,
    "healonendocoat": 1.357,
    "viscoat": 1.356,
    "zhyalcoat": 1.343,
    "combivisc": 1.353,
    "duovisc": 1.356,
    "twinvisc": 1.353,
}

### I/O AND MEASUREMENT NAME HANDLING ###
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

### MAP PROCESSING ###
def convert_ovd_map_to_um(heat_map, index, scan_depth_um=2900, aLen_plxs=512, dtype_return=np.uint16) :
    """
    >>> converts the values of the ovd thickness map from realtive a-Scan samples/pixels to µm
    """
    conversion_factor = (scan_depth_um * 1.34) / (index * aLen_plxs) # convert from pixels to µm acc. to opt. idx of OVD 
    return np.asarray( conversion_factor * heat_map, dtype=np.uint16 )

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

def stack_all_heat_maps_same_ovd_and_rep(main_path, ovd_name, meas_rep_num, mat_var_name='INTERPOL_THICKNESS_MAP', is_manual_path_selection=True) :
    """
    >>> returns 3D data tensor, containing the stacked thickness maps of the same OVDs from the same measurement repetition
    """
    if is_manual_path_selection :
        main_path = Backend.clean_path_selection("Please select path with thickness maps")  
    stacked_map_array = []
    # print(os.listdir(main_path))
    for file in os.listdir(main_path) :
        c_full_file_path = os.path.join(main_path, file)
        c_ovd_name = get_ovd_name(c_full_file_path)
        c_rep = get_repetition_number(c_full_file_path)
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) and c_ovd_name.lower()==ovd_name.lower() and c_rep==meas_rep_num:
            stacked_map_array.append( load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name) )    
    return np.dstack( np.asarray(stacked_map_array) )

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

## TODO: Continue here:
def find_inner_circle_value(c_map, radius_pxls) :
    """
    >>> Finds and returns values of the inner circle in a thickness map
    """
    inner_pnts = []
    return inner_pnts


### PLOTTING ###
def create_histogram(data_stack, ax, delta_bar, thickness_threshold_um=30, is_truncate_threshold=True, 
                     histo_label="Histogram", x_label="Thickness in [µm]", y_label="Count [n]",
                     update_rate=1, is_show_histos_full_screen=False) :
    """
    >>> creates histograms of OVD data stack and colors values below threshold differently if wanted
    """   
    data_stack = data_stack.reshape(np.size(data_stack))  
    _, _, patches = ax.hist(data_stack, bins=delta_bar)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(histo_label, fontsize=18)
    if is_truncate_threshold : 
        bar_thickness_value = round(np.amax(data_stack) / len(patches))
        if bar_thickness_value > thickness_threshold_um :
            ticks_boundary = 1
        else :
            ticks_boundary = round(thickness_threshold_um/bar_thickness_value)
        for i in range(int(ticks_boundary)) :    
            patches[i].set_facecolor('r')
    # Show plot on full screen 
    if is_show_histos_full_screen :
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
    # Show images for a certain time/ with a certain update rate 
    plt.draw()
    plt.pause(1/update_rate)
  
   
### Code example of how it can get done
# fig_size = (10, 5)
# f = plt.figure(figsize=fig_size)

# def plot_signal(time, signal, title='', xlab='', ylab='',
#                 line_width=1, alpha=1, color='k',
#                 subplots=False, show_grid=True, fig=f):

#     # Skipping a lot of other complexity here

#     axarr = f.add_subplot(1,1,1) # here is where you add the subplot to f
#     plt.plot(time, signal, linewidth=line_width,
#                alpha=alpha, color=color)
#     plt.set_xlim(min(time), max(time))
#     plt.set_xlabel(xlab)
#     plt.set_ylabel(ylab)
#     plt.grid(show_grid)
#     plt.title(title, size=16)
    
#     return(f)
# f = plot_signal(time, signal, fig=f)
# f

# Start processing
if __name__ == '__main__' :
    
    threshold_um = 50
    for name, index in index_dict.items() :    
        c_stack = stack_all_heat_maps_same_ovd_and_rep(r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm', 
                                                        name, 2, mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM', 
                                                        is_manual_path_selection=False)
        gr, le = calc_value_ratio_for_threshold(c_stack, threshold_um)
        print(f'{le}%')
        # print(f'{gr}%')
        # print(f'{name.upper()}')           
        # print(np.shape(c_stack), name)
        
    
    # ### HISTO creation for all individual OVDs 
    # path_loading = r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm'
    # path_saving = r'C:\Users\Philipp\Desktop\OVID Results\All OVDs Histos\All Histos 128 Bar Delta 50 Threshold'
    # mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM'
    # delta_bar = 128
    # thickness_threshold_um = 50
    # x_label='Thickness in [µm]' 
    # y_label='Count [n]'
    # my_dpi = 150
    
    # for file in tqdm(os.listdir(path_loading)) :
    #     c_full_file_path = os.path.join(path_loading, file)
    #     just_file = file.split('.mat')[0].split('_')
    #     just_file = [string + '_' for string in just_file]
    #     title_string = ''.join(just_file[1:])[:-1]
    #     plt.ion()
    #     # plt.figure(figsize=(1920/my_dpi, 1080/my_dpi))
    #     fig, ax = plt.subplots(figsize=(1920/my_dpi, 1080/my_dpi))
    #     if file.endswith('.mat') and os.path.isfile(c_full_file_path) :
    #         data_stack = load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name)
    #         histo_label = 'Histogram of ' + title_string 
    #         data_stack = data_stack.reshape(np.size(data_stack))  
    #         _, _, patches = ax.hist(data_stack, bins=delta_bar)
    #         ax.set_xlabel(x_label, fontsize=12)
    #         ax.set_ylabel(y_label, fontsize=12)
    #         ax.set_title(histo_label, fontsize=18)
    #         bar_thickness_value = round(np.amax(data_stack) / len(patches))
    #         if bar_thickness_value > thickness_threshold_um :
    #             ticks_boundary = 1
    #         else :
    #             ticks_boundary = round(thickness_threshold_um/bar_thickness_value)
    #             if math.isinf(ticks_boundary) :
    #                 ticks_boundary = 0 
    #         for i in range(int(ticks_boundary)) :    
    #             patches[i].set_facecolor('r')
    #         plt.show()
    #         # plt.pause(0.25)
    #         plt.savefig(os.path.join(path_saving, title_string + '.png'), format='png')
    #     plt.clf()