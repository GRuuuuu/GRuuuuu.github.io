---
title: "01.hyperledger sawtooth를 docker for window에서 돌릴수있게 해보자!"
draft: false
description: "01.hyperledger sawtooth를 docker for window에서 돌릴수있게 해보자!"
tags: ["Hyperledger", "Docker", "Sawtooth"]
series: ["Sawtooth-Starter"]
series_order: 1
date: 2018-07-01
---

`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`

## 1. Docker for windows설치

[Install Docker for windows](https://docs.docker.com/docker-for-windows/install/) 



## 2. Starting Sawtooth

도커의 초기설정이 끝나고 도커를 켜기 전에
원하는 위치에 폴더를 생성합니다.  
이후, 이 문서에 첨부되어있는 [sawtooth-default.yaml](https://github.com/GRuuuuu/sawtooth-starter/blob/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/sawtooth-default.yaml)을 
생성한 폴더에 다운받아 주세요. 

그다음 도커를 실행해보도록 하겠습니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/1.png)

powershell이든 cmd이든 상관없지만 이 문서에서는 
Windows PowerShell을 사용하도록 하겠습니다.  
  

다음 커맨드를 실행하여 Sawtooth이미지를 다운받습니다. 주의 해야할 점은 이 커맨드를 사용할 폴더에 sawtooth-default.yaml이 있어야 합니다.  
```
% docker-compose -f sawtooth-default.yaml up
```
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/2.png)


전부 다운이 받아지면 docker의 kitematic을 켜서 확인할 수 있습니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/3.png)  
돌아가고있는것을 확인할 수 있습니다.  

## 3. Stopping Sawtooth

sawtooth를 종료하려면 `CTRL-c`를 몇 회 누른 뒤,  
~~~
% docker-compose -f sawtooth-default.yaml down
~~~
커맨드를 입력합니다. 이를 통해 완전히 종료할 수 있습니다.

## 4. Logging Into The Client Contatiner

이 커맨드를 통해 sawtooth가 실행중인 상태여야 합니다.
~~~
% docker-compose -f sawtooth-default.yaml up
~~~


sawtooth가 실행중인 상태에서 다음 커맨드를 통해 client container에 접근할 수 있습니다.
~~~
% docker exec -it sawtooth-shell-default bash
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/4.png) 
root~~~이런식으로 실행되면 성공입니다  

### Confirming Connectivity

Validator가 동작중인것을 확인하기 위해 root에서 `curl`커맨드를 사용할 수 있습니다.
~~~
/# curl http://rest-api:8008/blocks
~~~
만약 validator가 실행중이고 접근이 가능하다면 output은 이런식으로 비슷하게 출력될 것입니다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/5.png) 

만약 validator에 문제가 있다면 `curl`커맨드는 타임아웃하거나 아무것도 반환하지 않을것입니다.

## 5. Using Sawtooth Commands

### Creating and Submitting Transactions with intkey

`intkey` 커맨드는 간단한 샘플 트랜잭션을 생성하여 테스팅할수있게 합니다. `intkey`커맨드는 뭔가 엄청 중요한 커맨드가 아니라 단순히 테스팅하는 용도로 사용하는 커맨드라고 생각하면 조금 머리가 편해집니다.

다음 스텝은 `intkey`를 사용하여 intkey transactions의 랜덤값을 가진 몇개의 key로 구성된 배치파일을 생성하게됩니다. 이 배치파일은 로컬에 저장되고 validator에 전달합니다.
~~~
$ intkey create_batch --count 10 --key-count 5
$ intkey load -f batches.intkey -U http://rest-api:8008
~~~

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/6.png) 

### Viewing the List of Blocks & Particular Block

다음 커맨드를 통해 블록의 리스트를 확인할 수 있습니다.
~~~
$ sawtooth block list --url http://rest-api:8008
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/7.png) 
방금전에 사용했던 intkey커맨드의 결과로 생성된 블록들을 확인할 수 있습니다.

특정 블록의 상태를 확인하고 싶다면 다음 커맨드를 이용합니다. BLOCK_ID에는 리스트에서 확인한 아이디중 하나를 집어넣으면 됩니다.
~~~
$ sawtooth block show --url http://rest-api:8008 {BLOCK_ID}
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/8.png) 
블럭의 상태를 확인할 수 있습니다. 헤더, 헤더의 시그니처, 트랜잭션등을 확인할 수 있습니다.

### Viewing Global State

다음 커맨드로 머클트리의 노드리스트를 확인할 수 있습니다.
~~~
$ sawtooth state list --url http://rest-api:8008
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/9.png) 

### Viewing Data at an Address
`sawtooth state list`커맨드를 통해 나온 address로 data를 확인할 수 있습니다.
~~~
$ sawtooth state show --url http://rest-api:8008 {STATE_ADDRESS}
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/10.png) 

## 6. Connecting to the REST API
`curl`를 사용해 REST API에 접근할 수 있습니다. 

### From Client Containter
클라이언트 컨테이너에서는 다음 커맨드를 사용합니다.
~~~
$ curl http://rest-api:8008/blocks
~~~

### From Host Operating System
호스트 시스템에서는 다음 커맨드를 사용합니다.
~~~
$ curl http://localhost:8008/blocks
~~~


## 7. Connecting to Each Container

### The Client Container

* 트랜잭션 submit
* sawtooth 커맨드 실행
* Container name : `sawtooth-shell-default`

~~~
% docker exec -it sawtooth-shell-default bash
~~~

### The Validator Container

* 단일 Validator 실행
* port 4004(default)에서 사용가능
* Hostname : `validator`
* Container name : `sawtooth-validator-default`

~~~
$ docker exec -it sawtooth-validator-default bash
~~~

### The REST API Container

* REST API 실행
* port 8008에서 사용가능
* Container name : `sawtooth-rest-api-default`

~~~
$ docker exec -it sawtooth-rest-api-default bash
~~~

### The Settings Transaction Processor Container

* 단일 Setting Transaction 프로세서 실행
* Setting Transaction 패밀리의 트랜잭션을 다룸
* Hostname : `settings-tp`
* Container name : `sawtooth-settings-tp-default`

~~~
$ docker exec -it sawtooth-settings-tp-default bash
~~~

### The IntegerKey Transaction Processor Container

* 단일 IntegerKey Transaction 프로세서 실행
* IntegerKey Transaction 패밀리의 트랜잭션을 다룸
* Hostname : `intkey-tp-python`
* Container name : `sawtooth-intkey-tp-python-default`

~~~
$ docker exec -it sawtooth-intkey-tp-python-default bash
~~~

### The XO Transaction Processor Container

* 단일 XO Transaction 프로세서 실행
* XO Transaction 패밀리의 트랜잭션을 다룸
* Hostname : `xo-tp-python`
* Container name : `sawtooth-xo-tp-python-default`

~~~
$ docker exec -it sawtooth-xo-tp-python-default bash
~~~

위의 컴포넌트가 실행되고있는 것을 확인하려면 `ps`커맨드를 사용
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/12.png) 



## 8. Viewing Log Files

로그파일을 보기 위해서는 다음 커맨드를 사용  
`{CONTAINER}`에는 `sawtooth-validator-default`같은 컨테이너 이름이 들어가야한다.
~~~
$ docker logs {CONTAINER}
~~~

## 9. 마치며

본 문서는 [hyperledger sawtooth docs](https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/docker.html) 의 튜토리얼을 보고 따라해본 문서입니당

---

<img width="100" height="100" src="https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2301%20using%20sawtooth%20with%20docker/img/p.png"/>