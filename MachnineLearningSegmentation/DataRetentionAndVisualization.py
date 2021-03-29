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
import random

import scipy.io
from scipy.io import savemat

import numpy as np
import pandas as pd
import seaborn as sns
# from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

# Custom imports
import BackendFunctions as Backend
# import TrainingMain as Train

# OVD optical index list (empirially found by M. Wuest - wuest.melanie96@gmail.com)
index_dict = {
    "provisc": 1.357, #cohesive
    "zhyalinplus": 1.364,
    "amviscplus": 1.356, 
    "discovisc": 1.337, #diperse
    "healonendocoat": 1.357,
    "viscoat": 1.356,
    "zhyalcoat": 1.343,
    "combivisc": 1.353, #combi-systems
    "duovisc": 1.356,
    "twinvisc": 1.353,
}

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

######################
### MAP PROCESSING ###
######################
def convert_ovd_map_to_um(heat_map, index, scan_depth_um=2900, aLen_plxs=512, dtype_return=np.uint16) :
    """
    >>> converts the values of the ovd thickness map from realtive a-Scan samples/pixels to µm
    """
    conversion_factor = (scan_depth_um * 1.34) / (index * aLen_plxs) # convert from pixels to µm acc. to opt. idx of OVD 
    return np.asarray( conversion_factor * heat_map, dtype=np.uint16 )

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

################
### PLOTTING ###
################
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
    
def dummy_histo_creation() :
    """
    >>> Create and save histograms
    """
    delta_bar = 64
    thickness_threshold_um = 50
    path_loading = r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm'
    path_saving = r'C:\Users\Philipp\Desktop\OVID Results\All OVDs Histos\All Histos 64 Bar Delta 50 Threshold'
    mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM'
    x_label='Thickness in [µm]' 
    y_label='Sample Count [n]'
    my_dpi = 150
    
    for file in tqdm(os.listdir(path_loading)) :
        c_full_file_path = os.path.join(path_loading, file)
        just_file = file.split('.mat')[0].split('_')
        just_file = [string + '_' for string in just_file]
        title_string = ''.join(just_file[1:])[:-1]
        plt.ion()
        # plt.figure(figsize=(1920/my_dpi, 1080/my_dpi))
        _, ax = plt.subplots(figsize=(1920/my_dpi, 1080/my_dpi))
        if file.endswith('.mat') and os.path.isfile(c_full_file_path) :
            data_stack = load_heat_map_from_current_sub_dir(c_full_file_path, mat_var_name)
            histo_label = 'Histogram of ' + title_string 
            data_stack = data_stack.reshape(np.size(data_stack))  
            _, _, patches = ax.hist(data_stack, bins=delta_bar)
            ax.set_xlabel(x_label, fontsize=12)
            ax.set_ylabel(y_label, fontsize=12)
            ax.set_title(histo_label, fontsize=18)
            bar_thickness_value = round(np.amax(data_stack) / len(patches))
            if bar_thickness_value > thickness_threshold_um :
                ticks_boundary = 1
            else :
                ticks_boundary = round(thickness_threshold_um/bar_thickness_value)
                if math.isinf(ticks_boundary) :
                    ticks_boundary = 0 
            for i in range(int(ticks_boundary)) :    
                patches[i].set_facecolor('r')
            plt.show()
            plt.savefig(os.path.join(path_saving, title_string + '.png'), format='png')
        plt.clf()
  
def dummy_thickness_map_creation() :
    """
    >>> Create and save thickness maps
    """
    path_loading = r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm'
    path_saving = r'C:\Users\Philipp\Desktop\OVID Results\ThicknessMaps'
    mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM'
    x_label='6mm [slow scanning axis]' 
    y_label='6mm [fast scanning axis]'
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
            plt.savefig(os.path.join( path_saving, (file.split('.mat')[0] + '.png') ), format='png')
        plt.clf()
  
