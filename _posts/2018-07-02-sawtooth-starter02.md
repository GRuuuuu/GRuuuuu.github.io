---
title: "02.XO Transaction Family"
categories: 
  - Sawtooth-Starter
tags:
  - Hyperledger
  - Docker
  - Sawtooth
last_modified_at: 2019-03-22T13:00:00+09:00
author_profile: true
sitemap :
  changefreq : daily
  priority : 1.0
---
`이 문서는 hyperledger sawtooth 1.0.4을 docker for windows(18.03.01-ce-win65)에서 다루며 os는 window 10 pro임`


## 1. XO게임?
XO는 Sawtooth SDK에 포함되어있는 transaction family 예제임. 쉽게 틱택토라고 생각하면 됨. 2인용 게임이며 보통 3x3크기의 테이블에 한명씩 돌아가면서 마킹을 하게 되고 1줄을 먼저 잇는사람이 우승하는 게임  
틱택토에 대해 더 자세한 설명은 [여기](https://namu.wiki/w/%ED%8B%B1%ED%83%9D%ED%86%A0) 

## 2. Playing XO with the XO Client

### XO게임을 시작하기 전에 필요한것들  
1. 최소 하나의 validator
2. XO family transaction processor
3. The REST API

먼저 sawtooth를 실행해줍니다. 
~~~
% docker-compose -f sawtooth-default.yaml up
~~~

다음 `sawtooth-shell-default bash`를 실행해줍니다.
~~~
% docker exec -it sawtooth-shell-default bash
~~~

### Create Players

게임에 참여할 두명의 플레이어의 키를 생성합니다.
~~~
$ sawtooth keygen jack
$ sawtooth keygen jill
~~~

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/1.png)


### Create a Game

다음으로는 게임을 진행할 게임판을 생성해야합니다.
~~~
$ xo create {Game name} --username jack --url http://rest-api:8008 
~~~
username의 파라미터값으로 온 jack은 Player1이 됩니다.

다음 이미지와 같이 Response가 온다면 제대로 게임이 생성된 것입니다.  
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/3.png)

>간혹 `--url`을 적지 않으면 
>~~~
>Error: Failed to connect to http://127.0.0.1:8008/batches: HTTPConnectionPool(host='127.0.0.1', port=8008): Max retries exceeded with url: /batches (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7f78baf33cc0>: Failed to establish a new connection: [Errno 111] Connection refused',))
>~~~
>이런 오류가 생기는데 url을 적어주면 문제가 해결됩니다.
> 
>XO클라이언트는 부분적으로 인증을 지원합니다. 그래서 REST API가 인증프록시에 연결되어있다면 xo커맨드를 사용할때 `--url`인자를 추가해주어야합니다.

생성한 게임의 리스트를 확인하기 위해서는 다음 커맨드를 사용합니다.

~~~
$ xo list --url http://rest-api:8008 
~~~

![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/4.png)

현재 생성한 게임인 `example`을 확인하기 위해서는 다음 커맨드를 사용합니다.
~~~
$ xo show {Game name} --url http://rest-api:8008 
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/5.png)

현재 게임의 상태 : Player1(Jack)의 차례  
게임판에 아무런 마킹이 없는 것을 확인할 수 있습니다.

### Playing

Player1과 Player2가 차례로 마킹해보도록 하겠습니다.
~~~
$ xo take game 5 --username jack --url http://rest-api:8008
$ xo take game 1 --username jill --url http://rest-api:8008
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/6.png)

~~~
$ xo show {Game name} --url http://rest-api:8008 
~~~
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/7.png)
5번자리와 1번자리에 마킹된 모습을 확인할 수 있습니다.

### Unexpected Event

* 자신의 차례가 아닌데 마킹하려는 경우  
Player1의 차례에 Player2가 마킹을 시도
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/8.png)
요청이 반영되지 않는것을 확인할 수 있다.

* 이미 마킹되어 있는곳에 마킹을 시도  
위와 마찬가지로 요청이 반영되지 않는다.

### Game End

게임이 종료되는 경우는 두가지로 
1. 한 명의 플레이어가 한 줄을 이었을 경우
2. 모든 칸이 마킹되어 더이상 마킹할 칸이 남아있지 않을 경우

Plyaer1이 이긴 경우(P1-WIN)
![Alt text](https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/9.png)

더이상 마킹할 칸이 남아있지 않은 경우(TIE)  
<img src="https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/10.png" height="200px"/>


---

<img width="100" height="100" src="https://raw.githubusercontent.com/GRuuuuu/sawtooth-starter/master/sawtooth/%2302%20xo%20transaction%20family/img/p.png"/>
