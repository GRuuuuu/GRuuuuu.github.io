---
title: "호다닥 공부해보는 CNN(Convolutional Neural Networks)"
slug: cnn-doc
tags:
  - ML
  - CNN
date: 2019-06-03T13:00:00+09:00
---

## CNN?
`CNN`은 이미지를 인식하기위해 패턴을 찾는데 특히 유용합니다. 데이터에서 직접 학습하고 패턴을 사용해 이미지를 분류합니다. 즉, 특징을 수동으로 추출할 필요가 없습니다.  
이러한 장점때문에 자율주행자동차, 얼굴인식과 같은 객체인식이나 computer vision이 필요한 분야에 많이 사용되고 있습니다.  

## CNN이 유용한 이유? 
`CNN`이 나오기 이전, 이미지 인식은 2차원으로 된 이미지(채널까지 포함해서 3차원)를 1차원배열로 바꾼 뒤 `FC(Fully Connected)`신경망으로 학습시키는 방법이었습니다.  

> ![image](https://user-images.githubusercontent.com/15958325/58844125-bde86180-86b0-11e9-8d58-5d068c26233e.png)    
>
>위와 같이 이미지의 형상은 고려하지 않고, raw data를 직접 처리하기 때문에 많은 양의 학습데이터가 필요하고 학습시간이 길어집니다.  
>
>또한 이미지가 회전하거나 움직이면 새로운 입력으로 데이터를 처리해줘야 합니다. 이미지의 특성을 이해하지 못하고 단순 1D데이터로 보고 학습을하는것이 특징입니다.  

이러한 방법은 이미지 데이터를 평면화 시키는 과정에서 공간정보가 손실될 수밖에 없습니다. 즉, 신경망이 특징을 추출하고 학습하는데 있어 비효율적이고 정확도를 높이는데 한계가 있게됩니다.  

이런 단점을 보완하여 **이미지의 공간정보를 유지한채 학습**을 하게하는 모델이 `CNN`입니다.  

## 그래서 어떻게 돌아가는거지?
`CNN`의 가장 핵심적인 개념은 이미지의 공간정보를 유지한채 학습을 한다는 것입니다.  
 
용어를 설명하면서 CNN의 구성요소들이 어떻게 동작하는지 알아보겠습니다.    

### 1-1 Convolution

`Convolution`의 사전적 정의는 합성곱입니다. 단순히 이렇게만들으면 의미를 잘 이해하지 못할수 있는데 알고보면 이 알고리즘을 가장 잘 표현한 용어같습니다.  

사실 `Convolution`은 처음 등장한 개념이 아니라 `CNN`이 등장하기 한참 전부터 이미지처리에서 사용되었던 개념입니다.  

그림으로 보자면 다음과 같습니다.  
![Convolution_schematic](https://user-images.githubusercontent.com/15958325/58780750-defb7480-8614-11e9-943c-4d44a9d1efc4.gif)    

위 gif의 첫번째 단계를 그림으로 보면 다음과 같습니다.  
![Picture3](https://user-images.githubusercontent.com/15958325/58845860-ca23ed00-86b7-11e9-805f-ef5c8adcab9f.png)    
빨간 박스는 필터가 적용될 영역이고 개발자의 임의로 gif처럼 한칸씩 이동시키면서 적용시킬건지, 두칸씩 이동할건지 정할 수 있습니다.(이 값을 `stride`라고 합니다.)  

이를 통해 이미지의 `feature map`을 만들 수 있습니다. `filter`(또는 `kernel`)의 구성에 따라 이미지의 특징을 뽑을수있습니다.  
### 1-2 Filter(Kernel)
Filter라는걸 통해서 어떻게 이미지의 feature를 뽑을 수 있는지 예시를 통해 보겠습니다.  

이미지처리에서 자주 등장하는 `sobel filter`는 이미지의 가로세로 feature를 뽑아낼 수 있는 필터입니다.  
필터를 보면 이런 값을 가지고 있습니다.     
![Picture5](https://user-images.githubusercontent.com/15958325/98335704-cd5b9f00-2048-11eb-8d3d-d3490e17cf46.PNG)  
  

![image](https://user-images.githubusercontent.com/15958325/58784251-ed01c300-861d-11e9-9e6f-9b30bb1d5d7a.png)    
(원본이미지)  

원본 이미지에 위 필터를 차례대로 적용시키면 다음과 같은 결과를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/58784105-97c5b180-861d-11e9-8b25-deab83350d99.png)    
(왼쪽: `sobel-x`적용, 오른쪽: `sobel-y`적용)  
각 이미지의 특징을 보니 왼쪽은 세로선이 detect되고 오른쪽은 가로선이 detect된 것을 확인할 수 있습니다.  

이 둘을 합치면 아래와 같이 원본사진의 feature를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/58784450-6b5e6500-861e-11e9-8a2a-55bb0f2a9c44.png)     

이와 같이 `CNN`에서도 여러개 필터를 이용해 이미지의 세부 특징을 추출해서 학습을 할 수 있습니다.  

위와같은 이미지 처리에서는 sobel필터와같이 유명한 필터들을 직접 사용자가 찾아서 사용해야했지만, **`CNN`은 신경망에서 학습을 통해 자동으로 적합한 필터를 생성해 준다는 것**이 특이사항 입니다.  

### 1-3 Channel  
여기서 잠깐! 우리가 보통 생각하는 color이미지는 red채널, blue채널, green채널이 합쳐진 이미지입니다.  
즉, 하나의 color이미지는 3개의 채널로 구성되어 있다는 것!  

![image](https://user-images.githubusercontent.com/15958325/58785285-3c48f300-8620-11e9-926a-04c90ef88750.png)  

보통은 연산량을 줄이기 위해(오차를 줄이기 위해) 전처리에서 이미지를 흑백(Channel:1)으로 만들어 처리합니다.  

흑백 이미지의 경우 다음 그림과 같이 처리됩니다.  
![Picture4](https://user-images.githubusercontent.com/15958325/58845636-d8253e00-86b6-11e9-80a7-cdbc61739b6f.png)  
  

만약 color이미지(Multi Channel)를 그대로 처리한다면 다음 그림과 같이 처리됩니다.  

![Picture1](https://user-images.githubusercontent.com/15958325/58845631-d5c2e400-86b6-11e9-87ae-3e82cd8da0c0.png)  

Multi Channel CNN에서 주의해서 보아야 할 점은 이렇습니다. 
- input data의 channel수와 filter의 channel수는 같아야 함  (예를들어 그림처럼 3ch가 input이라면 filter도 3channel)  
- input data의 channel의 수와 관계없이 filter의 개수만큼 output데이터가 나옴  

### 1-4 Padding

[1-1 Convolution](#1-1-convolution) 파트를 잠시 떠올려봅시다.  
![Picture6](https://user-images.githubusercontent.com/15958325/58845937-20912b80-86b8-11e9-8aaa-92fdaa3bbf10.png)   

`Convolution` 레이어에서는 Filter와 Stride의 작용으로 `Feature map`의 크기는 입력데이터보다 작습니다.  
>Stride : Filter를 몇 칸 이동할건지 정함    

이렇게 입력데이터보다 출력데이터가 작아지는것을 방지하는 방법이 `Padding`입니다.  

![Picture7](https://user-images.githubusercontent.com/15958325/58846398-ff313f00-86b9-11e9-8268-7989df7d38f2.png)  
위와 같이 0으로 둘러싸는 `padding`을 `zero padding`이라고 부릅니다. 단순히 0을 덧붙였으므로 특징이나 분해능에는 영향을 미치지 않습니다.  

이렇게 `padding`을 하게 되면 `convolution`을 해도 크기가 작아지지 않습니다.  

`Padding`에는 두가지 옵션이 있습니다.  
- **valid** : padding 0을 뜻합니다. 즉 입력보다 출력의 크기가 **작아집니다.**  
- **same** : padding이 존재하여 입력과 출력의 크기는 **같습니다.**  

### 1-5 Pooling
이미지의 크기를 계속 유지한 채 `FC(Fully Connected)`레이어로 가게 된다면 연산량이 기하급수적으로 늘것입니다.  

**적당히 크기도 줄이고, 특정 feature를 강조**할 수 있어야 하는데 그 역할을 `Pooling` 레이어에서 하게 됩니다.  

처리방법은 총 세가지가 있습니다.   
- **Max Pooling**
- Average Pooling
- Min Pooling  

>CNN에서는 주로 **Max Pooling**사용.  
>이는 뉴런이 가장 큰 신호에 반응하는것과 유사하다고 합니다.  
>이렇게 하면 노이즈가 감소하고 속도가 빨라지며 영상의 분별력이 좋아진다고 합니다.

![Picture8](https://user-images.githubusercontent.com/15958325/58851117-60620e00-86cc-11e9-9b68-ce400aa93de0.png)  
최댓값을 구하거나 평균을 구하는방식으로 동작합니다. 일반적으로 pooling의 크기와 stride의 크기를 같게 설정하여 모든 원소가 한번씩은 처리가 되도록 설정합니다.  

특징은 다음과 같습니다.
- 학습대상 파라미터가 없음  
- Pooling레이어를 통과하면 행렬의 크기가 감소함
- Pooling레이어를 통과해도 채널의 수는 변경없음  


## 전체 구조는?  
지금까지 CNN의 구성 요소들을 살펴보았습니다. 이제부터는 전체적인 그림을 보도록 하겠습니다.  

![image](https://user-images.githubusercontent.com/15958325/58851737-d9fafb80-86ce-11e9-8119-11876bc9e86c.png)  

`Input` : 이미지  

**특징 추출 단계(Feature Extraction)**  
- `Convolution Layer` : 필터를 통해 이미지의 특징을 추출.  
- `Pooling Layer` : 특징을 강화시키고 이미지의 크기를 줄임.  
(Convolution과 Pooling을 반복하면서 이미지의 feature를 추출)   

**이미지 분류 단계(Classification)**  
- `Flatten Layer` : 데이터 타입을 FC네트워크 형태로 변경. 입력데이터의 shape 변경만 수행.  
- `Softmax Layer` : Classification수행.  

`Output` : 인식결과  

## 파라미터는 어떻게 설정해야할까?
CNN의 파라미터로는 
- `Convolution Filter`의 개수  
- `Filter`의 사이즈
- `Padding`여부
- `Stride`  

이렇게 있습니다.   

### Convolution Filter의 개수
각 Layer에서의 연산시간/량을 비교적 일정하게 유지하며 시스템의 균형을 맞추는 것이 좋습니다.  
보통 `Pooling Layer`를 거치면 **1/4**로 출력이 줄어들기 때문에 `Convolution Layer`의 결과인 `Feature Map`의 개수를 **4배**정도 증가시키면 됩니다.  

### Filter 사이즈
작은 필터를 여러개 중첩하면 원하는 특징을 더 돋보이게하면서 연산량을 줄일 수 있습니다.  
요즘 대부분의 `CNN`은 3x3 size를 중첩해서 사용한다고 합니다.  

### Padding 여부
`Padding`은 `Convolution`을 수행하기 전, 입력 데이터 주변을 특정 픽셀 값으로 채워 늘리는 것입니다.  
`Padding`을 사용하게 되면 입력 이미지의 크기를 줄이지 않을 수 있습니다.  

### Stride
`Stride`는 `Filter`의 이동 간격을 조절하는 파라미터 입니다.  
이 값이 커지게 되면 결과 데이터의 사이즈가 작아지게 됩니다.  

>참고 : [link](http://blog.naver.com/PostView.nhn?blogId=laonple&logNo=221193389981&parentCategoryNo=&categoryNo=37&viewDate=&isShowPopularPosts=true&from=search)  

## 한줄요약
CNN은 `Convolution`과 `Pooling`을 반복적으로 사용하면서 불변하는 특징을 찾고, 그 특징을 입력데이터로 Fully-connected 신경망에 보내 `Classification`을 수행합니다.  

----