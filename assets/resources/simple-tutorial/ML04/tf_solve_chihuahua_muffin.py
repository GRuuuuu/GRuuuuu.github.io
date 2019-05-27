#@title MIT License
#
# Copyright (c) 2018 IBM
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

#%%
import glob, os
import re

# TensorFlow and tf.keras
import tensorflow as tf
from tensorflow import keras

# Helper libraries
import numpy as np
import matplotlib.pyplot as plt

import PIL
from PIL import Image

# input이미지를 8bit grey scale이미지 배열로 변환
def jpeg_to_8_bit_greyscale(path, maxsize):
	img = Image.open(path).convert('L')   # convert image to 8-bit grayscale

	# 이미지 cropping으로 가로세로비율을 1:1로 맞춤
	WIDTH, HEIGHT = img.size
	if WIDTH != HEIGHT:
		m_min_d = min(WIDTH, HEIGHT)
		img = img.crop((0, 0, m_min_d, m_min_d))
	# Anti-alias 기법으로 입력한 maxsize scale로 이미지 조정
	img.thumbnail(maxsize, PIL.Image.ANTIALIAS)
	img_rotate = img.rotate(90)
	print("rotating...")
	print(img_rotate.size)
	return (np.asarray(img), np.asarray(img_rotate))

class_names = ['chihuahua', 'muffin']
##
# 이미지 데이터셋을 로드하여 배열에 저장
# invert_image파라미터가 true이면 inv_image(반전이미지)도 정상이미지와 함께 같이 저장
def load_image_dataset(path_dir, maxsize, reshape_size, invert_image=False):
	images = []
	labels = []
	os.chdir(path_dir)
	for file in glob.glob("*.jpg"):
		(img, img_rotate) = jpeg_to_8_bit_greyscale(file, maxsize)
		inv_image = 255 - img
		if re.match('chihuahua.*', file):
			images.append(img.reshape(reshape_size))
			labels.append(0)
			if invert_image:
				images.append(inv_image.reshape(reshape_size))
				images.append(img_rotate.reshape(reshape_size))
				labels.append(0)
				labels.append(0)
		elif re.match('muffin.*', file):
			images.append(img.reshape(reshape_size))
			labels.append(1)
			if invert_image:
				images.append(inv_image.reshape(reshape_size))
				images.append(img_rotate.reshape(reshape_size))
				labels.append(1)
				labels.append(1)
	return (np.asarray(images), np.asarray(labels))

#테스트 셋 로드
def load_test_set(path_dir, maxsize):
	test_images = []
	os.chdir(path_dir)
	for file in glob.glob("*.jpg"):
		img = jpeg_to_8_bit_greyscale(file, maxsize)
		test_images.append(img)
	return (np.asarray(test_images))

maxsize = 50, 50
maxsize_w, maxsize_h = maxsize

(train_images, train_labels) = load_image_dataset(
	path_dir='/Users/SeungYeonLee/Documents/GRU/GitHub/image-recognition-tensorflow/chihuahua-muffin',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=False)
(test_images, test_labels) = load_image_dataset(
	path_dir='/Users/SeungYeonLee/Documents/GRU/GitHub/image-recognition-tensorflow/chihuahua-muffin/test_set',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=False)

#%%
#이미지들을 로드하고나서의 중간결과
#shape결과 -> (배열개수, w픽셀, h픽셀, 채널)
print(train_images.shape)
print(len(train_labels))
print(train_labels)
print(test_images.shape)
print(test_labels)

#%%
# 이미지 값을 0~1사이로 조정
train_images = train_images / 255.0
test_images = test_images / 255.0
print(train_images)

#%%
# 레이어 세팅
sgd = keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.04, nesterov=True)

model = keras.Sequential([
    keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  	keras.layers.Dense(128, activation=tf.nn.sigmoid),
  	keras.layers.Dense(16, activation=tf.nn.sigmoid),
    keras.layers.Dense(2, activation=tf.nn.softmax)
])


model.compile(optimizer=sgd, 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
model.fit(train_images, train_labels, epochs=100)


test_loss, test_acc = model.evaluate(test_images, test_labels)

print('Test accuracy:', test_acc)

predictions = model.predict(test_images)
print(predictions)

#%%
# Using matplotlib display images.
def display_images(images, labels, title = "Default"):
	plt.title(title)
	plt.figure(figsize=(10,10))
	grid_size = min(25, len(images))
	for i in range(grid_size):
		plt.subplot(5, 5, i+1)
		plt.xticks([])
		plt.yticks([])
		plt.grid(False)
		print(images[i].shape)
		plt.imshow(images[i], cmap=plt.cm.binary)
		plt.xlabel(class_names[labels[i]])



# train이미지와 라벨 출력 
display_images(train_images.reshape((len(train_images), maxsize_w, maxsize_h)), 
	train_labels)
plt.show() 

#첫번째 예측
display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)), 
	np.argmax(predictions, axis = 1))
plt.show() 


#%%
# Comparing different model size and how they perform against the challenge.
baseline_model = keras.models.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(128, activation=tf.nn.sigmoid),
		keras.layers.Dropout(0.25),
  		keras.layers.Dense(16, activation=tf.nn.sigmoid),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

baseline_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

