---
title: "Iris TensorFlow Basic Softmax"
categories: 
  - Simple-Tutorial
tags:
  - ML
  - Softmax
  - Python
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---

This tutorial introduces how to classify iris species using TensorFlow, Padas for data analysis. This tutorial is based on the Softmax Algorithm example from TensorFlow.  

## 1. Overview

이 문서는 iris(붓꽃)의 꽃잎과 꽃받침의 길이를 통해 각 붓꽃의 품종을 구별해 내는 모델을 소개하고 있습니다.  
`softmax`알고리즘을 사용해서 데이터를 분석할 것입니다.    

## 2. Prerequisites

개발에 사용할 언어와 툴의 version은 다음과 같습니다.  
`python: v3.6.5`  
`vscode: v1.33`  

또한 이 문서에서 코드의 실행은 `jupyter notebook`을 사용할건데, 따로 데스크탑버전이나 로컬로 실행하지 않고 `vscode`에 끼워서 사용할겁니다.  

코드만 실행할 수 있다면 상관없지만, `vscode`로 돌리고 싶으면 하단의 링크를 참조해서 환경을 세팅해 주세요.  
[참고링크](https://code.visualstudio.com/docs/python/jupyter-support)  

## 3. Iris Dataset
현대 통계학의 기초를 쌓았다고 알려진 통계학자인 [로널드 피셔](https://ko.wikipedia.org/wiki/%EB%A1%9C%EB%84%90%EB%93%9C_%ED%94%BC%EC%85%94)가 소개한 데이터입니다.   
붓꽃의 여러 특징들을 정리해둔 데이터셋입니다. 이 데이터셋에는 세가지 품종에 대해 정리가 되어있습니다.  

여담이지만 저는 이 문서를 만들기 전까지 붓꽃 품종이 이렇게 다양한지 몰랐습니다.   
![image](https://user-images.githubusercontent.com/15958325/56006054-5cd68a00-5d0e-11e9-8970-3cfb36cbdef7.png)  
요 사진처럼 생긴 꽃만 붓꽃인줄 알았더니 아래 사진처럼 정말 여러 종류의 붓꽃이 있다는것을 알게되었습니다.  
![image](https://user-images.githubusercontent.com/15958325/56006198-e5552a80-5d0e-11e9-9533-acf14a910fdf.png)

Iris dataset에는 총 세가지 품종의 붓꽃의 데이터가 저장되어 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/56006707-f69f3680-5d10-11e9-8609-25ba5034607e.png)  
순서대로 꽃창포, 부채붓꽃, Iris Virginica(한글이름 못찾음)입니다.  
흘깃 봐서는 비전문가인 저로써는 도저히 구분을 할 수가 없습니다. 구분하는 방법중 하나는 꽃받침(sepal)과 꽃잎(petal)의 길이와 너비를 비교하는 것이라고 합니다.  

150가지의 붓꽃의 꽃받침, 꽃잎, 품종을 담은 데이터셋을 가지고 비전문가인 저도 이 붓꽃은 부채붓꽃이야! 라고 할수있도록 모델을 만들어보겠습니다.  

데이터셋에 담긴 항목은 다음과 같습니다.  

컬럼명|의미
------|------
Id|번호
SepalLengthCm|꽃받침의 길이(cm)
SepalWidthCm|꽃받침의 너비(cm)
PetalLengthCm|꽃잎의 길이(cm)
PetalWidthCm|꽃잎의 너비(cm)
Species|붓꽃의 종. setosa, versicolor, virginica 세 가지 값 중 하나

## 4. Softmax
트레이닝을 시키기 전에 우리가 어떤 알고리즘으로 데이터를 분류해낼건지에 대해 알아보겠습니다.  

먼저 다음그래프를 봐주세요.  
![image](https://user-images.githubusercontent.com/15958325/56012894-60c3d580-5d29-11e9-8afc-091f004befef.png)  
(노랑+노랑아님) + (빨강+빨강아님) + (파랑+파랑아님) 이렇게 세가지의 binomial classification으로 표현될 수 있습니다.  
분류될 수 있는 class는 노랑, 빨강, 파랑이고 어떤값이든 노랑아니면 빨강아니면 파랑에 속하게 됩니다.  

각 class를 붓꽃의 품종이라고 생각을 해봅시다.  
어떤 붓꽃의 잎의 너비와 길이, 꽃받침의 너비와 길이가 input값으로 주어지면 그 데이터로 어떤 class에 속하게 되는지 분류해야 합니다.  

### Softmax 
input 데이터를 X라고 합시다.  
X라는 데이터가 들어올 때 어떤 품종이 될지 분류를 해주는 Classifier를 거치게됩니다. Classifier에 의해 세워진 회귀식(대략 Y=wX+b)에 대입되게 되고 출력값 Y가 나올것입니다.  
![image](https://user-images.githubusercontent.com/15958325/56019233-15b4bd00-5d3f-11e9-9631-1fef6cf038d1.png) 

나온 출력값을 0과 1사이로 바꿔주면서 각 출력값을 모두 더했을때 1이 되게 하는것이 softmax 알고리즘입니다.  
아래 사진을 보면 각 출력값들을 다 더했을때 1이 되는것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/56019540-dcc91800-5d3f-11e9-868d-5fc91676b8ff.png)  

이렇게 되면 출력값은 1이하의 소숫점이고, 전체 출력값의 합은 총합이 1이 되므로 출력을 "확률"로 해석할 수 있고 문제를 통계적으로 대응할 수 있게 됩니다.  

또한 softmax를 적용한 뒤에도 숫자로 지정된 데이터들의 대소관계로 계산량의증가, 오류를 방지하기 위해 `one-hot-encoding`을 적용해줍니다.  

`one-hot-encoding`이란 몇가지로 분류할 수 있는 데이터들 중 가장 큰 값을 만들고 나머지를 0으로 만드는 것을 말합니다.  
![image](https://user-images.githubusercontent.com/15958325/56019890-cbccd680-5d40-11e9-8982-4c040a8105b3.png)  


### cross-entropy

여기까지가 Hypothesis를 예측하는 모델을 살펴본 것입니다. 이제 이것을 이용해 실제값에서 예측값을 뺀 값, 비용(cost)를 측정해야 합니다. 이후 이 cost값을 최소화시키는 방향으로 학습을 계속하게 됩니다.  

softmax에서는 cost함수로 `cross-entropy`를 사용합니다.  
`cross-entropy`는 맞추면 0에 가까워지고 틀리면 무한대에 가까운 수가 됩니다.  

예를들어서 자세히 살펴봅시다.  

>class|value
>-----|------
>A|[1,0]
>B|[0,1]  

A인지 B인지 맞추는 모델을 만들었다고 합시다.  

실제값 : A([1,0])  
예측1 : [1,0]  ->A(o)       
예측2 : [0,1]  ->B(x)   

실제값이 A일때 예측1은 제대로 맞췄지만 예측2는 제대로 맞추지 못했습니다.    

아래 그래프는 밑이 자연로그e인 -log(x)의 그래프입니다. 0으로갈수록 무한대에 가깝고 1로갈수록 0에 가까워진다는 것을 알수있습니다. `cross-entropy`는 이 그래프를 기반으로 계산을 하니 잘 봐두시기 바랍니다.  
![image](https://user-images.githubusercontent.com/15958325/56021159-b3aa8680-5d43-11e9-9f32-d9952d5b2a0c.png)  

![image](https://user-images.githubusercontent.com/15958325/56021966-a8f0f100-5d45-11e9-9284-40da1cfc24ca.png)  
예측1은 cost가 0이나왔지만 예측2는 무한대에 가깝게 수렴됩니다.  

~~~
C(H(x),y) = ylog(H(x)) - (1-y)log(1-H(x))  
~~~
위처럼 표현될 수 있고 여러번 학습하여 전체cost를 합해 평균을 구합니다.  
마지막으로 `Gradient descent` 알고리즘을 사용하여 cost를 최소로 만들면 우리가 원하는 모델을 얻을 수 있습니다.  

## 5. Develop Code

이제 이 과정들을 소스코드로 봅시다!  

~~~py
#%%
import tensorflow as tf 
import pandas as pd 

#데이터 불러옴
iris_data = pd.read_csv("C:\\Users\\SeungYeonLee\\Documents\\GitHub\\GRuuuuu.github.io\\assets\\resources\\simple-tutorial\\ML03\\data\\Iris.csv")
iris_data.head()

#품종 column을 one-hot-encode
iris_data_one_hot_encoded = pd.get_dummies(iris_data)
iris_data_one_hot_encoded.head()

#전체 데이터를 80%은 트레이닝 20% 테스트로 쪼갬
iris_train_data = iris_data_one_hot_encoded.sample(frac=0.8, random_state=200)
iris_test_data = iris_data_one_hot_encoded.drop(iris_train_data.index)

#input은 꽃잎의 너비와길이, 꽃받침의 너비와길이
#output은 세개중 하나로
iris_train_input_data = iris_train_data.filter(['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'])
iris_train_label_data = iris_train_data.filter(['Species_Iris-setosa', 'Species_Iris-versicolor', 'Species_Iris-virginica'])

#x는 input값을 위한 placeholder
#w는 가중치
#b는 편차
#y는 트레이닝해서 나온 결과(가설)
#y_는 진짜 결과값
x = tf.placeholder(tf.float32,[None, 4])
W = tf.Variable(tf.zeros([4, 3]))
b = tf.Variable(tf.zeros([3]))
y = tf.nn.softmax(tf.matmul(x, W) + b)
y_ = tf.placeholder(tf.float32, [None, 3])

#cross_entropy를 cost함수로
cross_entropy = tf.reduce_mean(-tf.reduce_sum(y_ * tf.log(y), reduction_indices=[1]))

#cost를 최소화
train_step = tf.train.GradientDescentOptimizer(0.05).minimize(cross_entropy)

sess = tf.InteractiveSession()

#1000번학습
tf.global_variables_initializer().run()
for _ in range(1000):
    #Usually send batches to the training step. But since the dataset is small sending all
    sess.run(train_step, feed_dict={x: iris_train_input_data, y_: iris_train_label_data})

correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))

#정확도
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

print('Accuracy : ', sess.run(accuracy, feed_dict={x: iris_test_input_data, y_: iris_test_label_data}))
~~~

결과는 다음과 같이 나오게 됩니다.  
~~~
Accuracy :  0.96666664
~~~  

끝!


----