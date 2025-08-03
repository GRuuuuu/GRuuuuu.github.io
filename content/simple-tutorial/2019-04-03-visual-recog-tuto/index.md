---
title: "Build a Simple service using IBM Visual Recognition API"
slug: visual-recog-tuto
tags:
  - ML
  - Visual-Recognition
  - Watson
  - Cloud
date: 2019-04-03T13:00:00+09:00
---

## 1. Overview
이번 튜토리얼에서는 IBM Watson의 Visual Recognition 서비스를 통해 이미지를 인식하고, 서비스의 API를 이용한 간단한 web application제작, 마지막으로 기존 모델이 아닌 커스텀모델을 트레이닝시키는 작업까지 해보도록 하겠습니다.  

본 튜토리얼은 "[How to Build Machine Learning Apps with the IBM Visual Recognition API- Part 1](https://sourcedexter.com/ibm-visual-recognition-api-part-1/)"와 "[Building Custom Image Classifiers with IBM Visual Recognition Technology API – Part 2](https://sourcedexter.com/ibm-visual-recognition-technology-api-part-2/)"을 직접 해보고 작성한 튜토리얼입니다.  


관련 문서 : [Build a TensorFlow model using Watson ML CLI Tutorial](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/)

## 2. Prerequisites
`IBM Cloud`와 `IBM Watson`계정을 만들어주세요.  
`IBM Cloud` : [link](https://console.bluemix.net)  
`IBM Watson` : [link](https://dataplatform.cloud.ibm.com/) 

## 3. Set up Environment
### Watson Studio
Visual Recognition 서비스를 사용하기 위한 플랫폼인 왓슨 스튜디오를 다음과 같이 만들어줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55454290-5b280a80-561a-11e9-984d-9cd3db915dd5.png)

### Cloud Object Storage
다음 링크를 참고하여 cos도 추가 (버킷생성은 안해도됨)  
[참고링크](https://gruuuuu.github.io/simple-tutorial/mnist-tuto/#cloud-object-storage)

### IBM Visual Recognition Service
Cloud의 카탈로그 검색에서 visual을 검색하면 다음과 같이 보입니다. AI항목에서 Visual Recognition을 선택해 줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55454555-4730d880-561b-11e9-846f-9898be4187ed.png)  


이렇게 서비스를 만들어주고,  
![image](https://user-images.githubusercontent.com/15958325/55454592-63347a00-561b-11e9-9d4f-7861cdc12ca7.png)  

[Watsion Studio](https://dataplatform.cloud.ibm.com/home?context=data)의 대시보드를 가보면 서비스가 생성된 것을 확인할 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55454617-7c3d2b00-561b-11e9-888b-dd1f824d95eb.png)  

## 4. IBM Visual Recognition

### Object Recognition?  
실습을 진행하기 전에 객체 인식에 대해서 간단히 짚고 넘어가도록 하겠습니다.   
![image](https://user-images.githubusercontent.com/15958325/55456018-d42a6080-5620-11e9-8797-d35befaaa36d.png)   
이미지를 raw데이터로 보게되면 각 픽셀의 rgb값이 숫자로 표현되어 있습니다. 이러한 숫자들의 나열을 컴퓨터가 보고 이건 고양이야! 개야! 할 수 있도록 학습시키는 과정을 `Object Recognition`이라고 합니다.  
객체에 대한 인식은 이미지와 영상에 걸쳐 이루어질 수 있습니다.  

공부를 하다보면 <b>객체 탐지(Object Detection)</b>이라는 용어를 자주 볼 수 있을겁니다. 아래 사진을 봐주세요.    
![image](https://user-images.githubusercontent.com/15958325/55456946-67649580-5623-11e9-96bb-fdcf1180e486.png)   
`Object Recognition`은 이 사진을 "사과"라고 인식하고,  
`Object Detection`은 "사과"가 어디에 있는지 탐지합니다.  
정리하면 `Object Recognition`은 주어진 이미지가 무엇인지 인식하는 기술이고, `Object Detection`은 주어진 이미지에서 목표를 찾는 기술입니다.  
두 기술이 따로 분리된 것이아니라 Recognition기술 안에 Detect하는 기술이 있다고 생각하시면 됩니다.  

이러한 객체 인식 기술은 의료 이미징에서의 질병 식별과 산업 검사 및 로봇비전 등과 같은 다양한 분야에서 활용할 수 있습니다. 특히 자율주행 자동차에서 가장 많이 활용되는 핵심 기술로, 자동차가 정지 신호를 인식하고 보행자와 가로등을 구별할 수 있도록 합니다.  

### IBM Visual Recognition Test Model
본론으로 돌아와서 이러한 객체인식을 하기 위한 테스트모델을 제공해주고 커스텀모델을 생성할 수 있는 툴이 IBM Visual Recognition 입니다.  

IBM Visual Recognition를 실행시켜 봅시다.  
커스텀모델을 제외하고 여러가지 테스트모델들이 존재합니다. 이 중, food에 대한 모델을 테스트하여 봅시다!  
![image](https://user-images.githubusercontent.com/15958325/55457783-f4a8e980-5625-11e9-90ab-27146ba126d8.png)  

Test탭으로 가게 되면 다음과 같은 화면을 볼 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55457865-38035800-5626-11e9-8102-967055a32306.png)   
위 이미지에서 `Threshold` 파라미터는 답에 대한 기준을 의미합니다. 만약 0.8이라면 사과이미지일 확률이 0.8을 넘어야만 사과라고 인식한다는것.
최적의 `Threshold`값은 정해져 있는것이 아님! 그때그때마다 시도해보고 최적의 값을 찾아내야합니다.  

이미지를 다운받아서 drag&drop으로 대시보드로 옮겨봅시다.  
test 이미지는 [이곳](https://github.com/GRuuuuu/GRuuuuu.github.io/tree/master/assets/resources/simple-tutorial/ML02/food_images)    
![image](https://user-images.githubusercontent.com/15958325/55458337-a7c61280-5627-11e9-9c95-dd555bc23f9d.png)    
각 이미지에 대해 모델이 인식한 결과의 확률값을 태그로 붙여주고 있습니다.   

>비록 몇몇 결과는 틀린값을 보여주고 있지만 이러한 결과들은 더 많은 자료를 수집하여 커스텀 모델을 만들수밖에 없습니다.

### Using IBM Visual Recognition API

모델을 통해서 이미지를 인식하고, 그 결과값을 받아온다. 이러한 과정은 꼭 Watson Studio 내부 툴을 이용해서 할 필요는 없습니다. url을 통해 간단히 request하여 원하는 값을 받아오는 인터페이스, API를 사용하여 간단한 웹 application을 제작해보겠습니다.  

이 문서에서는 핵심 모듈만을 다루려고 합니다. 전체 코드는 [여기](https://raw.githubusercontent.com/GRuuuuu/GRuuuuu.github.io/master/assets/resources/simple-tutorial/ML02/testHTML.html)  

껍데기는 이렇게 생겼음  
![image](https://user-images.githubusercontent.com/15958325/55459762-3daf6c80-562b-11e9-843f-0c6c809e4afe.png)  

#### Image Preview
~~~js
var imgurl = "";
jQuery(document).ready(function($) {
    //img url이 들어오면 화면에 띄워줌
    $('#imageURLholder').bind('input', function() {
        $('#display_img').css('background-image', "url(" + $(this).val() + ")");
        imgurl = $(this).val();
    });
      //analyze버튼을 누르면 url을 담아 api를 call하는 send_request함수실행
    $("#analyze").click(function(){
        send_request(imgurl)
    });
~~~

#### Call Visualization API
~~~js
//Visualization API call func
function send_request(url){
    $.ajax
    ({
      //POST로 request api키는 본인의 api키를 넣어야함
      type: "POST",
      url: "https://gateway.watsonplatform.net/visual-recognition/api/v3/classify?version=2018-03-19&url=" + url,
      headers: {
        "Authorization": "Basic " + btoa("apikey" + ":" + "{apikey put here}")
      },
      //성공적으로 response가 오면 이미지와 분류된 결과를 출력하는 함수 호출
    success: function (response){
      console.log(response["images"][0]["classifiers"][0]["classes"][0])
      update_result(response);
      }
    });
};
~~~

본인의 API키는 Visual Recognition서비스의 Manage항목에서 찾을 수 있습니다.  
![image](https://user-images.githubusercontent.com/15958325/55460196-49e7f980-562c-11e9-8406-19e397de72cc.png)



#### Update Result
~~~js
function update_result(response){
    //전달받은 값에서 음식이름, 확률, 분류를 각각 뽑음
    var classification = response["images"][0]["classifiers"][0]["classes"][0]
    var food_name = classification["class"]
    var confidence_score = classification["score"]
    var hierarchy = classification["type_hierarchy"]
    //해당하는 div에 붙여넣기
    $('#resultdiv').html("")
    $('#resultdiv').append("<Span> <strong>RESULT</strong> </span><br><span> <strong> Food: </strong>" + food_name + "</span><br>")
    $('#resultdiv').append("<span> <strong> Confidence Score: </strong>" + confidence_score + "</span><br>")
    $('#resultdiv').append("<span> <strong> Hierarchy: </strong>" + hierarchy + "</span><br>")
    $('#display_img').css('background-size', "contain");
  };
~~~

#### Result

>사용한 이미지url : [https://t1.daumcdn.net/cfile/tistory/2413D1475859D92B05](https://user-images.githubusercontent.com/15958325/55460339-b95de900-562c-11e9-8663-4e8b5822d16c.png)   

결과 화면은 다음과 같습니다. 패스트푸드라고 잘 출력되고, 그에대한 확률값, 그리고 분류체계가 출력되는 것을 확인할 수 있습니다.     
![image](https://user-images.githubusercontent.com/15958325/55460279-8f0c2b80-562c-11e9-8cac-88136851ec65.png)   


그런데 외국에서 만든탓인지 제가 제일 좋아하는 김치찌개를 넣어보니 부야베스라는 프랑스 음식으로 인식해버리네요. 그외에도 낙지탕탕이를 넣어보니 오트밀로 인식하는등 그다지 마음에 들지 않는 결과를 도출해내고 있습니다.  
지금부터는 내 입맛에 맞는 커스텀모델을 구축해보도록 하겠습니다.    
![image](https://user-images.githubusercontent.com/15958325/55460681-86682500-562d-11e9-8b57-b92f1d41fd6e.png)

### Build Custom Model

먼저 분류를 원하는 객체를 고르고, 그 객체에 대한 다양한 이미지를 찾아 다운로드 합니다.  
저는 김치찌개와 낙지탕탕이를 골라서 진행해보겠습니다.  
주의해야할 점은, 각 클래스별 이미지가 11장 이상이어야 트레이닝이 가능하기 때문에 11장 이상으로 이미지를 모아줍시다.  
![image](https://user-images.githubusercontent.com/15958325/55461342-2b373200-562f-11e9-858b-951342d41354.png)  

>주의 : 이름에 들어가면 안되는 특문이 존재. 기본적으로 문자와 숫자는 가능. 되도록이면 문자와 숫자만으로 이름을 구성합시다.  

다음으로, 모델을 생성하기 위해 Visual Recognition의 Classify Images Create Model을 클릭해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/55461627-e069ea00-562f-11e9-80c7-d7b665644d31.png)  


다운받았던 이미지들을 모두 업로드 해줍니다.    
![image](https://user-images.githubusercontent.com/15958325/55461686-01323f80-5630-11e9-9bb9-9805d748cbe0.png)  

업로드된 이미지들을 각 클래스로 분류해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/55461720-16a76980-5630-11e9-95b6-7d4b08c5c265.png)    

분류가 완료되었다면 Train Model을 눌러 트레이닝을 시작합니다. 이미지의 개수에 따라 수분이 소요되니 끝날때까지 잠시 기다려줍니다.  

트레이닝이 성공적으로 종료되고 나면 이제 커스텀 모델을 사용할 수 있습니다!  
![image](https://user-images.githubusercontent.com/15958325/55461748-29ba3980-5630-11e9-88d3-47a349d4406b.png)  


커스텀 모델의 Overview 탭으로 이동하면 모델의 정보들이 짧게 요약되어 표시됩니다. 아래 사진 형광펜으로 표시된 부분이 API의 엔드포인트에서 내가만든 커스텀모델로 다이렉트 될수있는 식별자입니다.    
![image](https://user-images.githubusercontent.com/15958325/55462160-18256180-5631-11e9-8589-8b5115e00d68.png)  

모델ID를 파악했다면 위에서 만들었던 web application 소스코드파일을 약간만 수정해줍시다.  
~~~js
function send_request(url){
    $.ajax
    ({
      type: "POST",
      url: "https://gateway.watsonplatform.net/visual-recognition/api/v3/classify?version=2018-03-19&classifier_ids=custom_1103983787&url=" + url,
      headers: {
        "Authorization": "Basic " + btoa("apikey" + ":" + "{apikey put here}")
      },
    success: function (response){
      console.log(response["images"][0]["classifiers"][0]["classes"][0])
      update_result(response);
      }
    });
};
~~~
url에 `&classifier_ids={Model ID}`를 추가해주시면 됩니다.  

>사실 눈치가 빠른 분들은 눈치를 채셨겠지만 맨처음의 web application소스코드는 food모델에 리퀘스트를 날리는것이 아니라 general모델로 리퀘스트를 날리고있습니다. 실제로 send_request함수를 보면 classifier_ids에 관한 정의가 없어 default로 들어가게 됩니다.  
>원문에도 별다른 언급이 없어서 내용 흐름따라 food모델로 리퀘스트를 날리는 줄 알았는데 아니었네요...  

결과는 다음과 같습니다! 트레이닝하지 않았던 이미지를 입력값으로 주니 제대로 김치찌개라고 인식하는 모습을 확인할 수 있습니다!  
![image](https://user-images.githubusercontent.com/15958325/55462767-7737a600-5632-11e9-842b-e4333fed0aed.png)   

> 주의 : 이모델은 현재 김치찌개와 낙지탕탕이만 구분해낼수 있습니다. 더 다양한 음식을 구분해내고 싶다면 더많은 이미지! 더많은 클래스를 만들어봅시다! 

### Using Visual Recognition API with CLI
cli상에서도 아주아주 쉽게 api를 사용할 수 있습니다.  

GET POST방식으로 리퀘스트를 보낼 수 있으며, 각 방식의 틀은 다음과 같습니다.  

GET
~~~
curl -u "apikey:{api key}" "https://gateway.watsonplatform.net/visual-recognition/api/v3/classify?url={image 주소}&version=2018-03-19&classifier_ids={model id}"
~~~  
![image](https://user-images.githubusercontent.com/15958325/55463283-a7cc0f80-5633-11e9-8f45-43407ca999fe.png)  

POST
~~~
curl -X POST -u "apikey:{api key}" -F "url={image 주소}" -F "classifier_ids={model id}" "https://gateway.watsonplatform.net/visual-recognition/api/v3/classify?version=2018-03-19"  
~~~

![image](https://user-images.githubusercontent.com/15958325/55463521-38a2eb00-5634-11e9-9b0c-a9128e5325d2.png)  

>여러개 이미지 인식은 POST방식밖에 안됨! 시키고 싶다면 `-F "url={image 주소}"` 파라미터를 쭉쭉 붙이면됨  
>![image](https://user-images.githubusercontent.com/15958325/55464082-4e64e000-5635-11e9-8423-715bfb0cd81f.png)  



더 자세한 파라미터 관련 설명은 다음 링크를 참조하세요.  

[https://cloud.ibm.com/apidocs/visual-recognition#classify-an-image](https://cloud.ibm.com/apidocs/visual-recognition#classify-an-image)  

튜토리얼 끄읏  

----