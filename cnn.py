# -*- coding: utf-8 -*-
"""CNN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1e9ONFhTHp4kjdUCLaKQuKbxEgTi2kMWI

# Yeni Bölüm
"""

import cv2
import urllib
import itertools
import numpy as np
import pandas as pd
import seaborn as sns
import random,os,glob
from imutils import paths
import matplotlib.pyplot as plt
from sklearn.utils import shuffle
from urllib.request import urlopen

import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import confusion_matrix,classification_report

import tensorflow as tf


from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing import image
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.callbacks import ModelCheckpoint,EarlyStopping
from tensorflow.keras.layers import Conv2D,Flatten,MaxPooling2D,Dense,Dropout,SpatialDropout2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator,img_to_array,load_img,array_to_img

from google.colab import drive
drive.mount('/content/drive',force_remount=True)

dir_path= '/content/drive/MyDrive/Garbage classification'
print(dir_path)

#!unzip -u "/content/drive/MyDrive/Garbage classification.zip" -d "/content/drive/MyDrive"

#Definitaion Target size and label values
target_size=(224,224)
waste_labels = {"cardboard": 0,"glass": 1,"metal": 2,"paper": 3,"plastic": 4,"trash":5}

def load_datasets(path):
  """
 Reads the image in the directory containing the images and creates its labels.

  Parameters:
  Return:
  x:Holds matrix information of images
  labels:List holding the class information to which the image belongs.
  """
  x=[]
  labels=[]
  #Gönderdiğimiz pathdeki görüntüleri listeleyip sıralamaktadır
  image_paths=sorted(list(paths.list_images(path)))

  for image_path in image_paths:
    img=cv2.imread(image_path)#reading image
    img=cv2.resize(img,target_size)#adjusting size of image
    x.append(img)#Scaled images are added to the list x.
    label=image_path.split(os.path.sep)[-2]#/content/drive/MyDrive/Garbage classification/cardboard/images so ==> -2 = cardboard(label name)
    labels.append(waste_labels[label]) #A number is assigned to the label variable with waste_labels.   label değişkenine sayı atanır waste_labels ile


  x, labels = shuffle(x, labels, random_state=42)
  print(f"X boyutu : {np.array(x).shape}")
  print(f"Label sınıf sayısı : {len(np.unique(labels))} Gözlem sayısı: {len(labels)}")

  return x, labels

x, labels= load_datasets(dir_path)

#Keeping the dimensions of the image.
input_shape=(np.array(x[0]).shape[1],np.array(x[0]).shape[1] , 3)
print(input_shape)

def visualize_img(image_batch, label_batch):
  plt.figure(figsize=(10,10))
  for n in range(10):
    ax=plt.subplot(5,5,n+1)
    plt.imshow(image_batch[n])
    plt.title(np.array(list(waste_labels.keys()))[to_categorical(labels, num_classes=6)[n]==1][0].title())
    plt.axis('off')

visualize_img(x,labels)

"""3)VERİYİ HAZIRLAMA"""

from PIL import Image
#Verilen kurallara göre resimlerin bazı özelliklerini değişerek yeni fotoğraflar türetiriz
train=ImageDataGenerator(horizontal_flip=True,
                         vertical_flip=True,
                         validation_split=0.1, #test ratio
                         rescale=1./255,  #Converts the images to the range between 0 and 1.
                         shear_range=0.1, #Applies image rotation to the image. A value is given in degrees.
                         zoom_range=0.1,
                         width_shift_range=0.1,
                         height_shift_range=0.1)

test=ImageDataGenerator(rescale=1/255,
                        validation_split=0.1)

#flow from directory ile görüntüleri tensorflow'a getiririz
train_generator=train.flow_from_directory(directory=dir_path,
                                    target_size=(target_size),
                                    class_mode='categorical',
                                    subset='training')

test_generator=test.flow_from_directory(directory=dir_path,
                                    target_size=(target_size),
                                    batch_size=251, #dimension of datasets
                                    class_mode='categorical', #Represents the class of a categorical variable. If it were binary classification, we would use the term "binary" instead of "categorical".
                                    subset='validation')

