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
import glob
import time
import scipy.io
import numpy as np
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

def load_heat_map_from_current_sub_dir(path_file, mat_var_name) :
    """
    Load heat map from path parameter and returns 
    i)  heat map as 2D-array and
    ii) measurement name from file name
    """
    c_file = os.path.split(path_file)
    c_file_name = c_file[-1]
    ovd_name = c_file_name.split('_')[1] # assuming "<mapName>_<ovdName>_<measurement>_<repetition>_<DateTime>" - acc. to measurement structure
    c_file_path = os.path.join( c_file[0], (c_file_name + '.mat') ) # .mat - assuming folder structure in which all *.mat files are in one dir 
    # assert os.path.isfile(c_file_name)==True, "Input file path does not contain the correct file!"  
    heat_map = Backend.load_mat_file( c_file_path, mat_var_name, dtype=np.uint16 ) # change for more dynamic functionality
    return heat_map, c_file_name, ovd_name

def calculate_and_save_physical_thickness_maps_OVID(map_name_loading, map_name_saving, opt_ind_dict, 
                                                    file_dtype='.mat', scan_depth_um=2900, pixels_aLen=512, 
                                                    is_save_data=True, is_show_debug_prints=False) :
    """
    Calculates and saves the Thickness ("Heat") Maps of the OVDs
    Note: Index list found empirically for the evaluated OVDs in the ZEISS-financed "OVID-study"
    """
    
    path_loading = Backend.clean_path_selection('Please select folder with evaluated measurements')
    if is_save_data :
        path_saving = Backend.clean_path_selection('Please select a folder to save the data')
    else :
        path_saving = ''
    sub_dirs = Backend.get_subdirs_only(path_loading)
    
    # Iterate through all sub directories
    for path_file in sub_dirs :
        current_file = os.path.split(path_file)
        current_file_name = current_file[-1]
        file_name_parts = current_file_name.split('_')[0] # string with OVD name in current folder
        current_file_path = os.path.join( current_file[0], current_file_name, (pre_string + current_file_name + file_dtype) )
        current_heat_map = Backend.load_mat_file( current_file_path, map_name_loading, dtype=np.uint16 )
    
        for name, index in opt_ind_dict.items() :
            file_name_parts = file_name_parts.lower()
            if file_name_parts == name : # if the names of the OVDs match the index is used to recalculate the thickness maps 
                ovd_index = index    
                # Process the thicknesses with the optical index and then save them
                conversion_factor = (scan_depth_um * 1.34) / (ovd_index * pixels_aLen) # convert from pixels to microns
                current_heat_map_um = np.asarray( conversion_factor * current_heat_map, dtype=np.uint16 )         
                if is_show_debug_prints :
                    print( np.mean(current_heat_map_um) )
                if is_save_data :
                    scipy.io.savemat( os.path.join( path_saving, (map_name_saving + current_file_name + file_dtype) ) ,  
                                    {'INTERPOL_THICKNESS_MAP_SMOOTH_UM': current_heat_map_um.astype(np.uint16)} )


# Start processing
if __name__ == '__main__' :

    # main_path = Backend.clean_path_selection('Please select folder with evaluated measurements')
    map_ = load_heat_map_from_current_sub_dir(r'C:\Users\Philipp\Downloads\Thickness Maps in µm\ThicknessMapSmoothUm_AMVISCPLUS_1_1_Size6_OD-2020-05-15_084233',
                                              'INTERPOL_THICKNESS_MAP_SMOOTH_UM')
    plt.imshow(np.asarray(map_, dtype=np.uint16))
    plt.show()
    
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