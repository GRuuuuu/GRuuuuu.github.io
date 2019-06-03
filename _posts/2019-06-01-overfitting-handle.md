---
title: "Refine Machine Learning Model"
categories: 
  - Simple-Tutorial
tags:
  - ML
  - Tensorflow
  - Keras
  - Python
last_modified_at: 2019-06-01T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 이미지분석 모델을 만들고, 기본 모델을 강화시켜 정확도를 높이는 방법에 대해서 다뤄보겠습니다.

다음 문서를 직접 해보고 작성한 문서입니다.  
Image recognition with TensorFlow and Keras: [link](https://developer.ibm.com/articles/image-recognition-challenge-with-tensorflow-and-keras-pt1/)  
Refine your deep learning model: [link](https://developer.ibm.com/articles/image-recognition-challenge-with-tensorflow-and-keras-pt2/)  

## 2. Prerequisites
개발에 사용할 언어와 툴의 version은 다음과 같습니다.  
`python: v3.6.5`  
`vscode: v1.33`  

>(리빙포인트)   
>각 단계별로 실행시키려면 vscode에 jupyter 플러그인을 추가해서 사용하면 편합니다.  

## 3. Dataset
치와와랑 머핀은 굉장히 비슷하게 생겼습니다. 인터넷을 돌아다니다가 아래와 같은 짤을 보셨을 수도 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/58748846-f4f42280-84b8-11e9-8ca3-bac96fe28b13.png)  

멀리서보면 솔직히 사람도 한순간 착각할 수 있을 정도로 비슷하게 생겼습니다.  

그러면 지금부터 치와와와 머핀을 구분할 수 있는 모델을 만들어보도록 하겠습니다.  

## 4. Import Data

### Clone Git
먼저 이미지파일과 소스코드를 다운받습니다.  
~~~
$ git https://github.com/GRuuuuu/imageRecognition-ML04.git
$ cd image-recognition-tensorflow
~~~  

### Import TensorFlow, Keras, other lib
필요한 라이브러리들을 추가합니다.  
~~~
$ pip install tensorflow matplotlib pillow
~~~  

## 5. Base Code

### Load Data
데이터를 불러와서 grey scale로 변환하여 배열에 저장하는 부분입니다.  
~~~py
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

#train이미지와 test이미지를 로드
(train_images, train_labels) = load_image_dataset(
	path_dir='User/some/where/path/image-recognition-tensorflow/chihuahua-muffin',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=False)
(test_images, test_labels) = load_image_dataset(
	path_dir='User/some/where/path/image-recognition-tensorflow/chihuahua-muffin/test_set',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=False)

# 이미지 값을 0~1사이로 조정
train_images = train_images / 255.0
test_images = test_images / 255.0
~~~  

위 과정의 결과를 보면,  
~~~py
#이미지들을 로드하고나서의 중간결과
#shape결과 -> (배열개수, w픽셀, h픽셀, 채널)
print(train_images.shape)
print(len(train_labels))
print(train_labels)
print(test_images.shape)
print(test_labels)
~~~   
![image](https://user-images.githubusercontent.com/15958325/58749702-173f6d80-84c4-11e9-8a27-43f1ecd95a08.png)  
26개 50x50픽셀 1채널의 train 이미지,  
14개 50x50픽셀 1채널의 test 이미지가 로드된 것을 확인할 수 있습니다.  

그러면 로드된 이미지를 확인해보겠습니다.  
~~~py
# train이미지와 라벨 출력 
display_images(train_images.reshape((len(train_images), maxsize_w, maxsize_h)),
    train_labels)
plt.show() 
~~~
![image](https://user-images.githubusercontent.com/15958325/58749904-81f1a880-84c6-11e9-9268-af1658abfc04.png)
26개의 train시킬 이미지가 로드된 것을 확인할 수 있습니다.  

### Build Model

~~~py
# 레이어 세팅

# dense 1번째파라미터:hidden layer
model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(128, activation=tf.nn.relu),
	keras.layers.Dense(16, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
])
~~~
레이어를 알아보기 쉽게 도식화 시키면 다음 그림과 같습니다.  

![image](https://user-images.githubusercontent.com/15958325/58750231-b4050980-84ca-11e9-830d-17f11be63411.png)  

2차원의 이미지를 `Flatten Layer`에서 1차원배열로 만들고 각 인자를 `Fully Connected Layer`에 보내고 그 결과를 `softmax`알고리즘을 통해 치와와인지 머핀인지를 파악하게 됩니다.  

레이어를 구성했으니 cost를 최소화시키는 `optimizer`를 결정하고, `loss function`으로는 어떤것을 사용할것인지 정해야합니다.  
~~~py
#optimizer는 Adam을 사용
model.compile(optimizer=keras.optimizers.Adam(lr=0.001), 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])
~~~
`optimizer`로는 Adam을 사용할것입니다.  
Adam은 최적의 가중치 값을 구하기 위해 미분을 통해 기울기를 구하고 이를 통해 가중치 값을 갱신하는 방법인 SGD(`Stochastic Gradient Descent`:확률적 경사하강법)을 강화한 `optimizer`입니다.  
![image](https://user-images.githubusercontent.com/15958325/58750848-0d246b80-84d2-11e9-96b2-12f970d821dd.png)  
자세한 설명은 [이곳](https://dalpo0814.tistory.com/29)  

트레이닝 부분입니다. 전체 trainning data를 이용해 150번의 학습을 실행하겠습니다.  
~~~py
# epoch : 전체 sample데이터를 이용해 한바퀴 학습하는것
model.fit(train_images, train_labels, epochs=150)

# test이미지로 정확도 측정
test_loss, test_acc = model.evaluate(test_images, test_labels)
print('Test accuracy:', test_acc)

# test이미지에 예측한 값을 라벨링
predictions = model.predict(test_images)
print(predictions)
~~~

학습을 실행한 뒤 이 모델이 어느정도의 정확도를 가지고 있고, 실제 테스트이미지에 어떤 값을 라벨링했는지 보겠습니다.  
~~~py
#첫번째 예측
display_images(test_images.reshape((len(test_images), maxsize_w, maxsize_h)), 
	np.argmax(predictions, axis = 1))
plt.show() 
~~~

![image](https://user-images.githubusercontent.com/15958325/58750662-43f98200-84d0-11e9-80c6-f67fd381548e.png)  
![image](https://user-images.githubusercontent.com/15958325/58750667-4cea5380-84d0-11e9-9d85-4cf1a0ac5949.png)  

어느정도 test이미지의 값을 맞췄지만 몇몇 사진은 다르게 예측하는것을 볼 수 있습니다.  
이제부터는 모델을 좀 더 강화시키는 방법에 대해 알아보겠습니다.  
 
## 6. Refine Model
머신러닝에서 트레이닝셋을 과도하게 학습시켰을 경우 test셋에 대한 에러가 높아지는 현상을 `Overfitting`이라고 합니다.  
이 `Overfitting`은 머신러닝 알고리즘의 오차를 증가시키는 원인으로 작용합니다. 실제로 기존의 알고리즘을 이용하여 어떠한 데이터를 인식, 분류하다보면 굉장히 골치아픈 문제 중 하나입니다.  

일반적으로 학습데이터는 실제 데이터의 부분집합이며 실제 데이터를 모두 수집하는 것은 불가능하고, 학습 데이터만 가지고 실제 데이터의 오차가 증가하는 지점을 예측하기란 매우 어렵거나 불가능합니다.  

지금부터는 몇가지 방법을 통해 Model을 강화시키고 `Overfitting`을 줄여보도록 하겠습니다.  

> **Handle Overfitting**  
>- [Model Size](https://gruuuuu.github.io/simple-tutorial/overfitting-handle/#model-size)  
>- [Regularization](https://gruuuuu.github.io/simple-tutorial/overfitting-handle/#regularization)  
>- [Dropout](https://gruuuuu.github.io/simple-tutorial/overfitting-handle/#dropout)  
>- [Training Data](https://gruuuuu.github.io/simple-tutorial/overfitting-handle/#training-data)  

### Model Size
첫번째로 모델의 사이즈에 대해서 보겠습니다. 여기서 말하는 사이즈는 각 dense레이어층의 히든 레이어의 개수를 뜻합니다.  
만약 레이어의 개수가 당면한 문제보다 훨씬 클 경우 관련 없는 특징이나 패턴을 학습하여 일반화되지 않을 것이고, 작을경우 제대로 학습하지 못해 test 셋에 적합하지 못한 모델이 될것입니다.  

이전 baseline모델에서 레이어의 수를 줄이고 늘려서 테스트를 해보도록 하겠습니다.  

~~~py
##모델 정보
#기본모델 (hidden-128-16-2)
baseline_model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(128, activation=tf.nn.relu),
	keras.layers.Dense(16, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#hidden-64-2
smaller_model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(64, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#hidden-512-128-16-2
bigger_model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(512, activation=tf.nn.relu),
	keras.layers.Dense(128, activation=tf.nn.relu),
	keras.layers.Dense(16, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])

#COMPLIE: optimizer=Adam  loss=sparse_categorical_crossentropy
#다른모델도 동일
baseline_model.compile(optimizer=keras.optimizers.Adam(lr=0.001),
	loss='sparse_categorical_crossentropy',
	metrics=['accuracy','sparse_categorical_crossentropy'])
...

#FIT: epoch=150
baseline_model_history = baseline_model.fit(train_images, train_labels,
	epochs=150,
	validation_data=(test_images, test_labels),
	verbose=2,
	workers=4)
...

#그래프로 출력
plot_history([
	('baseline', baseline_model_history),
  ('smaller', smaller_model_history),
  ('bigger', bigger_model_history),
	])
plt.show()
~~~

![image](https://user-images.githubusercontent.com/15958325/58757090-557a7280-8540-11e9-9a36-592fe3a26954.png)  
epoch가 증가할수록 Crossentropy가 감소하는 모습을 확인할 수 있습니다.   

위 3모델중 bigger가 가장 빨리 0에 수렴하므로 한번 레이어를 더 늘려서 테스트해보겠습니다.  

~~~py
#hidden-1024-512-128-16-2
bigger_model2 = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(1024, activation=tf.nn.relu),
	keras.layers.Dense(512, activation=tf.nn.relu),
	keras.layers.Dense(128, activation=tf.nn.relu),
	keras.layers.Dense(16, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#그 외 동일한 조건
...
~~~   

small모델을 제외한 baseline과 bigger, bigger2의 그래프입니다.   
![image](https://user-images.githubusercontent.com/15958325/58757121-139dfc00-8541-11e9-9864-edd57a721e40.png)  
확실히 dense가 높아지니 crossentropy가 낮아지는게 눈에 들어오는것 같습니다. 지금부터는 결과가 좋았던 bigger와 bigger2모델을 가지고 진행해보도록 하겠습니다.  

### Regularization
![image](https://user-images.githubusercontent.com/15958325/58757345-c5d7c280-8545-11e9-81b2-de0a99d95b83.png)  

`Regularization`은 W(weight)가 너무 큰 값들을 갖지 않도록 하는 것을 말합니다. 값이 커지게 되면 구불구불한 형태의 코스트함수가 만들어지고 예측에 실패하게 되는데, 이를 머신러닝에서는 **"데이터보다 모델의 복잡도(Complexity)가 크다"** 라고 설명합니다.  
과도하게 복잡하기 때문에 발생하는 문제라고 보는 것이고, 이를 낮추기 위한 방법이 `Regularization`입니다.   

>가중치가 클수록 큰 패널티를 부과하여 `Overfitting`을 억제하는 방법

Regularization에는 L1정규화, L2정규화가 있는데 둘의 차이는 다음과 같습니다.  

- **L1 regularization** : 대부분의 요소값이 0인 `sparse feature`에 의존한 모델에서 불필요한 feature에 대응하는 가중치를 0으로 만들어 해당 feature를 모델이 무시하게 만듬. `feature selection`효과가 있다.  
- **L2 regularization** : 아주 큰 값이나 작은 값을 가지는 `outlier`모델 가중치에 대해 0에 가깝지만 0은 아닌값으로 만듬. 선형모델의 일반화능력을 개선시키는 효과가 있다.  

--> 패널티에 대한 효과를 크게보기 위해 L1보다 L2를 많이 사용하는 경향이 있음.  


bigger와 bigger2에 L2정규화를 적용한 그래프  
~~~py
bigger_model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(512, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(128, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(16, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
bigger_model2 = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(1024, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(512, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(128, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(16, activation=tf.nn.relu, kernel_regularizer=keras.regularizers.l2(0.001)),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
~~~  

![image](https://user-images.githubusercontent.com/15958325/58757497-57483400-8548-11e9-891d-f48766910a41.png)   

### Dropout
![image](https://user-images.githubusercontent.com/15958325/58757543-cc1b6e00-8548-11e9-91a3-6093a9c8d0b2.png)  
Dropout은 전체 weight를 계산에 참여시키는 것이 아니라, Layer에 포함된 weight중에서 일부만 참여시키는 방법입니다. 이렇게만 보면 어떻게 성능이 좋아진다는거지? 하지만 실제로 굉장히 좋은 성능을 낸다고 합니다.  

여러개의 모델을 만드는 대신에 모델 결합에 의한 투표효과와 비슷한 효과를 내기위해 학습 사이클이 진행되는 동안 무작위로 일부 뉴런을 생략합니다. 그렇게 되면 생략되는 뉴런의 조합만큼 지수함수적으로 다양한 모델을 학습시키는 것이니 모델결합의 효과를 누릴 수 있습니다.  

또한 실제로 실행시킬때에는 생략된 많은 모델을 실행시키는 것이 아니라, 생략된 모델들이 모두 파라미터를 공유하고 있기 때문에 각각의 뉴런들이 dropout하지 않을 확률을 각각의 가중치에 곱해주는 형태가 됩니다.  

**그래서 이런 dropout이 왜 regularization 효과를 갖는가?**  
학습을 시키다보면 학습데이터에 의해 각각의 weight들이 서로 동조화(Co-adaptation) 되는 현상이 발생할 수 있는데, 무작위로 생략시키며 학습을 시킴으로써 이런 동조화 현상을 피할 수 있게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/58757878-b315bb80-854e-11e9-9f9c-ef9fa9e0f92b.png)  
위 그림처럼 더 선명한 feature를 얻을 수 있게 됩니다.  

>참고 링크 : [dropout](http://blog.naver.com/PostView.nhn?blogId=laonple&logNo=220818841217&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=1&postListTopCurrentPage=1&from=postView)  

bigger와 bigger2에 dropout을 적용한 그래프입니다.  

~~~py
#dropout을 적용하지 않은 모델
base_bigger_model = keras.Sequential([
	keras.layers.Flatten(input_shape = ( maxsize_w, maxsize_h , 1)),
	keras.layers.Dense(512, activation=tf.nn.relu),
	keras.layers.Dense(128, activation=tf.nn.relu),
	keras.layers.Dense(16, activation=tf.nn.relu),
	keras.layers.Dense(2, activation=tf.nn.softmax)
	])
#dropout적용
#Dropout(0.5) : 50%의 노드만 사용  (0.6이면 60%노드만사용 | default는 0.5)
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
...
#epoch는 400으로 올림
~~~  

![image](https://user-images.githubusercontent.com/15958325/58758250-95972080-8553-11e9-9446-7305ccced902.png)  
(base : dropout을 적용하지 않은 bigger모델)  

(순서대로 base-bigger-bigger2모델) 정확도는 다음과 같습니다.
![image](https://user-images.githubusercontent.com/15958325/58758561-e741aa00-8557-11e9-8715-bca9c6c5f338.png)  

### Training Data
트레이닝 데이터가 많을수록 모델의 정확도를 높일 수 있습니다. 이미지의 반전, 회전 등을 통해 제한된 이미지를 더 늘려서 학습시킬수있습니다.  

~~~py
(train_images, train_labels) = load_image_dataset(
	path_dir='/Users/some/where/image-recognition-tensorflow/chihuahua-muffin',
	maxsize=maxsize,
	reshape_size=(maxsize_w, maxsize_h, 1),
	invert_image=True)
~~~
이미지를 로드할때 invert_image 파라미터를 True로 두고 로드를 시키면 반전이미지와 회전된 이미지까지 트레이닝 시킬 수 있습니다.  

모델의 정보는 바로 위와 같고, 트레이닝 이미지만 증가시킨 경우입니다.  
![image](https://user-images.githubusercontent.com/15958325/58758543-ae093a00-8557-11e9-84aa-5633ed958df0.png)  

그런데 모델의 정확도를 살펴보니 결과가 형편이 없습니다.   
![image](https://user-images.githubusercontent.com/15958325/58758587-469fba00-8558-11e9-9349-08074baead64.png)  

트레이닝 이미지가 많은것이 도움이 될 수도 있지만 테스트셋이 어떤 데이터로 이루어져있는지, 또 과도한 정보때문에 제대로된 판단을 못할수도 있습니다.  

개인적인 생각으로는 회전된 치와와사진이 트레이닝셋에 추가되었는데 테스트셋에는 회전된 치와와사진이나 머핀사진이 없었기 때문에 이런 결과가 나오지 않았나 싶습니다.  

## 7. Conclusion 
`Overfitting`을 핸들링하는 몇가지 방법을 위에서 배웠습니다.  
전부 다 적용해서 좋은 결과가 나오면 얼마나 편한 얘기겠냐만 현실은 그렇지 않습니다. 결과가 잘 나올것같은데 형편없는 결과가 나오고, 그 이유는 모르겠는 일이 비일비재합니다.  
결국 각 케이스에 알맞게 핸들링하는게 가장 중요한것 같습니다.  

마지막으로 몇가지 테스트를 거쳐 이 테스트케이스에 알맞은 모델을 만들어 봤습니다.  

~~~py
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
~~~
기본 모델에서 hidden layer를 더 추가시켜줬고(bigger_model), Dropout을 통해 Overfitting을 줄였습니다. 결과는 다음과 같습니다.  

![image](https://user-images.githubusercontent.com/15958325/58758866-e8c1a100-855c-11e9-8bac-c39a618cc481.png)    
![image](https://user-images.githubusercontent.com/15958325/58758872-f414cc80-855c-11e9-9bf3-a85b2ea74a89.png)  
![image](https://user-images.githubusercontent.com/15958325/58758869-ee1eeb80-855c-11e9-97f7-b99114b9304e.png)  

----