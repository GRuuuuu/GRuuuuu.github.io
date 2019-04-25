---
title: "05.Connect multi validator in local server"
categories: 
  - Sawtooth-Starter
tags:
  - Hyperledger
  - Docker
  - Sawtooth
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: false
sitemap :
  changefreq : daily
  priority : 1.0
sidebar:
  - nav: sawtooth-nav
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`

## 1. Overview
이번 문서에서는 여태까지 단일 validator에서 진행하던 sawtooth network를 키워서 멀-티 validator를 만들어보도록 하겠습니다! 로컬환경에서 진행하겠습니다. 다른 네트워크상에서 이어보는건 다음문서에서!

## 2. Prerequisites

공식 doc에서는 validator를 4개를 사용하여 연결되는 것을 보여주고있습니다.  
--> [참고링크](https://sawtooth.hyperledger.org/docs/core/nightly/master/app_developers_guide/sawtooth-default-poet.yaml)

이 문서에서는 보다 간편하게 설명하기 위해서 validator 2개만 가지고 설명할것임.  
우선 [요걸](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2305%20connect%20multi%20validator%20in%20local/sawtooth-default-poet.yaml) 다운로드 받아주세요

## 3. 일단 실행

다운로드받은 yaml파일이 있는 폴더로 이동해서 shell(이하 shell-1)에서 다음 커맨드를 쳐봅시다
~~~
docker-compose -f sawtooth-default-poet.yaml up
~~~
yaml파일에 미리 기록해두었던 이미지들이 실행될겁니다. 정상적으로 실행된다면 다음과같은 화면이 보일거에요. 

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2305%20connect%20multi%20validator%20in%20local/img/1.PNG)

### 연결확인

지금 켜져있는 shell-1을 끄지말고(로그 확인용) 하나 더켜서(이하 shell-2) bash를 실행
~~~
docker exec -it sawtooth-shell-default bash
~~~

`curl`커맨드로 peer가 제대로 연결되었는지 확인해봅시다.
~~~
curl http://sawtooth-rest-api-default-0:8008/peers
~~~

data에 validator-1이 존재하는 것을 확인할 수 있습니다.  
이는 validator-0(제네시스 블럭)과 validator-1이 연결되어 있다는 의미입니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2305%20connect%20multi%20validator%20in%20local/img/2.PNG)


### xo게임 실행

두개의 validator 실행에 성공하였다면 xo게임생성을 통해 블럭이 쌓이는 모습을 확인해보겠습니다.
~~~
이전 문서를 참고해서 키 만들고 xo게임생성 ㄱㄱ
xo create example --username a --url http://rest-api-0:8008
~~~
>이전 문서에서는 단순히 rest-api:8008만 했지만 yaml 파일을 생성할때 validator0번의 rest-api가 rest-api-0으로 명명되었으므로 이렇게 작성해 주어야함 

실행하게되면 shell-2에는 Response가 오게될 것
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2305%20connect%20multi%20validator%20in%20local/img/3.PNG)

이전에 띄워놓았던 shell-1을 확인해보면 validator 1개를 쓸 때보다 많은양의 로그가 기록되어있는것을 확인할 수 있음. 두개의 validator 모두 검증작업을 진행하기 때문이다.  
>로그의 내용은 따로 설명하지 않을 것. 읽으면 자연스레 알게되는 내용★

두개의 validator 모두 게임이 정상적으로 생성된 것을 확인할 수 있음!

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2305%20connect%20multi%20validator%20in%20local/img/4.PNG)

## 4. YAML파일 뜯어보기

### validator

~~~yaml
  validator-0:                                      //제네시스 블럭
    image: hyperledger/sawtooth-validator:1.0       //이미지 이름
    container_name: sawtooth-validator-default-0    //컨테이너 이름
    expose:                                         //사용할 포트
      - 4004
      - 8800
    command: "bash -c \"\                           //제네시스블럭을 생성
        sawadm keygen --force && \
        sawset genesis \
          -k /etc/sawtooth/keys/validator.priv \
          -o config-genesis.batch && \
        sawset proposal create \
          -k /etc/sawtooth/keys/validator.priv \
          sawtooth.consensus.algorithm=poet \
          sawtooth.poet.report_public_key_pem=\
          \\\"$$(cat /etc/sawtooth/simulator_rk_pub.pem)\\\" \
          sawtooth.poet.valid_enclave_measurements=$$(poet enclave measurement) \
          sawtooth.poet.valid_enclave_basenames=$$(poet enclave basename) \
          -o config.batch && \
        poet registration create -k /etc/sawtooth/keys/validator.priv -o poet.batch && \
        sawset proposal create \
          -k /etc/sawtooth/keys/validator.priv \
             sawtooth.poet.target_wait_time=5 \
             sawtooth.poet.initial_wait_time=25 \
             sawtooth.publisher.max_batches_per_block=100 \
          -o poet-settings.batch && \
        sawadm genesis \
          config-genesis.batch config.batch poet.batch poet-settings.batch && \
        sawtooth-validator -v \                    //validator 설정
          --bind network:tcp://eth0:8800 \         //bind : 포트를 고정시킴
          --bind component:tcp://eth0:4004 \
          --peering dynamic \                      //동적으로 peer를 붙임
          --endpoint tcp://validator-0:8800 \      //작업이 실제로 수행되는 지점
          --scheduler serial \                     //스케줄링은 serial하게(병렬도 있음)
          --network trust                          //신뢰하는 네트워크만
    \""
    environment:                                   //환경변수
      PYTHONPATH: "/project/sawtooth-core/consensus/poet/common:\
        /project/sawtooth-core/consensus/poet/simulator:\
        /project/sawtooth-core/consensus/poet/core"
    stop_signal: SIGKILL                          //종료는 ctrl+c

  validator-1:                                    //제네시스 블럭에 붙을 1번노드   
    image: hyperledger/sawtooth-validator:1.0 
    container_name: sawtooth-validator-default-1
    expose:
      - 4004
      - 8800
    command: |                                    //제네시스 블럭과 달리 블럭을  
      bash -c "                                   //생성할 필요가 없음!!!
        sawadm keygen --force && \
        sawtooth-validator -v \
            --bind network:tcp://eth0:8800 \
            --bind component:tcp://eth0:4004 \
            --peering dynamic \
            --endpoint tcp://validator-1:8800 \
            --seeds tcp://validator-0:8800 \      //붙을 노드의 ip(로컬에서는 이름)
            --scheduler serial \
            --network trust
      "
    environment:
      PYTHONPATH: "/project/sawtooth-core/consensus/poet/common:\
        /project/sawtooth-core/consensus/poet/simulator:\
        /project/sawtooth-core/consensus/poet/core"
    stop_signal: SIGKILL
~~~

### rest-api외 다른 이미지들
~~~yaml
  rest-api-0:                                      //validator에 붙일 이미지의 이름
    image: hyperledger/sawtooth-rest-api:1.0
    container_name: sawtooth-rest-api-default-0
    expose:
      - 4004
      - 8008
    command: |
      bash -c "
        sawtooth-rest-api \
          --connect tcp://validator-0:4004 \      //반드시 해당 블럭의 validator에 connect
          --bind rest-api-0:8008"
    stop_signal: SIGKILL

  rest-api-1:
    image: hyperledger/sawtooth-rest-api:1.0
    container_name: sawtooth-rest-api-default-1
    expose:
      - 4004
      - 8008
    command: |
      bash -c "
        sawtooth-rest-api \
          --connect tcp://validator-1:4004 \
          --bind rest-api-1:8008"
    stop_signal: SIGKILL
    
    ...

  xo-tp-0:
    image: hyperledger/sawtooth-xo-tp-python:1.0
    container_name: sawtooth-xo-tp-python-default-0
    expose:
      - 4004
    command: xo-tp-python -vv -C tcp://validator-0:4004
    stop_signal: SIGKILL

  xo-tp-1:
    image: hyperledger/sawtooth-xo-tp-python:1.0
    container_name: sawtooth-xo-tp-python-default-1
    expose:
      - 4004
    command: xo-tp-python -vv -C tcp://validator-1:4004
    stop_signal: SIGKILL
   
    //나머지 이미지들도 비슷
~~~

## 5. 마치며

여러개의 validator를 로컬 서버안에서 다뤄보는 작업을 하였고, 다음 문서에서는 서로 다른 네트워크상에서 validator를 이어보는 작업을 해볼것

---

---