# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing functionality to train Network for 
                        
                        AUTO SEGMENTATION

"""

# global imports

# local imports 
import BackendFunctions as Backend
    
# =============================================================================
# DATA PRE-PROCESSING - Training
# =============================================================================
def prepare_data_for_network(path, dims, bscan_name='raw_bScan',  
                             flag_check_for_matching_data=False, 
                             flag_add_flipped_data=True):
    """
    loads, pre-processes and displays data for training
    """
    # Load and preprocess
    
    #TODO: Continue here!
    print("[STARTING PREPROCESSING] data for training...")
    # rewrite image loading function to be able to load either '*.bmp' and '*.png'
    Backend.prepare_subfolders_for_training()
    x = load_images(path, dims)
    y = create_tripple_masks(path, dims=dims)
                    
    x = x[np.newaxis]
    x = np.swapaxes(x, 0, 3)
    
    # Add flipped versions of the all b-Scans to the training data
    if flag_add_flipped_data:
        #TODO: think of how the threre masks and the flipped pendants could work
        x = add_flipped_data(x)
        y = add_flipped_data(y)
    
    # Sanity check if inconsistencies in the data were observed
    # -> displays overlay of background and b-Scan           
    if flag_check_for_matching_data:
        sanity_check_training_data(x[:,:,:,0], y[:,:,:,2], update_rate_Hz=1) 
    
    print("[DONE PREPROCESSING] data for training")
    return x, y

# =============================================================================
                ############# MAIN / RUN #############   
# =============================================================================

if __name__ == '__main__':
    
# =============================================================================
#     """ GLOBALS """
#     train_path = r"C:\Users\Melli\Documents\Segmentation\Data\Training\training_data"
#     vali_path = r'C:\Users\Melli\Documents\Segmentation\Data\Training\validation_data'
#     img_width = 512 
#     img_height = 512
#     img_channels = 1
#     dims = (img_height, img_width)
# =============================================================================
# =============================================================================
#     DtPreTrain = DataPreprocessing(train_path)
#     X_train, Y_train = DtPreTrain.prepare_data_for_network()
#     DtPreVali = DataPreprocessing(vali_path)
#     X_test, Y_test = DtPreVali.prepare_data_for_network() 
#     model, *_ = build_and_train_uNet(img_height, img_width, img_channels, X_train, Y_train, train_path)  
# =============================================================================
