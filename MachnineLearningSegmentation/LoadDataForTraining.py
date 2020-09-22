# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:36:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna
            Center for Medical Physics and Biomedical Engineering
                
"""

# global imports
import matplotlib.pyplot as plt

# Proprietary imports 
import main_Training as DataPreProc

if __name__ == '__main__' :
    img_h = 1024
    img_w = 1024
    img_ch = 1
    dims = (img_h, img_w)
    
    x_train, y_train = DataPreProc.prepare_data_for_network(dims, 
                                                            is_add_flipped_data=True, 
                                                            is_user_select_data_path=True,
                                                            is_check_for_matching_data=False)
     