---
title: "AttrValue must not have reference type value of float_ref for attr 'tensor_type'"
categories: 
  - ERROR
tags:
  - GPU
  - ML
last_modified_at: 2019-10-10T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---


## Environment
`Arch : ppc64le(Power9)`   
`OS : RHEL 7.6`   
`CUDA : v10.1`   
`GPU : Tesla V100-SXM2-16GB`

## Purpose
keras코드를 multigpu로 돌리고자 함

## Problem

주 코드는 다음과 같다.  
~~~python
# 앞 코드 생략
...

# GPU옵션 (1번 2번 gpu만 사용, 메모리는 50%만 사용)
from keras.backend import tensorflow_backend as K
gpu_options = tf.GPUOptions(visible_device_list="1,2", per_process_gpu_memory_fraction=0.5)
config = tf.ConfigProto(gpu_options=gpu_options)
config.gpu_options.allow_growth = False
config.allow_soft_placement=True
config.log_device_placement=False
print('Set Session...')
K.set_session(tf.Session(config=config))

# 모델
model = Sequential()
model.add(Embedding(max_features, 128, input_length=maxlen))
model.add(LSTM(64))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

# multi gpu 설정 (gpu는 2개만 사용)
model = multi_gpu_model(model, gpus=2)

# Compile과 Training
print('Compile...')
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print('Train...')
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=1000,
          validation_data=[x_test, y_test])

~~~  


## ERROR

에러발생
~~~
...

Compile...
Train...
Train on 25000 samples, validate on 25000 samples
Epoch 1/10
2019-10-10 15:28:19.501873: E tensorflow/core/framework/op_segment.cc:53] Create kernel failed: Invalid argument: AttrValue must not have reference type value of float_ref
         for attr 'tensor_type'
; NodeDef: embedding_1/embeddings/_207 = _Recv[_start_time=0, client_terminated=false, recv_device="/job:localhost/replica:0/task:0/device:GPU:1", send_device="/job:localhost/replica:0/task:0/device:GPU:0", send_device_incarnation=1, tensor_name="edge_1153_embedding_1/embeddings", tensor_type=DT_FLOAT_REF, _device="/job:localhost/replica:0/task:0/device:GPU:1"](^training/Adam/sub_4/_209); Op<name=_Recv; signature= -> tensor:tensor_type; attr=tensor_type:type; attr=tensor_name:string; attr=send_device:string; attr=send_device_incarnation:int; attr=recv_device:string; attr=client_terminated:bool,default=false; is_stateful=true>
~~~

# Solution

## Caused by : 잘모르겠다
아무리 찾아도 모르겠다.  

## How to solve?
아무것도 안건들이고 모델 생성코드에 다음 라인만 추가  

~~~python
#cpu:0추가
with tf.device('/cpu:0'):
  model = Sequential()
  model.add(Embedding(max_features, 128, input_length=maxlen))
  model.add(LSTM(64))
  model.add(Dropout(0.5))
  model.add(Dense(1, activation='sigmoid'))
~~~

![image](https://user-images.githubusercontent.com/15958325/66548881-12c74780-eb7d-11e9-85dd-73db2926c80b.png)  

잘된다!  

----
