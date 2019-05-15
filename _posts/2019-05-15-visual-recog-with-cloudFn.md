---
title: "Serverless Image Recognition with Cloud Functions"
categories: 
  - Simple-Tutorial
tags:
  - Cloudant
  - Watson
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

## 1. Overview
이번 문서에서는 `Apache OpenWhisk`기반의 `IBM Cloud Functions`를 사용하여 `Cloudant`에 저장된 이미지를 `Watson Visual Recognition`으로 분류하는 application을 만들어 볼것입니다.

다음 문서를 직접 해보고 작성한 문서입니다.  
링크: [link](https://github.com/IBM/ibm-cloud-functions-refarch-serverless-image-recognition)  

## 2. Prerequisites
IBM Cloud 계정 : [link](https://console.bluemix.net)  
IBM Watson 계정 : [link](https://dataplatform.cloud.ibm.com/)  
NodeJs설치 : [link](https://nodejs.org/ko/)  


> 환경이 window라면 git bash를 설치해주세요.  
> Git Bash : [link](https://gitforwindows.org/)  

## 3. Application Flow
application의 flow는 다음 그림과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/57744046-8b2af900-7702-11e9-89f5-dc8ba4a7d7ad.png)  

1. 이미지파일을 고릅니다.  
2. upload버튼을 통해 이미지파일은 `Cloudant DB`에 저장됩니다.  
3. 새로운 이미지가 DB에 저장되면 트리거에의해 `Cloud Function`이 실행됩니다.  
4. `Cloud Function`은 이미지를 가져와 처리를 위해 `Watson Visual Recognition`를 실행시킵니다.  
5. `Visual Recognition`의 결과값인 Score와 Class등을 `Cloudant`에 저장합니다.  
6. 유저는 자신이 업로드한 이미지에 대한 분류결과를 확인할 수 있습니다.  

## 4. Basic Concepts
### Apache OpenWhisk
`IBM Cloud Functions`의 기반이 되는 `Apache OpenWhisk`에 대해 알아보겠습니다.  
이벤트에 대해 함수를 실행시키는 Opensource Cloud Serverless 플랫폼으로, 개발자가 코드를 실행하는데 있어 컨테이너 관리나 운영으로부터 자유롭게 해줄 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/57756306-eb836000-772d-11e9-8bf4-ba0184a0c11a.png)  
용어에 대한 설명을 간략하게 하겠습니다.  
* **Trigger** : DB, 장치, 웹 등에서 발생한 이벤트들을 감지합니다.  
* **Actions** : 지원되는 프로그래밍 언어의 단일 함수로 구현된 코드로, 트리거가 발생하였을 때 실행되어 결과를 반환합니다.  
* **Rules** : 트리거에서 감지된 이벤트에 대해 어떤 액션이 실행될지 정의합니다.  
* **Sequences** : 액션을 연결하는 조합을 만들어 실행할 수 있습니다. 
* **Packages** : 트리거와 액션을 모아 하나의 패키지로 공개할 수 있습니다. 패키지로 정의된 외부 서비스를 사용할 수도 있고, 직접 만든 패키지를 외부에 공개할 수도 있습니다.  

### Serverless? 
Serverless는 서버 없이 모든 규모의 이벤트에 대해 코드를 실행하여 응답하는 클라우드 컴퓨팅 방식입니다. 서버가 없다는 것은 해당 이벤트에 대해 별도로 할당된 서버가 없어 사용자가 인프라 및 플랫폼 관리를 할 필요가 없다는 의미입니다.  

Serverless 플랫폼에서는 요청이 있을 때만 필요한 코드를 실행하고, 요청이 많을 경우에는 그에 비례하는 자원을 할당하여 동시에 처리하는 방법으로 사용률과 확장성을 극대화할 수 있습니다.

## 5. Step
### Clone the git
웹페이지를 구성할 소스코드를 클론받습니다.  
~~~bash
$ git clone https://github.com/IBM/serverless-image-recognition
~~~  
>링크가 터졌을 때를 대비한 링크 : [link](https://github.com/GRuuuuu/GRuuuuu.github.io/tree/master/assets/resources/simple-tutorial/CLOUD01/serverless-image-recognition)  

![image](https://user-images.githubusercontent.com/15958325/57749256-4447fe00-7718-11e9-8a1c-3afe045549fd.png)  

### Cloudant Create&Config
먼저 Cloudant를 생성합니다.  
생성링크 -> [link](https://cloud.ibm.com/catalog/services/cloudant)  

생성할 때, `use both legacy credentials and IAM`을 체크해주는 것을 잊지맙시다!   
![image](https://user-images.githubusercontent.com/15958325/57749404-e667e600-7718-11e9-9ef9-5830922b8a4d.png)  

만들고 난 뒤 인증정보를 생성합니다.  
![image](https://user-images.githubusercontent.com/15958325/57749461-1a430b80-7719-11e9-82a7-7ce75946bac5.png)  

생성한 인증정보에서 password와 username을 찾아서 클론받은 프로젝트 내부 `local.env`에 기재합니다.  
![image](https://user-images.githubusercontent.com/15958325/57749503-3e065180-7719-11e9-8355-0bba54528233.png)  

Image를 담을 DB와 Tag를 담을 Tag DB의 이름을 images와 tags으로 기입합니다. 혹시 자신이 다른이름을 사용할 것이라면 수정하셔도 됩니다.
![image](https://user-images.githubusercontent.com/15958325/57749505-3fd01500-7719-11e9-8f6d-b22ef2302e7b.png)  

이제 Cloudant 웹 콘솔을 실행시켜 DB를 생성해보겠습니다.  
DB의 이름은 앞서 적었던것과 같은 이름으로 적어주세요.  
![image](https://user-images.githubusercontent.com/15958325/57749641-d8669500-7719-11e9-8051-65965198410c.png)  

### Watson Visual Recognition
먼저 인스턴스를 생성해줍니다.  
생성링크 -> [link](https://cloud.ibm.com/catalog/services/visual-recognition)  

Cloudant와 마찬가지로 서비스 인증정보를 만들어 줍니다.  
![image](https://user-images.githubusercontent.com/15958325/57751303-37c7a380-7720-11e9-99d5-d6e459bd797b.png)  
apikey를 복사하여 `local.env`의 apikey에 붙여넣어줍시다.  

![image](https://user-images.githubusercontent.com/15958325/57751348-6180ca80-7720-11e9-9d8a-704830a863e9.png)  

### Add Trigger
IBM Cloud Functions Console로 이동 -> [link](https://cloud.ibm.com/openwhisk/create)  

트리거 탭으로 이동해서 create를 누르고 cloudant를 선택합니다.  
![image](https://user-images.githubusercontent.com/15958325/57751519-ff749500-7720-11e9-9b7e-2f51f3a328c2.png)  

다음 이미지와 같이 빈칸들을 채워주시면 됩니다.  
username, password, host는 cloudant의 서비스인증정보를 참조, DB의 이름은 트리거에 의해 이미지를 `watson visual recognition`에 보내야 하므로 source DB의 이름을 적어주어야 합니다.   
![image](https://user-images.githubusercontent.com/15958325/57751650-6a25d080-7721-11e9-97af-03a9e76332c0.png)  

### Add Action
이제 트리거가 발생하였을 때, 어떠한 액션을 취할 것인지를 정의해주어야 합니다.  
Connected Action > Create로 이동합니다.  
![image](https://user-images.githubusercontent.com/15958325/57751825-eddfbd00-7721-11e9-8821-f09f350d2f27.png)   

액션의 이름과 Runtime환경을 정의해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/57751943-41520b00-7722-11e9-86ca-7ce746c745e7.png)  

source code -> [link](https://raw.githubusercontent.com/GRuuuuu/GRuuuuu.github.io/master/assets/resources/simple-tutorial/CLOUD01/serverless-image-recognition/actions/updateDocumentWithWatson.js)  

소스코드를 Code탭에 복사 붙여넣기 합니다.  
![image](https://user-images.githubusercontent.com/15958325/57752006-7d856b80-7722-11e9-8b9c-b1b5c22baddb.png)  

Parameters탭에서 각 parameter들을 입력해줍니다.  
username과 password는 cloudant에서 참조.  
![image](https://user-images.githubusercontent.com/15958325/57752025-90983b80-7722-11e9-8372-11d901662389.png)

### Deploy

`wskdeploy`를 설치합니다.  
설치 링크 : [link](https://github.com/apache/incubator-openwhisk-wskdeploy/releases)  

>**wskdeploy?**   
>yaml로 쓰여진 Manifest파일을 사용하여 [OpenWhisk](https://gruuuuu.github.io/simple-tutorial/visual-recog-with-cloudFn/#apache-openwhisk) Programming 모델을 구성해주는 utility입니다.  

`local.env`에 저장하였던 환경변수들을 세팅해줍니다.  
~~~bash
$ source local.env
~~~  

wskdeploy를 설치하였던 폴더경로를 참고하여 `local.env`가 있는 폴더에서 wskdeploy를 실행합니다.  
~~~bash
$ wskdeploy
~~~   

`web/scripts/upload.js` 에서 다음 파라미터들을 수정해줍니다.  
~~~js
usernameCloudant = "YOUR_CLOUDANT_USERNAME"
passwordCloudant = "YOUR_CLOUDANT_PASSWORD"
~~~  

필요한 패키지들을 설치해주고 application을 실행시킵니다.  
~~~bash
$ npm install
$ npm start
~~~  

일렉트론 앱이 실행되고, 이미지를 실제로 넣어보면 분류가 되는 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/57753713-d1468380-7727-11e9-9ccc-b8d3c0321afc.png)  

## 6. Another Step (CLI)

위의 과정 중, 몇몇 과정을 커맨드라인으로 입력하는 방법입니다.  

### set up
IBM Cloud Functions CLI 설정을 위해 플러그인을 설치합니다.  
~~~bash
$ ibmcloud plugin install cloud-functions
~~~

ibmcloud에 로그인합니다.  
~~~bash
$ ibmcloud login --sso
$ ibmcloud target -cf
~~~  
![image](https://user-images.githubusercontent.com/15958325/57762188-ff34c380-7739-11e9-8073-5ed0c7a05b3a.png)

환경변수를 설정합니다.  
~~~bash
$ source local.env
~~~


아래 명령으로 cloudantDB를 사용하기 위한 package를 설치하고 env셋업을 합니다.
~~~bash
$ bx wsk package refresh
~~~

### Add Trigger -cli
~~~bash
$ ibmcloud wsk trigger create update-trigger2 --feed serverless-pattern-cloudant-package/changes --param dbname images
~~~  
![image](https://user-images.githubusercontent.com/15958325/57761829-440c2a80-7739-11e9-9b7d-b4a4a0781def.png)  

### Add Action -cli
~~~bash
$ ibmcloud wsk action create update-document-with-watson2 actions/updateDocumentWithWatson.js \
--kind nodejs:8 \
--param USERNAME $CLOUDANT_USERNAME \
--param PASSWORD $CLOUDANT_PASSWORD \
--param DBNAME $CLOUDANT_IMAGE_DATABASE \
--param DBNAME_PROCESSED $CLOUDANT_TAGS_DATABASE \
--param WATSON_VR_APIKEY $WATSON_VISUAL_APIKEY
~~~  
![image](https://user-images.githubusercontent.com/15958325/57762397-68b4d200-773a-11e9-8d93-090a9ad970ce.png)  

### Make Rule -cli
~~~bash
$ ibmcloud wsk rule create update-trigger-rule2 update-trigger2 update-document-with-watson2
~~~  
![image](https://user-images.githubusercontent.com/15958325/57762464-841fdd00-773a-11e9-985d-d1e38f58e8a4.png)  

### Delete
~~~bash
$ ibmcloud wsk package delete serverless-pattern-cloudant-package
$ ibmcloud wsk trigger delete update-trigger2
$ ibmcloud wsk action delete update-document-with-watson2
$ ibmcloud wsk rule delete update-trigger-rule2
~~~

----