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
from scipy.stats import wilcoxon, ranksums#, RanksumsResult   
import matplotlib.pyplot as plt

import BackendFunctions as Backend

def adjust_the_array_length(set1, set2) :
    set1 = set1.flatten()
    set2 = set2.flatten()
    if len(set1) >= len(set2) :
        set1 = set1[:len(set2)]
    else :
        set2 = set2[:len(set1)]
    return set1, set2

def apply_wilcoxon(set1, set2, text='') :
    set1, set2 = adjust_the_array_length(set1, set2)
    w, p = wilcoxon(set1, set2)
    return w, p

def apply_ranksumtest(set1, set2, text='') :
    set1, set2 = adjust_the_array_length(set1, set1)
    w, p = ranksums(set1, set2)
    return w, p

# def get_ranksum_result(set1, set2, text='') :
#     w, p = RanksumsResult(set1, set2)
#     return w, p

if __name__ == '__main__' :
    # path for loading
    path_file1 = r'C:\Users\Philipp\Desktop\OVID Results\PhacoTipData\ValuesNonPhacotipArea_AMVISCPLUS_1_1_Size6_OD-2020-05-15_084233.mat' #Backend.clean_file_selection("Please select file No. 1")
    path_file2 = r'C:\Users\Philipp\Desktop\OVID Results\PhacoTipData\ValuesPhacotipArea_AMVISCPLUS_1_1_Size6_OD-2020-05-15_084233.mat' #Backend.clean_file_selection("Please select file No. 2")
    set_one = Backend.load_mat_file(path_file1, 'non_phacotip_area_vector', dtype=np.float64)
    set_two = Backend.load_mat_file(path_file2, 'phacotip_area_vector', dtype=np.float64)
    # load data
    
    # apply test
    w, p = apply_ranksumtest(set_one, set_two)
    print(w, p)
    w, p = apply_wilcoxon(set_one, set_two)
    print(w, p)