---
title: "08.Configuring Permission"
categories: 
  - Sawtooth-Starter
tags:
  - Hyperledger
  - Docker
  - Sawtooth
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for ubuntu(18.03.01-ce)에서 다루며 os는 ubuntu-18.04 LTS임`

## 1. Overview
이번 문서에서는 Transaction과 Batch의 권한 생성 및 설정에 대해서 다뤄보겠습니다.

## 2. Prerequisites

이번 문서부터는 os를 ubuntu환경으로 바꾸었습니다. 도커기반인건 바뀌지 않았지만 core에서 코드를 내려받아서 그대로 실행할것이기 때문에 참고하시기 바랍니다.


먼저 [sawtooth-core](https://github.com/hyperledger/sawtooth-core)를 클론해주세요

폴더 만들고 폴더안에서 다음 커맨드 입력
~~~
git clone https://github.com/hyperledger/sawtooth-core
~~~

## 3. 일단 실행하기 전에

>처음엔 윈도우 환경 하에서 sawtooth-core를 올려보려고 했지만 개발자체가 리눅스 환경하에서 만들어진것같아서 파이썬 소스코드를 실행할 때, 인코딩문제가 좀 있는거 같더군요. 
>
>~~~
>/usr/bin/env: ‘python3\r’: No such file or directory
>~~~ 
>위와 같은 오류에 대해 몇가지 해결방법이 있긴 하지만 생각보다 까다롭고 귀찮아서 os를 리눅스로 바꿨습니다.  
>윈도우 유저분들은 VirtualBox나 Hyper-V와 같은 가상머신을 사용하는 것을 추천합니다. 

>linux에서의 도커설정도 윈도우와 마찬가지입니다. 하나 참고해야할 점은 `docker-compose` 버전이 최신버전이어야 합니다. 제가 core를 돌렸을 때의 버전은 `docker-compose version 1.22.0, build f46880fe` 입니다.

다운로드 받은 폴더에 들어가서 `docker-compose.yaml` 파일을 열어봅시다.
~~~
vim docker-compose.yaml
~~~

현재 `sawtooth-core`내의 `docker-compose.yaml`파일 안에는 identity에 대한 이미지 설정이 들어있지 않습니다.  
>대신 `devmode-rust`라는게 들어가있는데, 이것까지 포함해서 yaml파일을 실행시켜 policy 설정 및 `identity`관련 커맨드를 입력하면 devmode-rust 프로세서는 죽더군요... `poet-engine`이라는 이미지는 실행만하면 죽던데 사실 이 두개의 프로세서의 역할과 왜 죽는지는 해결하지 못했습니다. 추후 알아내면 업데이트하겠습니다.  

우선 `devmode-rust`와 `poet-engine`를 제외하고 `sawtooth-identity`를 추가해서 실행시켜보도록 하겠습니다.  
~~~
  identity-tp:
    build:
      context: .
      dockerfile: families/identity/Dockerfile 
    image: sawtooth-identity-local:${ISOLATION_ID}
    volumes:
      - ./:/project/sawtooth-core
    container_name: sawtooth-identity-local
    depends_on:
      - validator
    command: |
      bash -c "
        bin/protogen
        cd families/identity
        python3 setup.py clean --all
        python3 setup.py build
        identity-tp -vv -C tcp://validator:4004
      "
    stop_signal: SIGKILL
~~~
위와 같은 코드를 `docker-compose.yaml`파일에 추가시킨 뒤, yaml파일을 돌려봅시다.

~~~
docker-compose up
~~~
>docker-compose에 따로 파일이름을 기재하지 않는 이유는 파일이름이 `docker-compose.yaml`이기 때문입니다. 만약 파일이름이 `a.yaml`이라면 
>~~~
>docker-compose -f a.yaml up 
>~~~
>위와 같이 나오겠죠.


## 4. 기다림기다림기다림

파일이 많아서 그런지 아주 오래 기다려야합니다. 

## 5. authorized_keys
블록체인 상에서 다른 transactor들의 권한을 관리할 수 있는 transactor는 (아무런 설정을 하지 않았을 시) genesis block을 서명한 transactor입니다. genesis block을 서명한 transactor는 도커파일을 보면 알 수 있는데,
~~~
    sawadm keygen            //  etc/sawtooth/keys/validator.priv와 pub키생성
    sawtooth keygen          //  root/.sawtooth/keys/root.priv와 pub키생성
    sawset genesis           //root.priv로 서명
    sawadm genesis config-genesis.batch
    sawtooth-validator -v \
        --endpoint tcp://localhost:8800 \
        --bind component:tcp://eth0:4004 \
        --bind network:tcp://eth0:8800 \
        --bind consensus:tcp://eth0:5050 \
~~~
위 코드는 root의 비밀키로 genesis블록을 서명하여 생성합니다. 

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/1.PNG)  
위 사진은 root의 비밀키와 공개키입니다. 다음 사진은 genesis block인데 signer의 공개키가 root의 공개키와 같다는 것을 볼 수 있습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/2.PNG)  

또한 다음사진은 genesis block에 담긴 payload를 Base64 디코딩한 사진입니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/3.PNG)  

`sawtooth.settings.vote.authorized_keys`는 다음과 같은 의미를 지니고 있습니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/4.PNG)  

>쉽게 얘기해서 `sawtooth`의 설정을 변경할 때 `authorized_keys`가 하나일경우 인증받은 키 하나만 동의하면 설정이 변경되고, `authorized_keys`가 여러개일 경우, 일정 퍼센트 이상이 동의해야 설정을 변경할 수 있습니다.

즉 root의 공개키는 `sawtooth`의 설정을 변경할 수 있는 키가 되었다는 것이고, 이제 Transactor와 Validator의 권한설정을 위해 필요한 권한을 원하는 키에 할당해 주어야 합니다.

## 6. allowed_keys
identity 프로세서를 통해 권한을 설정할 수 있는 권한을 가진 키는 
~~~
sawset proposal create sawtooth.identity.allowed_keys=<public key>
~~~ 
를 통해 설정할 수 있습니다.  

`sawtooth`에서 지정할 수 있는 정책은 두가지입니다.  
>PERMIT_KEY <transactor의 공개키>: 허가  
>DENY_KEY <transactor의 공개키>: 거절  

현재 `sawtooth`에서 설정할 수 있는 Transactor의 role은 5개로 다음과 같습니다.

>default:  
>   기본 설정은 "PERMIT_KEY *" 임. 특정 role을 지정해주지 않았다면 default가 됨.
>
>transactor:  
>   transaction과 batch를 서명할 수 있는 최상위 role. 만약 transactor에 DENY_KEY를 준다면 transactor와 batch에 관한 요청 모두 거절됨.
>
>transactor.transaction_signer:  
>   transaction의 서명에 관한 role
>
>transactor.transaction_signer.{tp_name}:  
>   특정 transaction processor(Family)의 서명에 관한 role
>
>transactor.batch_signer:  
>   batch의 서명에 관한 role
>

role에 정책을 적용할 때는 다음과 같이 작성합니다.
~~~
transactor.SUB_ROLE = POLICY_NAME
~~~

>예시)  
>sawtooth identity policy create policy_1 "DENY_KEY *"  
>sawtooth identity role create transactor policy_1  
>  
>모든 키에대해 DENY하는 정책인 policy_1을 만들고, policy_1을 transaction과 batch를 서명할 수 있는 최상위 role에 부여합니다.  
>이러면 모든 키는 transaction과 batch에 서명할 수 없게 됩니다.(본인포함)

정말 주의해야할 점은, policy는 순차적으로 적용된다는 것입니다. (if-else를 생각하면 이해가 쉬움.)  

예시1)
1. a,b,c의 키쌍이 있음
2. a,b,c의 <공개키>를 이용해 정책을 만듬 
3. DENY_KEY a => transactor에 적용(위 예시참고)
4. 우리 모두의 생각: a만 transactor에 관한 권한이 DENY되겠지, b와 c는 PERMIT일거야
5. 현실: 전부 DENY됨

예시2)  
1. a,b,c의 키쌍이 있음
2. 각 공개키를 사용해 정책을 만들것
3. DENY_KEY a, PERMIT_KEY *, DENY_KEY b 의 정책을 만든 뒤
4. DENY_KEY a  
PERMIT_KEY *  
DENY_KEY b  의 순으로 transactor에 정책 적용
5. 예상: a와 b는 DENY되고 c는 PERMIT될거야!
6. 현실: a만 DENY되고 b와 c는 PERMIT됨

위의 두 예시를 잘 보면 순서대로 정책이 적용되는 것을 볼 수 있습니다. switch-case처럼 해당되는 정책에 빨려들어가서 break가 걸려서 switch문을 빠져나오는것과 같습니다.

예시2를 실제로 실행해봅시다. 이전에 authorized_keys로 설정된 키로 allowed_keys를 설정해줄겁니다.
~~~
sawset proposal create sawtooth.identity.allowed_keys=038d91da5969ac3958649a25b27165c78c1ee46a3bc93aecea660a47a843bd5b6d --url http://rest-api:8008
~~~
현재 문서에서는 authorized_keys는 genesis 블록을 서명한 root입니다. 

>sawset를 통해 제안하는 커맨드의 default 키설정은 root/.sawtooth/keys의 root.priv입니다. 따라서 위와 똑같은 커맨드를 작성하려면 root/.sawtooth/keys의 root가 authorized되어야하며 커맨드를 입력하는 폴더가 root/.sawtooth/keys 안이어야 합니다. 
> 
>만약, root.priv가 아닌 다른 키로 설정하려면 다음과 같이 -k 옵션을 달아주면 됩니다.
>~~~
>sawset proposal create sawtooth.identity.allowed_keys=<공개키> -k 설정하려고하는 다른키의 위치/다른키.priv --url ...
>~~~  


~~~
sawtooth keygen a
...
~~~
a,b,c의 키를 생성한 뒤, 예제2와같이 정책을 설정

~~~
sawtooth identity policy create p1 "DENY_KEY <a공개키>" "PERMIT_KEY *" "DENY_KEY <b공개키>" --url http://rest-api:8008
~~~

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/5.PNG)  
~~~
sawtooth identity policy list --url http://rest-api:8008
~~~
위와같은 커맨드를 통해 현재 만들어진 정책들의 list를 볼 수 있습니다.  

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/6.PNG)  
예제2와같이 transactor에 정책을 설정해주고 
~~~
sawtooth identity role list --url http://rest-api:8008
~~~
위와같은 커맨드를 통해 현재 설정된 role의 list를 볼 수 있습니다.

그럼 테스트로 xo게임을 create하는 트랜잭션을 만들어 보겠습니다. 예제2의 예상대로면 a와 b는 트랜잭션이 거절되어야하고 c만 xo게임이 만들어져야 합니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2308%20configuring%20permission/img/7.PNG)  
하지만 a의 트랜잭션만 거절되고 나머지 b와 c는 제대로 트랜잭션이 들어간 것을 확인할 수 있습니다.



---


현재 `sawtooth`에서 설정할 수 있는 Validator의 role은 2개로 다음과 같습니다.

>network:  
>peer를 붙이는(현재 validator에 붙으려는 요청)요청이 올 때, 그 요청을 보내는 public key가 policy에 의하여 거절되었다면 이 요청은 거절되고 `AuthorizationViolation` 메세지가 리턴되고 커넥션은 끊어지게 됩니다.
>  
>network.consensus:  
>validator가 새로운 블록을 만들자는 GossipMessage를 받았을 때, 그 요청을 보내는 public key가 policy에 의해 거절되었다면 요청거절->`AuthorizationViolation` 메세지가 리턴되고 커넥션 종료
>  
>



## 7. 마치며

공식doc를 열심히 봅시다^^.... 

---

---