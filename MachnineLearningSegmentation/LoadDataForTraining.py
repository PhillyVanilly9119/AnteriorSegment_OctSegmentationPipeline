# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 10:36:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna
            Center for Medical Physics and Biomedical Engineering
                
"""

# Proprietary imports 
import main_Training as DataPreProc

if __name__ == '__main__' :
    dims = (1024, 1024)
    x_train, y_train = DataPreProc.prepare_data_for_network(dims, fl)
     