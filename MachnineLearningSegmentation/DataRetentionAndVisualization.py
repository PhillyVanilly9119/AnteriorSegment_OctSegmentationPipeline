# -*- coding: utf-8 -*-
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

def save_mat_file_as_xls() :
    main_path_loading = Backend.clean_path_selection("Please select the path from which you want to load the data")
    path_for_saving = Backend.clean_path_selection("Please select the path from which you want to save the data")
    

    # ## convert your array into a dataframe
    # df = pd.DataFrame (array)

    # ## save to xlsx file

    # filepath = 'my_excel_file.xlsx'

    # df.to_excel(filepath, index=False)



### PLOTTING ###

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
def create_histogram(data_stack, delta_bar, thickness_threshold=30, is_truncate_threshold=True, 
                     histo_label="Histogram", x_label="Thickness in [µm]", y_label="Count [n]") :
    """
    >>> creates histograms of OVD data stack and colors values below threshold differently if wanted
    """    
    data_stack = data_stack.reshape(np.size(data_stack))
    _, ax = plt.subplots() 
    _, _, patches = ax.hist(data_stack, bins=delta_bar)
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(histo_label, fontsize=18)
    if is_truncate_threshold : 
        bar_thickness_value = round(np.amax(data_stack) / len(patches))
        if bar_thickness_value > thickness_threshold :
            ticks_boundary = 1
        else :
            ticks_boundary = round(thickness_threshold/bar_thickness_value)
        for i in range(ticks_boundary) :    
            patches[i].set_facecolor('r')
    # Show plot on full screen - uncomment next two lines if they throw errors
    mng = plt.get_current_fig_manager()
    mng.window.showMaximized()

## TODO: Continue here
# def save_thickness_maps
#     sub_dirs = Backend.get_subdirs_only(r'E:\OVID_DataForPaper\OVID_segmentedDataForPaper\EvaluatedData')

#     pre_string = 'ThicknessMapSmoothUm_'
#     file_dtype = '.mat'
    
#     for i, files in enumerate(sub_dirs) :
#         current_file = os.path.split(files)
#         current_file_name = current_file[-1]
#         file_name_parts = current_file_name.split('_')[0] # string with OVD name in current folder
#         current_file_path = os.path.join(r'C:\Users\Philipp\Downloads\Thickness Maps in µm', (pre_string + current_file_name + file_dtype))
#         current_heat_map = Backend.load_mat_file(current_file_path, 'INTERPOL_THICKNESS_MAP_SMOOTH_UM', dtype=np.uint16)
#         # plot
#         fig, ax = plt.subplots()
#         ax.set_xlabel("Optical X-direction", fontsize=10)
#         ax.set_ylabel("Optical Y-direction", fontsize=10)
#         cax = fig.add_axes()
#         im = ax.imshow(current_heat_map)
#         cbar = fig.colorbar(im, cax=cax)
#         cbar.set_label('OVD layer thicknss in [µm]', fontsize=12)
#         im.set_clim(0, 2250)
#         # plt.show()
#         plt.savefig( os.path.join( r'C:\Users\Philipp\Desktop\ThicknessMaps_PhysicalDimensions_Original', (current_file_name + '.png') ), 
#                     format='png' )
#         plt.clf()
#         plt.close('all')


# Start processing
if __name__ == '__main__' :
    for i in range(10) :
        stack = stack_all_heat_maps_in_dir('', mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM')
        create_histogram(stack, 100, thickness_threshold=30)
    
# def save_current_figure(img_file_name, path_saving, img_dtype='png', is_manual_path_selection=False) :
#     if is_manual_path_selection :
#         path_saving = Backend.clean_path_selection( "Where do you want to save your plot?" )
#     plt.show()
#     plt.savefig( os.path.join( path_saving, (img_file_name + '.' + img_dtype) ), format=img_dtype )