def dummy_boxplot_group_creation() :
    c = 0
    data = []
    title_string = ''
    for name, _ in index_dict.items() :    
        c+=1
        first_stack = stack_all_heat_maps_same_ovd_and_rep(r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm', 
                                                        name, 1, mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM', 
                                                        is_manual_path_selection=False)
        second_stack = stack_all_heat_maps_same_ovd_and_rep(r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm', 
                                                        name, 2, mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM', 
                                                        is_manual_path_selection=False)
        first_vals = []
        second_vals = []
        for i in range(10) :
            first_vals.append(find_values_in_inner_circle(first_stack[:,:,i], 128)[0])
            second_vals.append(find_values_in_inner_circle(second_stack[:,:,i], 128)[0])
        first_vals, second_vals = np.asarray(first_vals), np.asarray(second_vals)
        ## Save data if you want to 
        # savemat(os.path.join(r'C:\Users\Philipp\Desktop', ('CombinedThicknessMapInner3mm_' + name.upper() + '_firstRep.mat')),  
        #                     {'ALL_THICKNESS_MAPs': first_vals.astype(np.uint16)})
        # savemat(os.path.join(r'C:\Users\Philipp\Desktop', ('CombinedThicknessMapInner3mm_' + name.upper() + '_secondRep.mat')),  
        #                     {'ALL_THICKNESS_MAPs': second_vals.astype(np.uint16)})
        first_vals = first_vals.flatten()
        second_vals = second_vals.flatten()
        data.append(second_vals.flatten())
        title_string += ' ' + str(c) + ' ' + name.upper()
    _, ax = plt.subplots()
    ax.boxplot(data, 0, '')
    ax.set_title('Box Plots of all OVDs inner 3mm of second measurement (phaco)') 
    ax.set_xlabel('OVD Number')
    ax.set_ylabel('Thickness in [µm]')
    fontP = FontProperties()
    fontP.set_size('small')

    ax.legend(
        ('1 PROVISC', 
         '2 ZHYALINPLUS',
         '3 DISCOVISC',
         '4 AMVISCPLUS', 
         '5 HEALONENDOCOAT',
         '6 VISCOAT', 
         '7 ZHYALCOAT', 
         '8 COMBIVISC', 
         '9 DUOVISC', 
         '10 TWINVISC'), 
        title='Names OVDs', 
        bbox_to_anchor=(1, 1), 
        loc='upper left',
        prop=fontP) 
    plt.show()  

def load_entire_data_base_and_sort_after_ovd_groups(is_save_mat_files=False) :
    
    cohesive_f = []
    cohesive_s = []
    disperse_f = []
    disperse_s = []
    combi_f = []
    combi_s = []
    data = []
    
    c = 0   
    for name, index in index_dict.items() :
        print(name, c)    
        first_stack = stack_all_heat_maps_same_ovd_and_rep(r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm', 
                                                        name, 1, mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM', 
                                                        is_manual_path_selection=False)
        second_stack = stack_all_heat_maps_same_ovd_and_rep(r'C:\Users\Philipp\Desktop\OVID Results\Thickness Maps in µm', 
                                                        name, 2, mat_var_name='INTERPOL_THICKNESS_MAP_SMOOTH_UM', 
                                                        is_manual_path_selection=False)

        def grab_inner_circle_vals_only(first_stack, second_stack) :
            first_vals = []
            second_vals = []
            for i in range(10) :
                first_vals.append(find_values_in_inner_circle(first_stack[:,:,i], 128)[0])
                second_vals.append(find_values_in_inner_circle(second_stack[:,:,i], 128)[0])
            return np.asarray(first_vals), np.asarray(second_vals)

        # first_stack, second_stack = grab_inner_circle_vals_only(first_stack, second_stack)

        if c in range(2) : # 0,1
            cohesive_f.append(first_stack)
            cohesive_s.append(second_stack)
            # print("cohesive", name, c)
        elif c in range(2, 7) : # 2,3,4,5,6
            disperse_f.append(first_stack)
            disperse_s.append(second_stack)
            # print("disperse", name, c)
        elif c in range(7, 10) : # 7,8,9
            combi_f.append(first_stack)
            combi_s.append(second_stack)
            # print("combi", name, c)   
        else :
            ValueError("counter index out of bounds.")
            
        c += 1
        
    cohesive_f = np.asarray(cohesive_f)
    cohesive_s = np.asarray(cohesive_s)
    disperse_f = np.asarray(disperse_f)
    disperse_s = np.asarray(disperse_s)
    combi_f = np.asarray(combi_f)
    combi_s = np.asarray(combi_s)

    # gr, le = calc_value_ratio_for_threshold(cohesive, threshold_um)
    
    if is_save_mat_files :
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                             ('CombinedThicknessMapOVDGroup_' + 'COHESIVE_firstRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': cohesive_f.astype(np.uint16)})
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                            ('CombinedThicknessMapOVDGroup_' + 'COHESIVE_secondRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': cohesive_s.astype(np.uint16)})
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                             ('CombinedThicknessMapOVDGroup_' + 'DISPERSE_firstRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': disperse_f.astype(np.uint16)})
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                            ('CombinedThicknessMapOVDGroup_' + 'DISPERSE_secondRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': disperse_s.astype(np.uint16)})
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                             ('CombinedThicknessMapOVDGroup_' + 'COMBI_firstRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': combi_f.astype(np.uint16)})
        savemat(os.path.join(r'C:\Users\Philipp\Desktop\OVID Results\DATA\CombinedMapsOvdGroupsInner3mm', 
                            ('CombinedThicknessMapOVDGroup_' + 'COMBI_secondRep.mat')), {'ALL_COMBINED_GROUP_THICKNESS_MAPs': combi_s.astype(np.uint16)})

    data = [cohesive_f.flatten(), cohesive_s.flatten(), 
            disperse_f.flatten(), disperse_s.flatten(), 
            combi_f.flatten(), combi_s.flatten()]
    
    # return cohesive_f, cohesive_s, disperse_f, disperse_s, combi_f, combi_s
    return data    

