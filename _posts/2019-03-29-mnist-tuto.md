---
title: "Build a TensorFlow model using Watson ML CLI Tutorial"
categories: 
  - Simple-Tutorial
tags:
  - ML
  - ICOS
  - Watson
  - Cloud
last_modified_at: 2019-03-29T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
최근 ML(Machine Learning)에 대한 관심이 높아지면서 너도나도 ML에 발을 담그고 있습니다. 하지만 ML은 매우 많은 연산량을 요구하고 보통의 컴퓨터로는 결과를 내려면 굉장히 많은 시간이 소요됩니다.  
이번 문서에서는 IBM Cloud와 IBM Watson Studio를 통해 빠르고 쉽게 모델을 training 시키고, deploy하는 과정을 진행하겠습니다.  

[CLI tutorial: Build a TensorFlow model to recognize handwritten digits using the MNIST data set](https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/ml_dlaas_tutorial_tensorflow_cli.html?linkInPage=true#step3)을 직접 해보고 작성한 튜토리얼입니다.

## 2. Prerequisites
`IBM Cloud`와 `IBM Watson`계정을 만들어주세요.  
`IBM Cloud` : [link](https://console.bluemix.net)  
`IBM Watson` : [link](https://dataplatform.cloud.ibm.com/) 

## 3. Set up Cloud, ML plugin
### IBM Cloud CLI 설치

현재 사용하고 있는 os에 맞는 cli를 설치합니다.  
link : [https://console.bluemix.net/docs/cli/reference/ibmcloud/download_cli.html#install_use](https://console.bluemix.net/docs/cli/reference/ibmcloud/download_cli.html#install_use)  

설치가 끝난다면 터미널을 열어서 로그인을 진행합니다.  
~~~bash
$ ibmcloud login --sso
~~~  
![image](https://user-images.githubusercontent.com/15958325/55232302-64a32280-5268-11e9-9a6b-e07a25de99aa.png)  
![image](https://user-images.githubusercontent.com/15958325/55232352-8ef4e000-5268-11e9-9a9a-9aea5c238d85.png)  
>이 문서에서 지역은 `us-south`로 통일하도록 하겠습니다.   

### Install ML plugin

그 다음으로 ML 플러그인을 설치해줍니다.  
~~~bash
$ bx plugin install machine-learning
~~~
![image](https://user-images.githubusercontent.com/15958325/55232365-9c11cf00-5268-11e9-8d34-20a95e51ec2c.png)  
이제 플러그인에서 사용할 환경변수를 세팅해주어야합니다.  

[Watson Studio](https://dataplatform.cloud.ibm.com/)로 이동하여 Services > Watson Service에서 ML서비스를 생성합니다.  

생성한 ML서비스를 선택하고, 서비스 인증정보 탭을 들어가서 credential정보를 추가합니다. 각 항목에 들어가는 정보는 다음 사진과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/55232892-2eff3900-526a-11e9-9e04-14b5c4192e91.png)  

credential 정보를 생성하면 json형식의 데이터를 확인할 수 있습니다.  

그다음 터미널을 열어서 환경변수를 세팅해 줍니다.   

| 환경변수 | credentials info |  
|----|----|  
| ML_ENV | url |  
| ML_USERNAME | username |   
| ML_PASSWORD | password |  
| ML_INSTANCE | instance_id |  

window의 경우  
~~~bash
set ML_ENV= https://us-south.ml.cloud.ibm.com
set ML_USERNAME=xxx-xxx-xxx-xxx-xxx 
set ML_PASSWORD=xxx-xxx-xxx-xxx-xxx 
set ML_INSTANCE=xxx-xxx-xxx-xxx-xxx 
~~~

linux와 macOS의 경우
~~~bash
export ML_ENV= https://us-south.ml.cloud.ibm.com
export ML_USERNAME=xxx-xxx-xxx-xxx-xxx  
export ML_PASSWORD=xxx-xxx-xxx-xxx-xxx  
export ML_INSTANCE=xxx-xxx-xxx-xxx-xxx 
~~~

### Test

제대로 설치가 되었는지 확인해보겠습니다.  

~~~bash
$ bx login --sso 
$ bx ml version
~~~
![image](https://user-images.githubusercontent.com/15958325/55233276-6c17fb00-526b-11e9-81db-0315d688a40c.png)  

>[INFO] 윈도우10의 cmd창으로 이 명령어를 실행하니 일부 화면이 제대로 보이지 않는 오류가 있었습니다.  
>저는 cmd창말고 <b>git bash</b>를 깔아서 진행하였습니다.  


## 4. Set up Cloud Object Storage

### Cloud Object Storage
먼저 cloud object storage(이하 cos) 서비스를 추가시켜야 합니다.  
[Watson Studio](https://dataplatform.cloud.ibm.com/)로 이동하여 Services > Data Services > Add Service 로 이동합니다.  

cos를 추가합니다.  
![image](https://user-images.githubusercontent.com/15958325/55233809-02005580-526d-11e9-88b8-51e3abdb3c4f.png)  

cos서비스로 이동하여 Manage in IBM Cloud를 클릭합니다.  

서비스 인증정보 탭에서 credential을 추가합니다. 이는 watson ML에서 cos에 접근하기 위해 필요한 정보들입니다.  
각 항목에 들어가는 값은 다음 사진과 같습니다. 

> `Watson ML은 HMAC인증방식을 이용해서 COS와 통신합니다.`  
> HMAC(Hash-based Message Authentication) : 해싱기법을 적용해 메시지의 위변조를 방지하는 기법. 

![image](https://user-images.githubusercontent.com/15958325/55233856-1a707000-526d-11e9-886c-02fac9ba2ac5.png)   
>생성하고나서 access_key_id와 secret_access_key의 정보는 다른곳에 기입해 둡시다!  
>ex)  
> "access_key_id": "xxxxx",  
> "secret_access_key": "xxxxxx"

### Make Bucket
COS세팅이 되었다면 이제 Bucket을 두개 만들어 줄겁니다. 하나는 트레이닝 시킬 데이터들의 셋, 하나는 트레이닝하고 난 결과 데이터셋을 저장할 버킷입니다.  
위치는 watson ML의 위치와 똑같이 세팅해 줍니다.  
![image](https://user-images.githubusercontent.com/15958325/55235183-43463480-5270-11e9-973d-d82bc7662d73.png)    

bucket을 다 만들고 나면 다음 사진과 같이 리스트를 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55235292-8e604780-5270-11e9-8048-19afbc88c9a2.png)  
>다 만들고 나서, 버킷의 엔드포인트는 다른곳에 적어둡시다!  
> ex)  
> private : s3.private.us-south.cloud-object-storage.appdomain.cloud  
> public : s3.us-south.cloud-object-storage.appdomain.cloud

### MNIST Dataset

이 튜토리얼에서 사용할 데이터셋을 다운받습니다.  
손글씨 인식을 위한 데이터셋인 MNIST를 다운받습니다.  
link : [http://yann.lecun.com/exdb/mnist/](http://yann.lecun.com/exdb/mnist/)  
>MNIST를 이용한 손글씨 인식 모델 :  
>손글씨로 적혀진 숫자의 이미지 사진을 트레이닝하여 어떤 숫자에 대한 사진(혹은 로우데이터)이 주어졌을때 값을 예측할 수 있는 모델  

![image](https://user-images.githubusercontent.com/15958325/55233429-f6605f00-526b-11e9-8e26-c4e767add426.png)   
다운받은 4개의 파일  
- Training images
- Training labels
- Test images
- Test labels  

모두 트레이닝 시킬 데이터셋 버킷에 저장해 둡니다.  

![image](https://user-images.githubusercontent.com/15958325/55235569-3413b680-5271-11e9-9838-8b7687885195.png)  

## 5. Train the Model
이제 본격적으로 모델을 트레이닝해보겠습니다.  
모델을 빌드할 convolutional_network.py와 MNIST데이터를 다운로드하고 읽을 input_data.py가 담겨있는 [tf-model](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/simple-tutorial/ML01/tf-model.zip) 파일과, 이 파일들을 실행시키고 설정값들을 부여할 [tf-train.yaml](https://raw.githubusercontent.com/GRuuuuu/GRuuuuu.github.io/master/assets/resources/simple-tutorial/ML01/tf-train.yaml)파일을 다운로드합시다.  
파일을 다 받고 나면 yaml파일은 몇군데 수정해줘야할 부분이 있습니다.  
~~~yaml
model_definition:
  name: tf-mnist-showtest1
  author:
    name: DL Developer
    email: "{IBMid eamil 주소}"
  description: Simple MNIST model implemented in TF
  framework:
    name: tensorflow
    version: "1.5"
    runtimes: 
      name: python
      version: "3.5"
...
training_data_reference:
  name: {cos의 training dataset name}
  connection:
    endpoint_url: "{endpoint}"
    access_key_id: "{access_key}"
    secret_access_key: "{secret_access_key}"
  source:
    bucket: {cos의 training dataset name}
  type: s3
training_results_reference:
  name: {cos의 result dataset name}
  connection:
    endpoint_url: "{endpoint}"
    access_key_id: "{access_key}"
    secret_access_key: "{secret_access_key}"
  target:
    bucket: {cos의 result dataset name}
  type: s3
~~~
email주소, cos 버킷들의 이름, cos의 endpoint, 버킷의 access_key 그리고 secret access key까지 추가해줍시다.  

다음으로 이 yaml파일과 핵심 코드가 담겨있는 zip파일이 있는 폴더에서 터미널을 띄웁니다.  

~~~bash
$ bx ml train tf-model.zip tf-train.yaml
~~~
모델이 생성되는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55236914-4e02c880-5274-11e9-88f6-d70c22933d12.png)    
모델의 이름을 잘 기억해 둡시다. 여기선 "model-mlfh7a2r"  

training되는 과정에서의 로그를 모니터링할 수 있습니다.  
~~~bash
$ bx ml monitor training-runs {model-id}
~~~
![image](https://user-images.githubusercontent.com/15958325/55236968-6d99f100-5274-11e9-899c-ad875301250b.png)  
중간중간 스코어링할때 Accuracy들이 출력되고,  
![image](https://user-images.githubusercontent.com/15958325/55238468-eea6b780-5277-11e9-9e82-2f554570977b.png)  
마지막에 최종 Accuracy가 출력되며, 모델이 저장된 위치를 출력하고 트레이닝을 마칩니다.  
![image](https://user-images.githubusercontent.com/15958325/55238470-f0707b00-5277-11e9-8686-2e45a4335bac.png)  

## 6. Deploy the trained model

모델을 deploy하기 전에 생성한 모델을 watson ML repository에 저장해야 합니다.  
~~~bash
$ bx ml store training-runs {model id}
~~~
![image](https://user-images.githubusercontent.com/15958325/55238674-7260a400-5278-11e9-82e6-72cf6936b697.png)  

repository에 저장된 Model ID를 참조하여 모델을 deploy할 수 있습니다.  
~~~bash
$ bx ml deploy {Model-ID} "{deploy-model-name}"
~~~
![image](https://user-images.githubusercontent.com/15958325/55238847-cff4f080-5278-11e9-974d-cbc347b21605.png)    

## 7. Test the deployed model

마지막으로, deploy한 모델을 가지고 테스트를 해보겠습니다.  

숫자 5와 4의 사진의 raw데이터를 가지고 있는 [json파일](https://raw.githubusercontent.com/GRuuuuu/GRuuuuu.github.io/master/assets/resources/simple-tutorial/ML01/tf-mnist-test-payload.json)을 다운로드 받아봅시다.  

json파일도 몇군데 수정해야합니다.
~~~json
{
    "modelId": "{deploy했던 model의 id}", 
    "deploymentId": "{바로 위 사진에서 deploymentId}", 
    "payload": {
       "values": [
           [5의 raw데이터],
           [4의 raw데이터]
        ]
    }
 }
~~~

model ID와 deploymentID를 추가해주고 나서, scoring을 진행합니다.
~~~bash
$ bx ml score tf-mnist-test-payload.json
~~~
![image](https://user-images.githubusercontent.com/15958325/55239376-e8193f80-5279-11e9-92f6-408a20188b12.png)  
일정 시간이 지난뒤, 제대로 5와 4라고 예측하는 것을 확인할 수 있습니다.  

튜토리얼 끝!

----
