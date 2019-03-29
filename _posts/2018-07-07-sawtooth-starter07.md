---
title: "07.Make Custom Processor and Connect to Validator"
categories: 
  - Sawtooth-Starter
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`

## 1. Overview
이번 문서에서는 커스텀 프로세서를 만들어 validator에 연결해보도록 하겠습니다. 빠른 진행을 위해 xo게임을 수정해서 붙여보겠습니다.

## 2. Prerequisites

이전문서에서는 validator들을 서로 다른 네트워크에서 이어보는 작업을 진행했습니다. 이번 문서의 작업을 제대로 이해하기 위해서는 이전문서를 꼭 읽어보고 오시기 바랍니당

먼저 [NEWxo.jar](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2307%20making%20custom%20processor/new-xoGAME.jar)와 [Dockerfile](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2307%20making%20custom%20processor/Dockerfile)그리고 [YAML파일](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2307%20making%20custom%20processor/sawtooth-default-poet.yaml)을 다운로드 받아주세요


## 3. 일단 실행

다운로드 받은 폴더에서 yaml 파일을 실행해봅시다.
~~~
docker-compose -f sawtooth-default-poet.yaml up
~~~

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2307%20making%20custom%20processor/img/1.PNG)  
jar파일을 build해서 이미지로 만드는 과정입니다. 이 과정을 통해서 커스텀 프로세서를 구현하고 validator에 붙여 sawtooth 네트워크를 구성할 수 있습니다.

새롭게 추가한 new-xoGAME의 달라진 기능은 별거없습니다. X표시가 A표시로 바뀐것 뿐입니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2307%20making%20custom%20processor/img/2.PNG)  
xo커맨드를 사용하여 게임을 만들고 각 플레이어끼리 게임을 진행한 뒤, 게임판을 show하니 X표시가 A표시로 바뀐 것을 확인할 수 있습니다.


## 4. JAVA to Jar

자바프로그램은 sawtooth sdk예제로 나온 [xo transaction](https://github.com/GRuuuuu/sawtooth-starter/tree/master/sawtooth/%2303%20transaction%20processor%20tutorial/sawtooth/examples/xo)을 사용하였고, X를 저장하는 부분의 코드를 A로 바꿨습니다.  

자바프로그램을 Jar파일로 바꾸는 과정은 인터넷을 참고 ㄱㄱ  
또한 자바프로그램이 제대로 실행되지 않는 파일이라면 당연히 Jar파일을 쓸수없습니당

## 5. Dockerfile 뜯어보기

~~~
FROM anapsix/alpine-java                      //자바
MAINTAINER new-xoGAME:1.0                     //이름:버전
COPY new-xoGAME.jar /home/new-xoGAME.jar      //현재위치폴더의 jar를 docker내 home폴더로 이동시킴
CMD ["java","-cp","/home/new-xoGAME.jar", "src.sawtooth.examples.xo.XoTransactionProcessor","tcp://validator-0:4004"]
//java, -cp, jar파일이름.jar, jar파일내 main이 존재하는 class이름, main의 argument
~~~

main의 argument를 집어넣는 부분은 yaml파일의  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2307%20making%20custom%20processor/img/3.PNG)  
command부분과 형식이 같습니다.  
이 부분은 현재 실행되고있는 validator에 붙이는 부분입니다.

## 6. YAML파일 뜯어보기

### 새로 추가된 new-xoGAME
기본적으로 이전문서의 yaml구성과 비슷합니다. dockerfile을 통해 이미지를 생성하는 방법은 주의깊게 봐주시기 바랍니다.
~~~
  new-xogame-1:
    build:                                    //빌드할것
      context: .
      dockerfile: ./Dockerfile                //현재위치 폴더의 도커파일을 불러옴
    image: sawtooth-new-xogame:1.0
    container_name: new-xogame
    expose:
      - 4004
    ports:
      - "4004:4004"
    stop_signal: SIGKILL
~~~
외에는 똑같음.

## 5. 마치며

생각보다 자료가 정말 없어서 정말 고생했던것 같습니다. 최대한 쉽게 커스텀 프로세서를 추가하는 방법을 다뤄봤습니다. 이제는 원하는 작업을 만들어서 validator에 붙이기만 하면 내가원하는 블럭체인 네트워크 완-성!

---

---