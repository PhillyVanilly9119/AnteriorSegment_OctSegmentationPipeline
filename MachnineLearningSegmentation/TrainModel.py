# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna
            Center for Medical Physics and Biomedical Engineering
                
"""

# Proprietary imports 
import main_Training as DataPreProc
from ModelUNet import build_and_train_uNet as Unet

if __name__ == '__main__' :
    img_h = 1024
    img_w = 1024
    img_ch = 1
    dims = (img_h, img_w)
    
    x_train, y_train = DataPreProc.prepare_data_for_network(dims, 
                                                            is_add_flipped_data=True, 
                                                            is_user_select_data_path=True,
                                                            is_check_for_matching_data=False)
    model, checkpoint, results = Unet(img_h, img_w, img_ch, x_train, y_train,
                                      vali_split=0.15, batch_size=2)
     