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
	path_dir='C:/Users/GRu/Downloads/image-recognition-tensorflow/chihuahua-muffin',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=False)
(test_images, test_labels) = load_image_dataset(
	path_dir='C:/Users/GRu/Downloads/image-recognition-tensorflow/chihuahua-muffin/test_set',
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


# 이미지 값을 0~1사이로 조정
train_images = train_images / 255.0
test_images = test_images / 255.0


#%%
# 레이어 세팅
#sgd = keras.optimizers.SGD(lr=0.01, decay=1e-6, momentum=0.04, nesterov=True)

#dense 1st:hidden layer
model = keras.Sequential([
    keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  	keras.layers.Dense(128, activation=tf.nn.relu),
  	keras.layers.Dense(16, activation=tf.nn.relu),
    keras.layers.Dense(2, activation=tf.nn.softmax)
])


model.compile(optimizer=keras.optimizers.Adam(lr=0.001), 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

#epoch : 전체 sample데이터를 이용해 한바퀴 학습하는것
model.fit(train_images, train_labels, epochs=400)


test_loss, test_acc = model.evaluate(test_images, test_labels)

print('Test accuracy:', test_acc)

predictions = model.predict(test_images)
print(predictions)

#%%
# Using matplotlib display images.
def display_images(images, labels, title = "Default"):
	plt.title(title)
	plt.figure(figsize=(10,10))
	grid_size = min(49, len(images))
	for i in range(grid_size):
		plt.subplot(7, 7, i+1)
		plt.xticks([])
		plt.yticks([])
		plt.grid(False)
		print(images[i].shape)
		plt.imshow(images[i], cmap=plt.cm.binary)
		plt.xlabel(class_names[labels[i]])

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

datagen = keras.preprocessing.image.ImageDataGenerator(
		featurewise_center=False,
    horizontal_flip=False,  # randomly flip images
    vertical_flip=False)  # randomly flip images

# train이미지와 라벨 출력 
display_images(train_images.reshape((len(train_images), maxsize_w, maxsize_h)), 
	train_labels)
plt.show() 

#첫번째 예측
display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)), 
	np.argmax(predictions, axis = 1))
plt.show() 

#%%
## 수정1 : model size에 따라

#기본모델 (hidden-128)
baseline_model = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(128, activation=tf.nn.relu),
  		keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#hidden-64
smaller_model = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
 			keras.layers.Dense(64, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#hidden-512
bigger_model = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(512, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
			keras.layers.Dense(128, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
			keras.layers.Dense(16, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

#COMPLIE: optimizer=Adam
baseline_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])
smaller_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])
bigger_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])


#FIT: epoch=150
baseline_model_history = baseline_model.fit(train_images, train_labels,
	epochs=150,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)
smaller_model_history = smaller_model.fit(train_images, train_labels,
 	epochs=150,
 	validation_data=(test_images, test_labels),
 	verbose=2,
	workers=4)
bigger_model_history = bigger_model.fit(train_images, train_labels,
	epochs=150,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)


plot_history([
	('baseline', baseline_model_history),
  ('smaller', smaller_model_history),
  ('bigger', bigger_model_history),
	])

plt.show()

#%%
test_loss, test_acc,cross = baseline_model.evaluate(test_images, test_labels)
print('테스트 정확도1:', test_acc)

test_loss, test_acc,cross = smaller_model.evaluate(test_images, test_labels)
print('테스트 정확도2:', test_acc)

test_loss, test_acc,cross = bigger_model.evaluate(test_images, test_labels)
print('테스트 정확도3:', test_acc)


#%%
## 수정1-1 : model size를 더 늘려보자

#hidden-1024
bigger_model2 = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(1024, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
  		keras.layers.Dense(512, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
			keras.layers.Dense(128, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
			keras.layers.Dense(16, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

bigger_model2.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

bigger_model2_history = bigger_model2.fit(train_images, train_labels,
	epochs=150,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)

plot_history([
	('baseline', baseline_model_history),
  ('bigger', bigger_model_history),
  ('bigger2', bigger_model2_history),
	])


plt.show()
#%%
test_loss, test_acc,cross = bigger_model2.evaluate(test_images, test_labels)
print('테스트 정확도4:', test_acc)



#%%
# 수정2 : dropout적용
# overfitting막아줌
base_bigger_model = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(512, activation=tf.nn.relu),
			keras.layers.Dense(128, activation=tf.nn.relu),
			keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
d_bigger_model = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(512, activation=tf.nn.relu),
			keras.layers.Dropout(0.5),
			keras.layers.Dense(128, activation=tf.nn.relu),
			keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
d_bigger_model2 = keras.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
  		keras.layers.Dense(1024, activation=tf.nn.relu),
			keras.layers.Dropout(0.5),
  		keras.layers.Dense(512, activation=tf.nn.relu),
			keras.layers.Dropout(0.5),
			keras.layers.Dense(128, activation=tf.nn.relu),
			keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

base_bigger_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])
d_bigger_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])
d_bigger_model2.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

base_bigger_model_history = base_bigger_model.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)
d_bigger_model_history = d_bigger_model.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)
d_bigger_model2_history = d_bigger_model2.fit(train_images, train_labels,
	epochs=400,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)


plot_history([
  ('base', base_bigger_model_history),
  ('bigger', d_bigger_model_history),
  ('bigger2', d_bigger_model2_history),
	])

plt.show()

#%%
test_loss, test_acc,cross = base_bigger_model.evaluate(test_images, test_labels)
print('테스트 정확도1:', test_acc)

test_loss, test_acc,cross = d_bigger_model.evaluate(test_images, test_labels)
print('테스트 정확도2:', test_acc)

test_loss, test_acc,cross = d_bigger_model2.evaluate(test_images, test_labels)
print('테스트 정확도3:', test_acc)



#%%
#최적의 모델 -train image:26    test image:14
baseline_model = keras.models.Sequential([
    	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
			keras.layers.Dense(512, activation=tf.nn.relu),
  		keras.layers.Dense(128, activation=tf.nn.relu),
			keras.layers.Dropout(0.25),
  		keras.layers.Dense(16, activation=tf.nn.relu),
    	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

baseline_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])

baseline_model_history = baseline_model.fit(train_images, train_labels,
	epochs=300,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)

plot_history([
		('baseline', baseline_model_history),
	])

test_loss, test_acc,cross = baseline_model.evaluate(test_images, test_labels)
print('테스트 정확도:', test_acc)
predictions2 = baseline_model.predict(test_images)

display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)),
 np.argmax(predictions2, axis = 1), title = "")

plt.show()

#%%
 