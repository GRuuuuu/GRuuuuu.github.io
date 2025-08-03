---
title: "03.Transaction Processor Tutorial Java 1"
tags: ["Hyperledger", "Docker", "Sawtooth"]
series: ["Sawtooth-Starter"]
series_order: 3
date: 2018-07-03
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`

## 1. Overview
이전 문서에서는 xo게임을 powershell환경에서 실행해보는것을 해봤습니다. 이번 문서에서는 Sawtooth SDK에 기반하여 Java언어로 구성된 Sawtooth transaction family를 다뤄보겠습니다. 소스코드에 관한 자세한 설명은 다음문서에서 계속!
>첨부된 sdk폴더에는 xo게임의 완전히 구현된 버전이 포함되어있습니다. 이번 문서와 다음문서에서는 완전한 구현을 만드는 대신 만들어진 소스코드의 개념을 설명하는 것에 초점을 맞췄습니다. SDK는 여러 언어로 구성되어있으므로 [여기](https://sawtooth.hyperledger.org/docs/core/releases/1.0/app_developers_guide/sdk_table.html) 를 참조해주세요.

## 2. Prerequisites

[이전문서](https://gruuuuu.github.io/sawtooth-starter/sawtooth-starter02/)에서 xo게임을 실행까지 성공하고 따라해주세요.

### Download Java sdk

>Intellij에서 프로젝트를 만들었습니다.

첨부된 sawtooth폴더와 protos폴더, `pom.xml`를 다운로드  
첨부된 파일들은 [이곳](https://github.com/GRuuuuu/sawtooth-starter/tree/master/sawtooth/%2303%20transaction%20processor%20tutorial)을 참고  

Java project를 생성한 뒤, sawtooth폴더는 src밑으로, protos와 pom.xml은 각각 알아서 추가해줍시다.

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/1.PNG)

프로젝트 구성을 마치고나서 build하게되면 pom.xml에 적힌 dependancy가 외부라이브러리로 다운받아지게되고 소스코드의 빨간줄이 사라지게 됩니다. (야-호!) 

>이 구성을 제대로 설명해둔데가 없어서 매우 고생함^^

### Address Setting

자바 프로그램을 빌드하기 전, main파라미터의 값으로 sawtooth가 돌아가고있는 도커의 ip와 포트를 적어줘야 합니다.  

~~~java
 TransactionProcessor transactionProcessor = new TransactionProcessor("tcp://validator의ip(도커의ip):4004");
~~~

만약 로컬에서 돌리고있다면 이렇게 적어주면 됩니다.
~~~java
 TransactionProcessor transactionProcessor = new TransactionProcessor("tcp://localhost:4004");
~~~

## 3. Run

### Run program

`sawtooth-shell-default bash`가 실행되고 있는 상태부터 시작  
구성을 끝낸 뒤의 자바 프로그램을 실행해봅시다.  
현재는 아무런 트랜잭션이 오고가고 있지 않으므로 빈 화면입니다.
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/2.PNG)


두명의 플레이어의 key를 구성해준뒤, 게임판을 만들어봅시다.
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/3.PNG)
자바 프로그램에 game을 만들었다는 화면이 디스플레이 됩니다.

다음 첫번째 플레이어부터 마킹을 시작해봅시다.
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/4.PNG)
java프로그램에서 트랜잭션의 결과를 확인할 수 있습니다.

트랜잭션이 실패하였을 때 exception처리도 이곳에서 확인할 수 있습니다.
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/5.PNG)


---

<img width="100" height="100" src="https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2303%20transaction%20processor%20tutorial/img/p.png"/>
