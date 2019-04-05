---
title: "06.Connect multi validator in Remote network"
categories: 
  - Sawtooth-Starter
tags:
  - Hyperledger
  - Docker
  - Sawtooth
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`


## 1. Overview
이번 문서에서는 서로다른 네트워크에서 validator를 연결해보도록 하겠습니다. 

## 2. Prerequisites

이전문서에서는 validator 2개를 로컬환경에서 연결하는 작업을 했었음. 이번 문서의 작업을 제대로 이해하기 위해서는 이전문서를 꼭 읽어보고 오시기 바랍니당

먼저 [제네시스블럭을 생성하는 YAML](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/genesis/sawtooth-default-poet.yaml)과 [기타 validator의 YAML](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/validator/sawtooth-default-poet.yaml)을 다운로드 받아주세요

>이 문서는 포트를 다루고 있기 때문에 로컬환경에서 작업하던 이전 문서와 달리 예상치못한 네트워크 관련 문제가 (매우)많이 생길 수 있습니다.  
실제로 매우매우매우 고생했기 때문에...몇가지 해결방법을 미리 기술합니다.
>
> 1. 방화벽을 확인한다. 방화벽 고급설정의 인바운드 아웃바운드 규칙을 만들어줍시다.
> 2. yaml파일의 bind와 endpoint, seeds 그리고 connect 부분을 확인합니다.
> 3. 사용하는 공유기 또는 컴퓨터의 환경에 따라서 컴퓨터 자체의 로컬ip와(자기 자신을 가리키는) 외부에서 자신을 가리키는 ip가 다를 수 있습니다. 이런 경우에는 yaml파일에서는 자기자신을 가리키는 로컬ip를 사용해야하고 외부에서 블럭의 내용을 볼 때는 외부ip를 사용합니다.
> 4. 공유기를 사용하는 경우-> 일부 공유기는 특정 포트를 막아놓는 경우가 있습니다. 포트포워딩으로 뚫어줍시다.
> 5. [ssh키교환](https://github.com/GRuuuuu/GRuuuuu.github.io/blob/master/_posts/2019-02-19-openshift-rhel01.md#ssh-key-%EA%B5%90%ED%99%98)
> 6. 다했는데 안된다 -> 끄고 자면됨 -> 행복


## 3. 일단 실행

>genesis block이 있는 컴퓨터를 com-1, 기타 validator가 있는 컴퓨터를 com-2로 하겠습니다.

com-1과 com-2에서 다운받은 yaml파일을 실행해봅시다. genesis block을 생성하는 com-1에서 먼저 실행하고 그다음 com-2의 yaml파일을 실행해봅시다.
~~~
docker-compose -f sawtooth-default-poet.yaml up
~~~
yaml파일에 미리 기록해두었던 이미지들이 실행될겁니다. 

com-1에서 실행한 결과:  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/1.png)  
yaml파일에 기술되어있던 이미지들이 handler에 의해 validator에 붙게되고 chain heead를 생성한 뒤, 블럭의 top을 쌓게 됩니다. 그리고 다른 peer나 트랜잭션이 올 때까지 대기하게 됩니다.

com-1의 ip:8008/blocks를 주소창에 쳐보면 블럭이 생성된 모습을 확인할 수 있습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/2.PNG)

com-2에서 실행한 결과(비정상):  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/3.PNG)  
이 뒤로 아무것도 뜨지 않는다면 제대로 연결되지 않았음을 의미합니다.  
원인은 3가지정도가 있는데,  
1. 연결하려는 validator의 ip가 정확하지 않다.
2. 연결하고자하는 컴퓨터의 포트나 내 컴퓨터의 포트가 제대로 열려있지 않다.
3. 연결하고자하는 validator의 준비가 되지 않았다.  
이 경우는 com-2를 먼저 실행하고 com-1을 나중에 실행하는 경우가 되겠네요.

제대로 연결되지 않는다면 블럭이 제대로 생성되지 않아,  
com-2 ip:8008/blocks 을 주소에 쳤을 경우 이런 화면이 뜨게 됩니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/4.PNG)  

com-2에서 실행한 결과(정상):  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/5.PNG)  
위의 결과이후에 block을 building하기 시작합니다. 이러면 com-1과 연결이 성공했음을 알 수 있습니다.  

com-1의 화면을 잠깐 보면  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/6.PNG)  
같은 화면처럼 보이겠지만 두 사진은 서로 다른 네트워크에서 작업한 것입니다. 빨간 밑줄을 친 부분을 보면 block의 검증을 진행하고 검증이 완료되면 블럭을 업데이트하는 모습을 볼 수 있습니다.

그럼 이제 com-2 ip:8008/blocks 을 주소에 쳐보겠습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2306%20connect%20multi%20validator%20in%20remote/img/7.PNG)  
블럭의 길이가 1 증가된 모습을 확인할 수 있습니다. com-1의 blocks도 확인해보면 똑같은 블럭을 갖고 있는 모습을 확인할 수 있습니다.



## 4. YAML파일 뜯어보기

### validator
기본적으로 이전문서의 yaml구성과 비슷합니다. 하지만 정확한 ip를 명시해줘야 한다는 점을 잊으면 안됩니다.
~~~yaml
  validator-0:                                       //com-1의 validator(genesis)
    image: hyperledger/sawtooth-validator:1.0
    container_name: sawtooth-validator-default-0
    expose:
      - 4004
      - 8800
    ports:
      - "8800:8800"
    command: "bash -c \"\
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
        sawtooth-validator -v \
          --bind network:tcp://eth0:8800 \
          --bind component:tcp://eth0:4004 \
          --peering dynamic \
          --endpoint tcp://--.--.--.--:8800         //com-1의 ip주소
    \""
    environment:
      PYTHONPATH: "/project/sawtooth-core/consensus/poet/common:\
        /project/sawtooth-core/consensus/poet/simulator:\
        /project/sawtooth-core/consensus/poet/core"
    stop_signal: SIGKILL
 ~~~
 ~~~yaml 
  validator-1:                                        //com-2의 validator
    image: hyperledger/sawtooth-validator:1.0
    container_name: sawtooth-validator-default-1
    expose:
      - 4004
      - 8800
    ports:
      - "8800:8800"
    command: |
      bash -c "
        sawadm keygen --force && \
        sawtooth-validator -v \
            --bind network:tcp://eth0:8800 \
            --bind component:tcp://eth0:4004 \
            --peering dynamic \
            --endpoint tcp://--.--.--.--:8800 \      //com-2의 ip주소
            --seeds tcp://--.--.--.--:8800 \        //com-1의 ip주소
            --scheduler serial \
            --network trust
      "
    environment:
      PYTHONPATH: "/project/sawtooth-core/consensus/poet/common:\
        /project/sawtooth-core/consensus/poet/simulator:\
        /project/sawtooth-core/consensus/poet/core"
    stop_signal: SIGKILL
~~~
얘네 외에는 똑같음. endpoint에 주의!

## 5. 마치며

validator를 서로다른 네트워크 안에서 이어보는 작업을 하였고, 다음 문서에서는 커스텀이미지(processor)를 구축한 뒤, 실제로 validator에 붙여보는 작업을 할 것!

---

---