---
title: "CIFAR-10 이미지 분류를 위한 CNN을 구성해보자! (Keras)"
slug: cifar10-cnn
tags:
  - ML
  - CNN
  - Keras
date: 2019-08-20T13:00:00+09:00
---


# Overview
이 문서에서는 CIFAR-10 dataset에 대한 이미지 분류를 Keras를 사용한 CNN(Convolution Neural Network)로 구현해보도록 하겠습니다.  

본문에서 사용한 코드는 [이곳](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/machine-learning/CNN-CIFAR10/cifar10%20dropout%20test%20notebook-s.ipynb)  

# CIFAR-10
발음을 조심해야하는 이름을 가진 [CIFAR-10](https://en.wikipedia.org/wiki/CIFAR-10) dataset은 32x32픽셀의 60000개 컬러이미지가 포함되어있으며, 각 이미지는 10개의 클래스로 라벨링이 되어있습니다.  
또한, MNIST와 같이 머신러닝 연구에 가장 널리 사용되는 dataset중 하나입니다.  

![image](https://user-images.githubusercontent.com/15958325/63308580-41b7fe80-c32e-11e9-827f-98052675c0ea.png)  

60000개 중, 50000개 이미지는 트레이닝 10000개 이미지는 테스트용도로 사용됩니다.  

# CNN Archtecture
> **[참고]**  
>[CNN이란?](https://gruuuuu.github.io/ai/cnn-doc/)  

본문에서 사용한 CNN의 각 레이어 구조는 다음과 같습니다.  
![feature extraction](https://user-images.githubusercontent.com/15958325/63317956-c23b2700-c34f-11e9-82c2-6a40787579ec.png)
  
![classification](https://user-images.githubusercontent.com/15958325/63318014-f0206b80-c34f-11e9-9321-a1959b48b7fe.png)  

>**[용어 설명]**  
>**3channel** : color이미지  
>**ReLu** : 0이상의 값들은 그대로 출력하게하는 활성화함수   
>**Padding(Same)** : 입력크기==출력크기 [[INFO]](https://gruuuuu.github.io/ai/cnn-doc/#1-4-padding)  
>**Dropout** : 무작위로 뉴런들을 버림 [[INFO]](https://gruuuuu.github.io/simple-tutorial/overfitting-handle/#dropout)  
>**Pooling** : 크기도 줄이고 특정 feature를 강조 [[INFO]](https://gruuuuu.github.io/ai/cnn-doc/#1-5-pooling)    
>**Softmax** : classification [[INFO]](https://gruuuuu.github.io/simple-tutorial/iris-tensorflow/#4-softmax)  

  
# Source Code
지금부터는 소스코드를 보도록 하겠습니다.  
본문에서 사용한 full source는 [이곳](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/machine-learning/CNN-CIFAR10/cifar10%20dropout%20test%20notebook-s.ipynb)에서 받을 수 있습니다.  

>**구글 colab**을 이용해서 테스트하였습니다.  
>
>노트 설정에서 **GPU**를 선택하고 돌리는 것을 추천드립니다.  
>
>![image](https://user-images.githubusercontent.com/15958325/63320315-62954980-c358-11e9-9e90-27ceb3e7de5a.png)  
>설정한 다음 **Restart Kernel**을 해주세요

## Load CIFAR-10 Dataset
~~~py
#cifar10에서 데이터를 로드
#from keras.datasets import cifar10 이 필요
(X_train, y_train), (X_test, y_test) = cifar10.load_data()

print ("Training data:")
print ("Number of examples: ", X_train.shape[0])
print ("Number of channels:",X_train.shape[3]) 
print ("Image size:", X_train.shape[1], X_train.shape[2])
print
print ("Test data:")
print ("Number of examples:", X_test.shape[0])
print ("Number of channels:", X_test.shape[3])
print ("Image size:", X_test.shape[1], X_test.shape[2]) 
~~~  

![image](https://user-images.githubusercontent.com/15958325/63320543-0f6fc680-c359-11e9-8027-af3934346f47.png)  

트레이닝에 사용할 5만장의 이미지와 테스트에 사용할 1만장의 이미지(32x32, 3channel)가 로드된 것을 확인할 수 있습니다.  

일부 이미지를 실제로 출력해보면 제대로 다운로드받았는지 확인할 수 있습니다.  
~~~py
plt.subplot(141)
plt.imshow(X_train[0], interpolation="bicubic")
plt.grid(False)
plt.subplot(142)
plt.imshow(X_train[4], interpolation="bicubic")
plt.grid(False)
plt.subplot(143)
plt.imshow(X_train[8], interpolation="bicubic")
plt.grid(False)
plt.subplot(144)
plt.imshow(X_train[12], interpolation="bicubic")
plt.grid(False)
plt.show()
~~~  
![image](https://user-images.githubusercontent.com/15958325/63320482-e0f1eb80-c358-11e9-995c-9fe6471b4f24.png)  

## Data Normalization

코드를 보기 전에 잠시 데이터 정규화에 대해서 설명하고 넘어가도록 하겠습니다.  

머신러닝에서의 핵심중 하나는 `cost`를 구하고 `Gradient Descent`와 같은 알고리즘을 사용하여 `cost`를 최소화 시키는 것입니다. 그렇게 하기 위해 적당한 `Learning Rate`값을 찾는 것이 중요합니다.  

근데, `Learning Rate`와 데이터에 대한 정규화가 어떤 상관이 있을까요?  

다음 그림을 보면 좀 더 직관적으로 이해할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/63322353-2f55b900-c35e-11e9-8030-14d9285a5de8.png)   

정규화되지 않은 데이터셋은 타원모양으로 길게 늘어져 `Learning Rate`를 매우 **작게** 해야지만 학습이 될 수 있다는 것을 확인할 수 있습니다. 만약 충분히 작지 않다면 수평으로 이동할 때와 수직으로 이동할 때 불균형이 발생하여 `Gradient Descent` 알고리즘을 적용하기 어려울 수 있습니다.  

반면에 정규화된 데이터셋은 구의 모양을 띄고 있습니다. 때문에 `Gradient Descent`알고리즘을 적용하여 **쉽고 빠르게** 최적화 지점을 찾을 수 있습니다.  

앞선 이유 때문에 최적의 머신러닝을 하기 위해선 데이터에 대한 정규화작업을 거치는 것이 반드시 필요합니다.  

**Data Normalization**에는 크게 두가지 방법이 있습니다. (하나 더있는데 추후 서술)

**1. Normalization(Min/Max)**
<center><img src="https://user-images.githubusercontent.com/15958325/63323966-fcadbf80-c361-11e9-9819-d539ea4c7261.png"></center>
전체 구간을 [0,1]로 맞춰줍니다.  

**2. Standardization**
<center><img src="https://user-images.githubusercontent.com/15958325/63324105-5d3cfc80-c362-11e9-8708-d7d0e4c1025f.png"></center>   

![image](https://user-images.githubusercontent.com/15958325/63326514-6381a780-c367-11e9-9112-d128aa98e952.png)  
**original data** : 정규화 하기 전의 데이터 분포  
**zero-centered data** : 원 데이터에 평균을 뺌. 이로써 데이터의 분포가 가운데에 모이게 됩니다.  
**normalized data** : 표준편차를 나눠줌으로써 데이터의 분포가 일정해지는 효과를 얻게 됩니다. (가로 세로 길이가 같아짐)

+) 반드시 정규화를 하기 위한 평균, 표준편차, min, max등의 값들은 **train set에 있는 값만 사용**하여 구하고 validation, test set에 적용하여야 합니다.  
참고링크 : [cs231n](http://aikorea.org/cs231n/neural-networks-2-kr/)


>**내가 몰라서 적는 표준편차 구하는 법)**  
>표준편차는 자료의 관찰값이 **얼마나 흩어져 있는지**를 나타내는 값  
>관측값에서 평균을 뺀 모든 값의 제곱을 구하고 그 값의 평균을 제곱근하면 된다.


## Data Preprocessing -code
다시 본론으로 돌아와서 소스코드를 보겠습니다.  
아래 소스코드는 위의 설명 중 `Standardization`을 사용해서 정규화를 진행하였습니다.  
~~~py
print ("mean before normalization:", np.mean(X_train)) 
print ("std before normalization:", np.std(X_train))

mean=[0,0,0]
std=[0,0,0]
newX_train = np.ones(X_train.shape)
newX_test = np.ones(X_test.shape)
#train set에 있는 데이터로만 평균과 표준편차를 구함
for i in range(3):
    mean[i] = np.mean(X_train[:,:,:,i])
    std[i] = np.std(X_train[:,:,:,i])

#train과 test셋 모두 정규화 작업    
for i in range(3):
    newX_train[:,:,:,i] = X_train[:,:,:,i] - mean[i]
    newX_train[:,:,:,i] = newX_train[:,:,:,i] / std[i]
    newX_test[:,:,:,i] = X_test[:,:,:,i] - mean[i]
    newX_test[:,:,:,i] = newX_test[:,:,:,i] / std[i]
        
X_train = newX_train
X_test = newX_test

print ("mean after normalization:", np.mean(X_train))
print ("std after normalization:", np.std(X_train))
print(X_train.max())
~~~  

![image](https://user-images.githubusercontent.com/15958325/63320845-fa476780-c359-11e9-8c49-098d6ae0f90e.png)  


## Training
데이터 정규화까지 마쳤으니 이제 본격적으로 트레이닝을 해보도록 하겠습니다.  

각 중요 파라미터는 다음과 같습니다.  

~~~py
batchSize = 512            #-- Training Batch Size
num_classes = 10           #-- Number of classes in CIFAR-10 dataset
num_epochs = 50            #-- Number of epochs for training   
learningRate= 0.001        #-- Learning rate for the network
lr_weight_decay = 0.95     #-- Learning weight decay. Reduce the learn rate by 0.95 after epoch


img_rows = 32              #-- input image dimensions
img_cols = 32 

Y_train = np_utils.to_categorical(y_train, num_classes)
Y_test = np_utils.to_categorical(y_test, num_classes)
~~~

>**Keras의 to_categorical**
>~~~
>input :  [1,0,4,3]  
>output : [0,1,0,0,0]
>         [1,0,0,0,0]
>         [0,0,0,0,1]
>         [0,0,0,1,0]
>~~~

모델 구현은 다음과 같습니다.  

~~~py
from keras import initializers
import copy
result = {}
y = {}
loss = []
acc = []
dropouts = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
for dropout in dropouts:
    print ("Dropout: ", (dropout))
    model = Sequential()

    #-- layer 1
    model.add(Conv2D(64, 3, 3,
                            border_mode='same',
                            activation='relu'
                            input_shape=(img_rows, img_cols,3)))
    model.add(Dropout(dropout))  
    model.add(Conv2D(64, 3, 3, activation='relu',border_mode='same'))
    model.add(Dropout(dropout))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    ##--layer 2
    model.add(Conv2D(128, 3, 3, activation='relu',border_mode='same'))
    model.add(Dropout(dropout))                                        
    model.add(MaxPooling2D(pool_size=(2, 2)))

    ##--layer 3                         
    model.add(Conv2D(256, 3, 3, activation='relu',border_mode='same'))
    model.add(Dropout(dropout)) 
    model.add(MaxPooling2D(pool_size=(2, 2)))

    ##-- layer 4
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))

    #-- layer 5
    model.add(Dense(512, activation='relu'))

    #-- layer 6
    model.add(Dense(num_classes, activation='softmax'))
    
    model.compile(loss='categorical_crossentropy',
                  optimizer='sgd',
                  metrics=['accuracy'])
    
    model_cce = model.fit(X_train, Y_train, batch_size=batchSize, nb_epoch=num_epochs, verbose=1, shuffle=True, validation_data=(X_test, Y_test))
    score = model.evaluate(X_test, Y_test, verbose=0)
    y[dropout] = model.predict(X_test)
    print('Test score:', score[0])
    print('Test accuracy:', score[1])
    result[dropout] = copy.deepcopy(model_cce.history)   
    loss.append(score[0])
    acc.append(score[1])
~~~  

![image](https://user-images.githubusercontent.com/15958325/63327913-1bb04f80-c36a-11e9-80fc-d55af49ffc54.png)  
![image](https://user-images.githubusercontent.com/15958325/63327916-1d7a1300-c36a-11e9-9163-653c35ad2ca0.png)  

Dropout을 0.0부터 0.9까지 바꿔가며 테스트를 마친 뒤 Dropout별 Accuracy와 Loss입니다.  
![image](https://user-images.githubusercontent.com/15958325/63328617-6aaab480-c36b-11e9-976c-0b2bf812ec56.png)  
![image](https://user-images.githubusercontent.com/15958325/63328621-6bdbe180-c36b-11e9-8e93-9ea3d42289e1.png)  


Dropout이 0.5일때 Acc가 가장 높고, Loss가 가장 낮습니다.  

>여담으로 Acc와 Loss를 결정짓는 요소는 굉장히 다양하니 뭘 어떻게 바꿔야 성능이 눈에 띄게 좋아지는지 지금 제 수준으로는 판단하기 굉장히 어려운 것 같습니다. 이래서 데이터사이언티스트가 몸값이 높은가...생각이 듭니다. ( ._.)  

## 번외. Optimizer=Adadelta

완전히 동일한 과정이고 optimizer만 `Adadelta`로 바꾼 결과 입니다. 그래프만 봐도 `Adadelta`가 좀 더 성능이 좋은것 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/63328041-603beb00-c36a-11e9-97f6-0575deae5ef7.png)  
![image](https://user-images.githubusercontent.com/15958325/63328046-616d1800-c36a-11e9-9847-dcbc8b105a15.png)  
여기도 마찬가지로 Dropout 0.5에서 Acc가 제일 높네요!

대부분은 optimizer function을 `adam`이나 `adadelta`를 사용한다고 하는데 아직 정확히 뭐가 다른지는 모르겠습니다.  
추후에 optimizer에 대한 내용도 공부해서 따로 포스팅을 해야겠습니다.  

-끝-  

----