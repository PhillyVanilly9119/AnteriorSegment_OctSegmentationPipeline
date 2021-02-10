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
import h5py
import scipy.io
import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib.pyplot as plt

# Custom imports
import BackendFunctions as Backend
import TrainingMain as Train


# Start processing
if __name__ == '__main__' :

    main_path = r'E:\EvaluatedDataForPaper\OVID_segmentedDataForPaper\EvaluatedData'
    # main_folder = Backend.clean_path_selection('Please select folder with evaluated measurements')
    
    sub_dirs = Backend.get_subdirs_only(main_path)
    new_saving_dir = os.path.join(os.path.split(main_path)[0], '11_MatlabThicknessMaps')
    if not os.path.isdir(new_saving_dir) :
        os.makedirs(new_saving_dir)

    pre_string = 'CorrectedAndInterpolatedThicknessmap_'
    file_dtype = '.mat'
    
    for i, files in enumerate(sub_dirs) :
        current_file = os.path.split(files)
        current_file_name = current_file[-1]
        file_name_parts = current_file_name.split('_')[0] 
        print(file_name_parts)
        break
        current_file_path = os.path.join(current_file[0], current_file_name, (pre_string + current_file_name + file_dtype))
        if os.path.isfile(current_file_path) :
            current_heat_map = np.asarray(scipy.io.loadmat(current_file_path).get('INTERPOL_THICKNESS_MAP'))
            # Process the thicknesses with the optical index and then save them
            
            scipy.io.savemat(os.path.join(new_saving_dir, ('InterpolatedThicknessmap_' + current_file_name + '.mat')),  
                            {'INTERPOL_THICKNESS_MAP': current_heat_map.astype(np.uint16)}) 