def main() :    
    data = load_entire_data_base_and_sort_after_ovd_groups()    
    return data
    
# Start processing
if __name__ == '__main__' :    
    
    samples = 5_000_000
    
    data = main()
    c1_ = np.asarray(random.choices(data[0], k=samples))
    c2_ = np.asarray(random.choices(data[1], k=samples))
    d1_ = np.asarray(random.choices(data[2], k=samples))
    d2_ = np.asarray(random.choices(data[3], k=samples))
    cmb1_ = np.asarray(random.choices(data[4], k=samples))
    cmb2_ = np.asarray(random.choices(data[5], k=samples))
    del data
    
    key1 = "Thickness values in [µm]"
    key2 = "Type of measurement"
    key3 = "OVD groups"
    
    df1 = pd.DataFrame( {key1:c1_, key2:"after Irrigation and Aspiration", key3:"Cohesive"})
    df2 = pd.DataFrame( {key1:c2_, key2:"after I/A  & Phaco", key3:"Cohesive"})
    df3 = pd.DataFrame( {key1:d1_, key2:"after Irrigation and Aspiration", key3:"Disperse"})
    df4 = pd.DataFrame( {key1:d2_, key2:"after I/A  & Phaco", key3:"Disperse"} )
    df5 = pd.DataFrame( {key1:cmb1_, key2:"after Irrigation and Aspiration", key3:"Combi"})
    df6 = pd.DataFrame( {key1:cmb2_, key2:"after I/A  & Phaco", key3:"Combi"})
    
    df = pd.concat([df1,df2,df3,df4,df5,df6], ignore_index=True)
       
    fig, ax = plt.subplots(figsize=(32, 18))
    ax = sns.violinplot(ax=ax, data = df, x = key3, y = key1, linewidth=2.5, 
                        inner='quartile', hue=key2, split=True, cut=0, palette='Blues', 
                        fontsize=12, legend=False)

    ax.set_xlabel(key3, fontsize=30)
    ax.set_ylabel(key1, fontsize=25)
    ax.set_title('Thickness values distribution split after OVD categories', fontsize=36)
    ax.set_yticklabels(ax.get_yticks(), size=20)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize = 20)

    # plt.legend(title=key2, size=24, loc=1, bbox_to_anchor=(0.6,1))
    plt.setp(ax.get_legend().get_texts(), fontsize=20) # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize=24) # for legend title
    # ax._legend.set_title(key2, size=50) 

    plt.show()
    
    