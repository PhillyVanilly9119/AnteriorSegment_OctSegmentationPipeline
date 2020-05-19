# -*- coding: utf-8 -*-
"""
Created on Tue May 19 14:46:49 2020

@author: Philipp
"""

import os
from keras.models import load_model
from tkinter.filedialog import askdirectory
import matplotlib.pyplot as plt


# =============================================================================
# Enter path
# =============================================================================
path_source = askdirectory(title='Please data for segmentation') 
assert os.path.isdir(path_source), "Directory from which I am supposed to load data does not exist!"

# =============================================================================
# Functionality
# =============================================================================
def predict_segmentation(path, bscans):
    net_path = r''
    scan_path = r''
    load_pretrained_net(net_path)
    scans = load_data_from_folder(scan_path)
    b_scans = applytrainedNet()

def load_pretrained_net(path, file_name, network_name):
    json_file = os.path.join(path, file_name + '.json')
    h5_file = os.path.join(path, network_name + '.h5')
    # check if .h5-file exists, else load .json-file 
    if os.path.isfile(h5_file):
        # load file
        model = load_model(h5_file)
        print("Loaded model from disk")
    elif os.path.isfile(network_file):
        # load file
        json_file = open(os.path.join(path, json_file), 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = model_from_json(loaded_model_json)
        # load weights into new model
        model = loaded_model.load_weights(network_name + '.h5')
        print("Loaded model from disk")
    else:
        print("Could not find the model you specified...")
        break
        
    return model

def load_data_from_folder(path):
    pass    

def check_predicted_masks(scans, masks, main_path):
    """
    Sort and check if automatically segmented b-Scans were segemented correctly
    """
    path_good = os.path.join(main_path, 'CorrectScans')
    path_bad = os.path.join(main_path, 'IncorrectScans')
    assert scans.shape[2] != masks.shape[2], "Dimensions of data stacks do not match!"
    
    print("Please review automatically segmented images...")    
    for im in range(scans.shape[2]):
        plt.ion()
        plt.imshow(scans[:,:,im], 'gray', interpolation='none')
        plt.imshow(masks[:,:,im], 'jet', interpolation='none', alpha=0.65)
        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        plt.show()
        key = input("Please press \"y\" if scan was segmented correctly and \"n\" if not")
        if key == 'y':
            plt.imsave(os.path.join(path_good, mask[:,:,im], str(im) + '.png'))
        elif key == 'n':
            plt.imsave(os.path.join(path_bad, mask[:,:,im], str(im) + '.png'))
        else:
            raise ValueError("You\"ve hit the wrong key... Please enter either \"y\" or \"n\")
        plt.clf()
        
    print("Done displaying images!")