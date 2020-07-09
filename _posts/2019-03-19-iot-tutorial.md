---
title: "Simple IoT accelerometer game Tutorial"
categories: 
  - Simple-Tutorial
tags:
  - IoT
  - Watson
  - Cloud
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---

**2020/07/09 수정 : Node-Red설정**  

## 1. Overview
디바이스의 센서데이터를 cloud상에 저장시키고, 저장된 데이터를 왓슨스튜디오로 분석하여 센싱데이터의 에너지 총량을 도출할 수 있는 application입니다. 

IBM Developer blog에 게재된 "[Create a fun, simple IoT accelerometer game](https://developer.ibm.com/tutorials/iot-simple-iot-accelerometer-game/)"를 따라 진행해보도록 하겠습니다.  

>기대효과  
> * IoT에 대한 흥미유발
> * IBM Cloud 사용법과, Watson Studio의 사용법 숙지
> * 다수가 모인 자리에서 킬링타임용 게임진행

## 2. Prerequisites
`IBM Cloud`와 `IBM Watson`계정을 만들어주세요.  
`IBM Cloud` : [link](https://console.bluemix.net)  
`IBM Watson` : [link](https://dataplatform.cloud.ibm.com/)  
+) 센서 데이터를 수집해야 하므로, 테스트할 기기로 스마트폰 또는 노트북을 지참해주세요.

## 3. Deploy Application
센서데이터를 수집할 수 있는 웹 애플리케이션을 클라우드상에 배포해보는 과정입니다.   

다음 버튼을 클릭해서 IBM cloud상에 배포해봅시다.  
[![Deploy to Bluemix](https://bluemix.net/deploy/button.png)](https://bluemix.net/deploy?repository=https://github.com/romeokienzler/discover-iot-sample)
>출처: [romeokienzler/discover-iot-sample](https://github.com/romeokienzler/discover-iot-sample)

cloud에 배포하기전 설정 화면이 나타납니다.  
<img width="666" alt="1" src="https://user-images.githubusercontent.com/15958325/54485909-2ac73900-48c4-11e9-93cb-0638822ce06d.PNG">  
><b>주의</b> : 주의해야할 점은 지역을 댈러스로 선택해야 한다는 것입니다. <b>댈러스</b> 외의 다른 지역을 선택하면 앱을 실행하기 위한 몇가지 플러그인이 존재하지 않는 것 같습니다. 


지역을 선택한 뒤, API키 작성을 눌러 API키를 생성하고 Deploy버튼을 눌러 앱을 클라우드상에 배포합니다.  
<img width="370" alt="2" src="https://user-images.githubusercontent.com/15958325/54485946-cce72100-48c4-11e9-836a-7193d8d20884.PNG">  
<img width="477" alt="3" src="https://user-images.githubusercontent.com/15958325/54485993-61ea1a00-48c5-11e9-84d3-c42618d1bab8.PNG">  

Deliver Pipeline을 클릭해보면 github에서 가져온 코드가 클라우드상에 배포되고 있는 모습을 확인할 수 있습니다.   
<img width="445" alt="4" src="https://user-images.githubusercontent.com/15958325/54485995-63b3dd80-48c5-11e9-80da-6fe0a7b02c48.PNG">  

몇가지 설정을 바꾸기 위해 Deploy Stage의 단계구성을 클릭해줍니다.  
<img width="223" alt="5" src="https://user-images.githubusercontent.com/15958325/54485996-66163780-48c5-11e9-851e-0d000451eef5.PNG">  

아래 사진과 같이 입력유형을 Git 저장소, 분기를 master로 바꿔준 뒤 저장해 줍니다.  
<img width="419" alt="6" src="https://user-images.githubusercontent.com/15958325/54486041-e8066080-48c5-11e9-8da9-84cdd95db382.PNG">  
저장하고 난 뒤, 빌드부터 새로 재시작해줍니다.

앱이 정상적으로 가동된다면 앱URL방문을 클릭합니다.  
<img width="565" alt="7" src="https://user-images.githubusercontent.com/15958325/54486042-e89ef700-48c5-11e9-8c4c-71fc1159c2d7.PNG">  
   

방문하게 되면, Step1에 하나의 링크가 보이게 됩니다. 이 링크는 디바이스에서 센서데이터를 측정해서 화면에 띄워주는 웹기반 application입니다.  
<img width="575" alt="8" src="https://user-images.githubusercontent.com/15958325/54486043-e9378d80-48c5-11e9-9dbd-2ff30d271358.PNG">  
이 링크를 따라 접속해봅시다.

User의 Id와 Pw를 입력하고나면 연결되었다는 표시와 함께 Movement, Acceleration에 관한 센서값들을 확인할 수 있습니다.  
<img width="606" alt="9" src="https://user-images.githubusercontent.com/15958325/54486044-ea68ba80-48c5-11e9-9210-74a69866780a.PNG">  

## 4. Node-Red 설정
센서데이터를 클라우드로 가져오기 위해서, `Node-Red`라는 오픈소스 GUI flow 에디터를 사용하겠습니다. `Node-Red`를 통해 디바이스에서 송신되는 `MQTT`기반 데이터들을 DB에 저장할 것입니다.   

app을 배포하게되면 클라우드 리소스리스트는 아래와 비슷하게 보일 것입니다.  
![image](https://user-images.githubusercontent.com/15958325/87007413-34815800-c1fd-11ea-918d-41c39491faac.png)  


### Node-Red 배포
리소스 검색에서 `Node-Red`를 검색한 뒤, 생성해줍시다.  

![image](https://user-images.githubusercontent.com/15958325/87007635-89bd6980-c1fd-11ea-8b61-7779321e2b08.png)  

지역은 배포한 app이 있는 지역으로 맞춰주시기 바랍니다.  
![image](https://user-images.githubusercontent.com/15958325/87007639-8b872d00-c1fd-11ea-9e2f-bbb3a7fa8ecd.png)  

이런 식으로 화면이 뜨게 됩니다. 이제 Node-Red를 클라우드에 배치하기 위해 Continuous Delivery를 구성해주겠습니다.   
우측의 앱배치를 눌러주세요.  
![image](https://user-images.githubusercontent.com/15958325/87007790-c38e7000-c1fd-11ea-83f9-fedac1d5ae12.png)  

API키는 신규 생성으로 만들어줍니다. 메모리는 기본으로 256MB가 할당되긴합니다. 최소요구량은 128MB이니 참고하시기 바랍니다.    
![image](https://user-images.githubusercontent.com/15958325/87007937-f46ea500-c1fd-11ea-9cdf-f2ca07b9d836.png)  

DevOps 도구 체인 이름을 설정해주고 작성하기를 클릭 :   
![image](https://user-images.githubusercontent.com/15958325/87009644-6a740b80-c200-11ea-90e4-d35323e2c577.png)  

좀 기다리면 앱배치가 성공적으로 마무리 되고, 앱URL이 뜹니다.  
![image](https://user-images.githubusercontent.com/15958325/87009806-a9a25c80-c200-11ea-9463-305dd37993bf.png)  
>배치하는 도중에 에러가 발생한다면 재배치를 눌러보세요.  

### Node-Red 초기 설정

배치가 성공하고나서 앱 URL을 누르게되면 Node-Red 앱으로 이동하게 됩니다.  
초기설정을 해주겠습니다. id와 password를 설정해주고 Next:   
![image](https://user-images.githubusercontent.com/15958325/87009949-d787a100-c200-11ea-94fa-b19f86e9a5c8.png)  

초기설정을 마치면 Node-Red초기 페이지가 뜨게 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/87010053-f9812380-c200-11ea-8634-60efb83cac1e.png)  

### IoT 모듈 추가
뒤에서 진행할 Node-Red플로우를 그리기 위해 필요한 IoT모듈을 Node-Red 노드에 추가해보겠습니다.  

Deployment Pipeline에서 GIT을 선택해 Node-Red의 깃랩프로젝트로 이동합니다.  
![image](https://user-images.githubusercontent.com/15958325/87010902-326dc800-c202-11ea-93c6-ad333447bf30.png)  

프로젝트 파일 중 `package.json`을 선택 :  
![image](https://user-images.githubusercontent.com/15958325/87010911-34378b80-c202-11ea-970a-d1f4ad730efd.png)  

dependencies에 다음 라인을 추가해줍니다.  
~~~
 "node-red-contrib-scx-ibmiotapp": "0.x",
~~~

![image](https://user-images.githubusercontent.com/15958325/87010929-37327c00-c202-11ea-9838-0737f854bc80.png)  

그리고나서 커밋해주면 자동으로 재빌드, 재배포 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/87011263-a1e3b780-c202-11ea-86a8-d18d76773228.png)  

### 기본 서비스 연결
이제 이 Node-Red서비스와 IoT서비스를 서로 연동시켜줄 것입니다.  

Node-Red 오버뷰의 서비스부분에서 **기존서비스추가**를 눌러서 위의 iot앱을 생성할 때 같이 생성되었던 IoT서비스를 추가해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/87011418-d8213700-c202-11ea-85e5-cb9a42174272.png)   

정상적으로 추가하고 나면 다음과 같은 화면이 됩니다.  
![image](https://user-images.githubusercontent.com/15958325/87011422-d9526400-c202-11ea-9010-62495c679549.png)  

그 다음, IoT서비스로 이동해서 연결 > 연결작성을 클릭합니다.  
![image](https://user-images.githubusercontent.com/15958325/87011649-2c2c1b80-c203-11ea-9e37-073bd1f16a58.png)  

위에서 작성했던 Node-Red 앱 선택  
![image](https://user-images.githubusercontent.com/15958325/87011657-2df5df00-c203-11ea-98e4-23fa7a5bd112.png)  

리스테이징 선택:  
![image](https://user-images.githubusercontent.com/15958325/87011662-2f270c00-c203-11ea-9f29-50b6692069d3.png)  

이렇게 하면 IoT서비스와 Node-Red앱이 연동되게 됩니다.  


## 5. Making Node-Red Graph

지금까지 과정은 단순히 클라우드에 앱을 배포하는 것입니다. 의미있는 데이터를 뽑아내기위해, 센서데이터들을 저장할 수 있는 DB가 필요합니다. 이번 챕터에서는 데이터들을 저장시킬 수 있는 DB설정에 대해 다뤄보겠습니다.  

우선 Watson IoT Platform을 시작시킵니다.  
<img width="592" alt="13" src="https://user-images.githubusercontent.com/15958325/54486142-26e8e600-48c7-11e9-9783-ae2093863ebb.PNG">  

실행시키면 왼쪽 메뉴가 가려져서 잘 안보이는데 마우스를 올리면 잘 보이게 됩니다. 자물쇠처럼 생긴 Security메뉴를 클릭합니다. 뜨는 리스트 중, 연결보안(Connection Security) 수정버튼을 클릭합니다.  
<img width="758" alt="14" src="https://user-images.githubusercontent.com/15958325/54486143-26e8e600-48c7-11e9-9b10-cc96edcc9482.PNG">  

Security Level을 **TLS Optional(TLS 선택적)**으로 변경시켜준 뒤, Refresh 시켜줍니다.  
><b>TLS Optional</b>  
>TLS Optional에서는 장치가 TLS 1.1 이상과 연결하지 않을 때 네트워크 통신의 암호화를 강제 실행하지 않습니다. 비TLS 연결을 사용하면 네트워크에 있는 다른 사용자가 디바이스 신임 정보와 민감한 데이터를 볼 수 있습니다. TLS Optional을 통해 전송되는 데이터를 보호할 책임은 전적으로 사용자에게 있습니다.  

저장하고 다시 IBM Cloud Foundry Apps로 돌아옵니다.  
App URL방문을 통해 `Node-Red`를 실행시킵시다.
<img width="636" alt="15" src="https://user-images.githubusercontent.com/15958325/54487078-a4ffb980-48d4-11e9-9125-a4075002f246.PNG">  

가이드에 따라 쭉쭉 진행한 뒤, 에디터 화면을 살펴보면 요상한 그래프들이 많이 보일겁니다. 다 지우고 아래 사진과 같이 세팅해 주세요.  
<img width="467" alt="16" src="https://user-images.githubusercontent.com/15958325/54487079-a4ffb980-48d4-11e9-83f5-2a7c1753c918.PNG">  

IBM IoT노드의 Authentication을 Bluemix Service로 바꿔줍니다. 이는 IBM IoT node가 MQTT브로커와 연결하기위한 credential를 Cloud Foundry credentials injection을 통해 가져오겠다는 뜻입니다.   
<img width="391" alt="17" src="https://user-images.githubusercontent.com/15958325/54487080-a4ffb980-48d4-11e9-8f7c-9f81da08324b.PNG">  
설정이 끝났다면 오른쪽상단의 Deploy버튼을 눌러줍니다.  
이전에 배포했던 IoT app을 디바이스에서 실행시킨 뒤, Debug탭을 눌러 날아오는 msg들을 확인할 수 있습니다.  
<img width="509" alt="18" src="https://user-images.githubusercontent.com/15958325/54487082-a5985000-48d4-11e9-9204-abd787b7c3d1.PNG">  
날아가는 데이터들은 `discover-iot-try-service`의 `Watson IoT Platform`>`Divices`탭에서 확인할 수 있습니다.  
<img width="581" alt="19" src="https://user-images.githubusercontent.com/15958325/54487313-3a507d00-48d8-11e9-923f-69ad118cd00a.PNG"> 

근데 msg가 object타입으로 날아와서 한눈에 알아보기가 힘드네요. function노드를 통해 msg를 꾸며봅시다.  
<img width="471" alt="18 5" src="https://user-images.githubusercontent.com/15958325/54487081-a5985000-48d4-11e9-8667-ea041f2837b0.PNG">   
~~~js
//function에 들어가야 할 부분
msg.payload =
{
X : msg.payload.d.ax,
Y : msg.payload.d.ay,
Z : msg.payload.d.az,
SENSORID : msg.payload.d.id
}
return msg;
~~~
 
날아오는 데이터를 Debug탭에서 확인해보면 바뀐것을 확인할 수 있습니다.  
<img width="189" alt="20" src="https://user-images.githubusercontent.com/15958325/54487314-3a507d00-48d8-11e9-9825-f9dce28eb7a5.PNG">  

이제 클라우드상에 데이터를 저장할 NoSQL DB로서 `Cloudant`를 추가시킵니다. db이름은 아무거나 설정해주시면 됩니다.     
>`IBM Cloudant`는 `ApacheCouchDB`에 기반하고 있습니다.  

<img width="592" alt="cloudant" src="https://user-images.githubusercontent.com/15958325/54487484-d8911280-48d9-11e9-836a-886bf56c73ef.PNG">    
<img width="308" alt="21" src="https://user-images.githubusercontent.com/15958325/54487316-3a507d00-48d8-11e9-9785-e92b9e7560da.PNG">      

추가적으로 데이터가 너무 빨리 송신되는 것을 막기 위해, delay node를 추가적으로 생성해 줍시다.  
<img width="615" alt="delay" src="https://user-images.githubusercontent.com/15958325/54487483-d7f87c00-48d9-11e9-8de7-84ca7cebf47d.PNG">  

노드의 전체 도식도는 다음과 같습니다.  
![image](https://user-images.githubusercontent.com/15958325/54487528-6d940b80-48da-11e9-8810-6a5ddf478869.png)

이제 센서데이터를 송신받아 `Cloudant`에 저장하는 것까지 완성되었습니다!  
하지만 단순히 데이터를 저장만 하는 것은 아무런 의미를 갖지 못합니다. 때문에 데이터를 분석하여 의미있는 값을 도출해 내는 것이 중요합니다.  

## 6. Analyze Data with Watson Studio
### watson studio
>왓슨스튜디오를 처음 사용하는 유저는 먼저 상단의 Upgrade 버튼을 누른 뒤, Watson Studio와 Knowledge Catalog Bundle들을 설치해주세요.  
>![image](https://user-images.githubusercontent.com/15958325/54487624-7a652f00-48db-11e9-8c13-58ef8649aa53.png)

새로운 프로젝트를 생성해 주세요.  
<img width="624" alt="22" src="https://user-images.githubusercontent.com/15958325/54487317-3ae91380-48d8-11e9-8e75-399805a199d3.PNG">  
<img width="625" alt="23" src="https://user-images.githubusercontent.com/15958325/54487318-3ae91380-48d8-11e9-8725-b6781a178de3.PNG">  

프로젝트에 Object Storage를 추가해 줍니다.  
<img width="729" alt="24" src="https://user-images.githubusercontent.com/15958325/54487664-1b53ea00-48dc-11e9-8524-f86a2b2e6e61.PNG">  
<img width="763" alt="25" src="https://user-images.githubusercontent.com/15958325/54487665-1b53ea00-48dc-11e9-8f2c-c48e40c98bd7.PNG">    

추가하고나서 Refresh버튼을 눌러줍니다.  
<img width="731" alt="26" src="https://user-images.githubusercontent.com/15958325/54487666-1b53ea00-48dc-11e9-96d4-9131a84824bb.PNG">   

### add spark
프로젝트를 생성하고 나서, Spark 서비스를 추가시킵니다.  
<img width="779" alt="27" src="https://user-images.githubusercontent.com/15958325/54487668-1b53ea00-48dc-11e9-94f3-285e1beebb9f.PNG">  
<img width="741" alt="28" src="https://user-images.githubusercontent.com/15958325/54487669-1bec8080-48dc-11e9-8a1e-e7b6741e0e4f.PNG">  
프로젝트의 초기 설정은 끝!  

### notebook 

다음은 실제로 어떻게 데이터를 분석할 것인지 정하는 `Notebook`을 구성해봅시다.  
프로젝트 상단에 Add to project버튼을 눌러보면 `Notebook`을 생성하는 버튼이 있습니다.   

이 튜토리얼은 하단의 github링크로부터 `Notebook`을 가져올 것입니다.
~~~
https://raw.githubusercontent.com/romeokienzler/developerWorks/master/boomboomshakeshakesparkv2.ipynb
~~~
![image](https://user-images.githubusercontent.com/15958325/54489749-df784f00-48f2-11e9-8dd8-9f5b6ed9a99a.png)    
runtime은 방금전에 만들었던 spark서비스를 가져옵니다.  

`Notebook`에서 분석용으로 사용할 DB Connection을 만들어줘야 합니다. 다음 사진을 보고 project page로 돌아가줍니다.  
<img width="597" alt="30" src="https://user-images.githubusercontent.com/15958325/54487671-1bec8080-48dc-11e9-8654-39e2dad9fbca.PNG">  
Connection을 클릭하고, 만들었던 Cloudant를 클릭한 뒤, Create버튼을 클릭해줍니다.  
![image](https://user-images.githubusercontent.com/15958325/54487808-8fdb5880-48dd-11e9-9724-44ab6ba7a980.png)  


다시 `Notebook`페이지로 돌아가서 하단의 코드블럭안에 Connection을 Insert합니다.
~~~python
#PLEASE INSERT TO CREDENTIALS TO CLOUDANT HERE USING THE IBM WATSON STUDIO CONNECTIONS TAB RIGHT TO THIS NOTEBOOK
#이곳에 Insert
~~~
<img width="783" alt="34" src="https://user-images.githubusercontent.com/15958325/54487794-6cb0a900-48dd-11e9-99d5-0a1677fb56e9.PNG">

><b>주의</b> : DB를 넣는 코드블럭 밑에 credentials을 참조하는 변수가 있습니다. credentials_1을 변수네임으로써 사용하고 있으므로 Connection을 Insert한 뒤, 이름을 credentials_1로 바꿔주어야 합니다.   

 
코드를 RUN하기 전에 고쳐야할 부분이 몇가지 있습니다. 패키지를 다운로드 받는 부분인 첫번째 코드블럭을 봐주세요.  
~~~python
import pixiedust
pixiedust.installPackage("https://github.com/romeokienzler/developerWorks/raw/master/coursera/spark-sql-cloudant_2.11-2.3.0-SNAPSHOT.jar")
pixiedust.installPackage("com.typesafe:config:1.3.1")
pixiedust.installPackage("com.typesafe.play:play-json_2.11:jar:2.5.9")
pixiedust.installPackage("org.scalaj:scalaj-http_2.11:jar:2.3.0")
pixiedust.installPackage("com.typesafe.play:play-functional_2.11:jar:2.5.9")
~~~

위 코드의 첫줄인 github에서 패키지를 다운로드 받는 부분은 주석처리를 해야합니다.
~~~python
#pixiedust.installPackage("https://github.com/romeokienzler/developerWorks/raw/master/coursera/spark-sql-cloudant_2.11-2.3.0-SNAPSHOT.jar")
~~~
첫번째로 예제로 올라온 링크가 유효하지 않다는 점.  
두번째로 유효한 링크를 넣어도 'NoneType' object has no attribute 'strip' 에러가 발생합니다.  
없애도 정상적으로 돌아갑니다...   
> spark-sql-cloudant_2.11-2.3.0-SNAPSHOT.jar파일이 정확히 어떤 역할을 하고, 없어도 제대로 돌아가는 이유에 대해서는 파악하지 못했습니다.  

다음으로 바꿔야 할 부분은 DB의 네임입니다.  
~~~python
df=spark.read.load({'cloudant의 이름'}, 'org.apache.bahir.cloudant')
df.createOrReplaceTempView('data')
~~~

이 튜토리얼에서 제가 썻던 이름은 harlemshake였으니 다음과 같이 구성될 것입니다.
~~~python
df=spark.read.load('harlemshake', 'org.apache.bahir.cloudant')
df.createOrReplaceTempView('data')
~~~

수정해야할 부분을 수정했다면 Cell>Run All 버튼을 클릭합시다. 
![image](https://user-images.githubusercontent.com/15958325/54489692-46493880-48f2-11e9-8898-573145d558dd.png)  
`Cloudant`에 접속하여 데이터를 전송했던 id들의 리스트가 `Notebook`에서 정의했던 규칙대로 정렬된 모습을 확인할 수 있습니다.  

>에너지 총량 계산 방법 : 
>~~~sql
>select sqrt(sum(X*X)+sum(Y*Y)+sum(Z*Z)) as energy, SENSORID from data group by SENSORID order by energy desc
>~~~
>![image](https://user-images.githubusercontent.com/15958325/54489777-38e07e00-48f3-11e9-93b1-ee0501562af1.png)  
>energy값으로 내림차순
>

-튜토리얼 끗-

----
<img width="100" height="100" src="https://user-images.githubusercontent.com/15958325/54489815-c58b3c00-48f3-11e9-81a1-b2e2afcd0ae7.png"/>