bigger_model = keras.models.Sequential([
		#keras.layers.Conv2D(64, 
		#kernel_size=3, strides=3, padding='same', input_shape=(maxsize_w, maxsize_h, 1)),
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
		keras.layers.Dense(256, activation=tf.nn.relu),
		keras.layers.Dropout(0.25),
  		keras.layers.Dense(128, activation=tf.nn.relu),
		keras.layers.Dropout(0.25),
		keras.layers.Dense(64, activation=tf.nn.relu),
		keras.layers.Dropout(0.5),
		keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

bigger_model1 = keras.models.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(128, activation=tf.nn.relu),
		keras.layers.Dropout(0.25),
		keras.layers.Dense(64, activation=tf.nn.relu),
		keras.layers.Dropout(0.5),
		keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

bigger_model1.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])


smaller_model1 = keras.models.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
 		keras.layers.Dense(64, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

smaller_model1.compile(optimizer='adam',
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

smaller_model = keras.models.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(512, activation=tf.nn.relu),
		keras.layers.Dropout(0.25),
		keras.layers.Dense(256, activation=tf.nn.relu),
		keras.layers.Dropout(0.25),
  		keras.layers.Dense(128, activation=tf.nn.relu),
		keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

vgg_style_model = keras.models.Sequential([
	keras.layers.Conv2D(128, (3, 3), activation='relu', input_shape = (maxsize_w, maxsize_h, 1)),
	keras.layers.Conv2D(64, (3, 3), activation='relu'),
	keras.layers.MaxPooling2D(pool_size=(2, 2)),
	keras.layers.Dropout(0.25),
	keras.layers.Conv2D(64, (3, 3), activation='relu'),
	keras.layers.Conv2D(64, (3, 3), activation='relu'),
	keras.layers.MaxPooling2D(pool_size=(2, 2)),
	keras.layers.Dropout(0.25),
	keras.layers.Flatten(),
	keras.layers.Dense(128, activation='relu'),
	keras.layers.Dropout(0.5),
	keras.layers.Dense(2, activation='softmax')
	])
datagen = keras.preprocessing.image.ImageDataGenerator(
        #zoom_range=0.2, # randomly zoom into images
		featurewise_center=False,
        #width_shift_range=0.2,  # randomly shift images horizontally (fraction of total width)
        #height_shift_range=0.2,  # randomly shift images vertically (fraction of total height)
        horizontal_flip=False,  # randomly flip images
        vertical_flip=False)  # randomly flip images
#datagen.fit(train_images)
sgd = keras.optimizers.SGD(lr=0.01, decay=1e-5, momentum=0.7, nesterov=True)
vgg_style_model.compile(loss='sparse_categorical_crossentropy',
 optimizer=keras.optimizers.Adam(lr=0.001),
 metrics=['accuracy','sparse_categorical_crossentropy'])

def plot_history(histories, key='sparse_categorical_crossentropy'):
  plt.figure(figsize=(16,10))
    
  for name, history in histories:
    val = plt.plot(history.epoch, history.history['val_'+key],
                   '--', label=name.title()+' Val')
    plt.plot(history.epoch, history.history[key], color=val[0].get_color(),
             label=name.title()+' Train')

  plt.xlabel('Epochs')
  plt.ylabel(key.replace('_',' ').title())
  plt.legend()
  plt.xlim([0, max(history.epoch)])
  plt.ylim([0, 1])

#keras.optimizers.Adam(lr=0.001)
bigger_model.compile(optimizer='adam',
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

baseline_model.compile(optimizer='adam',
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

smaller_model.compile(
	optimizer='adam',
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])


bigger_model1_history = bigger_model1.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)

# smaller_model1_history = smaller_model1.fit(train_images, train_labels,
# 	epochs=150,
# 	validation_data=(test_images, test_labels),
# 	verbose=2,
# 	workers=4)

bigger_model_history = bigger_model.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)

baseline_model_history = baseline_model.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)
# bigger_model_history = bigger_model.fit_generator(datagen.flow(train_images, train_labels),
# 	epochs=100,
# 	validation_data=(test_images, test_labels),
# 	verbose=2,
# 	workers=4)
# smaller_model_history = smaller_model.fit_generator(datagen.flow(train_images, train_labels),
# 	epochs=400,
# 	validation_data=(test_images, test_labels),
# 	verbose=2,
# 	workers=4)
# smaller_model_history = smaller_model.fit(train_images, train_labels,
# 	epochs=60,
# 	validation_data=(test_images, test_labels),
# 	verbose=2,
# 	workers=4)
# 

# vgg_style_model_history = vgg_style_model.fit_generator(
# 	datagen.flow(train_images, train_labels),
# 	#train_images, train_labels,
# 	epochs=120,
# 	validation_data=(test_images, test_labels),
# 	verbose=2,
# 	workers=4)

plot_history([
              #('smaller', smaller_model1_history),
              ('bigger', bigger_model1_history),
			  ('baseline', baseline_model_history),
			  ('bigger2', bigger_model_history)
			  
			  #('vgg', vgg_style_model_history)
			  ])

#plot_history([('smaller', smaller_model_history)])

#predictions = smaller_model.predict(test_images)
predictions2 = baseline_model.predict(test_images)

# predictions3 = vgg_style_model.predict(test_images)
#display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)),
# np.argmax(predictions3, axis = 1), title = "vgg")

# display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)),
#  np.argmax(predictions, axis = 1), title = "small")

display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)),
 np.argmax(predictions2, axis = 1), title = "")

#display_images(test_images, np.argmax(predictions, axis = 1), title = "small")
#print(predictions)
# print(predictions2)

plt.show()
