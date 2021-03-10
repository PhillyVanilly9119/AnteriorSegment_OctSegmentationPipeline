# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:32:10 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

@copyright: Medical University of Vienna,
            Center for Medical Physics and Biomedical Engineering
                
"""

import os 
import numpy as np
import pandas as pd

import BackendFunctions as Backend

if __name__ == '__main__' :
    
    path_text_file = r'C:\Users\Philipp\Desktop\TxtFiles\Stats1stRepInner3mm.txt' 
    path_excel_file = r'C:\Users\Philipp\Desktop\TxtFiles\Stats1stRepInner3mm.xlsx' 

    if os.path.isfile( path_text_file ) :
        with open( path_text_file, 'r' ) as f :
            lines = f.readlines()
        lines = [line.replace('\n', '') for line in lines]
        lines = [line.split(' ') for line in lines]
    
    flat_list = [item for sublist in lines for item in sublist]
       
    df = pd.DataFrame()
    df['OVD Name'] = flat_list[0::4]
    df['Measurement Number'] = flat_list[1::4]
    df['Mean'] = flat_list[2::4]
    df['Std'] = flat_list[3::4]
    df.to_excel(path_excel_file, index = False) 