# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 16:14:31 2020

@author:    Philipp
            philipp.matten@meduniwien.ac.at

    ---> Main File containing functionality to train an inplementation of UNet

            Basic archtecture was taken and modified (a lot!) from
                
                Python for Microscopists by Sreeni (Youtube): 
                https://www.youtube.com/watch?v=68HR_eyzk00
                    
                Check out his Github and feel free to cite Sreeni, 
                when you use his implementation (i.e. for a publication)
                
                also check out Seths' Repository to semantic segmentation:
                https://github.com/seth814/Semantic-Shapes    
                This also a great source of inspiration for your own 
                semantic segmentation projects ;)

"""

import os
import cv2
import numpy as np
from PIL import Image 
from tqdm import tqdm
import tensorflow as tf
import matplotlib.pyplot as plt

""" GLOBALS """
train_path = r"C:\Users\Melli\Documents\Segmentation\Data\Training\training_data"
vali_path = r'C:\Users\Melli\Documents\Segmentation\Data\Training\validation_data'
img_width = 512 
img_height = 512
img_channels = 1
dims = (img_height, img_width)
    
# =============================================================================
# DATA PRE-PROCESSING - Training
# =============================================================================
class DataPreprocessing() :
    
    # TODO: Rethink handling of dimensionality and image sizes for class
    # TODO: Think about making the Network class inherit dimensionality from this one
    def __init__(self, path, out_dims=(512,512)) :
        """ 
        path = string contanining the entire path to directory of data
        >>> file structure of [Data for ML]:
            '->[001] (contaning all kinds of masks and their corresponding b-Scans)
            '->[002] (-"-)
            '->[003] (-"-)
            ...
        """
        self.path = path
        self.out_dims = out_dims # out-dims of data right before training
        self.list_mask_files = ['mask_cornea', 
                                'mask_ovd', 
                                'mask_background']
        
    @staticmethod 
    def create_flipped_images(in_stack, axis=None) :
        print("Calculating flipped images...")
        assert np.size(np.shape(in_stack)) == 3, '[DIMENSIONAL MISMATCH] for images'
        images = np.shape(in_stack)[2]        
        
        print("Done calculating flipped images!")
        return np.dstack([np.flip(in_stack[:,:,i], axis) for i in tqdm(range(images))])
    
    def resize_img_stack_to_output_size(self, images) :
        assert images.ndim == 3, "[IMAGE RESIZING ERROR] Wrong dimensionality of image data!"
        in_dims = np.shape(images)
        print((self.out_dims[0], self.out_dims[1]))
        return [np.asarray(cv2.resize(images[:,:,i], 
                             (self.out_dims[0], self.out_dims[1]), 
                             interpolation = cv2.INTER_AREA) for i in tqdm(range(in_dims[2])))]
    
    @staticmethod
    def sanity_check_training_data(scans, masks, update_rate_Hz=2):
        """
        >>> Quick run-through of overlayed images (scans+masks) 
        to see if the scans and masks order matches in data stacks
        REMARK: June 26th image dimensions in pre-processing := (n_img, h, w)
        """       
        print("Displaying images...")
        if scans.shape[2] != masks.shape[2]:
            print("Dimensions of data stacks do not match!")
        for im in tqdm(range(scans.shape[0])):
            plt.ion()
            plt.imshow(scans[im,:,:], 'gray', interpolation='none')
            plt.imshow(masks[im,:,:], 'jet', interpolation='none', alpha=0.7)
            plt.show()
            plt.pause(1/update_rate_Hz)
            plt.clf()    
        print("Done displaying images!")

    @staticmethod 
    def load_images(path, name, dims, img_dtype='.png') :
        print(f"Loading all images >>{name+img_dtype}<< from >>{path}<<...")
        assert np.size(dims)==2, f"[RESHAPING DIMENSIONS MISMATCH] Please enter tuple containing (height, width)"
        h, w = dims[0], dims[1]
        files = os.listdir(path)
        try :
            if any([os.path.isfile(os.path.join(path, f, name + img_dtype)) for f in files]) :
                img_stack = [np.asarray(Image.open(os.path.join(path, f, name + img_dtype)).resize((h,w))) for f in tqdm(files)]
        except FileNotFoundError :
            print(f"There were no images named >>{name}<< found in any sub-directory of >>{path}<<")
        
        print("Done loading images!") 
        return np.dstack(img_stack)
    
    @staticmethod
    def create_tripple_mask(mask) :
        """
        Return two types of masks: 
        """
        dims = np.shape(mask) 
        cornea = np.zeros((dims))
        ovd = np.zeros((dims))
        background = np.zeros((dims))
        tripple_mask = np.zeros((dims))
        
        for ascan in range(dims[1]) : # iterate through A-Scans
            bndry_spots = np.squeeze(np.where(mask[:,ascan]==np.amax(mask)))
            if np.size(bndry_spots) == 2 : # case: only Cornea visible
                start_crn = np.amin(bndry_spots)
                end_crn = np.amax(bndry_spots)
                # cornea = 1
                tripple_mask[start_crn:end_crn, ascan] = 1
                cornea[start_crn:end_crn, ascan] = 255
            elif np.size(bndry_spots) == 3 :
                # cornea = 1
                tripple_mask[bndry_spots[0]:bndry_spots[1], ascan] = 1
                cornea[bndry_spots[0]:bndry_spots[1], ascan] = 255
                # "milk" = 2
                tripple_mask[bndry_spots[2]:, ascan] = 2
                ovd[bndry_spots[2]:, ascan] = 255
            else :
                pass # TODO: Maybe think of more sophisticated error handling
                #raise ValueError("[STUMBLED UPON INVALID ASCAN]")
           
            # Create Masks for 3-channel segmentation
            masks = []
            masks.append(cornea) # Mask No.1
            masks.append(ovd) # Mask No.2
            tmp = np.add(cornea, ovd)
            _, background = cv2.threshold(tmp, 127, 255, cv2.THRESH_BINARY_INV)
            masks.append(background) # Mask No.3
            
        return masks, tripple_mask
    
    @staticmethod
    def resize_no_interpol(image, dims) :
        assert np.size(dims) == 2, "[DIMENSION ERROR] please enter 2-D tuple as output-dimensions"
        return cv2.resize(image,
                          (dims[0], dims[1]), 
                          fx = 0, fy = 0,
                          interpolation=cv2.INTER_NEAREST)
    
    @staticmethod
    def show_images_in_subplots(images, num=None) :
        sizes = np.shape(images)
        if num == None:
            num = sizes[2] # number is images in stack
        else:
            num = num
        assert num <= 25, "You are trying to [DISPLAY TOO MANY IMAGES]"
        frame = int(np.ceil(np.sqrt(num)))
        fig, ax = plt.subplots(frame, frame)
        for f1 in range(frame) :
            for f2 in range(frame) :
                idx = ((f2+1)+(f1*frame))-1
                if idx < num :
                    ax[f1,f2].imshow(images[:,:,idx], cmap='gray')
                    ax[f1,f2].title.set_text(f'Scan No. {idx} (from stack)')
                else :
                    ax[f1,f2].imshow(images[:,:,0], cmap='gray')
                    ax[f1,f2].title.set_text(f'[CAUTION!] index out of bounds - displaying Scan No. {0} instead')
                
    def create_tripple_masks(self, path, dtype='.bmp', dims=(1024,1024), flag_saveNewMasks=True):
        """
        >>> Checks if three masks for U-Net segmentation already do exist and 
        loads them. 
        If the masks don't exist, they are created and [optionally] saved 
        in the directories of their respective origins
        
        -> Param 1: Input path containing all folders with B-Scans and corresponding masks	
        """
        print("Prepocessing masks [GROUND TROUTH] for training...")
        trip_masks = [] 
        files = os.listdir(path)
        for c, f in enumerate(tqdm(files)) :
            # Check if all the masks already exist load them, else create them
            crn_file = os.path.join(path, f, str(self.list_mask_files[0] + dtype))
            ovd_file = os.path.join(path, f, str(self.list_mask_files[1] + dtype))
            bg_file = os.path.join(path, f, str(self.list_mask_files[2] + dtype))
            if not os.path.isfile(crn_file) or not os.path.isfile(ovd_file) or not os.path.isfile(bg_file):
                # Load line-segmented mask
                # IMPORTANT: 
                raw_mask = np.asarray(Image.open(os.path.join(path, f, 'mask.png')).resize((1024, 1024)))
                # create and add all three masks in order
                masks, _ = self.create_tripple_mask(raw_mask)
                trip_masks.append(np.moveaxis(masks, 0, -1))
                masks = np.asarray(masks)

                def safe_singular_mask(mask, file_path) :
                    assert np.size(dims) == 2, "[DIMENSION ERROR] - please enter image height and width"
                    plt.imsave(file_path, mask, cmap='gray', format='bmp')
 
                if flag_saveNewMasks :
                    safe_singular_mask(masks[0,:,:], crn_file)
                    safe_singular_mask(masks[1,:,:], ovd_file)
                    safe_singular_mask(masks[2,:,:], bg_file)
                    print(f"\nSaved images from folder/ iteration No. {c}!")
                    
            else :
                cornea = np.asarray(Image.open(os.path.join(path, f, str(self.list_mask_files[0] + dtype))).resize((dims[0], dims[1])))
                ovd = np.asarray(Image.open(os.path.join(path, f, str(self.list_mask_files[1] + dtype))).resize((dims[0], dims[1])))
                background = np.asarray(Image.open(os.path.join(path, f, str(self.list_mask_files[2] + dtype))).resize((dims[0], dims[1])))
                new_masks = np.dstack((cornea[:,:,0], ovd[:,:,0], background[:,:,0]))
                trip_masks.append(new_masks)
       
# =============================================================================
#         if not os.path.isfile(crn_file) or not os.path.isfile(ovd_file) or not os.path.isfile(bg_file) :
#             trip_masks = self.resize_no_interpol(trip_masks, dims)
# =============================================================================
            
        print("Done [LOADING] and/or creating [MASKS]!")
        # return dimensions are (n_img, height, width, n_masks)        
        return np.asarray(trip_masks, dtype=np.uint8)
                   
    def add_flipped_data(self, images, flag_add_xAxis_flipped=True, flag_add_yAxis_flipped=True) :
        """
        >>> Adds flipped versions of the input data to the training data stack
        >> Change flag configuaration to either add 
        x-, y- and x-y-flip (TRUE & TRUE),
        x- and x-y-flip (TRUE & FALSE) or
        y- and x-y-flip (FALSE & TRUE)
        """
        stack = images
        dims = np.shape(images)   
        if flag_add_xAxis_flipped and flag_add_yAxis_flipped :
            def_stack = self.create_flipped_images(images)
            x_stack = self.create_flipped_images(images, axis=0)
            y_stack = self.create_flipped_images(images, axis=1)
            stack = np.concatenate((def_stack, 
                                   (np.concatenate((np.concatenate((images, 
                                                                    x_stack), axis=-1), 
                                                    y_stack), axis=-1))), axis=-1)
        elif flag_add_xAxis_flipped and not flag_add_yAxis_flipped : 
            def_stack = self.create_flipped_images(images)
            x_stack = self.create_flipped_images(images, axis=0)
            stack = np.concatenate((def_stack, 
                                    np.concatenate((images, 
                                                    x_stack), axis=-1)), axis=-1)
        elif not flag_add_xAxis_flipped and flag_add_yAxis_flipped :
            def_stack = self.create_flipped_images(images)
            y_stack = self.create_flipped_images(images, axis=1)
            stack = np.concatenate((def_stack, 
                                    np.concatenate((images, 
                                                    y_stack), axis=-1)), axis=-1)
        else : 
            print("You have chosen to not add any flipped images")
        
        print(f"Added {np.shape(stack)[2]-dims[2]} images to data [THROUGH FLIPPING] original data!")
        return stack
    
    def prepare_data_for_network(self, bscan_name='raw_bScan',  
                                 flag_check_for_matching_data=False, flag_add_flipped_data=False):
        """
        loads, pre-processes and displays data for training
        """
        # Load and preprocess
        print("[STARTING PREPROCESSING] data for training...")
        x = self.load_images(self.path, bscan_name, (512,512))
        y = self.create_tripple_masks(self.path, dims=(512,512))
        
        # Add flipped versions of the all b-Scans to the training data
        if flag_add_flipped_data:
            #TODO: think of how the threre masks and the flipped pendants could work
            x = self.add_flipped_data(x)
            y = self.add_flipped_data(y)
                        
        x = x[np.newaxis]
        x = np.swapaxes(x, 0, 3)
        
        # Sanity check if inconsistencies in the data were observed            
        if flag_check_for_matching_data:
            self.sanity_check_training_data(x[:,:,:,0], y[:,:,:,2], update_rate_Hz=1) 
        
        print("[DONE PREPROCESSING] data for training")
        return x, y
 
    
if __name__ == '__main__':
    DtPreTrain = DataPreprocessing(train_path)
    X_train, Y_train = DtPreTrain.prepare_data_for_network()
    DtPreVali = DataPreprocessing(vali_path)
    X_test, Y_test = DtPreVali.prepare_data_for_network() 
    
# =============================================================================
# UNet architecture and training structure
# =============================================================================
def build_and_train_uNet(img_height, img_width, img_channels, X_train, Y_train, path_saved_model, 
                         flag_saveModel=True, base_size = 4, n_classes = 3):
    """    
    >>> U-Net Layer structure:
            
        -> [INPUT](NxMx3x1) -> C1(NxMx3x1)                                  ,--> U9(NxMx32)->C8(NxMx32)->[OUTPUT](NxMx1)
                '--> P1(NxMx32)->C2(NxMx32)                         ,--> U8(512x512x32)->C8(NxMx32)
                    '--> P2(NxMx32)->C3(NxMx32)                 ,--> U7(NxMx32)->C7(NxMx32)
                         '--> P3(NxMx32)->C4(NxMx32) ----> U6(NxMx32)->C6(NxMx32)
                                     '--> P4(NxMx32) -> C5(NxMx32) --^
    """
   
    if n_classes == 1:
        loss_function = 'binary_crossentropy'
        final_act = 'sigmoid'
    elif n_classes > 1:
        loss_function = 'categorical_crossentropy'
        final_act = 'softmax'

    b = base_size
    layer_actication = 'relu'
    inputs = tf.keras.layers.Input((img_height, img_width, img_channels)) 
    conv_int = tf.keras.layers.Lambda(lambda x: x / 255)(inputs)
    
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
    checkpointer = tf.keras.callbacks.ModelCheckpoint('model_for_segmentation.h5', verbose=1, save_best_only=True)
    
    callbacks = [
            tf.keras.callbacks.EarlyStopping(patience=2, monitor='val_loss'),
            tf.keras.callbacks.TensorBoard(log_dir='logs')]
    
    results = model.fit(X_train, Y_train, validation_split=0.2, batch_size=8, epochs=25, callbacks=callbacks)
    
    if flag_saveModel:
        model.save(os.path.join(train_path.split('\\training_data')[0], 'current_best_model'), save_format='h5')

    return model, checkpointer, results   
   
    
model, *_ = build_and_train_uNet(img_height, img_width, img_channels, X_train, Y_train, train_path)  

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
        ax[0, img].imshow(Y_test[img,:,:,2])
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

# =============================================================================
# # =============================================================================
# #     DEPRECATED
# # =============================================================================
#     def create_bool_masks_from_bin_masks(self, masks):
#         
#         dims = np.shape(masks)
#         bool_mask = [np.asarray(masks[:,:,img] <= 1, dtype=bool) for img in range(dims[2])]
#         
#         return bool_mask
#         
#     def preprocess_tss_masks(self, mask_name='tripple_masks', dtype='.bmp', dims=(1024,1024), flag_saveNewMasks=True):
#         """
#         >>> Go through all folders in path (each containing one training example/B-Scan)
#         >> if "mask_file".PNG doesnt exist it is calculated from image "mask.PNG"
#                 > it gets returned with size self.dims -> ready to be fed to network
#                 > the 3-areas-mask (TSS = Tripple Semantic Segmentatation) then 
#                 is saved in its folder as "mask_name.png" in its respective folder
#                 with size = dims (functions parameter dims, not class var self.dims!)
#         >> else, load mask from its file and add it to the pile
#         """
#         print("Prepocessing masks [GROUND TROUTH] for training...")
#         tert_mask = [] # "air" and "ovd" get casted as "0" by default
#         files = os.listdir(self.path)
#         for f in tqdm(files) :
#             # CREATE MASK: target mask (with 3 marked regions) doesn't already exist
#             file_trip_mask = os.path.join(self.path, f, (mask_name + dtype))
#             if not os.path.isfile(file_trip_mask) :
#                 tmp_mask, mask_stack = self.create_tripple_mask(np.asarray(Image.open(os.path.join(self.path, f, 'mask.png'))))  
#                 tmp_mask = self.resize_no_interpol(tmp_mask, (self.out_dims[0],self.out_dims[1]))
#                 if flag_saveNewMasks:
#                     plt.imsave(file_trip_mask, cv2.resize(tmp_mask, dims, interpolation = cv2.INTER_AREA), cmap='gray', format='bmp')       
#                 tert_mask.append(tmp_mask)
#             else : 
#                 tmp_mask = self.resize_no_interpol(np.asarray(Image.open(file_trip_mask)), (self.out_dims[0],self.out_dims[1]))
#                 tmp_mask = self.round_to_tripple_values(tmp_mask[:,:,0])
#                 tert_mask.append(tmp_mask)
#                 
#         print("Done preprocessing masks!")        
#         return np.dstack(np.asarray(tert_mask, dtype=np.uint8)), np.dstack(np.asarray(mask_stack, dtype=np.uint8))
#  
# =============================================================================
