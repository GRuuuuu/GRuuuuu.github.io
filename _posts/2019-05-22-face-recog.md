---
title: "Face Recognition Terminal"
categories: 
  - Simple-Tutorial
tags:
  - IoT
  - Cloud
  - OpenCV
  - Watson
  - ICOS
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 local에서 실시간으로 촬영한 얼굴 이미지를 `Watson Visual Recognition`으로 분석하여 web UI로 볼 수 있게 구성해 보겠습니다.  

다음 문서를 직접 해보고 작성한 문서입니다.  
Chapter 6. Face Recognition Terminal: [link](https://www.redbooks.ibm.com/redbooks/pdfs/sg248385.pdf)  

## 2. Prerequisites
IBM Cloud 계정 : [link](https://console.bluemix.net)  
IBM Watson 계정 : [link](https://dataplatform.cloud.ibm.com/)  
Python설치 : [link](https://www.python.org/downloads/)  
Node js설치 : [link](https://nodejs.org/ko/)   

>**Local Test version**  
>`Node js` : v10.15.3  
>`Python` : v3.7.3   

## 3. Architecture
프로젝트의 구조는 아래 사진과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/58142773-5c250200-7c83-11e9-8956-efe1a8d900aa.png)  

0. Local에서 `Webcam`으로 이미지를 촬영  
1. Local device의 정보(`org_id`, `deviceType`, `mac주소`)를 `IoT Platform`으로 Publish
2. 이미지파일은 `COS`에 PUT
3. `Node-RED`에서 메세지를 `subscribe`하고 있음
4. `Node-RED`에서 `COS`의 이미지를 GET
5. GET한 이미지를 `Watson Visual Recognition`으로 분류
6. 결과를 `Node-RED`의 web base UI로 뿌려줌

## 4. STEP
### Create IoT Platform
Cloud Foundry App인 IoT Platform을 생성해줍니다.   
>리소스생성 > Internet of Things Platform 스타터   

![image](https://user-images.githubusercontent.com/15958325/58219572-65c36e00-7d46-11e9-8edc-4b16fefe75b1.png)

생성하게 되면 아래사진과 같이 `iotf-service`와 `cloudant`가 서비스로 붙게 됩니다.   
![image](https://user-images.githubusercontent.com/15958325/58219759-03b73880-7d47-11e9-8e8c-77547cd57a30.png)  

이 두 서비스를 이어주고 메세지를 전달해주며 우리가 앞으로 만들 프로그램의 중추역할을 할 코어는 해당 cloud foundry app의 `Node-RED`로 구현되어있습니다.  

`Node-RED`에 몇가지 파일을 추가하기 위해 로컬환경에서 편집을 진행할 수 있도록 `Continuous-Delivery`를 추가하도록 하겠습니다.  

### Configure Continuous-Delivery

절차는 다음 링크를 참조해주세요.  
[https://gruuuuu.github.io/simple-tutorial/icos-api/#continuos-delivery](https://gruuuuu.github.io/simple-tutorial/icos-api/#continuos-delivery)  

주의해야할 점은 저장소 유형을 "복제"로 해야한다는 것입니다.  
![image](https://user-images.githubusercontent.com/15958325/58220461-ee8fd900-7d49-11e9-84e5-be898129dc04.png)

git clone을 받아두고 auth까지 되면 다음단계로 넘어가 주세요.  

### add Node Dependency
로컬에 clone을 받고나면 directory구조는 다음과 같이 보일것입니다.    

![image](https://user-images.githubusercontent.com/15958325/58220531-3878bf00-7d4a-11e9-86dc-fb09dbd001c3.png)  

dependency를 추가하기 위해 package.json에 다음 라인을 추가해줍시다.  
~~~json
"dependencies": {
  ...
  "node-red-node-random":"0.x",
  "node-red-node-smooth":"0.x",
  "node-red-contrib-web-worldmap":"1.x",
  "node-red-node-geofence":"*",
  "node-red-contrib-slacker":"*",
  "node-red-node-base64": "*",
  "node-red-contrib-play-audio": "*",
  "node-red-dashboard":"node-red/node-red-dashboard",
  "request":"~2.74.0",
  "bluebird": "^3.3.3",
  "knox": "latest",
  "fs": "latest",
  "fs-extra": "latest",
  "node-uuid": "latest"
},
~~~  

그 다음, [node-red-contrib-cos.zip](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/simple-tutorial/CLOUD02/node-red-contrib-cos.zip)의 압축을 풀어서 nodes폴더 하에 옮겨둡니다.  

![image](https://user-images.githubusercontent.com/15958325/58220884-91952280-7d4b-11e9-88ef-c09534a46ec6.png)   

Push하고 `Delivery Pipeline`에서 deploy가 성공한 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/58225295-4cc5b780-7d5c-11e9-9bcb-2e309f993dd1.png)  

이제 필요한 dependency를 모두 추가하였으니 `Node-RED`에서의 Flow를 생성하여야 합니다.  

### Node-RED Flow

앱 URL방문을 클릭합니다.  
![image](https://user-images.githubusercontent.com/15958325/58225403-dd9c9300-7d5c-11e9-9bd5-bb01f7a50c55.png)  

계정을 생성해준뒤, default로 생성되어있는 flow들을 삭제합니다.  

그 뒤, [face_recognition_nodered_flow.txt](https://raw.githubusercontent.com/GRuuuuu/GRuuuuu.github.io/master/assets/resources/simple-tutorial/CLOUD02/face_recognition_nodered_flow.txt)를 복사해서 노드로 가져오기 합니다.  
![image](https://user-images.githubusercontent.com/15958325/58225533-64ea0680-7d5d-11e9-94d5-b1f61a4bad8e.png)  

불러온 노드의 모습은 다음과 같습니다. 위의 전체 구조와 비교해서 보신다면 더 잘 이해가 되실겁니다.  
![image](https://user-images.githubusercontent.com/15958325/58225597-b0041980-7d5d-11e9-91b3-928b7d6a537e.png)  

큰 틀은 완성이 되었습니다. 이제 각 서비스들을 구성해주어야 합니다.  

### Create Cloud Object Storage
먼저 로컬에서 생성한 이미지를 저장하기 위해 `Cloud Object Storage`를 생성해줍니다. 추가로 사용할 버킷도 미리 생성해 줍니다.    
참고 -> [link](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage)  

>인증정보 중 AccessKey와 SecretKey는 다른곳에 적어둡니다.  

### Configure IoT Service 
`iotf-service`의 dashboard를 열어주세요.  
![image](https://user-images.githubusercontent.com/15958325/58225691-48020300-7d5e-11e9-91b9-62c515498efc.png)  

해당 서비스로 메세지를 보낼 장치를 등록할 것입니다.  
디바이스 추가를 클릭합니다.  
![image](https://user-images.githubusercontent.com/15958325/58225723-6c5ddf80-7d5e-11e9-801d-6a3c6a216454.png)  

디바이스를 추가하기 위해선 해당 디바이스의 `MAC Address`가 필요합니다.  

윈도우에서 MAC주소는 다음 명령어를 통해 알 수 있습니다.  
~~~bash
$ getmac /v
~~~

![image](https://user-images.githubusercontent.com/15958325/58225921-353bfe00-7d5f-11e9-9193-dede19aa8aac.png)  

물리적 주소라고 적힌 부분이 MAC주소이고, '-'을 빼고 12자리 캐릭터를 디바이스 ID로 적어주시면 됩니다.  
디바이스 유형은 Laptop으로 적어줍니다.  
![image](https://user-images.githubusercontent.com/15958325/58225798-ca8ac280-7d5e-11e9-854e-67f5a1af2f47.png)  

저 두가지 항목만 적어주시고 완료버튼을 눌러 디바이스를 추가해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/58226015-b5626380-7d5f-11e9-921b-dd2637901a2f.png)  

디바이스를 추가하고 정보를 확인해보면 다음과 같이 나옵니다.  
조직ID와 인증토큰은 다른곳에 잘 저장해둡시다.  
로컬에서 `iotf-service`로 메세지를 보낼때 사용하게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/58226114-36b9f600-7d60-11e9-8b71-be49a1550720.png)  

이제 `iotf-service`의 구성은 마무리되었고, 핵심모듈중 하나인 `watson visual recognition`서비스를 추가하여야 합니다.  

### Add Watson Visual Recognition service 
리소스 추가 > visual검색 > Visual Recognition선택  
![image](https://user-images.githubusercontent.com/15958325/58226220-acbe5d00-7d60-11e9-923e-4ffce8ab7396.png)  

서비스를 생성합니다.  
![image](https://user-images.githubusercontent.com/15958325/58226245-c3fd4a80-7d60-11e9-9844-cec1d90c2c63.png)  

인증정보를 새로 생성하고, 다른 서비스와의 연결을 위해 `apikey`를 저장해둡니다.  
![image](https://user-images.githubusercontent.com/15958325/58226257-d2e3fd00-7d60-11e9-89b4-7e7de8fe0e53.png)  


여기까지 각 서비스들의 구성은 끝나게 됩니다. 이제 따로따로 떨어져있는 서비스들을 Node-RED를 사용해 하나로 엮어야 합니다.  

큰 틀은 위에서 구성하였으니 각 서비스 노드만 수정해주면 됩니다.  

### Fix Node-RED  
노드의 흐름을 잘 따라와주세요.  

첫번째로 내 디바이스에서 이벤트가 발생하였을때 `iotf-service`에서 이벤트를 수집하는 노드입니다.  
내 디바이스가 무엇인지 식별하기 위해 장치의 Mac Address를 Device Id에 작성해줍니다.  
반드시 `iotf-service`에서 등록했던 장치의 Mac Address여야합니다.  
![image](https://user-images.githubusercontent.com/15958325/58226532-fb202b80-7d61-11e9-8f18-aea350131f0f.png)  

두번째로는 로컬에서 이미지를 저장하고 `Visual Recognition`에서 식별할 이미지를 가져올 장소인 COS노드를 수정해줍니다.  

cos-config의 노드타입 추가를 선택하고 연필버튼을 클릭해 줍니다.  
![image](https://user-images.githubusercontent.com/15958325/58226920-b5fcf900-7d63-11e9-80cf-fff6a4168444.png)  

COS만들때 생성했던 인증정보를 토대로 `Access Key`와 `Secret Key`, `Endpoint`를 적어줍니다. 다음으로 연속적으로 불러올 이미지인 `campic.jpg`를 ObjectName으로 적어주고 해당 이미지가 저장되어있을 장소인 Bucket이름을 적어주면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/58226994-070ced00-7d64-11e9-91a1-6d95b69569a8.png)  

>frame단위로 저장할 이미지의 이름: `campic.jpg`  
>해당이미지는 n초단위로 같은이름으로 COS에 저장되고, `Visual Recognition`에서 분류되기때문에 거의 실시간의 detection이 가능하다.   

마지막으로 COS에서 가져온 이미지를 식별해줄 `Watson Visual Recognition`을 연결해줍시다. `Face Detection`노드를 클릭하여 `API Key`와 `Service Endpoint`를 입력해줍니다.  
각 항목은 Visual Recognition의 인증정보(`apikey`와 `url`)를 참조하여 작성하시면 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/58226434-99f85800-7d61-11e9-881c-2bf4c82b41e2.png)  

여기까지 각 노드의 구성은 마무리가 되었고 이제 로컬에서 웹캠으로 촬영하는 단계만 남았습니다!  

### face_detection_terminal.py 
웹캠을 실행하고, `iotf-service`에 메세지를 보내고, COS에 이미지를 보내는 프로그램입니다.  
소스코드는 [이곳](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/assets/resources/simple-tutorial/CLOUD02/face_detection_terminal.py)  

당연히 서비스에 연결하려면 인증정보를 입력해야 합니다.  

`iotf-service`에 연결하기 위해 수정해야하는 코드입니다.  
각 라인에 올바른 값을 넣어주시면 됩니다.  
>organization은 `iotf-service`의 일반설정에서 확인할 수 있습니다.   
>![image](https://user-images.githubusercontent.com/15958325/58230443-4d1b7e00-7d6f-11e9-9678-27a36b77e4aa.png)

![image](https://user-images.githubusercontent.com/15958325/58227477-f3fb1c80-7d65-11e9-8b1c-94dca2776666.png)  

COS에 연결하기 위해 수정해야하는 코드입니다.  
각 라인에 올바른 값을 넣어주세요.  
>endpoint_url은 COS인증정보의 url을 참조하시면됩니다.  

![image](https://user-images.githubusercontent.com/15958325/58227369-7e8f4c00-7d65-11e9-8647-1cef5ae1d5e3.png)  

수정이 끝났다면 실행에 필요한 라이브러리들을 받아야 합니다.  

- paho-mqtt
  ~~~bash
  $ pip install paho-mqtt
  ~~~
  ![image](https://user-images.githubusercontent.com/15958325/58230739-227df500-7d70-11e9-8f9d-16f0dd5d3038.png)  

- OpenCV
  ~~~bash
  $ python -m pip install opencv-python
  ~~~


>(주의) 아무 이미지를 다운받아서 tmp/campic.jpg로 저장해두고 프로그램을 실행시켜야합니다.  

프로그램을 실행시키고 Node-RED의 디버그창을 확인해보면 다음과 같이 각 노드에서의 메세지들을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/58231391-d8960e80-7d71-11e9-9cd7-4774b0af1bd3.png)  

또한 다음 링크로 접속하게되면 UI창을 확인할 수 있습니다.  
~~~
https://{APP_NAME}.mybluemix.net/ui
~~~  

웹캠에 보여지는 얼굴을 인식해서 나이와 성별을 예측하는 화면입니다.  
![image](https://user-images.githubusercontent.com/15958325/58231461-02e7cc00-7d72-11e9-938d-466e66e1e9a9.png)  

![image](https://user-images.githubusercontent.com/15958325/58231464-04b18f80-7d72-11e9-92ad-f3783969d76f.png)  

끗

----