---
title: "호다닥 공부해보는 RNN 친구들(1) - RNN(Recurrent Neural Networks)"
slug: lstm-doc
tags:
  - ML
  - RNN
  - LSTM
  - GRU
date: 2019-09-23T13:00:00+09:00
---

## Overview
호다닥 공부해보는 시리즈가 2편째가 되었습니다. 이번에는 머신러닝의 꽃이라고도 불리는 `RNN`을 들고 왔습니다. 다음 포스팅에서는 `RNN`친구들인 `LSTM`과 `GRU`도 소개하도록 하겠습니다.  

# RNN?
## Concept
`RNN`은 그 이름에서 알 수 있듯이, **Recurrent**한 모델입니다.   
다시말하면, input->`RNN`->output->input->`RNN`->output....이러한 구조가 계속 반복되는 모델입니다.  
생긴게 1자로 쭉 이어져서 **sequence**한 모델이라고도 합니다.  
아래 사진은 위에서 언급한 RNN의 성질을 표현한 그림입니다.  

![1](https://user-images.githubusercontent.com/15958325/65409665-3f602d00-de23-11e9-8185-01c7082ec6de.png)  

![image](https://user-images.githubusercontent.com/15958325/65409847-c1505600-de23-11e9-9389-60843b383748.png)  

A의 꼬부랑선은 단순히 아래 그림처럼 반복된다는 것을 표현한 선입니다.  

이전 단계에서의 **결과**가 다음단계의 **입력**이 되는 순환적인 구조를 띄고 있기에 RNN은 **연속적인 이벤트**, 또는 **자연어 처리 용도**로 사용되어 왔습니다.    

연속적인 이벤트 :  
![recursive](https://user-images.githubusercontent.com/15958325/65613449-0a093a00-dff1-11e9-9916-7354c15e3ca0.png)   

자연어 처리 :  
![text](https://user-images.githubusercontent.com/15958325/65613448-0a093a00-dff1-11e9-842d-1a921bf07caf.png)   

> 이전단계의 결과를 다음 단계의 입력으로 사용하는 순환적인 구조는, 과거의 일을 토대로 미래를 예측할 수 있게 해줍니다.   

## Deep Dive
그럼 지금부터는 수식을 통해 `RNN`을 좀 더 자세히 알아보겠습니다.  

위의 그림에 수식에 필요한 변수들을 적어둔 그림입니다.  

<center><img src="https://user-images.githubusercontent.com/15958325/65486512-9a575a00-dedf-11e9-8a6f-17bb29672ec5.png"></center>  

한눈에 봐서는 선뜻 이해가 가지 않을 것입니다. 지금부터는 해당 그림을 차근차근 설명하도록 하겠습니다.  

### 알아두어야 할 정보
`RNN`은 앞서 말씀드렸듯이 **Recurrent**한 모델입니다. 그렇기 때문에 Input값(X)과 hidden state(h), Output(Y)값을 제외하고는 모든 변수가 같습니다.  
하나의 `RNN`모델에서 각 값을 위한 **가중치값(W)**, **활성화함수(f)**는 변하지 않습니다.  

또한 이 예제에서 bias(b)값은 제외하고 설명하겠습니다.  

### Input(Initial)
`RNN`에서의 **Input**은 이전 state의 정보를 포함하고 있기 때문에 이전 state의 hidden state값이 반드시 필요합니다.  
하지만 이번 단계에서는 이해하기 쉽게 초기상태라고 가정해봅시다.  

> **hidden state** : 시간 t일때의 상태. output과 같다고 생각할 수 있지만 hidden state를 용도에 맞게 정제한 결과가 output이라고 생각하면 됨.

초기상태에서는 이전 state의 hidden state값이 없으니 들어온 Input만으로 처리해야 합니다.  

<center><img src="https://user-images.githubusercontent.com/15958325/65488778-ca552c00-dee4-11e9-933b-80b63b305e3b.png"></center>  

초기 상태의 Input값은 `X0`이라고 정의하고 Input값을 위한 가중치를 `Wx`라고 했을때 각 변수를 곱하고 활성화 함수 f를 적용한 값이 **hidden state**가 됩니다.  


### Activation Function

앞선 과정에서 "활성화 함수 f"를 적용한다고 했습니다.  
`RNN`에서 주로 사용하는 활성화함수는 비선형 함수인 Sigmoid, tanh가 있습니다.  

여기서 잠시 이런 의문이 드실 수도 있습니다. 
> relu도 비선형함수 아닌가? sigmoid나 tanh보다 성능이 좋다고 들었던 것 같은데...  

네, relu도 비선형함수입니다. 하지만 relu의 그래프의 모양을 잘 기억해 봅시다.  

![image](https://user-images.githubusercontent.com/15958325/65489394-0046e000-dee6-11e9-9284-39c2ead442b9.png)   

위 사진을 참고해서 보면 Sigmoid와 tanh는 값들이 **-1~1**사이에 분포해있습니다. (Sigmoid는 **0~1**)  
반면에 relu는 x축이 양수가 되는 지점에서 y=x그래프의 형상을 보이고 있습니다.  

`RNN`계열은 계속 같은 레이어를 **여러번 반복**하는 성질을 가지고 있기 때문에 1보다 큰 값이 들어오게 되면 반복하면서 값이 너무 커질 수 있습니다.  

예를 들어 1.1의 100승을 생각해봅시다. 1보다 고작 0.1밖에 크지 않지만 13,780.6123398...이라는 어마어마한 값이 나오게 됩니다.  

그래서 RNN 내부에서는 relu가 아닌 Sigmoid나 tanh를 사용합니다.  

물론 RNN외부에서는 relu가 더 좋은 성능을 발휘하겠죠  

### Input(next state)
t=0에서의 hidden state도 구했으니 다음 state로 넘어가봅시다.   

![rnn2](https://user-images.githubusercontent.com/15958325/65490994-24f08700-dee9-11e9-9829-beb92912cdc7.png)

초기상태의 Input 계산과 똑같습니다. 달라진건 0번째 hidden state의 계산이 추가된 것 뿐입니다.  

정리하면:  
0번째 hidden state와 그 가중치의 곱 + 1번째 Input값과 그 가중치의 곱 = 1번째 hidden state  
가 되겠습니다.  

이와같이 각 hidden state는 이전 state들의 정보를 모두 포함하고 있습니다. 이러한 특징때문에 연속적인 이벤트처리나 자연어 처리같은 곳에 쓰이게 됩니다.  

### Output
hidden state가 Output아니냐! 할 수 있지만 저 위의 식을 보세요. 과연 hidden state가 유저가 원하는 결과를 보여줄 수 있을까요? 아마 한번보고는 이해할 수 없는 숫자일 것입니다.  

예를 들어서 이진 분류를 해야하는 경우라면 `Sigmoid`함수를 사용할 수 있고 다양한 카테고리 중에서 선택해야하는 문제라면 `Softmax`함수를 사용하게 될 것입니다.  

요번 예제에서는 softmax를 사용한 분류를 살펴봅시다.  
![rnn3](https://user-images.githubusercontent.com/15958325/65494655-2e312200-def0-11e9-8b9a-fb7b2b9f9ca2.png)  

1번 상태에서의 hidden state값에 가중치 Wy(이 값에 따라 벡터의 크기가 결정됩니다.)를 곱한 값이 초기 출력값 Y1입니다.  

그 다음 one-hot-encoding을 해 주면 쉽게 분류할 수 있습니다.  


### Generalization

위의 과정들을 일반화 시키면 다음과 같은 식을 얻을 수 있습니다.  

(단계t일때,)  
**hidden state(h)**  
![image](https://user-images.githubusercontent.com/15958325/65610817-d5937f00-dfec-11e9-8d89-be41e35127c1.png)  

**output(y)**  
![image](https://user-images.githubusercontent.com/15958325/65610944-1095b280-dfed-11e9-9b7c-675e63f6a202.png)  


## Code (Keras)

다음 코드는 Keras로 구현된 가장 기본적인 RNN layer입니다.  
~~~python
model.add(SimpleRNN(hidden_size, input_shape=(timesteps, input_dim)))
~~~  
>Keras Doc : [SimpleRNN](https://keras.io/layers/recurrent/#simplernn)  

`hidden_size` : 다음 step의 input으로 보낼 데이터의 크기, `units`이라고도함.  
`timesteps(=input_length)` : step의 수  
`input_dim` : input 데이터의 크기  

다음 예제코드를 보겠습니다.  
~~~python
from keras.models import Sequential
from keras.layers import SimpleRNN

model = Sequential()
model.add(SimpleRNN(3, input_shape=(2,5)))
model.summary()
~~~
~~~python
###########################################
# output : model summary
###########################################

Model: "sequential_1"
_________________________________________________________________
Layer (type)                 Output Shape              Param #   
=================================================================
simple_rnn_1 (SimpleRNN)    (None, 3)                 27        
=================================================================
Total params: 27
Trainable params: 27
Non-trainable params: 0
~~~


한눈에 보는 그림 :  
![rnn4](https://user-images.githubusercontent.com/15958325/66182220-25d6a500-e6af-11e9-9ab4-157ceea82ad3.png)  

`hidden_size`=3  : output_dim의 크기  
`timesteps(=input_length)`=2 : step의 수는 2  
`input_dim`=5 : input 데이터의 크기는 5, 고로 input의 가중치W는 (input_dim, hidden_size)의 행렬  

# Bidirectional RNN
## Concept
양방향 순환 신경망(Bidirectional RNN)은 과거의 정보만 활용하던 기존의 RNN과 달리 **미래의 정보**까지 활용하는 RNN입니다.  

예를 들어, 다음과 같은 문장을 봅시다.   
> "오늘 엄청 맛있는 고기를 먹었는데 기분이 _____, 아니 글쎄 고기가 상해서 병원에 갔지 뭐야"  
> 1. 좋았어
> 2. 나빴어

이 문장에서 빈칸에 들어갈 단어를 과거의 문장만 보고서는 제대로 맞출 수 있을까요?   

**빈 칸 이전의 문장**은 맛있는 고기를 먹었다는 정보밖에 없기 때문에 긍정적인 답을 생각할 수 있겠지만, **빈 칸 이후의 문장**은 상한 고기를 먹고 병원에 갔다는 내용이기 때문에 결국 빈 칸에는 부정적인 답이 오게 됩니다.  

이와 같이 과거의 정보만으로는 제대로 예측할 수 없는 상황이 있기 때문에 미래의 정보도 활용하도록 고안된 RNN이 `Bidirectional RNN`입니다.  


![image](https://user-images.githubusercontent.com/15958325/66189726-62ad9680-e6c5-11e9-800e-75ab3a7aecf6.png)

A는 정방향(과거->미래)으로 진행되는 보통의 RNN계산과 같음.  
A'는 역방향(미래->과거)로 진행되며 계산 자체는 보통 RNN과 같다.(반대로 이뤄질 뿐)  

t시점의 결과값은 hidden layer h(t)와 h'(t)의 concatinate를 통해 얻을 수 있다.  

>수식 :  
>![image](https://user-images.githubusercontent.com/15958325/66190854-eff1ea80-e6c7-11e9-83c2-40161d82487f.png)


# 한줄요약
`Simple RNN`은 과거의 정보만을 사용, `Bidirectional RNN`은 과거와 미래 두개의 정보를 사용하여 학습한다!  

----