"""4)MODELLEME(MODELING)

4.1)Sıfırdan CNN Modeli Kurma


*   Sequantial
*   Evrişim Katmanı(Convolution Layer,Vonv2d)
*   Havuzlama katmanı(Pooling Layer)
*   Aktivasyon Fonksiyonu Katmanı
*   Flattening Katmanı
*   Dense Katmanı
*   Dropout Katmanı

"""

model=Sequential() #Constructs a neural network with sequential layers.
model.add(Conv2D(filters=32 , kernel_size=(3,3) , padding='same' , input_shape=(input_shape) , activation='relu'))
#filters:      the number of filters to be applied on the image
#kernel size:  the size of the filter
#padding:      sets the input to have zeros around it, so that the output has the same height as the input matrix
#input_shape:  represents the dimensions of the input images

model.add(MaxPooling2D(pool_size=2 , strides=(2,2)))
#MaxPooling:   takes the maximum value of the points visited by the filter

model.add(Conv2D(filters=64 , kernel_size=(3,3) , padding='same' , input_shape=(input_shape) , activation='relu'))
model.add(MaxPooling2D(pool_size=2 , strides=(2,2)))

model.add(Conv2D(filters=32 , kernel_size=(3,3) , padding='same' , input_shape=(input_shape) , activation='relu'))
model.add(MaxPooling2D(pool_size=2 , strides=(2,2)))

model.add(Flatten())
#the data into a one-dimensional array

model.add(Dense(units=64 , activation='relu'))
model.add(Dropout(rate=0.2))
#Dropout is used to prevent overfitting

model.add(Dense(units=32 , activation='relu'))
model.add(Dropout(rate=0.2))


model.add(Dense(units=6 , activation='softmax')) #The reason for having 6 is that we are trying to classify the object into 6 different classes.

"""4.2)Optimizasyon ve Değerlendirme Metriklerinin Ayarlanması"""

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=[tf.keras.metrics.Precision() , tf.keras.metrics.Recall() , 'acc'])
#We try to increase the accuracy value according to the loss function. If there were 2 classes, we would use binary_crossentropy.
#There can be different optimization methods such as adam, sgd, or rms.
#We want to see the recall and precision values with metrics (accuracy is automatically included).

callbacks = [EarlyStopping(monitor='vall_loss' , patience=50 , verbose=1 , mode='min'),
            ModelCheckpoint(filepath='mymodel.h5' , monitor='vall_loss' , mode='min' , save_best_only=True , save_weights_only=False , verbose=1)]
#EarlyStopping helps to prevent overfitting. 'Monitor' determines which value to monitor for stopping. 'Patience' determines the number of epochs with no improvement after which it is considered as overfitting.
#In this case, if there is no progress after 50 epochs, the system identifies it as overfitting.
#'Verbose' can take values 0, 1, or 2. 'Mode' can be min, max, or auto.
#ModelCheckpoint helps us to save the best model.

"""4.3)MODELİN EĞİTİLMESİ"""

history= model.fit_generator(generator=train_generator,
                             epochs=100,
                             validation_data=test_generator,
                             callbacks=callbacks,
                             workers=4,
                             steps_per_epoch=2276/32,
                             validation_steps=251/32)
#As the loss decreases, it indicates better performance.
#Higher values of precision, recall, and accuracy indicate better performance as well.

"""4.5)Accuarcy ve Loss Grafikleri"""

plt.figure(figsize=(20,5))
plt.subplot(1,2,1)
plt.plot(history.history['acc'],label='Training Accuarcy')
plt.plot(history.history['val_acc'],label='Validation Accuarcy')
plt.legend(loc='lower right')
plt.xlabel('Epoch',fontsize=16)
plt.ylabel('Accuarcy',fontsize=16)
plt.ylim([min(plt.ylim()),1])
plt.title('Training and Validaiton Accuarcy', fontsize=16)


plt.subplot(1,2,1)
plt.plot(history.history['loss'],label='Training Loss')
plt.plot(history.history['val_loss'],label='Validation Loss')
plt.legend(loc='upper right')
plt.xlabel('Epoch',fontsize=16)
plt.ylabel('Loss',fontsize=16)
plt.ylim([0,max(plt.ylim())])
plt.title('Training and Validaiton Loss', fontsize=16)
plt.show()