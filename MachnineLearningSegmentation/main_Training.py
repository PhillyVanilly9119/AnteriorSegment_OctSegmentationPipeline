# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing functionality to train UNet-like-NN

            Basic archtecture was taken and modified from
                
                Python for Microscopists by Sreeni (Youtube): 
                https://www.youtube.com/watch?v=68HR_eyzk00
                    
                Check out his Github and feel free to cite Sreeni, 
                when you use his implementation (i.e. for a publication)

"""

import os
import datetime
import numpy as np
from PIL import Image 
from tqdm import tqdm
import tensorflow as tf
import matplotlib.pyplot as plt


""" GLOBALS """
train_path = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\Set1\training_data"
vali_path = r'C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\Set1\validation_data'
img_width = 512 
img_height = 512
img_channels = 1
dims = (img_height, img_width)
IMG_CHANNELS = 1
    
# =============================================================================
# DATA PRE-PROCESSING - Training
# =============================================================================

def load_data_from_files(path, dims, bscan_name, mask_name):
    """
    >>> file structure of training data:
        [Data for ML]
            '->[001] (contaning all kinds of masks and their corresponding b-Scans)
            '->[002] (-"-)
            '->[003] (-"-)
            ...
            
    >>> bscan_name and mask_name should be the scans mask with which training 
        should be carried out, e.g. 'raw_bScan' and 'thick_mask'
    
    >>> default image data is .png and should remain so, since created 
    segmented data is saved as .png from Matlab pipeline     
    """
    
    img_dt = '.png'
    h, w = dims[0], dims[1] #important for resizing the images and masks equaly
    files = os.listdir(path)
    bscan_img_stack = tqdm([np.asarray(Image.open(os.path.join(path, f, bscan_name + img_dt)).resize((h,w))) for f in files])
    x_train = np.dstack(bscan_img_stack)
    mask_img_stack = tqdm([np.asarray(Image.open(os.path.join(path, f, mask_name + img_dt)).resize((h,w))) for f in files])
    y_train = np.dstack(mask_img_stack)
 
    return x_train, y_train

def sanity_check_training_data(scans, masks):
    """
    fast display of overlayed images of masks and corresponding raw scans to 
    see if data import was carried out correctly
    """
    
    print("Displaying images...")    
    if scans.shape[2] != masks.shape[2]:
        print("Dimensions of data stacks do not match!")
    for im in tqdm(range(scans.shape[2])):
        plt.ion()
        plt.imshow(scans[:,:,im], 'gray', interpolation='none')
        plt.imshow(masks[:,:,im], 'jet', interpolation='none', alpha=0.7)
        plt.show()
        plt.pause(0.5)
        plt.clf()
        
    print("Done displaying images!")
 
def create_bool_masks_from_bin_masks(masks):
    
    dims = np.shape(masks)
    bool_mask = [np.asarray(masks[:,:,img] <= 1, dtype=bool) for img in range(dims[2])]
    
    return bool_mask

def prepare_data_for_network(path, dims, bscan_name='raw_bScan', mask_name='binary_mask', flag_checkDataMatch=False):
    """
    loads, pre-processes and displays data for training
    """
    x, y = load_data_from_files(path, dims, bscan_name, mask_name)        
    if flag_checkDataMatch:
        sanity_check_training_data(x, y)   
    x = x[np.newaxis]
    x = np.swapaxes(x, 0, 3)
    y = create_bool_masks_from_bin_masks(y) 
    y = np.dstack(y)
    y = y[np.newaxis]
    y = np.swapaxes(y, 0, 3)

    return x, y

# =============================================================================
# [1.)] LOAD DATA AND PREPROCESS
# =============================================================================

X_train, Y_train = prepare_data_for_network(train_path, dims)
X_test, Y_test = prepare_data_for_network(vali_path, dims)
print("Done pre-processing the data!")

# =============================================================================
# TRAINING PARAMS
# =============================================================================
def build_and_train_network(img_height, img_width, img_channels, 
                            X_train, Y_train,
                            path_saved_model, flag_saveModel=True):
    """    
    >>> U-Net Layer structure:
            
        -> [INPUT](NxMx1) -> C1(NxMx1)                                  ,--> U9(NxMx32)->C8(NxMx32)->[OUTPUT](NxMx1)
                '--> P1(NxMx32)->C2(NxMx32)                         ,--> U8(512x512x32)->C8(NxMx32)
                    '--> P2(NxMx32)->C3(NxMx32)                 ,--> U7(NxMx32)->C7(NxMx32)
                         '--> P3(NxMx32)->C4(NxMx32) ----> U6(NxMx32)->C6(NxMx32)
                                     '--> P4(NxMx32) -> C5(NxMx32) --^
    """
   
    inputs = tf.keras.layers.Input((img_height, img_width, img_channels)) 
    conv_int = tf.keras.layers.Lambda(lambda x: x / 255)(inputs)
    
    #Contraction path
    c1 = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(conv_int)
    c1 = tf.keras.layers.Dropout(0.1)(c1)
    c1 = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c1)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)
    
    c2 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p1)
    c2 = tf.keras.layers.Dropout(0.1)(c2)
    c2 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c2)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)
     
    c3 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p2)
    c3 = tf.keras.layers.Dropout(0.2)(c3)
    c3 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c3)
    p3 = tf.keras.layers.MaxPooling2D((2, 2))(c3)
     
    c4 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p3)
    c4 = tf.keras.layers.Dropout(0.2)(c4)
    c4 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c4)
    p4 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(c4)
     
    c5 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(p4)
    c5 = tf.keras.layers.Dropout(0.3)(c5)
    c5 = tf.keras.layers.Conv2D(256, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c5)
    
    #Expansive path 
    u6 = tf.keras.layers.Conv2DTranspose(128, (2, 2), strides=(2, 2), padding='same')(c5)
    u6 = tf.keras.layers.concatenate([u6, c4])
    c6 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u6)
    c6 = tf.keras.layers.Dropout(0.2)(c6)
    c6 = tf.keras.layers.Conv2D(128, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c6)
     
    u7 = tf.keras.layers.Conv2DTranspose(64, (2, 2), strides=(2, 2), padding='same')(c6)
    u7 = tf.keras.layers.concatenate([u7, c3])
    c7 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u7)
    c7 = tf.keras.layers.Dropout(0.2)(c7)
    c7 = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c7)
     
    u8 = tf.keras.layers.Conv2DTranspose(32, (2, 2), strides=(2, 2), padding='same')(c7)
    u8 = tf.keras.layers.concatenate([u8, c2])
    c8 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u8)
    c8 = tf.keras.layers.Dropout(0.1)(c8)
    c8 = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c8)
     
    u9 = tf.keras.layers.Conv2DTranspose(16, (2, 2), strides=(2, 2), padding='same')(c8)
    u9 = tf.keras.layers.concatenate([u9, c1], axis=3)
    c9 = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(u9)
    c9 = tf.keras.layers.Dropout(0.1)(c9)
    c9 = tf.keras.layers.Conv2D(16, (3, 3), activation='relu', kernel_initializer='he_normal', padding='same')(c9)
     
    outputs = tf.keras.layers.Conv2D(1, (1, 1), activation='sigmoid')(c9)
     
    model = tf.keras.Model(inputs=[inputs], outputs=[outputs])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    model.summary()
    
    ################################
    # Modelcheckpoint
    checkpointer = tf.keras.callbacks.ModelCheckpoint('model_for_segmentation.h5', verbose=1, save_best_only=True)
    
    callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=2, monitor='val_loss'),
            tf.keras.callbacks.TensorBoard(log_dir='logs')]
    
    results = model.fit(X_train, Y_train, validation_split=0.10, batch_size=4, epochs=25, callbacks=callbacks)
    
    if flag_saveModel:
        model.save(os.path.join(train_path.split('\\training_data')[0], 'current_best_model'), save_format='h5')

    return model, checkpointer, results

model, *_ = build_and_train_network(img_height, img_width, img_channels, X_train, Y_train, 
                        train_path)      

# =============================================================================
#   Testing, Prediction and Saving Model
# =============================================================================
def show_predictions(model, X_test, Y_test):
    preds_test = model.predict(X_test, verbose=1)
    preds_test_t = (preds_test > 0.5).astype(np.uint8)
    preds_test_t = preds_test_t[:,:,:,0] # delete image-channel-dimension

    size = np.shape(preds_test_t)[0]
    fig, ax = plt.subplots(4, size)
    for img in range(size):
        ax[0, img].imshow(Y_test[img,:,:,0])
        ax[0, img].set_title("Manually segmented mask - GROUND TRUTH")
        ax[1, img].imshow(preds_test_t[img,:,:])
        ax[1, img].set_title("Automatically segmented mask - PREDICTED")
        ax[2, img].imshow(X_test[img,:,:,0], cmap='jet')
        ax[2, img].set_title("Filtered b-Scan (from which the net segmented the mask)")
        diff_img = np.absolute(np.subtract(Y_test[img,:,:,0], preds_test_t[img,:,:]))
        ax[3, img].imshow(diff_img)
        ax[3, img].set_title("Difference image of ground-trouth (mask) and predicted (mask)")
        # add saving logic with training params

show_predictions(model, X_test, Y_test)  
