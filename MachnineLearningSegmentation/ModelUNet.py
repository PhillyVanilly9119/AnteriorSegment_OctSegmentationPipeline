# -*- coding: utf-8 -*-
"""
Created on Thu Sep 17 14:57:28 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing inplementation of UNet

            Basic archtecture was taken from and modified (a lot) 
            https://www.youtube.com/watch?v=68HR_eyzk00
            https://github.com/seth814/Semantic-Shapes   
            
            c@: No rights reserved for this file
                
"""

# global imports
import os
import tensorflow as tf

# local imports 
import BackendFunctions as Backend

def build_and_train_uNet(img_height, img_width, img_channels, X_train, Y_train,
                         vali_split=0.2, batch_size=8,
                         model_name=None, is_save_trained_model=True, is_select_storage_path=True, 
                         base_size = 4, n_classes = 3):
    """    
    >>> U-Net Layer structure:
            
        -> [INPUT](NxMx1) -> C1(NxMx1)                                              ,--> U9(NxMx32)->C8(NxMx2^(b))->[OUTPUT](NxMx3)
                '--> P1(NxMx2^(b))->C2(NxMx2^(b))                               ,--> U8(512x512x32)->C8(NxMx2^(b+1))
                    '--> P2(NxMx2^(b+1))->C3(NxMx2^(b+1))                 ,--> U7(NxMx32)->C7(NxMx2^(b+2))
                         '--> P3(NxMx2^(b+2))->C4(NxMx2^(b+2)) ----> U6(NxMx32)->C6(NxMx2^(b+3))
                                     '--> P4(NxMx2^(b+4)) -> C5(NxMx2^(b+4)) --^
    """
    # PRE DEFINITIONS
    if is_save_trained_model :
        if is_select_storage_path :
            path_saved_model = Backend.clean_path_selection('Please choose directory to save model')
        else :
            path_saved_model = r"C:\Users\Philipp\Desktop"
    
    if not model_name :
        model_name = 'current_best_model'
    # else : model_name = model_name
    
    if n_classes == 1:
        loss_function = 'binary_crossentropy'
        final_act = 'sigmoid'
    elif n_classes > 1:
        loss_function = 'categorical_crossentropy'
        final_act = 'softmax'

    # MODEL PARAMS
    b = base_size
    layer_actication = 'relu'
    inputs = tf.keras.layers.Input((img_height, img_width, img_channels)) 
    conv_int = tf.keras.layers.Lambda(lambda x: x / 255)(inputs)
    
    # MODEL
    #Contraction path
    c1 = tf.keras.layers.Conv2D(2**b, (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (conv_int)
    c1 = tf.keras.layers.Dropout(0.1)(c1)
    c1 = tf.keras.layers.Conv2D(2**b, (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c1)
    p1 = tf.keras.layers.MaxPooling2D((2, 2))(c1)
    
    c2 = tf.keras.layers.Conv2D(2**(b+1), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (p1)
    c2 = tf.keras.layers.Dropout(0.1)(c2)
    c2 = tf.keras.layers.Conv2D(2**(b+1), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c2)
    p2 = tf.keras.layers.MaxPooling2D((2, 2))(c2)
     
    c3 = tf.keras.layers.Conv2D(2**(b+2), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (p2)
    c3 = tf.keras.layers.Dropout(0.2)(c3)
    c3 = tf.keras.layers.Conv2D(2**(b+2), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c3)
    p3 = tf.keras.layers.MaxPooling2D((2, 2))(c3)
     
    c4 = tf.keras.layers.Conv2D(2**(b+3), (3, 3), activation=layer_actication,  kernel_initializer='he_normal', padding='same') (p3)
    c4 = tf.keras.layers.Dropout(0.2)(c4)
    c4 = tf.keras.layers.Conv2D(2**(b+3), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c4)
    p4 = tf.keras.layers.MaxPooling2D(pool_size=(2, 2))(c4)
     
    c5 = tf.keras.layers.Conv2D(2**(b+4), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (p4)
    c5 = tf.keras.layers.Dropout(0.3)(c5)
    c5 = tf.keras.layers.Conv2D(2**(b+4), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c5)
    
    #Expansive path 
    u6 = tf.keras.layers.Conv2DTranspose(2**(b+3), (2, 2), strides=(2, 2), padding='same') (c5)
    u6 = tf.keras.layers.concatenate([u6, c4])
    c6 = tf.keras.layers.Conv2D(2**(b+3), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (u6)
    c6 = tf.keras.layers.Dropout(0.2)(c6)
    c6 = tf.keras.layers.Conv2D(2**(b+3), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c6)
     
    u7 = tf.keras.layers.Conv2DTranspose(2**(b+2), (2, 2), strides=(2, 2), padding='same') (c6)
    u7 = tf.keras.layers.concatenate([u7, c3])
    c7 = tf.keras.layers.Conv2D(2**(b+2), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (u7)
    c7 = tf.keras.layers.Dropout(0.2)(c7)
    c7 = tf.keras.layers.Conv2D(2**(b+2), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c7)
     
    u8 = tf.keras.layers.Conv2DTranspose(2**(b+1), (2, 2), strides=(2, 2), padding='same')(c7)
    u8 = tf.keras.layers.concatenate([u8, c2])
    c8 = tf.keras.layers.Conv2D(2**(b+1), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (u8)
    c8 = tf.keras.layers.Dropout(0.1)(c8)
    c8 = tf.keras.layers.Conv2D(2**(b+1), (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c8)
     
    u9 = tf.keras.layers.Conv2DTranspose(2**b, (2, 2), strides=(2, 2), padding='same')(c8)
    u9 = tf.keras.layers.concatenate([u9, c1], axis=3)
    c9 = tf.keras.layers.Conv2D(2**b, (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (u9)
    c9 = tf.keras.layers.Dropout(0.1)(c9)
    c9 = tf.keras.layers.Conv2D(2**b, (3, 3), activation=layer_actication, kernel_initializer='he_normal', padding='same') (c9)
     
    outputs = tf.keras.layers.Conv2D(n_classes, (1, 1), activation=final_act) (c9)
     
    model = tf.keras.Model(inputs=[inputs], outputs=[outputs])
    model.compile(optimizer='adam', loss=loss_function, metrics=['accuracy'])
    model.summary()
    
    ################################
    # Modelcheckpoint
    checkpointer = tf.keras.callbacks.ModelCheckpoint('model_for_segmentation.h5', 
                                                      verbose=1, save_best_only=True)
    
    callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=2, monitor='val_loss'),
            tf.keras.callbacks.TensorBoard(log_dir='logs')
            ]
    
    results = model.fit(X_train, Y_train, 
                        validation_split=vali_split, batch_size=batch_size, epochs=25, 
                        callbacks=callbacks)
    
    if is_save_trained_model:
        model.save(os.path.join(path_saved_model, model_name), save_format='h5')

    return model, checkpointer, results  
