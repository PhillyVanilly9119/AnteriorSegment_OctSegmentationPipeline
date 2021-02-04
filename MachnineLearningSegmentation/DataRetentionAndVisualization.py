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

# Scipy imports are based on version 1.4.1 
# -> TODO: Fix for any version!
from scipy.io import savemat
from scipy.ndimage import median_filter
from scipy.interpolate import interp1d

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