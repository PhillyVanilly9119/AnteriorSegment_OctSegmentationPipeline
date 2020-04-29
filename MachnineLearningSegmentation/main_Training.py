# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing functionality to train U-Net like NN

                Basic archtecture was taken and modified from
                
                    Python for Microscopists by Sreeni (Youtube): 
                    https://www.youtube.com/watch?v=68HR_eyzk00
                    
                    Check out his Github and feel free to cite Sreeni, 
                    when you use his implementation

"""

import os
import random
import numpy as np
from PIL import Image 
from tqdm import tqdm
import tensorflow as tf
import matplotlib.pyplot as plt


""" GLOBALS """
main_pth = r"C:\Users\Philipp\Documents\00_PhD_Stuff\90_Melli\ML_Data\Training\Set1"
IMG_WIDTH = 512 #TODO: Maybe net had to be adjusted to 1024x512 image sizes
IMG_HEIGHT = 512
IMG_CHANNELS = 1
    

""" DATA PRE-PROCESSING """
def getValidationData(path, dims, flag_plot=False):
    
    h, w = dims[0], dims[1]
    file_path = os.path.join(path, 'validation')
    files = os.listdir(file_path)
    imgs_vali = []
    
    for f in files:
        im = Image.open(os.path.join(file_path, f))
        new_img = im.resize((h,w))
        imgs_vali.append(np.array(new_img)) 
    
    imgs_vali = np.dstack(imgs_vali) 
    imgs_vali = np.rollaxis(imgs_vali,-1)       
    
    if flag_plot:
        fig, ax = plt.subplots(nrows=1, ncols=imgs_vali.shape[0])
        for row in range(imgs_vali.shape[0]):
            ax[row].imshow(imgs_vali[row], aspect='equal')
            ax[row].axis('off')
            ax[row].set_title(row+1)
        
    return imgs_vali

def sanityCheckData(scans, masks):
    if scans.shape[2] != masks.shape[2]:
        print("Dimensions of data stacks do not match!")
    for im in range(scans.shape[2]):
        plt.ion()
        plt.imshow(scans[:,:,im], 'gray', interpolation='none')
        plt.imshow(masks[:,:,im], 'jet', interpolation='none', alpha=0.7)
        plt.show()
        plt.pause(0.125)
        plt.clf()
        
    print("Done with displaying all images :)!")

def prepareDataForTraining_ColSinglePix(path, dims):
    
    img_width, img_height = dims[0], dims[1]
    scan_path = os.path.join(path, 'image')
    mask_path = os.path.join(path, 'mask')
    scan_files = os.listdir(scan_path)
    mask_files = os.listdir(mask_path)
    imgs_scan = [np.asarray(Image.open(os.path.join(scan_path, f)).resize((img_width, img_height))) for f in scan_files]
    x_train = np.dstack(imgs_scan)
    imgs_mask = [np.asarray(Image.open(os.path.join(mask_path, f)).resize((img_width, img_height))) for f in mask_files]
    imgs_mask = np.array(imgs_mask, dtype=np.uint8)
    imgs_mask = np.swapaxes(imgs_mask,0,2)
    y_train = np.swapaxes(imgs_mask,0,1)

    return x_train, y_train


X_train, Y_train = prepareDataForTraining_ColSinglePix(main_pth, (IMG_WIDTH, IMG_HEIGHT))
sanityCheckData(X_train, Y_train)


# =============================================================================
# TRAINING PARAMS
# =============================================================================
flag_trainAndPredict = False
img_h, img_w = IMG_HEIGHT, IMG_WIDTH

#Build the model
if flag_trainAndPredict:    
    inputs = tf.keras.layers.Input((img_h, img_w, 1)) #3rd parameter is channels
    conv_int = tf.keras.layers.Lambda(lambda x: x / 255)(inputs)
    
    """
    
    U-Net Layer structure:
        
    --> input (1024x512x1)                                                      --^ U6(NxMx32)->C7(NxMx32)
        -> C1(NxMx1)                                                        --^ U6(NxMx32)->C7(NxMx32)
            '--> P1(NxMx32)->C2(NxMx32)                                 --^ U6(NxMx32)->C7(NxMx32)
                    '--> P2(NxMx32)->C3(NxMx32)                     --^ U6(NxMx32)->C7(NxMx32)
                            '--> P3(NxMx32)->C4(NxMx32) ----> U6(NxMx32)->C7(NxMx32)
                                        '--> P4(NxMx32) -> C5(NxMx32) --^
    """
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
    #Modelcheckpoint
    checkpointer = tf.keras.callbacks.ModelCheckpoint('model_for_nuclei.h5', verbose=1, save_best_only=True)
    
    callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=2, monitor='val_loss'),
            tf.keras.callbacks.TensorBoard(log_dir='logs')]
    
    results = model.fit(X_train, Y_train, validation_split=0.1, batch_size=16, epochs=25, callbacks=callbacks)
    
    ####################################
    
    idx = random.randint(0, len(X_train))
    
    preds_train = model.predict(X_train[:int(X_train.shape[0]*0.9)], verbose=1)
    preds_val = model.predict(X_train[int(X_train.shape[0]*0.9):], verbose=1)
    preds_test = model.predict(X_test, verbose=1)
    
     
    preds_train_t = (preds_train > 0.5).astype(np.uint8)
    preds_val_t = (preds_val > 0.5).astype(np.uint8)
    preds_test_t = (preds_test > 0.5).astype(np.uint8)
    
